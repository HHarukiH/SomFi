import numpy as np
import sounddevice as sd
import convert

# --- CONFIGURAÇÕES SÍNCRONAS (MÉTODO 2) ---
TAXA_AMOSTRAGEM = 44100
DURACAO_START = 0.40
DURACAO_SOM = 0.20

frequencias = {
    "START": 4000,
    "0000": 800,
    "0001": 1000,
    "0010": 1200,
    "0011": 1400,
    "0100": 1600,
    "0101": 1800,
    "0110": 2000,
    "0111": 2200,
    "1000": 2400,
    "1001": 2600,
    "1010": 2800,
    "1011": 3000,
    "1100": 3200,
    "1101": 3400,
    "1110": 3600,
    "1111": 3800 
    }

def gerar_onda_senoidal(frequencia, duracao):
    """Sintetiza a onda pura matemática na memória."""
    tempo = np.linspace(0, duracao, int(TAXA_AMOSTRAGEM * duracao), False)
    return np.sin(2 * np.pi * frequencia * tempo)

def gerar_audio_fsk(texto):
    """
    Recebe uma string de 8 bits (ex: '10110011').
    Calcula a soma, monta o quadro de 12 bits e sintetiza o áudio.
    Retorna o quadro em formato string e o array de áudio pronto a tocar.
    """
    bits_n = ""
    for i in texto:
        bits_n += convert.converter(i)
        print(bits_n)
        
    soma_inteira = bits_n.count('1')
    bits_soma = format(soma_inteira, '08b')
    quadro_completo = bits_n + bits_soma
    
    audio_final = np.array([])
    
    # 1. Injeta o START
    audio_final = np.concatenate((audio_final, gerar_onda_senoidal(frequencias["START"], DURACAO_START)))
    
    # 2. Injeta os Símbolos (Pares de Bits)
    pares = [quadro_completo[i:i+4] for i in range(0, len(quadro_completo), 4)]
    for par in pares:
        audio_final = np.concatenate((audio_final, gerar_onda_senoidal(frequencias[par], DURACAO_SOM)))
        print(par)
        
    return quadro_completo, audio_final

def transmitir(audio_array):
    """Envia o array matemático diretamente para o alto-falante."""
    sd.stop() # Para qualquer áudio que esteja a tocar para evitar sobreposição
    sd.play(audio_array, TAXA_AMOSTRAGEM)
    # Não usamos sd.wait() aqui para não congelar a interface gráfica enquanto o som toca.