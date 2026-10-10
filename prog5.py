import numpy as np
import sounddevice as sd
import convert

# --- CONFIGURAÇÕES SÍNCRONAS (MÉTODO 2 / 16-FSK) ---
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
    Abordagem de Length Header:
    [8 Bits Tamanho] + [N Bits de Dados ASCII] + [8 Bits Checksum]
    """
    bits_n = ""
    for i in texto:
        bits_n += convert.converter(i)
        
    # 1. Cabeçalho de Tamanho (Length Header)
    tamanho_bits_dados = len(bits_n)
    bits_tamanho = format(tamanho_bits_dados, '08b')
        
    # 2. Checksum (Calculado apenas sobre os dados reais)
    soma_inteira = bits_n.count('1')
    bits_soma = format(soma_inteira, '08b')
    
    # 3. Montagem da Fita (Azul + Verde + Vermelho)
    quadro_completo = bits_tamanho + bits_n + bits_soma
    
    audio_final = np.array([])
    
    print("\n[TRANSMISSÃO INICIADA]")
    print(f" > Tamanho : {bits_tamanho} ({tamanho_bits_dados} bits)")
    print(f" > Dados   : {bits_n}")
    print(f" > Soma    : {bits_soma} ({soma_inteira} uns)")
    
    # Injeta o START
    audio_final = np.concatenate((audio_final, gerar_onda_senoidal(frequencias["START"], DURACAO_START)))
    
    # Injeta os Símbolos (Quartetos de Bits)
    pares = [quadro_completo[i:i+4] for i in range(0, len(quadro_completo), 4)]
    for par in pares:
        audio_final = np.concatenate((audio_final, gerar_onda_senoidal(frequencias[par], DURACAO_SOM)))
        
    return quadro_completo, audio_final

def transmitir(audio_array):
    """Envia o array matemático diretamente para o alto-falante."""
    sd.stop() 
    sd.play(audio_array, TAXA_AMOSTRAGEM)