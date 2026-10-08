import sounddevice as sd
import numpy as np
import time

# --- CALIBRAÇÃO DO RELÓGIO E RADAR ---
TAXA_AMOSTRAGEM = 44100
BLOCO_AUDIO = 1024         # [AJUSTADO] Resolução 2x mais rápida (~23 milissegundos por foto)
LIMIAR_VOLUME = 5.0
MARGEM_HZ = 50             # [AJUSTADO] Margem maior para tolerar a distorção do alto-falante do celular

DURACAO_SOM = 0.20
MEIO_DO_SOM = 0.10         # O "miolo" perfeito da nota musical, longe da fronteira de transição

# --- VARIÁVEIS DA MÁQUINA DE ESTADO TEMPORAL ---
state = "WAITING_SYNC"     # Estados: WAITING_SYNC -> WAITING_DATA_START -> RECEIVING_DATA
sync_time = 0.0            
simbolos_lidos = 0         
bit_buffer = []

is_paused = False
esperando_silencio = False # Mantido apenas para a interface acender o estado ocupado

# Variáveis da GUI
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

def validar_quadro_soma(frame_bits):
    global resultado_validacao, ultima_mensagem_tempo, historico_quadros
    
#    dados = frame_bits[:8]
#    bits_soma = frame_bits[8:12]

    bits_soma = frame_bits[len(frame_bits)-8:len(frame_bits)]
    dados = frame_bits[:len(frame_bits)-8]
    
    soma_real_dados = sum(dados)
    soma_recebida_int = int("".join(str(b) for b in bits_soma), 2)
    sucesso = (soma_real_dados == soma_recebida_int)
    
    str_dados = "".join(str(b) for b in dados)
    if sucesso:
        resultado_validacao = f"[SUCESSO] Dados: {str_dados} | Soma Rec: {soma_recebida_int}"
        print(f"\n[SUCESSO] Quadro de 12 bits alinhado! Soma confere: {soma_real_dados}\n")
    else:
        resultado_validacao = f"[FALHA] Dados: {str_dados} | Soma Esp: {soma_real_dados} | Rec: {soma_recebida_int}"
        print(f"\n[FALHA] Corrupção de ruído. Esp: {soma_real_dados}, Rec: {soma_recebida_int}\n")
        
    ultima_mensagem_tempo = time.time()
    historico_quadros.append({"bits": list(frame_bits), "sucesso": sucesso})
    if len(historico_quadros) > 4: historico_quadros.pop(0)

def processar_audio_fsk(indata, frames, time_info, status):
    global state, sync_time, simbolos_lidos, bit_buffer, esperando_silencio, is_paused
    
    if is_paused:
        return
        
    volume = np.linalg.norm(indata) * 10
    if volume < LIMIAR_VOLUME:
        # Se houve um silêncio absoluto no meio do caminho, resetamos por segurança
        if state == "WAITING_DATA_START" or state == "RECEIVING_DATA":
            state = "WAITING_SYNC"
            esperando_silencio = False
            bit_buffer.clear()
        return 
        
    # Cálculos da Transformada Rápida de Fourier (FFT)
    espectro = np.abs(np.fft.rfft(indata[:, 0]))
    frequencias = np.fft.rfftfreq(frames, 1.0 / TAXA_AMOSTRAGEM)
    frequencia_pico = frequencias[np.argmax(espectro)]
    
    tempo_atual = time.time()

    # --- FASE 1: OUVIR O START (O RELÓGIO NÃO COMEÇA AQUI) ---
    if state == "WAITING_SYNC":
        if abs(frequencia_pico - 4000) <= 150: # Margem elástica para o tom agudo
            print("\n[SISTEMA] Preâmbulo detectado (4000 Hz). Aguardando a Borda de Descida...")
            state = "WAITING_DATA_START"
            
    # --- FASE 2: A BORDA DE DESCIDA (O DISPARO DO CRONÔMETRO) ---
    elif state == "WAITING_DATA_START":
        # Esperamos o instante exato em que a nota DEIXA de ser 5000 Hz.
        if abs(frequencia_pico - 5000) > 200:
            par_bits = mapear_frequencia(frequencia_pico)
            
            # Se a frequência que tocou em seguida mapear para um dado válido, ALINHAMOS!
            if par_bits is not None:
                sync_time = tempo_atual
                bit_buffer.clear()
                bit_buffer.extend(par_bits)
                simbolos_lidos = 1
                state = "RECEIVING_DATA"
                esperando_silencio = True
                print(f"[0.00s] PRIMEIRO SÍMBOLO: {par_bits[0]}{par_bits[1]}{par_bits[2]}{par_bits[3]} ({frequencia_pico:.0f}Hz)")
                
    # --- FASE 3: LEITURA MATEMÁTICA CIRÚRGICA ---
    elif state == "RECEIVING_DATA":
        tempo_decorrido = tempo_atual - sync_time
        
        # TIMEOUT: Áudio picotou ou acabou incompleto
        if tempo_decorrido > ((6 * DURACAO_SOM) + 0.5):
            print("[ALERTA] Timeout! Áudio incompleto.")
            state = "WAITING_SYNC"
            esperando_silencio = False
            bit_buffer.clear()
            return
            
        # ALVO = Quantos símbolos já lemos * 0.20s + 0.10s (Caímos sempre no meio do tom)
        alvo_temporal = (simbolos_lidos * DURACAO_SOM) + MEIO_DO_SOM
        
        if tempo_decorrido >= alvo_temporal:
            par_bits = mapear_frequencia(frequencia_pico)
            
            if par_bits is not None:
                bit_buffer.extend(par_bits)
                print(f"[{tempo_decorrido:.2f}s] LIDO: {par_bits[0]}{par_bits[1]}{par_bits[2]}{par_bits[3]} ({frequencia_pico:.0f}Hz)")
            else:
                # O ruído estava tão alto que a FFT se perdeu
                bit_buffer.extend([1, 1])
                print(f"[{tempo_decorrido:.2f}s] ERRO FÍSICO! Freq Incoerente: {frequencia_pico:.0f}Hz")
                
            simbolos_lidos += 1
            
            if simbolos_lidos == 6:
                validar_quadro_soma(bit_buffer)
                bit_buffer.clear()
                state = "WAITING_SYNC"
                esperando_silencio = False

if __name__ == "__main__":
    print("Motor Síncrono (Borda de Descida) Iniciado.")
    try:
        with sd.InputStream(callback=processar_audio_fsk, channels=1, samplerate=TAXA_AMOSTRAGEM, blocksize=BLOCO_AUDIO):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\nMotor desligado.")