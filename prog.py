import sounddevice as sd
import numpy as np
import time

TAXA_AMOSTRAGEM = 44100
BLOCO_AUDIO = 1024

# CALIBRAÇÃO FÍSICA DO AMBIENTE
LIMIAR_VOLUME = 0.10       # Baixo o suficiente para ouvir; alto o suficiente para ignorar ruído branco
DEBOUNCE_ECO = 0.20        # Tempo cego após um estalo para ignorar ecos da sala
JANELA_BIT_1 = 0.55        # Tempo máximo permitido para a segunda batida (Bit 1)
JANELA_SILENCIO = 0.80     # Tempo de silêncio necessário para fechar/confirmar o bit

state = "WAITING_START"
bit_buffer = []
historico_quadros = []
resultado_validacao = ""
ultima_mensagem_tempo = 0.0

is_paused = True
_foi_pausado_antes = True

tempo_ultima_batida = 0.0
contador_batidas_no_bit = 0
estagio_bit = "AGUARDANDO_PRIMEIRA"
tempo_inicio_escuta = 0.0  

def validar_quadro_paridade(bits):
    global resultado_validacao, ultima_mensagem_tempo, historico_quadros
    if len(bits) < 9:
        return
        
    dados = bits[:8]
    bit_paridade_recebido = bits[8]
    
    uns = dados.count(1)
    paridade_calculada = 0 if uns % 2 == 0 else 1
    
    sucesso = (paridade_calculada == bit_paridade_recebido)
    
    try:
        bytes_dados = [dados[i:i+8] for i in range(0, len(dados), 8)]
        texto_final = "".join([chr(int("".join(str(b) for b in byte), 2)) for byte in bytes_dados])
    except:
        texto_final = "???"

    if sucesso:
        resultado_validacao = f"[SUCESSO] Bits íntegros: '{texto_final}'"
    else:
        resultado_validacao = f"[FALHA] Erro de Paridade Par detectado!"
        
    print(f"\n{resultado_validacao}")
    ultima_mensagem_tempo = time.time()
    
    historico_quadros.append({
        "bits": list(bits),
        "sucesso": sucesso
    })
    if len(historico_quadros) > 5: historico_quadros.pop(0)

def process_audio_stream(indata, frames, time_info, status):
    global state, bit_buffer, tempo_ultima_batida, contador_batidas_no_bit
    global estagio_bit, is_paused, tempo_inicio_escuta, _foi_pausado_antes
    
    if is_paused:
        _foi_pausado_antes = True 
        return
        
    tempo_atual = time.time()
    
    if _foi_pausado_antes:
        tempo_inicio_escuta = tempo_atual
        _foi_pausado_antes = False
        print("[SISTEMA] Escuta ativada. Calibrado para cadência humana.")
        
    # Bloqueio de clique do mouse inicial
    if tempo_atual - tempo_inicio_escuta < 0.8:
        return

    # Usamos percentil 95 em vez do pico absoluto (np.max). 
    # Isso evita que um único "estalo elétrico" na placa de som engane o microfone.
    energia_impacto = np.percentile(np.abs(indata), 95)
    
    if energia_impacto > LIMIAR_VOLUME:
        if tempo_atual - tempo_ultima_batida > DEBOUNCE_ECO: 
            if estagio_bit == "AGUARDANDO_PRIMEIRA":
                tempo_ultima_batida = tempo_atual
                contador_batidas_no_bit = 1
                estagio_bit = "COLETANDO_SEGUNDA"
                print("\n[*] Impacto 1...")
            elif estagio_bit == "COLETANDO_SEGUNDA":
                if tempo_atual - tempo_ultima_batida <= JANELA_BIT_1: 
                    contador_batidas_no_bit = 2
                    tempo_ultima_batida = tempo_atual
                    print("[*] Impacto 2...")
                    
    # Lógica de fechamento de Bit pelo Silêncio
    if estagio_bit == "COLETANDO_SEGUNDA" and (tempo_atual - tempo_ultima_batida > JANELA_SILENCIO):
        bit_lido = 0 if contador_batidas_no_bit == 1 else 1
        bit_buffer.append(bit_lido)
        
        print(f"[RECEPTOR] => Bit {bit_lido}")
        
        contador_batidas_no_bit = 0
        estagio_bit = "AGUARDANDO_PRIMEIRA"
        
        if len(bit_buffer) == 9:
            validar_quadro_paridade(bit_buffer)
            bit_buffer.clear()
            is_paused = True