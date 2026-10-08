import pygame
import sounddevice as sd
import time
import prog   # Receptor M1 (Batidas)
import prog2  # Receptor M2 (FSK)
import prog3  # Transmissor M2 (FSK)
import prog4 
import prog5

# --- CONFIGURAÇÕES DA INTERFACE ---
LARGURA, ALTURA = 900, 700
PRETO = (15, 15, 15)
VERDE_RETRO = (50, 255, 50)
VERMELHO_ALERTA = (255, 50, 50)
CINZENTO_ESCURO = (40, 40, 40)
CINZENTO_CLARO = (150, 150, 150) # NOVO: Cor com bom contraste para subtítulos
BRANCO = (200, 200, 200)
AZUL_SOMA = (50, 150, 255) 

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Camada Física - Monitor Acústico Central")

fonte_titulo = pygame.font.SysFont('courier', 28, bold=True)
fonte_bits = pygame.font.SysFont('courier', 40, bold=True)
fonte_pequena = pygame.font.SysFont('courier', 16, bold=True)
fonte_mini = pygame.font.SysFont('courier', 14, bold=True)

# Variáveis Globais de Gestão
tela_atual = "MENU" 
stream_audio = None

# Variáveis do Transmissor (M3)
m3_input_text = ""
m3_quadro = ""
m3_audio = None
m3_msg = ""

# Variáveis do Transmissor (M5)
m5_input_text = ""
m5_quadro = ""
m5_audio = None
m5_msg = ""

def desenhar_botao_voltar():
    pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 20, 110, 40), 2)
    ecra.blit(fonte_pequena.render("< VOLTAR", False, BRANCO), (30, 30))

def desenhar_botao_pause(pausado):
    pygame.draw.rect(ecra, CINZENTO_ESCURO, (720, 20, 60, 60), 2)
    if pausado:
        pygame.draw.polygon(ecra, VERDE_RETRO, [(735, 30), (735, 70), (765, 50)])
        ecra.blit(fonte_pequena.render("EM PAUSA", False, VERMELHO_ALERTA), (630, 40))
    else:
        pygame.draw.rect(ecra, VERDE_RETRO, (735, 30, 10, 40))
        pygame.draw.rect(ecra, VERDE_RETRO, (755, 30, 10, 40))

