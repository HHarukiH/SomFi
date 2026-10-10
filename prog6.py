import numpy as np
import sounddevice as sd

TAXA_AMOSTRAGEM = 44100

def criar_estalo():
    # Mantemos 50ms de duração, mas baixamos a frequência para 1500Hz 
    # para que caixas de som comuns de notebook consigam reproduzir melhor o impacto.
    t = np.linspace(0, 0.05, int(TAXA_AMOSTRAGEM * 0.05), False)
    onda = np.sin(2 * np.pi * 1500 * t) * np.exp(-t * 30)
    return onda

def gerar_audio_batidas(bits_dados):
    estalo = criar_estalo()
    # Tempos ajustados para imitar a cadência humana relaxada do vídeo
    silencio_curto = np.zeros(int(TAXA_AMOSTRAGEM * 0.35)) 
    silencio_longo = np.zeros(int(TAXA_AMOSTRAGEM * 1.20))
    
    uns = bits_dados.count('1')
    bit_paridade = '0' if uns % 2 == 0 else '1'
    quadro_completo = bits_dados + bit_paridade
    
    audio_final = np.array([])
    
    for bit in quadro_completo:
        if bit == '0':
            audio_final = np.concatenate((audio_final, estalo, silencio_longo))
        else:
            audio_final = np.concatenate((audio_final, estalo, silencio_curto, estalo, silencio_longo))
            
    return quadro_completo, audio_final

def transmitir(audio_array):
    sd.stop()
    sd.play(audio_array, TAXA_AMOSTRAGEM)