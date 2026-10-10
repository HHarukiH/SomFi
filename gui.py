import pygame
import sounddevice as sd
import time
import prog   
import prog2  
import prog3  
import prog4 
import prog5
import prog6 

LARGURA, ALTURA = 900, 700
PRETO = (15, 15, 15)
VERDE_RETRO = (50, 255, 50)
VERMELHO_ALERTA = (255, 50, 50)
CINZENTO_ESCURO = (40, 40, 40)
CINZENTO_CLARO = (150, 150, 150)
BRANCO = (200, 200, 200)
AZUL_SOMA = (50, 150, 255) 

pygame.init()
pygame.key.set_repeat(400, 50) 
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Camada Física - Monitor Acústico Central")

fonte_titulo = pygame.font.SysFont('courier', 28, bold=True)
fonte_bits = pygame.font.SysFont('courier', 40, bold=True)
fonte_pequena = pygame.font.SysFont('courier', 16, bold=True)
fonte_mini = pygame.font.SysFont('courier', 14, bold=True)

tela_atual = "MENU" 
stream_audio = None

m6_input_text = ""
m6_quadro = ""
m6_audio = None
m6_msg = ""

m3_input_text = ""
m3_quadro = ""
m3_audio = None
m3_msg = ""

m4_historico_ativo = None 

m5_input_text = ""
m5_quadro = ""
m5_audio = None
m5_msg = ""

def exportar_wav(audio_array):
    try:
        import tkinter as tk
        from tkinter import filedialog
        import scipy.io.wavfile as wavfile
        import numpy as np
        
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        
        caminho = filedialog.asksaveasfilename(
            title="Salvar Áudio WAV",
            defaultextension=".wav",
            filetypes=[("Arquivos WAV", "*.wav")]
        )
        
        root.destroy()
        
        if caminho:
            audio_int16 = np.int16(audio_array * 32767)
            wavfile.write(caminho, 44100, audio_int16)
            return True, caminho
        return False, ""
    except Exception as e:
        return False, str(e)

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