def desenhar_menu():
    ecra.fill(PRETO)
    
    # Título centralizado matematicamente
    titulo = fonte_titulo.render("SISTEMA DE COMUNICAÇÃO ACÚSTICA", False, VERDE_RETRO)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 50)))
    
    # 1. Receptor Batidas (Caixas redimensionadas de 500 para 600px)
    rect_b1 = pygame.Rect(100, 120, 600, 80)
    pygame.draw.rect(ecra, CINZENTO_ESCURO, rect_b1, 2)
    txt_m1 = fonte_bits.render("1. RECEPTOR (BATIDAS)", False, BRANCO)
    ecra.blit(txt_m1, txt_m1.get_rect(center=rect_b1.center))
    
    # 2. Receptor FSK
    rect_b2 = pygame.Rect(100, 230, 600, 80)
    pygame.draw.rect(ecra, CINZENTO_ESCURO, rect_b2, 2)
    txt_m2 = fonte_bits.render("2. RECEPTOR (FSK)", False, BRANCO)
    ecra.blit(txt_m2, txt_m2.get_rect(center=rect_b2.center))

    # 3. Transmissor FSK
    rect_b3 = pygame.Rect(100, 340, 600, 80)
    pygame.draw.rect(ecra, AZUL_SOMA, rect_b3, 2)
    txt_m3 = fonte_bits.render("3. TRANSMISSOR (FSK)", False, BRANCO)
    ecra.blit(txt_m3, txt_m3.get_rect(center=(LARGURA//2, 365)))
    # Subtítulo com cor visível (CINZENTO_CLARO)
    lbl_m3 = fonte_pequena.render("Gerador Síncrono de Áudio", False, CINZENTO_CLARO)
    ecra.blit(lbl_m3, lbl_m3.get_rect(center=(LARGURA//2, 395)))

    #4. Receptor
    rect_b4 = pygame.Rect(100, 450, 600, 80)
    pygame.draw.rect(ecra, CINZENTO_ESCURO, rect_b4, 2)
    txt_m4 = fonte_bits.render("4. RECEPTOR (FSK)", False, BRANCO)
    ecra.blit(txt_m4, txt_m4.get_rect(center=rect_b4.center))

    #5. Transmissor
    rect_b5 = pygame.Rect(100, 560, 600, 80)
    pygame.draw.rect(ecra, AZUL_SOMA, rect_b5, 2)
    txt_m5 = fonte_bits.render("5. TRANSMISSOR (FSK)", False, BRANCO)
    ecra.blit(txt_m5, txt_m5.get_rect(center=(LARGURA//2, 585)))
    # Subtítulo com cor visível (CINZENTO_CLARO)
    lbl_m5 = fonte_pequena.render("Gerador Síncrono de Áudio", False, CINZENTO_CLARO)
    ecra.blit(lbl_m5, lbl_m5.get_rect(center=(LARGURA//2, 615)))

def desenhar_m1():
    ecra.fill(PRETO)
    desenhar_botao_voltar()
    desenhar_botao_pause(prog.is_paused)
    
    titulo = fonte_titulo.render("MÉTODO 1 - RECEPTOR BATIDAS", False, VERDE_RETRO)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 35)))
    ecra.blit(fonte_pequena.render(f"Estado: {prog.state}", False, BRANCO), (150, 70))
    
    pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 100, 760, 110), 2)
    for i in range(9):
        x_pos = 45 + (i * 80)
        y_pos = 125
        if i == 8: ecra.blit(fonte_pequena.render("PARIDADE", False, VERDE_RETRO), (x_pos-10, y_pos-20))
        else: ecra.blit(fonte_pequena.render(f"B{i+1}", False, CINZENTO_CLARO), (x_pos+15, y_pos-20))

        if i < len(prog.bit_buffer):
            v = prog.bit_buffer[i]
            cor = VERDE_RETRO if v == 1 else BRANCO
            pygame.draw.rect(ecra, cor, (x_pos, y_pos, 60, 60), 2)
            ecra.blit(fonte_bits.render(str(v), False, cor), (x_pos+15, y_pos+10))
        else:
            pygame.draw.rect(ecra, CINZENTO_ESCURO, (x_pos, y_pos, 60, 60), 1)

    if time.time() - prog.ultima_mensagem_tempo < 4.0:
        c = VERDE_RETRO if "[SUCESSO]" in prog.resultado_validacao else VERMELHO_ALERTA
        ecra.blit(fonte_titulo.render(prog.resultado_validacao, False, c), (20, 230))

    ecra.blit(fonte_pequena.render("HISTÓRICO DE TRANSMISSÃO:", False, BRANCO), (20, 280))
    y_hist = 310
    for reg in prog.historico_quadros:
        cor_status = VERDE_RETRO if reg["sucesso"] else VERMELHO_ALERTA
        ecra.blit(fonte_mini.render("SUCESSO" if reg["sucesso"] else "FALHA", False, cor_status), (20, y_hist + 5))
        for idx, bit in enumerate(reg["bits"]):
            x_bit = 120 + (idx * 30)
            cor_c = cor_status if bit == 1 else CINZENTO_ESCURO
            pygame.draw.rect(ecra, cor_c, (x_bit, y_hist, 25, 25), 1)
            ecra.blit(fonte_mini.render(str(bit), False, cor_c if bit == 1 else BRANCO), (x_bit + 8, y_hist + 5))
            if idx == 8: pygame.draw.rect(ecra, cor_status, (x_bit, y_hist, 25, 25), 2)
        y_hist += 35

def desenhar_m2():
    ecra.fill(PRETO)
    desenhar_botao_voltar()
    desenhar_botao_pause(prog2.is_paused)
    
    titulo = fonte_titulo.render("MÉTODO 2 - RECEPTOR FSK", False, VERDE_RETRO)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 35)))
    ecra.blit(fonte_pequena.render(f"Estado Relógio: {prog2.state}", False, BRANCO), (150, 70))
    
    pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 100, 760, 110), 2)
    for i in range(12):
        x_pos = 35 + (i * 60)
        y_pos = 125
        if i >= 8: ecra.blit(fonte_pequena.render(f"S{i-7}", False, AZUL_SOMA), (x_pos+15, y_pos-20))
        else: ecra.blit(fonte_pequena.render(f"B{i+1}", False, CINZENTO_CLARO), (x_pos+15, y_pos-20))

        if i < len(prog2.bit_buffer):
            v = prog2.bit_buffer[i]
            cor = VERDE_RETRO if v == 1 else BRANCO
            pygame.draw.rect(ecra, cor, (x_pos, y_pos, 50, 50), 2)
            ecra.blit(fonte_bits.render(str(v), False, cor), (x_pos+12, y_pos+5))
        else:
            pygame.draw.rect(ecra, CINZENTO_ESCURO, (x_pos, y_pos, 50, 50), 1)

    if time.time() - prog2.ultima_mensagem_tempo < 4.0:
        c = VERDE_RETRO if "[SUCESSO]" in prog2.resultado_validacao else VERMELHO_ALERTA
        ecra.blit(fonte_pequena.render(prog2.resultado_validacao, False, c), (20, 230))

    ecra.blit(fonte_pequena.render("HISTÓRICO DE TRANSMISSÃO:", False, BRANCO), (20, 270))
    y_hist = 300
    for reg in prog2.historico_quadros:
        cor_status = VERDE_RETRO if reg["sucesso"] else VERMELHO_ALERTA
        ecra.blit(fonte_mini.render("SUCESSO" if reg["sucesso"] else "FALHA", False, cor_status), (20, y_hist + 5))
        for idx, bit in enumerate(reg["bits"]):
            x_bit = 100 + (idx * 25)
            cor_c = cor_status if bit == 1 else CINZENTO_ESCURO
            pygame.draw.rect(ecra, cor_c, (x_bit, y_hist, 20, 20), 1)
            ecra.blit(fonte_mini.render(str(bit), False, cor_c if bit == 1 else BRANCO), (x_bit + 5, y_hist + 3))
            if idx >= 8: pygame.draw.rect(ecra, cor_status, (x_bit, y_hist, 20, 20), 2)
        y_hist += 30

def desenhar_m3():
    ecra.fill(PRETO)
    desenhar_botao_voltar()
    
    titulo = fonte_titulo.render("MÉTODO 2 - TRANSMISSOR FSK", False, AZUL_SOMA)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 35)))
    
    ecra.blit(fonte_pequena.render("Digite 8 bits (0 e 1):", False, BRANCO), (20, 90))
    pygame.draw.rect(ecra, VERDE_RETRO if len(m3_input_text)==8 else CINZENTO_ESCURO, (20, 110, 200, 40), 2)
    ecra.blit(fonte_titulo.render(m3_input_text + ("_" if int(time.time()*2) % 2 == 0 else ""), False, BRANCO), (30, 115))
    
    btn_conf = pygame.Rect(240, 110, 130, 40)
    pygame.draw.rect(ecra, CINZENTO_ESCURO, btn_conf, 2)
    ecra.blit(fonte_pequena.render("CONFIRMAR", False, BRANCO), (260, 122))
    
    pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 180, 760, 110), 2)
    for i in range(12):
        x_pos = 35 + (i * 60)
        is_soma = i >= 8
        cor_base = AZUL_SOMA if is_soma else VERDE_RETRO
        
        lbl = f"S{i-7}" if is_soma else f"B{i+1}"
        ecra.blit(fonte_pequena.render(lbl, False, cor_base), (x_pos+15, 185))

        if m3_quadro and i < len(m3_quadro):
            valor = m3_quadro[i]
            cor_txt = cor_base if valor == '1' else BRANCO
            pygame.draw.rect(ecra, cor_txt, (x_pos, 205, 50, 50), 2)
            ecra.blit(fonte_bits.render(valor, False, cor_txt), (x_pos+12, 210))
        else:
            pygame.draw.rect(ecra, CINZENTO_ESCURO, (x_pos, 205, 50, 50), 1)

    ecra.blit(fonte_pequena.render(m3_msg, False, CINZENTO_CLARO), (20, 310))
    
    if m3_audio is not None:
        btn_play = pygame.Rect(280, 350, 240, 60)
        pygame.draw.rect(ecra, AZUL_SOMA, btn_play, 2)
        pygame.draw.polygon(ecra, AZUL_SOMA, [(320, 365), (320, 395), (345, 380)])
        ecra.blit(fonte_titulo.render("TRANSMITIR", False, BRANCO), (360, 365))

