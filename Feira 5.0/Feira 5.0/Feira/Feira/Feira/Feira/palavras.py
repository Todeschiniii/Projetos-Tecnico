import time
from collections import deque
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QLineEdit, QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
import cv2  # Câmera
from PIL import ImageFont, ImageDraw, Image  # Suporta Unicode ( Emojis )
import numpy as np  # Arrays sofiticados
from collections import deque  # Sistema de Fila, Contagem da maior quantidade de vezes que um índice aparece
import time  # Sistema de Tempo
from libras import *


class PalavrasWindow(QWidget):
    def __init__(self, stacked, cursor_label, main_window, caminho_pasta):
        super().__init__()

        self.stacked = stacked
        self.cursor_label = cursor_label
        self.main_window = main_window
        self.caminho_pasta = caminho_pasta

        self.setWindowTitle("Detector de Libras - Video Chat")
        # ---------- STYLE SHEET PRINCIPAL ----------
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 14px;
            }
        """)
        # ---------- DETECÇÃO DE TELA PARA RESPONSIVIDADE ----------
        self.setFixedSize(1366, 768)

        # Caixa principal (container fixo dentro da janela)
        self.box = QWidget(self)
        self.box.setGeometry(40, 30, 1286, 708)
        self.box.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border-radius: 20px;
            }
        """)

        # Layout interno da box
        main_layout = QVBoxLayout(self.box)
        main_layout.setContentsMargins(100, 80, 80, 120) # esquerda, topo, direita, inferior ( ajustar margens internas )

        # ---------- HEADER ----------
        header = QLabel("Detector de Libras - Video Chat")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: white;
                background: transparent;
                padding: 20px;
            }
        """)
        main_layout.addWidget(header)

        # Título principal no topo da janela
        titulo = QLabel("PALAVRAS", self)
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setGeometry(0, 50, 1366, 80)   # largura total da janela
        titulo.setStyleSheet("""
            QLabel {
                font-size:100px;
                font-weight: bold;
                color: #5b6092;
                background: transparent;
                border:none;
            }
        """)
        titulo.raise_()

        # Layout horizontal ou vertical
        content_layout = QHBoxLayout()
        content_layout.setSpacing(200)

        main_layout.addLayout(content_layout)

        # ---------- VÍDEO ----------
        video_widget = QWidget()
        video_widget.setStyleSheet("""
            QWidget {
                background-color: #463d77 !important;  /* Fundo roxo escuro */
                border: 2px solid #463d77;  /* Borda roxa-azulada opcional, como no menu; remova se não quiser */
                border-radius: 20px;                   /* Radius maior */
            }
        """)
        video_widget.setFixedSize(540, 400)

        video_layout = QVBoxLayout(video_widget)
        video_layout.setContentsMargins(15, 15, 15, 15)  # 20px de margem em volta
        self.label_camera = QLabel("📷")
        self.label_camera.setAlignment(Qt.AlignCenter)
        self.label_camera.setStyleSheet("""
            border-radius: 20px;
            background-color: black !important;
        """)
        video_layout.addWidget(self.label_camera)
        
        # ---------- CHAT ----------
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.chat_box.setStyleSheet("""
            QTextEdit {
                background-color: #2e2459;   /* roxo escuro */
                color: #d6b8ff;              /* lilás claro */
                border-radius: 20px;          /* bordas mais arredondadas */
                font-size: 18px;
                padding: 10px;
            }
        """)
        self.chat_box.setFixedSize(400, 350)
        right_layout.addWidget(self.chat_box)
        right_layout.addSpacing(200)

        # Entrada
        input_widget = QWidget()
        input_widget.setFixedWidth(400)
        input_layout = QHBoxLayout(input_widget)
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Digite sua mensagem...")
        self.input_box.setFixedHeight(50)
        self.input_box.move(self.input_box.x(), self.input_box.y() - 50)
        
        self.input_box.setStyleSheet("""
            QLineEdit {
                background: white !important;
                border: 2px solid #3399ff;
                border-radius: 15px;
                padding: 10px;
                font-size: 18px;
                color: #003366;
            }
            QLineEdit:focus {
                border: 5px solid #0077cc;
                background: #f9fcff !important;
            }
        """)

        self.btn_cancel = QPushButton("❌")
        btn_size = 50
        self.btn_cancel.setFixedSize(btn_size, btn_size)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                border-radius: {btn_size // 2}px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e60000, stop:1 #cc0000) !important;
                font-size: {22}px;
                font-weight: bold;
                color: white;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff3333, stop:1 #e60000);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a00000, stop:1 #cc0000);
            }}
        """)
        self.btn_cancel.clicked.connect(self.limpar_palavra)

        self.btn_send = QPushButton("✅")
        self.btn_send.setFixedSize(btn_size, btn_size)
        self.btn_send.setStyleSheet(f"""
            QPushButton {{
                border-radius: {btn_size // 2}px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #28a745, stop:1 #218838) !important;
                font-size: {22}px;
                font-weight: bold;
                color: white;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2ecc71, stop:1 #28a745);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e7e34, stop:1 #218838);
            }}
        """)
        self.btn_send.clicked.connect(self.enviar_palavra)

        self.btn_voltar = QPushButton(" VOLTAR ", self)  # Filho da janela principal
        self.btn_voltar.setFixedSize(400, 80)  # Tamanho similar ao TesteWindow
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                font-size: 40px;
                padding: 10px 20px;
                background-color: #463d77;
                color: white;
                border: 2px solid #212741;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a4a1e9;
                color: #212741;
            }
            QPushButton:pressed {
                background-color: #f3e8f9;
                color: #003366;
            }
        """)
        self.btn_voltar.clicked.connect(self.open_firstPage)  # Conecta à função existente
        self.btn_voltar.show()
        self.btn_voltar.setParent(self.box)  # botão dentro do container principal
        self.btn_voltar.move(
            (self.box.width() - self.btn_voltar.width()) // 2,  # centralizado no eixo X
            self.box.height() - self.btn_voltar.height() - 20   # 20px acima do fundo
        )
        right_layout.setContentsMargins(0, 0, 0, 0)  # remove margem superior original
        
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.btn_cancel)
        input_layout.addWidget(self.btn_send)
        right_layout.addWidget(input_widget)

        # Adiciona ao layout principal
        content_layout.addWidget(video_widget)
        content_layout.addWidget(right_widget)

        # ---------- BACKEND ----------

        # Formação de Palavras
        self.letra_estavel = None
        self.frames_mesma_letra = 0
        self.frames_necessarios = 10
        self.letra_aceita_recentemente = False

        self.palavra_atual = ""
        self.ultimo_tempo = 0
        self.intervalo_minimo = 1.0

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
                                {"✅": self.btn_send, "❌": self.btn_cancel}
                            )

                            self.cursor_label.show()

                        # desenha linhas de trajetória no frame (em coordenadas do frame)
                        for i in range(1, tamanho):
                            pt1 = self.trajetoria_suavizada[i - 1]['indicador'][:2]
                            pt2 = self.trajetoria_suavizada[i]['indicador'][:2]
                            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

                # Adiciona valores a lista "historico_frames"
                self.historico_frames = process_detector(frame, results, self.historico_frames, self.trajetoria,
                                                         self.trajetoria_suavizada)

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

            letra_detectada = self.letra

            if letra_detectada == "":
                self.letra_estavel = None
                self.frames_mesma_letra = 0
                self.letra_aceita_recentemente = False
            else:
                if letra_detectada == self.letra_estavel:
                    self.frames_mesma_letra += 1
                else:
                    self.letra_estavel = letra_detectada
                    self.frames_mesma_letra = 1

                if self.frames_mesma_letra >= self.frames_necessarios:
                    agora = time.time()
                    if not self.letra_aceita_recentemente and (agora - self.ultimo_tempo > self.intervalo_minimo):
                        self.palavra_atual += letra_detectada
                        self.input_box.setText(self.palavra_atual)
                        self.letra_aceita_recentemente = True
                        self.ultimo_tempo = agora
                        self.letra = ""

            # --- desenha texto com PIL e atualiza QLabel (mantido da sua versão) ---
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)

            font_status = ImageFont.truetype("seguiemj.ttf", 30)
            font_letra = ImageFont.truetype("seguiemj.ttf", 40)

            draw.text((10, 30), self.status, font=font_status, fill=(255, 255, 255))
            draw.text((10, 70), f"Letra: {self.letra}", font=font_letra, fill=(255, 0, 0))

            frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

            # atualiza QLabel
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qimg).scaled(self.label_camera.width(), self.label_camera.height())
            self.label_camera.setPixmap(pixmap)

        except Exception as e:
            # se alguma coisa falhar, loga e não deixa travar o loop do CameraManager
            import traceback
            print("Erro em ConversorPage.process_frame:", e)
            traceback.print_exc()

    def enviar_palavra(self):
        if self.palavra_atual:
            timestamp = time.strftime("%H:%M")
            mensagem = f'<p style="text-align:left; font-size:24px; margin:5px 0;"><small style="color:#666;">{timestamp}</small> - <strong>{self.palavra_atual}</strong></p>'
            self.chat_box.append(mensagem)
            self.chat_box.verticalScrollBar().setValue(self.chat_box.verticalScrollBar().maximum())
            self.palavra_atual = ""
            self.input_box.clear()

    def limpar_palavra(self):
        self.palavra_atual = ""
        self.input_box.clear()

    def open_firstPage(self):
        self.main_window.switch_to_page(0)
        self.cursor_label.hide()