def desenhar_grelha_agrupada(ecra, buffer_bits, fonte_mini, fonte_pequena, start_x=66, start_y=160):
    if not buffer_bits: return
    
    for b in range(len(buffer_bits) // 8):
        byte_bits = buffer_bits[b*8 : (b+1)*8]
        row = (b * 8) // 32
        y = start_y + row * 65 

        if b == 0: cor = AZUL_SOMA
        elif b == (len(buffer_bits)//8) - 1 and len(buffer_bits) >= 16: cor = VERMELHO_ALERTA
        else: cor = VERDE_RETRO

        x_start = 0
        x_end = 0

        for i, bit in enumerate(byte_bits):
            col = (b * 8 + i) % 32
            x = start_x + col * 24
            
            if i == 0: x_start = x
            if i == 7: x_end = x + 20

            v = int(bit)
            cor_txt = cor if v == 1 else BRANCO
            pygame.draw.rect(ecra, cor_txt, (x, y, 20, 20), 1 if v == 0 else 2)
            ecra.blit(fonte_mini.render(str(v), False, cor_txt), (x+5, y+2))

        y_bracket = y + 26
        pygame.draw.line(ecra, cor, (x_start, y_bracket), (x_start, y_bracket+4), 2)
        pygame.draw.line(ecra, cor, (x_end, y_bracket), (x_end, y_bracket+4), 2)
        pygame.draw.line(ecra, cor, (x_start, y_bracket+4), (x_end, y_bracket+4), 2)

        val_int = int("".join(str(x) for x in byte_bits), 2)
        if b == 0 or b == (len(buffer_bits)//8) - 1:
            texto = str(val_int) 
        else:
            texto = chr(val_int) if 32 <= val_int <= 126 else "?" 

        txt_surf = fonte_pequena.render(texto, False, cor)
        txt_rect = txt_surf.get_rect(center=((x_start + x_end)//2, y_bracket+4))
        pygame.draw.rect(ecra, PRETO, txt_rect.inflate(8, 0)) 
        ecra.blit(txt_surf, txt_rect)

def desenhar_menu():
    ecra.fill(PRETO)
    titulo = fonte_titulo.render("SISTEMA DE COMUNICAÇÃO ACÚSTICA", False, VERDE_RETRO)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 40)))
    
    opcoes = [
        ("1. TRANSMISSOR (BATIDAS)", AZUL_SOMA, "Gerador de Estalos + Paridade Par"),
        ("2. RECEPTOR (BATIDAS)", CINZENTO_ESCURO, ""),
        ("3. TRANSMISSOR (FSK)", AZUL_SOMA, "Gerador Síncrono de Áudio"),
        ("4. RECEPTOR (FSK)", CINZENTO_ESCURO, ""),
        ("5. TRANSMISSOR (16-FSK)", AZUL_SOMA, "Gerador Dinâmico ASCII"),
        ("6. RECEPTOR (16-FSK)", CINZENTO_ESCURO, "")
    ]
    
    y_pos = 90
    for i, (texto, cor, sub) in enumerate(opcoes):
        rect_b = pygame.Rect(100, y_pos, 700, 75)
        pygame.draw.rect(ecra, cor, rect_b, 2)
        
        if sub:
            txt_surf = fonte_bits.render(texto, False, BRANCO)
            ecra.blit(txt_surf, txt_surf.get_rect(center=(rect_b.centerx, rect_b.centery - 12)))
            lbl_surf = fonte_pequena.render(sub, False, CINZENTO_CLARO)
            ecra.blit(lbl_surf, lbl_surf.get_rect(center=(rect_b.centerx, rect_b.centery + 18)))
        else:
            txt_surf = fonte_bits.render(texto, False, BRANCO)
            ecra.blit(txt_surf, txt_surf.get_rect(center=rect_b.center))
            
        y_pos += 95

def desenhar_m6():
    ecra.fill(PRETO)
    desenhar_botao_voltar()
    
    titulo = fonte_titulo.render("MÉTODO 1 - TRANSMISSOR BATIDAS", False, AZUL_SOMA)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 35)))
    
    ecra.blit(fonte_pequena.render("Digite 8 bits (Dados). O 9º bit (Paridade) será gerado:", False, BRANCO), (20, 90))
    pygame.draw.rect(ecra, VERDE_RETRO if len(m6_input_text)==8 else CINZENTO_ESCURO, (20, 115, 200, 40), 2)
    ecra.blit(fonte_titulo.render(m6_input_text + ("_" if int(time.time()*2) % 2 == 0 else ""), False, BRANCO), (30, 120))
    
    btn_conf = pygame.Rect(240, 115, 130, 40)
    pygame.draw.rect(ecra, CINZENTO_ESCURO, btn_conf, 2)
    ecra.blit(fonte_pequena.render("CONFIRMAR", False, BRANCO), (260, 127))
    
    pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 180, 760, 110), 2)
    for i in range(9):
        x_pos = 45 + (i * 80)
        is_paridade = i == 8
        cor_base = AZUL_SOMA if is_paridade else VERDE_RETRO
        
        lbl = "PAR" if is_paridade else f"B{i+1}"
        ecra.blit(fonte_pequena.render(lbl, False, cor_base), (x_pos+10 if is_paridade else x_pos+15, 185))

        if m6_quadro and i < len(m6_quadro):
            valor = m6_quadro[i]
            cor_txt = cor_base if valor == '1' else BRANCO
            pygame.draw.rect(ecra, cor_txt, (x_pos, 205, 50, 50), 2)
            ecra.blit(fonte_bits.render(valor, False, cor_txt), (x_pos+12, 210))
        else:
            pygame.draw.rect(ecra, CINZENTO_ESCURO, (x_pos, 205, 50, 50), 1)

    ecra.blit(fonte_pequena.render(m6_msg, False, CINZENTO_CLARO), (20, 310))
    
    if m6_audio is not None:
        btn_play = pygame.Rect(200, 350, 240, 60)
        pygame.draw.rect(ecra, AZUL_SOMA, btn_play, 2)
        pygame.draw.polygon(ecra, AZUL_SOMA, [(230, 365), (230, 395), (255, 380)])
        txt_trans = fonte_titulo.render("TRANSMITIR", False, BRANCO)
        ecra.blit(txt_trans, txt_trans.get_rect(center=(btn_play.centerx + 15, btn_play.centery)))
        
        btn_save = pygame.Rect(460, 350, 240, 60)
        pygame.draw.rect(ecra, VERDE_RETRO, btn_save, 2)
        pygame.draw.polygon(ecra, VERDE_RETRO, [(480, 375), (500, 375), (490, 390)])
        pygame.draw.rect(ecra, VERDE_RETRO, (485, 365, 10, 10))
        pygame.draw.line(ecra, VERDE_RETRO, (480, 395), (500, 395), 3)
        txt_save = fonte_titulo.render("DOWNLOAD", False, BRANCO)
        ecra.blit(txt_save, txt_save.get_rect(center=(btn_save.centerx + 15, btn_save.centery)))

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
        btn_play = pygame.Rect(200, 350, 240, 60)
        pygame.draw.rect(ecra, AZUL_SOMA, btn_play, 2)
        pygame.draw.polygon(ecra, AZUL_SOMA, [(230, 365), (230, 395), (255, 380)])
        txt_trans = fonte_titulo.render("TRANSMITIR", False, BRANCO)
        ecra.blit(txt_trans, txt_trans.get_rect(center=(btn_play.centerx + 15, btn_play.centery)))
        
        btn_save = pygame.Rect(460, 350, 240, 60)
        pygame.draw.rect(ecra, VERDE_RETRO, btn_save, 2)
        pygame.draw.polygon(ecra, VERDE_RETRO, [(480, 375), (500, 375), (490, 390)])
        pygame.draw.rect(ecra, VERDE_RETRO, (485, 365, 10, 10))
        pygame.draw.line(ecra, VERDE_RETRO, (480, 395), (500, 395), 3)
        txt_save = fonte_titulo.render("DOWNLOAD", False, BRANCO)
        ecra.blit(txt_save, txt_save.get_rect(center=(btn_save.centerx + 15, btn_save.centery)))

