import sounddevice as sd
import numpy as np
import time

# --- CALIBRAÇÃO DO RELÓGIO E RADAR ---
TAXA_AMOSTRAGEM = 44100
BLOCO_AUDIO = 1024         
LIMIAR_VOLUME = 5.0
MARGEM_HZ = 50             

DURACAO_SOM = 0.20
MEIO_DO_SOM = 0.10         

# --- VARIÁVEIS DA MÁQUINA DE ESTADO TEMPORAL ---
state = "WAITING_SYNC"     
sync_time = 0.0            
tempo_inicio_rx = 0.0      # NOVO: Regista o instante exato em que a receção começa
simbolos_lidos = 0         
bit_buffer = []
total_simbolos_esperados = None 

is_paused = True           # NOVO: Inicia sempre pausado por segurança
esperando_silencio = False 

resultado_validacao = ""
ultima_mensagem_tempo = 0.0
historico_quadros = []

def mapear_frequencia(freq):
    if abs(freq - 800) <= MARGEM_HZ: return [0, 0, 0, 0]
    if abs(freq - 1000) <= MARGEM_HZ: return [0, 0, 0, 1]
    if abs(freq - 1200) <= MARGEM_HZ: return [0, 0, 1, 0]
    if abs(freq - 1400) <= MARGEM_HZ: return [0, 0, 1, 1]
    if abs(freq - 1600) <= MARGEM_HZ: return [0, 1, 0, 0]
    if abs(freq - 1800) <= MARGEM_HZ: return [0, 1, 0, 1]
    if abs(freq - 2000) <= MARGEM_HZ: return [0, 1, 1, 0]
    if abs(freq - 2200) <= MARGEM_HZ: return [0, 1, 1, 1]
    if abs(freq - 2400) <= MARGEM_HZ: return [1, 0, 0, 0]
    if abs(freq - 2600) <= MARGEM_HZ: return [1, 0, 0, 1]
    if abs(freq - 2800) <= MARGEM_HZ: return [1, 0, 1, 0]
    if abs(freq - 3000) <= MARGEM_HZ: return [1, 0, 1, 1]
    if abs(freq - 3200) <= MARGEM_HZ: return [1, 1, 0, 0]
    if abs(freq - 3400) <= MARGEM_HZ: return [1, 1, 0, 1]
    if abs(freq - 3600) <= MARGEM_HZ: return [1, 1, 1, 0]
    if abs(freq - 3800) <= MARGEM_HZ: return [1, 1, 1, 1]
    return None

def validar_quadro_dinamico(frame_bits, tempo_transmissao):
    global resultado_validacao, ultima_mensagem_tempo, historico_quadros
    
    if len(frame_bits) < 16:
        return
    
    bits_tamanho = frame_bits[:8]
    bits_soma = frame_bits[-8:]
    dados = frame_bits[8:-8]
    
    tamanho_recebido = int("".join(str(b) for b in bits_tamanho), 2)
    soma_recebida = int("".join(str(b) for b in bits_soma), 2)
    soma_real_dados = sum(dados)
    
    sucesso = (soma_real_dados == soma_recebida and len(dados) == tamanho_recebido)
    
    try:
        bytes_dados = [dados[i:i+8] for i in range(0, len(dados), 8)]
        texto_final = "".join([chr(int("".join(str(b) for b in byte), 2)) for byte in bytes_dados])
    except:
        texto_final = "???"

    # Se falhar, sobrepõe a mensagem com ERRO para a interface
    texto_historico = texto_final if sucesso else "ERRO"

    if sucesso:
        resultado_validacao = f"[SUCESSO] Tempo: {tempo_transmissao:.2f}s"
        print(f"\n{resultado_validacao}")
    else:
        resultado_validacao = f"[FALHA] Falha na integridade dos dados."
        print(f"\n{resultado_validacao}")
        
    ultima_mensagem_tempo = time.time()
    
    # Guarda todos os metadados necessários para a inspeção forense na interface
    historico_quadros.append({
        "texto": texto_historico, 
        "sucesso": sucesso,
        "bits": list(frame_bits),
        "tempo": tempo_transmissao
    })
    
    if len(historico_quadros) > 5: historico_quadros.pop(0)

def processar_audio_fsk(indata, frames, time_info, status):
    global state, sync_time, tempo_inicio_rx, simbolos_lidos, bit_buffer, esperando_silencio, is_paused, total_simbolos_esperados
    
    if is_paused:
        return
        
    volume = np.linalg.norm(indata) * 10
    if volume < LIMIAR_VOLUME:
        if state == "WAITING_DATA_START" or state == "RECEIVING_DATA":
            state = "WAITING_SYNC"
            esperando_silencio = False
            bit_buffer.clear()
        return 
        
    espectro = np.abs(np.fft.rfft(indata[:, 0]))
    frequencias = np.fft.rfftfreq(frames, 1.0 / TAXA_AMOSTRAGEM)
    frequencia_pico = frequencias[np.argmax(espectro)]
    tempo_atual = time.time()

    if state == "WAITING_SYNC":
        if abs(frequencia_pico - 4000) <= 150: 
            print("\n[SISTEMA] Preâmbulo detectado (4000 Hz). Aguardando Descida...")
            state = "WAITING_DATA_START"
            
    elif state == "WAITING_DATA_START":
        if abs(frequencia_pico - 4000) > 200:
            par_bits = mapear_frequencia(frequencia_pico)
            if par_bits is not None:
                sync_time = tempo_atual
                tempo_inicio_rx = tempo_atual # Dispara o relógio de transmissão total
                bit_buffer.clear()
                bit_buffer.extend(par_bits)
                simbolos_lidos = 1
                total_simbolos_esperados = None
                state = "RECEIVING_DATA"
                esperando_silencio = True
                
    elif state == "RECEIVING_DATA":
        tempo_decorrido = tempo_atual - sync_time
        alvo_temporal = (simbolos_lidos * DURACAO_SOM) + MEIO_DO_SOM
        
        timeout = (total_simbolos_esperados * DURACAO_SOM) + 1.0 if total_simbolos_esperados else 30
        if tempo_decorrido > timeout:
            print("[ALERTA] Timeout! Áudio incompleto.")
            state = "WAITING_SYNC"
            esperando_silencio = False
            is_paused = True # Auto-pause por falha
            return
        
        if tempo_decorrido >= alvo_temporal:
            par_bits = mapear_frequencia(frequencia_pico)
            if par_bits is not None:
                bit_buffer.extend(par_bits)
            else:
                bit_buffer.extend([1, 1, 1, 1]) 
                
            simbolos_lidos += 1
            
            if simbolos_lidos == 2:
                bits_tamanho = bit_buffer[:8]
                tamanho_bits_dados = int("".join(str(b) for b in bits_tamanho), 2)
                total_simbolos_esperados = 2 + (tamanho_bits_dados // 4) + 2
            
            if total_simbolos_esperados is not None and simbolos_lidos == total_simbolos_esperados:
                tempo_total_tx = (time.time() - tempo_inicio_rx) + DURACAO_SOM
                validar_quadro_dinamico(bit_buffer, tempo_total_tx)
                bit_buffer.clear()
                state = "WAITING_SYNC"
                esperando_silencio = False
                is_paused = True # AUTO-PAUSE SUCESSO: Desliga a escuta automaticamente

if __name__ == "__main__":
    print("Motor Síncrono 16-FSK (Dinâmico) Iniciado.")
    try:
        with sd.InputStream(callback=processar_audio_fsk, channels=1, samplerate=TAXA_AMOSTRAGEM, blocksize=BLOCO_AUDIO):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        pass