def desenhar_m4():
    ecra.fill(PRETO)
    desenhar_botao_voltar()
    desenhar_botao_pause(prog4.is_paused)
    
    titulo = fonte_titulo.render("MÉTODO 3 - RECEPTOR FSK", False, VERDE_RETRO)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 35)))
    ecra.blit(fonte_pequena.render(f"Estado Relógio: {prog4.state}", False, BRANCO), (150, 70))
    
    pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 100, 760, 110), 2)
    for i in range(len(prog4.bit_buffer) if prog4.bit_buffer else 12):
        x_pos = 35 + (i * 60)
        y_pos = 125
        if i >= 8: ecra.blit(fonte_pequena.render(f"S{i-7}", False, AZUL_SOMA), (x_pos+15, y_pos-20))
        else: ecra.blit(fonte_pequena.render(f"B{i+1}", False, CINZENTO_CLARO), (x_pos+15, y_pos-20))

        if i < len(prog4.bit_buffer):
            v = prog4.bit_buffer[i]
            cor = VERDE_RETRO if v == 1 else BRANCO
            pygame.draw.rect(ecra, cor, (x_pos, y_pos, 50, 50), 2)
            ecra.blit(fonte_bits.render(str(v), False, cor), (x_pos+12, y_pos+5))
        else:
            pygame.draw.rect(ecra, CINZENTO_ESCURO, (x_pos, y_pos, 50, 50), 1)

    if time.time() - prog4.ultima_mensagem_tempo < 4.0:
        c = VERDE_RETRO if "[SUCESSO]" in prog4.resultado_validacao else VERMELHO_ALERTA
        ecra.blit(fonte_pequena.render(prog4.resultado_validacao, False, c), (20, 230))

    ecra.blit(fonte_pequena.render("HISTÓRICO DE TRANSMISSÃO:", False, BRANCO), (20, 270))
    y_hist = 300
    for reg in prog4.historico_quadros:
        cor_status = VERDE_RETRO if reg["sucesso"] else VERMELHO_ALERTA
        ecra.blit(fonte_mini.render("SUCESSO" if reg["sucesso"] else "FALHA", False, cor_status), (20, y_hist + 5))
        for idx, bit in enumerate(reg["bits"]):
            x_bit = 100 + (idx * 25)
            cor_c = cor_status if bit == 1 else CINZENTO_ESCURO
            pygame.draw.rect(ecra, cor_c, (x_bit, y_hist, 20, 20), 1)
            ecra.blit(fonte_mini.render(str(bit), False, cor_c if bit == 1 else BRANCO), (x_bit + 5, y_hist + 3))
            if idx >= 8: pygame.draw.rect(ecra, cor_status, (x_bit, y_hist, 20, 20), 2)
        y_hist += 30