def desenhar_m4():
    ecra.fill(PRETO)
    desenhar_botao_voltar()
    desenhar_botao_pause(prog4.is_paused)
    
    titulo = fonte_titulo.render("MÉTODO 3 - RECEPTOR 16-FSK", False, VERDE_RETRO)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 35)))
    ecra.blit(fonte_pequena.render(f"Estado Relógio: {prog4.state}", False, BRANCO), (150, 70))
    
    if m4_historico_ativo is not None and m4_historico_ativo < len(prog4.historico_quadros):
        bits_historico = prog4.historico_quadros[m4_historico_ativo]['bits']
        pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 100, 860, 420), 1)
        ecra.blit(fonte_pequena.render("INSPEÇÃO FORENSE DA MSG LIDA:", False, AZUL_SOMA), (30, 110))
        desenhar_grelha_agrupada(ecra, bits_historico, fonte_mini, fonte_pequena, start_x=45, start_y=160)
    elif prog4.bit_buffer:
        pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 100, 860, 420), 1)
        desenhar_grelha_agrupada(ecra, prog4.bit_buffer, fonte_mini, fonte_pequena, start_x=45, start_y=160)
    else:
        pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 100, 860, 420), 1)
        if prog4.is_paused:
            ecra.blit(fonte_pequena.render("SISTEMA DESLIGADO. CLIQUE NO PLAY PARA ESCUTAR.", False, CINZENTO_CLARO), (210, 290))
        else:
            ecra.blit(fonte_pequena.render("AGUARDANDO GATILHO (4000 Hz)...", False, CINZENTO_CLARO), (280, 290))

    ecra.blit(fonte_pequena.render("HISTÓRICO DE TRANSMISSÃO:", False, BRANCO), (20, 540))
    y_hist = 570
    
    for idx, reg in enumerate(prog4.historico_quadros):
        cor_status = VERDE_RETRO if reg["sucesso"] else VERMELHO_ALERTA
        
        texto_msg = f"MSG: '{reg['texto']}'"
        ecra.blit(fonte_pequena.render(texto_msg, False, cor_status), (20, y_hist))
        ecra.blit(fonte_pequena.render(f"({reg['tempo']:.2f}s)", False, CINZENTO_CLARO), (500, y_hist))
        
        btn_dots = pygame.Rect(600, y_hist - 2, 40, 20)
        pygame.draw.rect(ecra, CINZENTO_CLARO, btn_dots, 1)
        ecra.blit(fonte_pequena.render("...", False, BRANCO), (608, y_hist))
        
        y_hist += 25

