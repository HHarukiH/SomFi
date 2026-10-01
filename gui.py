import pygame
import sounddevice as sd
import time
import Prog

LARGURA, ALTURA = 800, 550
PRETO = (15, 15, 15)
VERDE_RETRO = (50, 255, 50)
VERMELHO_ALERTA = (255, 50, 50)
CINZENTO_ESCURO = (40, 40, 40)
BRANCO = (200, 200, 200)

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Camada Física - Monitor Acústico")

# Fontes
fonte_titulo = pygame.font.SysFont('courier', 28, bold=True)
fonte_bits = pygame.font.SysFont('courier', 40, bold=True)
fonte_pequena = pygame.font.SysFont('courier', 16, bold=True)
fonte_mini = pygame.font.SysFont('courier', 14, bold=True)

def desenhar_interface():
    ecra.fill(PRETO)
    
    # 1. CABEÇALHO
    titulo = fonte_titulo.render("CAMADA FISICA", False, VERDE_RETRO)
    ecra.blit(titulo, (20, 20))
    
    estado_texto = fonte_pequena.render(f"Estado do Motor: {Prog.state}", False, BRANCO)
    ecra.blit(estado_texto, (20, 60))
    
    # 2. QUADRO DE RECEÇÃO (9 BITS)
    pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 100, 760, 110), 2)
    
    for i in range(9):
        x_pos = 45 + (i * 80)
        y_pos = 125
        
        if i == 8:
            lbl_paridade = fonte_pequena.render("PARIDADE", False, VERDE_RETRO)
            ecra.blit(lbl_paridade, (x_pos - 10, y_pos - 20))
        else:
            lbl_bit = fonte_pequena.render(f"B{i+1}", False, CINZENTO_ESCURO)
            ecra.blit(lbl_bit, (x_pos + 15, y_pos - 20))

        if i < len(Prog.bit_buffer):
            valor_bit = Prog.bit_buffer[i]
            cor = VERDE_RETRO if valor_bit == 1 else BRANCO
            
            pygame.draw.rect(ecra, cor, (x_pos, y_pos, 60, 60), 2)
            texto_bit = fonte_bits.render(str(valor_bit), False, cor)
            ecra.blit(texto_bit, (x_pos + 15, y_pos + 10))
        else:
            pygame.draw.rect(ecra, CINZENTO_ESCURO, (x_pos, y_pos, 60, 60), 1)

    # 3. RESULTADO DA VALIDAÇÃO
    if time.time() - Prog.ultima_mensagem_tempo < 4.0:
        msg = Prog.resultado_validacao
        cor_msg = VERDE_RETRO if "[SUCESSO]" in msg else VERMELHO_ALERTA
        texto_val = fonte_titulo.render(msg, False, cor_msg)
        ecra.blit(texto_val, (20, 230))

    # 4. TABELA DE HISTÓRICO PIXELADA
    lbl_hist = fonte_pequena.render("HISTÓRICO DE TRANSMISSÃO:", False, BRANCO)
    ecra.blit(lbl_hist, (20, 290))
    
    y_hist = 320
    for registro in Prog.historico_quadros:
        cor_status = VERDE_RETRO if registro["sucesso"] else VERMELHO_ALERTA
        texto_status = "SUCESSO" if registro["sucesso"] else "FALHA"
        
        lbl_status = fonte_mini.render(texto_status, False, cor_status)
        ecra.blit(lbl_status, (20, y_hist + 5))
        
        for idx, bit in enumerate(registro["bits"]):
            x_hist_bit = 120 + (idx * 30)
            cor_caixa = cor_status if bit == 1 else CINZENTO_ESCURO
            
            pygame.draw.rect(ecra, cor_caixa, (x_hist_bit, y_hist, 25, 25), 1)
            txt_b = fonte_mini.render(str(bit), False, cor_caixa if bit == 1 else BRANCO)
            ecra.blit(txt_b, (x_hist_bit + 8, y_hist + 5))
            
            if idx == 8:
                pygame.draw.rect(ecra, cor_status, (x_hist_bit, y_hist, 25, 25), 2)
            
        y_hist += 35

    pygame.display.flip()

def iniciar_gui():
    print("A iniciar interface gráfica...")
    stream = sd.InputStream(callback=Prog.process_audio_stream, channels=1, samplerate=44100)
    stream.start()
    
    relogio = pygame.time.Clock()
    a_executar = True
    
    while a_executar:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                a_executar = False
                
        desenhar_interface()
        relogio.tick(30)
        
    stream.stop()
    pygame.quit()

if __name__ == "__main__":
    iniciar_gui()