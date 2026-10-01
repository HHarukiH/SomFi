import sounddevice as sd
import numpy as np
import time

# --- PARÂMETROS DE CALIBRAÇÃO ---
THRESHOLD_AMPLITUDE = 20.0  # Limiar de corte de ruído
DEBOUNCE_TIME = 0.2        # Supressão de eco mecânico (segundos)
BIT_1_MAX_GAP = 0.6        # Tempo máximo entre duas batidas para virar um Bit 1
BIT_0_TIMEOUT = 0.8        # Tempo de silêncio para fechar um Bit 0

# --- VARIÁVEIS GLOBAIS DE ESTADO (Motor) ---
last_impact_time = 0.0
state = "IDLE"
bit_buffer = []

# --- VARIÁVEIS GLOBAIS DE ESTADO (Interface) ---
resultado_validacao = ""
ultima_mensagem_tempo = 0.0
historico_quadros = []

def validate_frame(frame_bits):
    """
    Recorta os 8 primeiros bits, calcula a paridade e compara com o 9º bit recebido.
    """
    global resultado_validacao, ultima_mensagem_tempo, historico_quadros
    
    dados = frame_bits[:8]
    bit_paridade_recebido = frame_bits[8]
    
    qtd_uns = sum(dados)
    paridade_esperada = 0 if qtd_uns % 2 == 0 else 1
    
    sucesso = (paridade_esperada == bit_paridade_recebido)
    bits_str = "".join(str(b) for b in frame_bits)
    
    if sucesso:
        resultado_validacao = f"[SUCESSO] Dados: {bits_str[:8]} | Par.: {bit_paridade_recebido}"
        print(f"\n[SUCESSO] Quadro íntegro. Paridade confere.")
    else:
        resultado_validacao = f"[FALHA] Recebido: {bits_str} | Esp: {paridade_esperada}"
        print(f"\n[FALHA] Corrupção. Esperado: {paridade_esperada}, Recebido: {bit_paridade_recebido}")
        
    ultima_mensagem_tempo = time.time()
    
    # Grava uma cópia da lista na memória para a tabela do histórico
    historico_quadros.append({
        "bits": list(frame_bits), 
        "sucesso": sucesso
    })
    
    if len(historico_quadros) > 4:
        historico_quadros.pop(0)

def process_audio_stream(indata, frames, time_info, status):
    """Callback assíncrono que extrai os bits através do volume e do tempo."""
    global last_impact_time, state, bit_buffer
    
    amplitude = np.linalg.norm(indata) * 10
    current_time = time.time()
    delta_time = current_time - last_impact_time
    
    # 1. DETECÇÃO DE IMPACTO
    if amplitude > THRESHOLD_AMPLITUDE and delta_time > DEBOUNCE_TIME:
        if state == "IDLE":
            state = "WAITING_SECOND"
            last_impact_time = current_time
            print(f"[SINAL] Batida 1 (Amp: {amplitude:.2f})")
            
        elif state == "WAITING_SECOND":
            if delta_time <= BIT_1_MAX_GAP:
                bit_buffer.append(1)
                print(">>> BIT 1 Registrado")
                state = "IDLE"
                last_impact_time = current_time
                
    # 2. DETECÇÃO DE SILÊNCIO
    if state == "WAITING_SECOND" and (current_time - last_impact_time) > BIT_0_TIMEOUT:
        bit_buffer.append(0)
        print(">>> BIT 0 Registrado")
        state = "IDLE"
        
    # 3. VERIFICAÇÃO DO QUADRO
    if len(bit_buffer) == 9:
        validate_frame(bit_buffer)
        bit_buffer.clear()

if __name__ == "__main__":
    print("Motor Acústico Iniciado em Modo Texto. (Pressione Ctrl+C para encerrar)")
    try:
        with sd.InputStream(callback=process_audio_stream, channels=1, samplerate=44100):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\nRecepção encerrada.")