def desenhar_m5():
    ecra.fill(PRETO)
    desenhar_botao_voltar()
    
    titulo = fonte_titulo.render("MÉTODO 3 - TRANSMISSOR 16-FSK", False, AZUL_SOMA)
    ecra.blit(titulo, titulo.get_rect(center=(LARGURA//2, 35)))
    
    ecra.blit(fonte_pequena.render("Digite ASCII Livre (Máx 31 chars):", False, BRANCO), (20, 90))
    
    largura_caixa = max(200, len(m5_input_text) * 18 + 20)
    pygame.draw.rect(ecra, VERDE_RETRO if len(m5_input_text)>0 else CINZENTO_ESCURO, (20, 110, largura_caixa, 40), 2)
    ecra.blit(fonte_titulo.render(m5_input_text + ("_" if int(time.time()*2) % 2 == 0 else ""), False, BRANCO), (30, 115))
    
    btn_conf = pygame.Rect(largura_caixa + 30, 110, 130, 40)
    pygame.draw.rect(ecra, CINZENTO_ESCURO, btn_conf, 2)
    ecra.blit(fonte_pequena.render("CONFIRMAR", False, BRANCO), (largura_caixa + 50, 122))
    
    if m5_quadro:
        pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 160, 860, 390), 1)
        desenhar_grelha_agrupada(ecra, m5_quadro, fonte_mini, fonte_pequena, start_x=45, start_y=180)
    else:
        pygame.draw.rect(ecra, CINZENTO_ESCURO, (20, 160, 860, 390), 1)

    ecra.blit(fonte_pequena.render(m5_msg, False, CINZENTO_CLARO), (20, 560))
    
    if m5_audio is not None:
        btn_play = pygame.Rect(200, 600, 240, 60)
        pygame.draw.rect(ecra, AZUL_SOMA, btn_play, 2)
        pygame.draw.polygon(ecra, AZUL_SOMA, [(230, 615), (230, 645), (255, 630)])
        txt_trans = fonte_titulo.render("TRANSMITIR", False, BRANCO)
        ecra.blit(txt_trans, txt_trans.get_rect(center=(btn_play.centerx + 15, btn_play.centery)))
        
        btn_save = pygame.Rect(460, 600, 240, 60)
        pygame.draw.rect(ecra, VERDE_RETRO, btn_save, 2)
        pygame.draw.polygon(ecra, VERDE_RETRO, [(480, 625), (500, 625), (490, 640)])
        pygame.draw.rect(ecra, VERDE_RETRO, (485, 615, 10, 10))
        pygame.draw.line(ecra, VERDE_RETRO, (480, 645), (500, 645), 3)
        txt_save = fonte_titulo.render("DOWNLOAD", False, BRANCO)
        ecra.blit(txt_save, txt_save.get_rect(center=(btn_save.centerx + 15, btn_save.centery)))

def acionar_confirmacao_m6():
    global m6_quadro, m6_audio, m6_msg
    if len(m6_input_text) == 8:
        m6_quadro, m6_audio = prog6.gerar_audio_batidas(m6_input_text)
        m6_msg = "[SISTEMA] Quadro gerado! Bit de paridade par calculado. Pronto para transmissão acústica."
    else:
        m6_msg = "[ERRO] Digite exatamente 8 bits antes de confirmar."

def acionar_confirmacao_m3():
    global m3_quadro, m3_audio, m3_msg
    if len(m3_input_text) == 8:
        m3_quadro, m3_audio = prog3.gerar_audio_fsk(m3_input_text)
        m3_msg = "[SISTEMA] Quadro gerado! 4 Bits de soma calculados. Pronto para transmitir."
    else:
        m3_msg = "[ERRO] Digite exatamente 8 bits antes de confirmar."

def acionar_confirmacao_m5():
    global m5_quadro, m5_audio, m5_msg
    if len(m5_input_text) > 0:
        m5_quadro, m5_audio = prog5.gerar_audio_fsk(m5_input_text)
        m5_msg = f"[SISTEMA] Header (8b) + Dados ({len(m5_input_text)*8}b) + Checksum (8b) gerados."
    else:
        m5_msg = "[ERRO] A mensagem não pode estar vazia."

def iniciar_gui():
    global tela_atual, stream_audio, m6_input_text, m6_quadro, m6_audio, m6_msg, m3_input_text, m3_quadro, m3_audio, m3_msg, m5_input_text, m5_quadro, m5_audio, m5_msg, m4_historico_ativo
    
    relogio = pygame.time.Clock()
    a_executar = True
    
    while a_executar:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                a_executar = False
                
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos
                
                if tela_atual == "MENU":
                    if 100 <= mx <= 800:
                        if 90 <= my <= 165:
                            m6_input_text = ""
                            m6_quadro = ""
                            m6_audio = None
                            m6_msg = ""
                            tela_atual = "M6"
                            if stream_audio: stream_audio.stop(); stream_audio.close()
                            
                        elif 185 <= my <= 260:
                            prog.bit_buffer.clear()
                            prog.historico_quadros.clear()
                            prog.resultado_validacao = ""
                            prog.is_paused = True; tela_atual = "M1"
                            if stream_audio: stream_audio.stop(); stream_audio.close()
                            stream_audio = sd.InputStream(callback=prog.process_audio_stream, channels=1, samplerate=44100)
                            stream_audio.start()
                            
                        elif 280 <= my <= 355:
                            m3_input_text = ""
                            m3_quadro = ""
                            m3_audio = None
                            m3_msg = ""
                            tela_atual = "M3"
                            if stream_audio: stream_audio.stop(); stream_audio.close()
                            
                        elif 375 <= my <= 450:
                            prog2.bit_buffer.clear()
                            prog2.historico_quadros.clear()
                            prog2.resultado_validacao = ""
                            prog2.is_paused = True; tela_atual = "M2"
                            if stream_audio: stream_audio.stop(); stream_audio.close()
                            stream_audio = sd.InputStream(callback=prog2.processar_audio_fsk, channels=1, samplerate=44100, blocksize=1024)
                            stream_audio.start()
                            
                        elif 470 <= my <= 545:
                            m5_input_text = ""
                            m5_quadro = ""
                            m5_audio = None
                            m5_msg = ""
                            tela_atual = "M5"
                            if stream_audio: stream_audio.stop(); stream_audio.close()

                        elif 565 <= my <= 640:
                            prog4.bit_buffer.clear()
                            prog4.historico_quadros.clear()
                            prog4.resultado_validacao = ""
                            prog4.total_simbolos_esperados = None
                            prog4.is_paused = True 
                            m4_historico_ativo = None
                            tela_atual = "M4"
                            if stream_audio: stream_audio.stop(); stream_audio.close()
                            stream_audio = sd.InputStream(callback=prog4.processar_audio_fsk, channels=1, samplerate=44100, blocksize=1024)
                            stream_audio.start()

                elif tela_atual in ["M6", "M1", "M2", "M3", "M4", "M5"]:
                    if 20 <= mx <= 130 and 20 <= my <= 60:
                        sd.stop() 
                        if stream_audio: stream_audio.stop(); stream_audio.close(); stream_audio = None
                        tela_atual = "MENU"
                    
                    if tela_atual in ["M1", "M2", "M4"] and 720 <= mx <= 780 and 20 <= my <= 80:
                        if tela_atual == "M1":
                            prog.is_paused = not prog.is_paused
                            if not prog.is_paused: prog.last_impact_time = time.time()
                        elif tela_atual == "M2":
                            prog2.is_paused = not prog2.is_paused
                        elif tela_atual == "M4":
                            prog4.is_paused = not prog4.is_paused
                            if not prog4.is_paused:
                                m4_historico_ativo = None 
                                prog4.bit_buffer.clear()
                                
                    if tela_atual == "M6":
                        if 240 <= mx <= 390 and 110 <= my <= 150:
                            acionar_confirmacao_m6()
                        elif m6_audio is not None and 200 <= mx <= 440 and 350 <= my <= 410:
                            prog6.transmitir(m6_audio)
                            m6_msg = "[SISTEMA] A transmitir áudio de batidas mecânicas..."
                        elif m6_audio is not None and 460 <= mx <= 700 and 350 <= my <= 410:
                            sucesso, caminho = exportar_wav(m6_audio)
                            if sucesso: m6_msg = f"[SUCESSO] Guardado em: {caminho}"
                            
                    if tela_atual == "M3":
                        if 240 <= mx <= 390 and 110 <= my <= 150:
                            acionar_confirmacao_m3()
                        elif m3_audio is not None and 200 <= mx <= 440 and 350 <= my <= 410:
                            prog3.transmitir(m3_audio)
                            m3_msg = "[SISTEMA] A transmitir áudio FSK..."
                        elif m3_audio is not None and 460 <= mx <= 700 and 350 <= my <= 410:
                            sucesso, caminho = exportar_wav(m3_audio)
                            if sucesso: m3_msg = f"[SUCESSO] Guardado em: {caminho}"

                    if tela_atual == "M4":
                        y_hist = 570
                        for idx, reg in enumerate(prog4.historico_quadros):
                            btn_dots = pygame.Rect(600, y_hist - 2, 40, 20)
                            if btn_dots.collidepoint(mx, my):
                                m4_historico_ativo = idx if m4_historico_ativo != idx else None
                            y_hist += 25

                    if tela_atual == "M5":
                        larg_btn = max(200, len(m5_input_text) * 18 + 20) + 30
                        if larg_btn <= mx <= larg_btn + 130 and 110 <= my <= 150:
                            acionar_confirmacao_m5()
                        elif m5_audio is not None and 200 <= mx <= 440 and 600 <= my <= 660:
                            prog5.transmitir(m5_audio)
                            m5_msg = "[SISTEMA] A transmitir áudio 16-FSK..."
                        elif m5_audio is not None and 460 <= mx <= 700 and 600 <= my <= 660:
                            sucesso, caminho = exportar_wav(m5_audio)
                            if sucesso: m5_msg = f"[SUCESSO] Guardado em: {caminho}"
                            
            elif evento.type == pygame.KEYDOWN and tela_atual == "M6":
                if evento.key == pygame.K_BACKSPACE:
                    m6_input_text = m6_input_text[:-1]
                elif evento.key == pygame.K_RETURN:
                    acionar_confirmacao_m6()
                elif evento.unicode in ['0', '1']:
                    if len(m6_input_text) < 8:
                        m6_input_text += evento.unicode
                        
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
                elif evento.unicode.isprintable(): 
                    if len(m5_input_text) < 31: 
                        m5_input_text += evento.unicode

        if tela_atual == "MENU": desenhar_menu()
        elif tela_atual == "M6": desenhar_m6()
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