def desenhar_m5():
    ecra.fill(PRETO)
    desenhar_botao_voltar()
    
    titulo = fonte_titulo.render("MÉTODO 3 - TRANSMISSOR FSK", False, AZUL_SOMA)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 35)))
    
    ecra.blit(fonte_pequena.render("Digite 8 bits (0 e 1):", False, BRANCO), (20, 90))
    pygame.draw.rect(ecra, VERDE_RETRO if len(m5_input_text)==8 else CINZENTO_ESCURO, (20, 110, 200, 40), 2)
    ecra.blit(fonte_titulo.render(m5_input_text + ("_" if int(time.time()*2) % 2 == 0 else ""), False, BRANCO), (30, 115))
    
    btn_conf = pygame.Rect(240, 110, 130, 40)
    pygame.draw.rect(ecra, CINZENTO_ESCURO, btn_conf, 2)
    ecra.blit(fonte_pequena.render("CONFIRMAR", False, BRANCO), (260, 122))
    
    pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 180, 760, 110), 2)
    for i in range(len(m5_quadro) if m5_quadro else 12):
        x_pos = 35 + (i * 60)
        is_soma = i >= 8
        cor_base = AZUL_SOMA if is_soma else VERDE_RETRO
        
        lbl = f"S{i-7}" if is_soma else f"B{i+1}"
        ecra.blit(fonte_pequena.render(lbl, False, cor_base), (x_pos+15, 185))

        if m5_quadro and i < len(m5_quadro):
            valor = m5_quadro[i]
            cor_txt = cor_base if valor == '1' else BRANCO
            pygame.draw.rect(ecra, cor_txt, (x_pos, 205, 50, 50), 2)
            ecra.blit(fonte_bits.render(valor, False, cor_txt), (x_pos+12, 210))
        else:
            pygame.draw.rect(ecra, CINZENTO_ESCURO, (x_pos, 205, 50, 50), 1)

    ecra.blit(fonte_pequena.render(m5_msg, False, CINZENTO_CLARO), (20, 310))
    
    if m5_audio is not None:
        btn_play = pygame.Rect(280, 350, 240, 60)
        pygame.draw.rect(ecra, AZUL_SOMA, btn_play, 2)
        pygame.draw.polygon(ecra, AZUL_SOMA, [(320, 365), (320, 395), (345, 380)])
        ecra.blit(fonte_titulo.render("TRANSMITIR", False, BRANCO), (360, 365))

