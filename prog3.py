import numpy as np
import sounddevice as sd

# --- CONFIGURAÇÕES SÍNCRONAS (MÉTODO 2) ---
TAXA_AMOSTRAGEM = 44100
DURACAO_START = 0.20
DURACAO_SOM = 0.10

frequencias = {
    "START": 3500,
    "00": 1200,
    "01": 1600,
    "10": 2200,
    "11": 2800
}

def gerar_onda_senoidal(frequencia, duracao):
    """Sintetiza a onda pura matemática na memória."""
    tempo = np.linspace(0, duracao, int(TAXA_AMOSTRAGEM * duracao), False)
    return np.sin(2 * np.pi * frequencia * tempo)

def gerar_audio_fsk(bits_8):
    """
    Recebe uma string de 8 bits (ex: '10110011').
    Calcula a soma, monta o quadro de 12 bits e sintetiza o áudio.
    Retorna o quadro em formato string e o array de áudio pronto a tocar.
    """
    soma_inteira = bits_8.count('1')
    bits_soma = format(soma_inteira, '04b')
    quadro_completo = bits_8 + bits_soma
    
    audio_final = np.array([])
    
    # 1. Injeta o START
    audio_final = np.concatenate((audio_final, gerar_onda_senoidal(frequencias["START"], DURACAO_START)))
    
    # 2. Injeta os Símbolos (Pares de Bits)
    pares = [quadro_completo[i:i+2] for i in range(0, 12, 2)]
    for par in pares:
        audio_final = np.concatenate((audio_final, gerar_onda_senoidal(frequencias[par], DURACAO_SOM)))
        
    return quadro_completo, audio_final

def transmitir(audio_array):
    """Envia o array matemático diretamente para o alto-falante."""
    sd.stop() # Para qualquer áudio que esteja a tocar para evitar sobreposição
    sd.play(audio_array, TAXA_AMOSTRAGEM)
    # Não usamos sd.wait() aqui para não congelar a interface gráfica enquanto o som toca.