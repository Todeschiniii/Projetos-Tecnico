from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, Qt, QFont, QColor, QPainter
from PySide6.QtCore import Qt, QTimer, QRect
from collections import deque
import mediapipe as mp # Pontos da Mão
import time # Sistema de Tempo
from camera_manager import CameraManager

class MenuWindow(QWidget):
    def __init__(self, stacked, cursor_label, main_window, caminho_pasta):
        super().__init__()
        self.stacked = stacked
        self.cursor_label = cursor_label
        self.main_window = main_window
        self.caminho_pasta = caminho_pasta
        self.camera_manager = CameraManager()
        # Dicionário para armazenar progresso de cada botão
        self.progresso_botoes = {}
        # Dicionário para armazenar o tempo que cada botao foi pressionado
        self.tempos_botoes = {}
        self.trajetoria = deque(maxlen = 2)
        self.timecursor = time.time()

        # Caixa principal
        self.box = QLabel(self)
        self.box.setGeometry(40, 30, 1286, 708)
        self.box.setStyleSheet("""
            background-color: #ffffff;
            border: 2px solid #5b6092;
            border-radius: 20px;
        """)
        self.box.show()

        # Área da câmera (placeholder)
        self.cam = QLabel(self.box)
        self.cam.setGeometry(20, 15, 1366, 768)
        self.cam.setStyleSheet("""
            background-color: #5b6092;
            border: 2px solid #5b6092;
            border-radius: 30px;
        """)
        self.cam.hide()
        
        # Título
        self.title = QLabel("LIBRAS", self.box)
        self.title.setFixedSize(900, 100)
        self.title.setStyleSheet("""
            color: #5b6092;
            font-weight: bold;
            font-family: Arial;
            font-size: 90px;
            border: none;  /* 🔹 remove qualquer borda */
            background: transparent;  /* 🔹 fundo transparente */
        """)
        self.title.move(470, 70)
        self.title.show()

        # Botão - Sair
        self.button_exit = QPushButton("", self)
        self.button_exit.setGeometry(570, 620, 220, 70)
        self.button_exit.setFlat(True)
        self.button_exit.setStyleSheet("""
            QPushButton {
                background-color: #463d77;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #5c4d99;
                color: white;
            }
            QPushButton:pressed {
                background-color: #3a3166;
                color: white;
            }
        """)

        self.layout_exit = QVBoxLayout(self.button_exit)
        self.layout_exit.setContentsMargins(15, 15, 15, 15)  # esquerda, topo, direita, inferior ( ajustar margens internas )
        self.layout_exit.setAlignment(Qt.AlignCenter)

        title_exit = QLabel("SAIR")
        title_exit.setStyleSheet("""
            font-size:26pt;
            font-weight:bold;
            border: none;
            background: transparent;
            color:white;
        """)

        self.layout_exit.addWidget(title_exit)
        self.button_exit.clicked.connect(self.exit)
        # Botão - Teste
        self.button_teste = QPushButton("", self)
        self.button_teste.setGeometry(120, 260, 350, 260)
        self.button_teste.setFlat(True)
        self.button_teste.setStyleSheet("""
            QPushButton {
                background-color: #463d77;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #5c4d99;
                color: white;
            }
            QPushButton:pressed {
                background-color: #3a3166;
                color: white;
            }
        """)

        self.layout_teste = QVBoxLayout(self.button_teste)
        self.layout_teste.setContentsMargins(15, 15, 15, 15)  # esquerda, topo, direita, inferior ( ajustar margens internas )
        self.layout_teste.setAlignment(Qt.AlignTop)

        title_teste = QLabel("TESTE")
        title_teste.setStyleSheet("""
            font-size:26pt;
            font-weight:bold;
            border: none;
            background: transparent;
            color:white;
        """)
        
        text_teste = QLabel(
            "   Teste nosso detector de LIBRAS sem nenhum mecanismo especial! Faça o Sinal em LIBRAS e veja seu significado em Português!"
        )
        text_teste.setWordWrap(True)
        text_teste.setMaximumWidth(self.button_teste.width() - 30)
        text_teste.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        text_teste.setStyleSheet("""
            font-size:18pt; 
            border: none;
            background: transparent;
            color:white;
        """)


        self.layout_teste.addWidget(title_teste)
        self.layout_teste.addWidget(text_teste)

        self.button_teste.clicked.connect(self.open_teste)
        self.button_teste.show()

        # Botão do jogo da jogo        
        self.button_jogo = QPushButton("", self)
        self.button_jogo.setGeometry(500, 260, 350, 300)
        self.button_jogo.setFlat(True)
        self.button_jogo.setStyleSheet("""
            QPushButton {
                background-color: #463d77;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #5c4d99;
                color: white;
            }
            QPushButton:pressed {
                background-color: #3a3166;
                color: white;
            }
        """)

        self.layout_jogo = QVBoxLayout(self.button_jogo)
        self.layout_jogo.setContentsMargins(15, 15, 15, 15)  # esquerda, topo, direita, inferior ( ajustar margens internas )
        self.layout_jogo.setAlignment(Qt.AlignTop)

        title_jogo = QLabel("  JOGO DA FORCA")
        title_jogo.setStyleSheet("""
            font-size:26pt;
            font-weight:bold;
            border: none;
            background: transparent;
            color:white;
        """)

        text_jogo = QLabel(
            "   Utilize dos sinais de Libras para jogar o jogo da Forca. Cada acerto revela uma letra da palavra!<br>Cuidado⚠️: Você tem tentativas limitadas"
        )
        text_jogo.setWordWrap(True)
        text_jogo.setMaximumWidth(self.button_jogo.width() - 30)
        text_jogo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        text_jogo.setStyleSheet("""
            font-size:18pt; 
            border: none;
            background: transparent;
            color:white;
        """)


        self.layout_jogo.addWidget(title_jogo)
        self.layout_jogo.addWidget(text_jogo)

        self.button_jogo.clicked.connect(self.open_jogo)
        self.button_jogo.show()

        # Botão Formação de Palavras
        self.button_palavras = QPushButton("", self)
        self.button_palavras.setGeometry(880, 260, 350, 260)
        self.button_palavras.setFlat(True)
        self.button_palavras.setStyleSheet("""
            QPushButton {
                background-color: #463d77;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #5c4d99;
                color: white;
            }
            QPushButton:pressed {
                background-color: #3a3166;
                color: white;
            }
        """)

        self.layout_palavras = QVBoxLayout(self.button_palavras)
        self.layout_palavras.setContentsMargins(15, 15, 15, 15)  # esquerda, topo, direita, inferior ( ajustar margens internas )
        self.layout_palavras.setAlignment(Qt.AlignTop)

        title_palavras = QLabel("PALAVRAS")
        title_palavras.setStyleSheet("""
            font-size:26pt;
            font-weight:bold;
            border: none;
            background: transparent;
            color:white;
        """)

        text_palavras = QLabel(
            "   Utilize de Sinais em LIBRAS para formar palavras e frases! Faça esse símbolo: 🤚 para registrar sua palavra!"
        )
        text_palavras.setWordWrap(True)
        text_palavras.setMaximumWidth(self.button_palavras.width() - 30)
        text_palavras.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        text_palavras.setStyleSheet("""
            font-size:18pt; 
            border: none;
            background: transparent;
            color:white;
        """)


        self.layout_palavras.addWidget(title_palavras)
        self.layout_palavras.addWidget(text_palavras)

        self.button_palavras.clicked.connect(self.open_palavras)
        self.button_palavras.show()

        title_teste.setAlignment(Qt.AlignCenter)
        text_teste.setAlignment(Qt.AlignCenter)

        title_palavras.setAlignment(Qt.AlignCenter)
        text_jogo.setAlignment(Qt.AlignCenter)

        title_palavras.setAlignment(Qt.AlignCenter)
        text_palavras.setAlignment(Qt.AlignCenter)

    # ------------------------
    # Métodos da classe
    # ------------------------
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
        """Processa landmarks da mão e move cursor"""
        if results.multi_hand_landmarks:
            self.timecursor = time.time()
            for hand_landmarks in results.multi_hand_landmarks:
                centro = hand_landmarks.landmark[0]
                coord = (centro.x, centro.y)
                self.trajetoria.append(coord)

                if len(self.trajetoria) > 2:
                    ultimas = list(self.trajetoria)
                    media_x = sum(p[0] for p in ultimas) / 3
                    media_y = sum(p[1] for p in ultimas) / 3
                    dedo_x = int((media_x - 0.5) * 2.0 * 1366 + 683)
                    dedo_y = int((media_y - 0.5) * 2.0 * 768 + 384)
                    dedo_x = max(0, min(1366, dedo_x))
                    dedo_y = max(0, min(768, dedo_y))

                    self.cursor_label.move(
                        dedo_x - self.cursor_label.width() // 2,
                        dedo_y - self.cursor_label.height() // 2
                    )

                    self.verificar_dedo_botao(
                        (dedo_x, dedo_y),
                        {"button_teste": self.button_teste, "button_jogo": self.button_jogo, "button_palavras": self.button_palavras}
                    )

                    self.trajetoria.clear()

            self.cursor_label.show()
        elif time.time() - self.timecursor > 0.5:
                self.cursor_label.hide()

        self.cursor_label.raise_()

    def open_teste(self):
        """Troca para página de Teste"""
        self.cursor_label.hide()
        self.main_window.switch_to_page(1)
        self.camera_manager.show_rectangle = True

    def open_jogo(self):
        """Troca para página da Formação de Palavras"""
        self.cursor_label.hide()
        self.main_window.switch_to_page(2)
        self.camera_manager.show_rectangle = False

    def open_palavras(self):
        """Troca para página da Formação de Palavras"""
        self.cursor_label.hide()
        self.main_window.switch_to_page(3)
        self.camera_manager.show_rectangle = False

    def exit(self):
        import main
        main.QApplication.quit()