def acionar_confirmacao_m3():
    global m3_quadro, m3_audio, m3_msg
    if len(m3_input_text) == 8:
        m3_quadro, m3_audio = prog3.gerar_audio_fsk(m3_input_text)
        m3_msg = "[SISTEMA] Quadro gerado! 4 Bits de soma calculados. Pronto para transmitir."
    else:
        m3_msg = "[ERRO] Digite exatamente 8 bits antes de confirmar."

def acionar_confirmacao_m5():
    global m5_quadro, m5_audio, m5_msg
#    if len(m5_input_text)%4 == 0:
    m5_quadro, m5_audio = prog5.gerar_audio_fsk(m5_input_text)
    m5_msg = "[SISTEMA] Quadro gerado! Bits de soma calculados. Pronto para transmitir."
#    else:
#        m5_msg = "[ERRO] Digite exatamente 8 bits antes de confirmar."

def iniciar_gui():
    global tela_atual, stream_audio, m3_input_text, m3_quadro, m3_audio, m3_msg, m5_input_text, m5_quadro, m5_audio, m5_msg
    
    relogio = pygame.time.Clock()
    a_executar = True
    
    while a_executar:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                a_executar = False
                
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos
                
                if tela_atual == "MENU":
                    # Nova área de clique expandida para os botões de 600px
                    if 100 <= mx <= 700:
                        if 120 <= my <= 200:
                            prog.bit_buffer.clear()
                            prog.historico_quadros.clear()
                            prog.resultado_validacao = ""
                            prog.is_paused = True; tela_atual = "M1"
                            if stream_audio: stream_audio.stop(); stream_audio.close()
                            stream_audio = sd.InputStream(callback=prog.process_audio_stream, channels=1, samplerate=44100)
                            stream_audio.start()
                            
                        elif 230 <= my <= 310:
                            prog2.bit_buffer.clear()
                            prog2.historico_quadros.clear()
                            prog2.resultado_validacao = ""
                            prog2.is_paused = True; tela_atual = "M2"
                            if stream_audio: stream_audio.stop(); stream_audio.close()
                            stream_audio = sd.InputStream(callback=prog2.processar_audio_fsk, channels=1, samplerate=44100, blocksize=1024)
                            stream_audio.start()
                            
                        elif 340 <= my <= 420:
                            m3_input_text = ""
                            m3_quadro = ""
                            m3_audio = None
                            m3_msg = ""
                            tela_atual = "M3"
                            if stream_audio: stream_audio.stop(); stream_audio.close()

                        elif 450 <= my <= 530:
                            prog4.bit_buffer.clear()
                            prog4.historico_quadros.clear()
                            prog4.resultado_validacao = ""
                            prog4.is_paused = True; tela_atual = "M4"
                            if stream_audio: stream_audio.stop(); stream_audio.close()
                            stream_audio = sd.InputStream(callback=prog2.processar_audio_fsk, channels=1, samplerate=44100, blocksize=1024)
                            stream_audio.start()

                        elif 560 <= my <= 640:
                            m5_input_text = ""
                            m5_quadro = ""
                            m5_audio = None
                            m5_msg = ""
                            tela_atual = "M5"
                            if stream_audio: stream_audio.stop(); stream_audio.close()

                elif tela_atual in ["M1", "M2", "M3", "M4", "M5"]:
                    if 20 <= mx <= 130 and 20 <= my <= 60:
                        sd.stop() 
                        if stream_audio: stream_audio.stop(); stream_audio.close(); stream_audio = None
                        tela_atual = "MENU"
                    
                    if tela_atual in ["M1", "M2"] and 720 <= mx <= 780 and 20 <= my <= 80:
                        if tela_atual == "M1":
                            prog.is_paused = not prog.is_paused
                            if not prog.is_paused: prog.last_impact_time = time.time()
                        elif tela_atual == "M2":
                            prog2.is_paused = not prog2.is_paused
                            
                    if tela_atual == "M3":
                        if 240 <= mx <= 390 and 110 <= my <= 150:
                            acionar_confirmacao_m3()
                        elif m3_audio is not None and 280 <= mx <= 520 and 350 <= my <= 410:
                            prog3.transmitir(m3_audio)
                            m3_msg = "[SISTEMA] A transmitir áudio FSK..."

                    if tela_atual == "M4":
                        prog4.is_paused = not prog4.is_paused

                    if tela_atual == "M5":
                        if 240 <= mx <= 390 and 110 <= my <= 150:
                            acionar_confirmacao_m5()
                        elif m5_audio is not None and 280 <= mx <= 520 and 350 <= my <= 410:
                            prog5.transmitir(m5_audio)
                            m5_msg = "[SISTEMA] A transmitir áudio FSK..."
                        
            elif evento.type == pygame.KEYDOWN and tela_atual == "M3":
                if evento.key == pygame.K_BACKSPACE:
                    m3_input_text = m3_input_text[:-1]
                elif evento.key == pygame.K_RETURN:
                    acionar_confirmacao_m3()
                elif evento.unicode in ['0', '1']:
                    if len(m3_input_text) < 8:
                        m3_input_text += evento.unicode
            elif evento.type == pygame.KEYDOWN and tela_atual == "M5":
                if evento.key == pygame.K_BACKSPACE:
                    m5_input_text = m5_input_text[:-1]
                elif evento.key == pygame.K_RETURN:
                    acionar_confirmacao_m5()
                elif evento.unicode in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z' , ' ']:
#                    if len(m5_input_text) < 8:
                    m5_input_text += evento.unicode

        if tela_atual == "MENU": desenhar_menu()
        elif tela_atual == "M1": desenhar_m1()
        elif tela_atual == "M2": desenhar_m2()
        elif tela_atual == "M3": desenhar_m3()
        elif tela_atual == "M4": desenhar_m4()
        elif tela_atual == "M5": desenhar_m5()

        pygame.display.flip()
        relogio.tick(30)
        
    sd.stop()
    if stream_audio: stream_audio.stop(); stream_audio.close()
    pygame.quit()

if __name__ == "__main__":
    iniciar_gui()