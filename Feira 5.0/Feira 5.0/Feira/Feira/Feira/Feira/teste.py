from PySide6.QtWidgets import QWidget, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import cv2 # Câmera
from PIL import ImageFont, ImageDraw, Image # Suporta Unicode ( Emojis )
import mediapipe as mp # Pontos da Mão
import numpy as np # Arrays sofiticados
from collections import deque # Sistema de Fila, Contagem da maior quantidade de vezes que um índice aparece
import time # Sistema de Tempo
from libras import *

class TesteWindow(QWidget):
    def __init__(self, stacked, cursor_label, main_window, caminho_pasta):
        super().__init__()
        self.stacked = stacked
        self.cursor_label = cursor_label
        self.main_window = main_window
        self.caminho_pasta = caminho_pasta

        # Verificação - LIBRAS
        self.trajetoria = deque(maxlen=3)  # guarda temporariamente os últimos 3 frames ( coordenadas )
        self.trajetoria_suavizada = deque(maxlen=100)  # guarda os últimos 300 frames ( coordenadas )
        self.historico_frames = deque(maxlen=15)  # guarda os últimos 15 "pacotes" ( Informações importantes do frame )

        # Para controlar o tempo que o dedo ficou sobre cada botão
        self.tempos_botoes = {}
        self.progresso_botoes = {}

        self.gravando = False  # Estado de gravação
        self.gravou = False  # Já Gravou?
        self.tempo_inicio = None  # horário que a gravação foi iniciada
        self.tempo_botao_voltar = None  # Começou a tocar no Botão
        self.aguardando_inicio = False  # movimentou a mão e está esperando o timer de 2seg passar para iniciar a gravação
        self.status = "Movimente a Mao Para Iniciar a Gravacao"  # Texto que vai aparecer na parte de cima da câmera
        self.letra = ""  # Letra Detectada
        self.rotacao_inicial = None  # Ex: Frente, Trás, Lado, Diagonal
        self.rotacao_final = None  # Ex: Frente, Trás, Lado, Diagonal
        self.timecursor = time.time()  # Tempo que a pessoa tem que ficar com a mao fora da camera pro cursor sumir

        # PySide6
        self.setGeometry(0, 0, 1366, 768)

        # ========== NOVO: BOX PRINCIPAL (caixa branca com borda e radius, similar aos outros; câmera dentro) ==========
        self.box = QLabel(self)
        self.box.setGeometry(40, 30, 1286, 708)  # Mantida a geometry original para caber na tela
        self.box.setStyleSheet("""
            background-color: #ffffff;  /* Branco como nos outros boxes */
            border: 2px solid #463d77;  /* Borda roxa-azulada opcional, como no menu; remova se não quiser */
            border-radius: 20px;
        """)
        self.box.show()

        # ========== ADICIONADO: Área da câmera (agora dentro do novo box branco) ==========
        self.cam = QLabel(self.box)  # Filho do box
        self.cam.setGeometry(300, 120, 700,
                             500)  # AJUSTADO: Altura reduzida para 600px (deixa espaço abaixo para o botão)
        self.cam.setStyleSheet("""
            background-color: #463d77 !important;  /* Fundo roxo escuro */
            border: 6px solid #463d77;             /* Borda escura */
            border-radius: 20px;                    /* Cantos arredondados */
        """)

        self.cam.setContentsMargins(15, 15, 15, 15)

        self.cam.show()
        # ========== FIM DA CÂMERA ==========

         # Título principal no topo da janela
        titulo = QLabel("TESTE", self.box)
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setGeometry(0, 20, 1286, 80)   # largura total da janela
        titulo.setStyleSheet("""
            QLabel {
                font-size:100px;
                font-weight: bold;
                color: #5b6092;
                background: transparent;
                border:none;
            }
        """)

        # Botão Voltar (AJUSTADO: Agora dentro do box, abaixo da câmera, centralizado)
        self.button_back = QPushButton(" Voltar ", self.box)  # Mudado para filho do box
        self.button_back.setGeometry(475, 640, 400,
                                     60)  # Posição relativa ao box: centralizado abaixo da câmera (ajuste largura/altura se quiser)
        self.button_back.setStyleSheet("""
            border-radius: 10px; 
            font-size: 40px;
            background-color: #463d77;  /* Fundo roxo-azulado para combinar com o tema */
            color: white;
            font-weight: bold;
            border: 2px solid #212741;
        """)
        self.button_back.clicked.connect(self.open_firstPage)
        self.button_back.show()

    def verificar_dedo_botao(self, centro, botoes):
        """Verifica se o dedo está dentro de um botão"""
        x, y = centro[:2]

        for nome, botao in botoes.items():
            bx, by, bw, bh = botao.geometry().getRect()
            dentro = (bx <= x <= bx + bw and by <= y <= by + bh)

            if dentro:
                # Se o dedo acabou de entrar
                if nome not in self.tempos_botoes or self.tempos_botoes[nome] is None:
                    self.tempos_botoes[nome] = time.time()
                    self.progresso_botoes[nome] = 0
                else:
                    # Calcula progresso do carregamento
                    progresso = (time.time() - self.tempos_botoes[nome]) / 2.0

                    if progresso >= 1.0:
                        botao.click()
                        self.tempos_botoes[nome] = None
                        self.progresso_botoes[nome] = 0
            else:
                self.tempos_botoes[nome] = None
                self.progresso_botoes[nome] = 0

    def process_frame(self, ret, frame, results, mp_hands, mp_draw):
        """
        frame: frame BGR do OpenCV
        results: saída do MediaPipe (hands.process)
        mp_hands, mp_draw: objetos passados pelo CameraManager
        """
        try:
            # DEBUG: confirmar chamada
            # print("process_frame chamado", bool(results and results.multi_hand_landmarks))

            if results is None:
                return

            if results.multi_hand_landmarks:
                self.timecursor = time.time()
                for idx, mao in enumerate(results.multi_hand_landmarks):
                    # desenha os landmarks no frame (opcional)
                    mp_draw.draw_landmarks(frame, mao, mp_hands.HAND_CONNECTIONS)
                    # Obtém os Pontos da Mão
                    landmarks = mao.landmark

                    # controle de gravação / estados (mantive sua lógica)
                    if self.gravando:
                        if movimento_parado(self.trajetoria_suavizada):
                            # limpa alguns pontos e marca gravado
                            for i in range(10):
                                if self.trajetoria_suavizada:
                                    self.trajetoria_suavizada.pop()
                            self.gravando = False
                            self.gravou = True
                    elif movimento_andando(self.trajetoria_suavizada):
                        self.aguardando_inicio = True
                        if self.tempo_inicio is None:
                            self.tempo_inicio = time.time()

                    if self.aguardando_inicio:
                        t = time.time() - (self.tempo_inicio or 0)
                        if t < 0.5:
                            self.status = "Gravando em 2s..."
                        elif t < 0.8:
                            self.status = "Gravando em 1s..."
                        elif t < 1.1:
                            self.status = "Gravando..."
                        else:
                            self.gravando = True
                            self.aguardando_inicio = False
                            self.tempo_inicio = None
                            self.trajetoria_suavizada.clear()

                    tamanho = len(self.trajetoria_suavizada)

                    # desenha a trajetória e atualiza cursor
                    if tamanho > 1:
                        ultimas = list(self.trajetoria_suavizada)
                        ultimas = ultimas[-2:]
                        media_x = sum(p['centro'][0] for p in ultimas) / 2
                        media_y = sum(p['centro'][1] for p in ultimas) / 2

                        # Começa do Centro, não do canto esquerdo
                        dedo_x = int((media_x - 0.5) * 2.0 * 1366 + 683)
                        dedo_y = int((media_y - 0.5) * 2.0 * 768 + 384)
                        dedo_x = max(0, min(1366, dedo_x))
                        dedo_y = max(0, min(768, dedo_y))
                        
                        x = landmarks[9].x
                        y = landmarks[9].y
                        # ponto está dentro do frame?
                        inside_frame = (0.20 <= x <= 0.80 and 0.20 <= y <= 0.80)
                        print(inside_frame)

                        if inside_frame:
                            self.cursor_label.hide()

                        else:
                            self.cursor_label.move(
                                dedo_x - self.cursor_label.width() // 2,
                                dedo_y - self.cursor_label.height() // 2
                            )

                            self.verificar_dedo_botao(
                                (dedo_x, dedo_y),
                                {"button_back": self.button_back}
                            )

                            self.cursor_label.show()

                        # desenha linhas de trajetória no frame (em coordenadas do frame)
                        for i in range(1, tamanho):
                            pt1 = self.trajetoria_suavizada[i - 1]['indicador'][:2]
                            pt2 = self.trajetoria_suavizada[i]['indicador'][:2]
                            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

                # Adiciona valores a lista "historico_frames"      
                self.historico_frames = process_detector(frame, results, self.historico_frames, self.trajetoria, self.trajetoria_suavizada)

            elif time.time() - self.timecursor > 0.5:
                self.cursor_label.hide()

            # Quando a gravação terminou, faz a detecção de letra
            if not self.gravando and self.gravou and landmarks is not None and self.trajetoria_suavizada:
                try:
                    self.status = "Movimente a Mão Para Iniciar a Gravação"
                    self.tempo_inicio = None
                    self.gravou = False
                    self.aguardando_inicio = False
                    # Detecta a letra 
                    self.letra = detectar_letras(self.historico_frames)
                finally:
                    # limpa estado depois da tentativa
                    self.rotacao_final = None
                    self.rotacao_inicial = None
                    self.trajetoria_suavizada.clear()

            # --- desenha texto com PIL e atualiza QLabel (mantido da sua versão) ---
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)

            font_status = ImageFont.truetype("seguiemj.ttf", 30)
            font_letra  = ImageFont.truetype("seguiemj.ttf", 40)

            draw.text((10, 30), self.status, font=font_status, fill=(255, 255, 255))
            draw.text((10, 70), f"Letra: {self.letra}", font=font_letra, fill=(255, 0, 0))

            frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

            # atualiza QLabel
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qimg).scaled(self.cam.width(), self.cam.height())
            self.cam.setPixmap(pixmap)

        except Exception as e:
            # se alguma coisa falhar, loga e não deixa travar o loop do CameraManager
            import traceback
            print("Erro em ConversorPage.process_frame:", e)
            traceback.print_exc()

    def open_firstPage(self):
        self.main_window.switch_to_page(0)
        self.cursor_label.hide()