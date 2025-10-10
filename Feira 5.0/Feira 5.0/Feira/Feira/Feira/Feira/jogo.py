import os
import cv2
import time
import random
import traceback
import numpy as np  # Arrays sofiticados
from collections import deque
from PIL import ImageFont, ImageDraw, Image  # Suporta Unicode ( Emojis )
from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSpacerItem
from PySide6.QtGui import QPixmap, QImage, QIcon
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtWidgets import QSizePolicy
from libras import *  # seu detector de LIBRAS

BG_COLOR = "#5b6092"
CARD_BG = "#a4a1e9"
CARD_TEXT = "#212741"
ACCENT = "#f3e8f9"
MUTED = "#003366"


class ForcaWindow(QWidget):
    def __init__(self, stacked, cursor_label, main_window, caminho_pasta, camera_manager):
        super().__init__()
        self.stacked = stacked
        self.cursor_label = cursor_label
        self.main_window = main_window
        self.caminho_pasta = caminho_pasta

        self.setWindowTitle("Jogo da Forca com LIBRAS")
        self.setGeometry(100, 100, 1366, 768)

        # Verificação da Letra
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

        # Estado do jogo
        self.letras_usadas = set()
        self.letras_acertadas = []
        self.erros = 0
        self.max_erros = 6
        self.palavra = ""
        # Tempo inicial (em segundos) - 3 minutos
        self.tempo_restante = 180  # 3 minutos

        self.setStyleSheet("background-color: white;")

        # ========== NOVO: BOX PRINCIPAL (similar ao menu: container com borda e radius) ==========
        self.box = QLabel(self)
        self.box.setGeometry(40, 30, 1286, 708) # CORRIGIDO: Ajustado para caber na janela 1366x768, centralizado (sem overflow)
        self.box.setStyleSheet(f"""
            background-color: #ffffff;
            border-radius: 20px;
        """)
        self.box.show()

        # CORREÇÃO: Layout interno no box para centralizar elementos automaticamente (vertical e horizontal)
        layout_box = QVBoxLayout(self.box)
        layout_box.setSpacing(60)  # Espaçamento entre elementos (ajuste se quiser mais/menos)
        layout_box.setAlignment(Qt.AlignCenter)  # Centraliza tudo verticalmente no box

        # Mensagem: Escolha uma categoria (agora adicionado ao layout_box, centralizado)
        self.titulo = QLabel("Escolha uma categoria para começar o jogo!")
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setStyleSheet("""
            background-color: #463d77;
            color: white;
            font-size: 35px;
            font-weight: bold;
            border-radius: 10px;
            border: 2px solid #212741;
            padding: 12px 20px;
        """)
        self.titulo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout_box.addWidget(self.titulo)

        # Mensagem: Categorias (agora adicionado ao layout_box, centralizado)
        self.instrucao = QLabel("CATEGORIAS:")
        self.instrucao.setAlignment(Qt.AlignCenter)
        self.instrucao.setStyleSheet("""
            color: #5b6092;
            font-size: 80px;
            font-weight: bold;
            background: transparent;  /* Transparente para se encaixar no box branco */
        """)
        self.instrucao.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout_box.addWidget(self.instrucao)

        # ================= Botões de categoria =================
        self.widget_categorias = QWidget(self.box)
        layout_categorias = QGridLayout(self.widget_categorias)
        layout_categorias.setContentsMargins(0, 0, 0, 0)
        layout_categorias.setSpacing(35)  # Ajustado para caber 6 botões sem apertar

        self.botoes_categoria = {}
        categorias = ["alimentos", "objetos", "paises", "animais", "frutas",
                      "pch"]  # Adicionada "partes_corpo"
        imagens = {
            "alimentos": os.path.join(caminho_pasta, "imagemComida.png"),
            "animais": os.path.join(caminho_pasta, "animais.jpeg"),
            "objetos": os.path.join(caminho_pasta, "objetos.jpeg"),
            "paises": os.path.join(caminho_pasta, "paises.jpeg"),
            "frutas": os.path.join(caminho_pasta, "frutas.jpeg"),
            "pch": os.path.join(caminho_pasta, "pch.png")
            # Assumindo imagem; adicione o arquivo se quiser hover
        }

        posicoes = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]  # Ajustado para 3x2 grid (6 posições)
        nomes_botoes = {  # Mapeamento para nomes amigáveis nos botões
            "alimentos": "Alimentos",
            "objetos": "Objetos",
            "paises": "Países",
            "animais": "Animais",
            "frutas": "Frutas",
            "pch": "PCH"
            # Nome curto para caber; mude para "Partes do Corpo Humano" se preferir (ajuste font-size se necessário)
        }
        for cat, pos in zip(categorias, posicoes):
            nome_amigavel = nomes_botoes.get(cat, cat.capitalize())  # Usa nome amigável ou capitalize padrão
            btn = QPushButton(nome_amigavel, self.widget_categorias)
            btn.setFixedSize(285, 55)
            caminho_img = imagens.get(cat, "")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #463d77;
                    color: white;
                    font-size: 28px;  /* Ligeiramente menor para caber texto longo */
                    font-weight: bold;
                    border-radius: 10px;
                    border: 2px solid #212741;
                }}
                QPushButton:hover {{
                    background-image: url("{caminho_img}");
                    background-repeat: no-repeat;
                    background-position: center;
                    background-size: cover;
                    color: #212741;
                }}
                QPushButton:pressed {{
                    background-color: #a4a1e9;
                    color: #212741;
                }}
            """)
            btn.clicked.connect(lambda checked, c=cat: self.iniciar_jogo(c))
            layout_categorias.addWidget(btn, pos[0], pos[1], alignment=Qt.AlignHCenter)
            self.botoes_categoria[cat] = btn

        layout_box.addWidget(self.widget_categorias, alignment=Qt.AlignCenter)

        layout_box.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ================= Botão Voltar sobreposto =================
        self.btn_voltar_menu = QPushButton(" VOLTAR ", self.box)  # filho de self.box, não do grid
        self.btn_voltar_menu.setFixedSize(380, 65)  # tamanho maior
        self.btn_voltar_menu.setStyleSheet("""
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
        self.btn_voltar_menu.clicked.connect(self.voltar_menu)

        # Posiciona o botão flutuante centralizado horizontalmente, abaixo dos botões de categoria
        layout_box.addWidget(self.btn_voltar_menu, alignment=Qt.AlignHCenter)

        self.btn_voltar_menu.show()
        self.widget_categorias.show()
        print(self.btn_voltar_menu)
        print("AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")

        # Adiciona stretch para centralizar verticalmente e preencher o espaço inferior com branco
        layout_box.addStretch(1)

        # Ativa o layout no box
        self.box.setLayout(layout_box)

        # ========== FIM DA TELA INICIAL (dentro do box, agora centralizada) ==========

        # Ocultar temporariamente os elementos principais do jogo (fora do box)

        # Tela do jogo (mantida exatamente como original: layouts e alinhamentos inalterados)
        self.widget_jogo = QWidget()
        self.layout_jogo = QVBoxLayout(self.widget_jogo)
        self.layout_jogo.setAlignment(Qt.AlignTop)
        self.layout_jogo.setSpacing(10)

        # Tema (abaixo da forca)
        self.label_categoria = QLabel("")
        self.label_categoria.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: white;
            background-color: #463d77;
            padding: 10px 18px;
            border-radius: 8px;
            border: 2px solid #212741;
        """)
        self.label_categoria.setAlignment(Qt.AlignCenter)

        # Letras usadas (abaixo do tema)
        self.label_letras_usadas = QLabel("Letras já usadas: ")
        self.label_letras_usadas.setStyleSheet("""
            font-size: 20px;
            color: white;
            background-color: #463d77;
            padding: 8px 16px;
            border-radius: 8px;
            border: 2px solid #212741;
        """)
        self.label_letras_usadas.setAlignment(Qt.AlignCenter)

        # Iniciar detector em thread separada
        # self.thread_detector = threading.Thread(target=libras.iniciar_detector, daemon=True)
        # self.thread_detector.start()

        # Tempo inicial (em segundos) - 3 minutos
        self.tempo_restante = 180  # 3 minutos

        # Tempo restante (abaixo da câmera)
        self.label_tempo = QLabel("Tempo restante: 03:00")  # Padronizado
        self.label_tempo.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: red;
            background-color: #ffffff;
            padding: 10px 18px;
        """)
        self.label_tempo.setAlignment(Qt.AlignCenter)

        # Botão Reiniciar (abaixo do tempo)
        self.btn_reiniciar = QPushButton("Reiniciar")
        self.btn_reiniciar.setStyleSheet("""
            QPushButton {
                font-size: 20px; 
                padding: 10px 22px;
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
        """)
        self.btn_reiniciar.clicked.connect(self.reiniciar_jogo)
        self.btn_reiniciar.hide()

        # Timer para contagem regressiva - NÃO INICIA AQUI (só em iniciar_jogo)
        self.timer_cronometro = QTimer()
        self.timer_cronometro.timeout.connect(self.atualizar_tempo)
        # self.timer_cronometro.start(1000)  # REMOVIDO: Inicia só no jogo

        # Câmera
        self.label_camera = QLabel()
        self.label_camera.setMinimumSize(320, 240)
        self.label_camera.setMaximumSize(400, 300)
        self.label_camera.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.label_camera.setScaledContents(True)

        camera_container = QWidget()
        camera_layout = QVBoxLayout(camera_container)
        camera_layout.setContentsMargins(4, 4, 4, 4)
        camera_layout.setSpacing(0)
        camera_container.setStyleSheet("""
            border: 6px solid #212741;
            border-radius: 5px;
            background-color: #463d77;
        """)
        camera_layout.addWidget(self.label_camera)

        # Forca
        self.label_forca = QLabel()
        self.label_forca.setFixedSize(300, 300)
        self.label_forca.setAlignment(Qt.AlignCenter)
        self.label_forca.setStyleSheet("background-color: transparent;")

        # Container principal para câmera (esquerda) e forca (direita)
        container_principal = QWidget()
        layout_principal = QHBoxLayout(container_principal)
        layout_principal.setSpacing(400)
        layout_principal.setContentsMargins(30, 10, 30, 10) # esquerda, topo, direita, inferior ( ajustar margens internas )

        # ========== COLUNA DA ESQUERDA (Forca - agora com tema no topo) ==========
        coluna_esquerda = QWidget()  # Renomeado para clareza: agora é a coluna da forca
        layout_esquerda = QVBoxLayout(coluna_esquerda)
        layout_esquerda.setSpacing(15)
        layout_esquerda.setAlignment(Qt.AlignCenter)

        ### MUDANÇA: Adiciona tema no topo da coluna esquerda (canto superior esquerdo)
        layout_esquerda.addWidget(self.label_categoria, alignment=Qt.AlignCenter)
        layout_esquerda.addWidget(self.label_forca, alignment=Qt.AlignCenter)
        layout_esquerda.addWidget(self.label_letras_usadas, alignment=Qt.AlignCenter)

        # ========== COLUNA DA DIREITA (Câmera - agora com tempo no topo) ==========
        coluna_direita = QWidget()  # Renomeado para clareza: agora é a coluna da câmera
        layout_direita = QVBoxLayout(coluna_direita)
        layout_direita.setSpacing(15)
        layout_direita.setAlignment(Qt.AlignCenter)

        ### MUDANÇA: Adiciona tempo no topo da coluna direita (canto superior direito)
        layout_direita.addWidget(self.label_tempo, alignment=Qt.AlignCenter)
        layout_direita.addWidget(camera_container, alignment=Qt.AlignCenter)
        layout_direita.addWidget(self.btn_reiniciar, alignment=Qt.AlignCenter)

        # ========== JUNTA AS DUAS COLUNAS ==========
        ### MUDANÇA: Mantém inversão (forca à esquerda, câmera à direita)
        layout_principal.addWidget(coluna_esquerda)  # Coluna da forca (à esquerda)
        layout_principal.addWidget(coluna_direita)  # Coluna da câmera (à direita)

        # ========== PALAVRA A SER FORMADA (CENTRO, ABAIXO) ==========
        self.label_palavra = QLabel("")
        self.label_palavra.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
            letter-spacing: 10px;
            color: #463d77;  /* CORRIGIDO: Adicionado # para evitar erro de cor inválida */
            background-color: white;
            padding: 20px 40px;
            border-radius: 10px;
            border: 2px solid #463d77;
            margin: 20px;
        """)
        self.label_palavra.setAlignment(Qt.AlignCenter)
        self.layout_jogo.addWidget(self.label_palavra, alignment=Qt.AlignCenter)

        # ========== ADICIONA O CONTAINER PRINCIPAL AO LAYOUT DO JOGO ==========
        self.layout_jogo.addWidget(container_principal)

        ## ========== ADICIONA O JOGO AO LAYOUT PRINCIPAL E ESCONDE ==========
        layout = QVBoxLayout(self) # Layout principal simples, só para o jogo
        self.setLayout(layout)
        layout.addWidget(self.widget_jogo)
        self.widget_jogo.hide()

        self.label_categoria.hide()
        self.label_palavra.hide()
        self.label_letras_usadas.hide()
        self.label_tempo.hide()

        # Força atualização visual para limpar qualquer cache
        self.update()
        self.repaint()

        # Mostrar imagem inicial
        self.atualizar_imagem()

    def reiniciar_jogo(self):
        # Para timers
        self.timer_cronometro.stop()

        # Reseta variáveis
        self.erros = 0
        self.letras_usadas = set()
        self.letras_acertadas = []
        self.tempo_restante = 180
        self.palavra = ""

        # Atualiza interface para estado inicial
        self.label_categoria.hide()
        self.label_forca.hide()
        self.label_palavra.hide()
        self.label_letras_usadas.hide()
        self.label_tempo.hide()
        self.btn_reiniciar.hide()

        self.widget_categorias.show()
        self.widget_jogo.hide()
        self.titulo.show()
        self.instrucao.show()

        self.label_palavra.setText("")
        self.label_letras_usadas.setText("Letras já usadas: ")
        self.label_tempo.setText("TEMPO RESTANTE: 03:00")

        # Atualiza imagem da forca para o estado inicial
        self.atualizar_imagem()
        self.label_camera.show()  # garante que esteja visível

    def voltar_menu(self):
        """Função vazia para o botão Voltar ao Menu (torne funcional depois se quiser)"""
        self.main_window.switch_to_page(0)
        pass

    def iniciar_jogo(self, categoria_escolhida):
        self.categoria = categoria_escolhida
        # Mapeamento para nome amigável no label (para "partes_corpo" exibir "Partes do Corpo Humano")
        nomes_categorias = {
            "alimentos": "Alimentos",
            "objetos": "Objetos",
            "paises": "Países",
            "animais": "Animais",
            "frutas": "Frutas",
            "pch": "PCH"
        }
        nome_categoria_display = nomes_categorias.get(self.categoria, self.categoria.capitalize())
        self.label_categoria.setText(f"Tema: {nome_categoria_display}")

        self.widget_categorias.hide()
        self.titulo.hide()
        self.instrucao.hide()
        self.widget_jogo.show()

        # Banco de palavras (adicionada categoria 'partes_corpo')
        bancoDePalavras = {
            'alimentos': [
                'BANANA', 'LARANJA', 'MORANGO', 'ABACAXI', 'ARROZ',
                'BATATA', 'CENOURA', 'TOMATE', 'LEITE', 'QUEIJO',
                'IOGURTE', 'CHOCOLATE', 'PAO'  # 'pão' sem acento
            ],
            'objetos': [
                'MESA', 'CADEIRA', 'COMPUTADOR', 'TELEFONE', 'CANETA',
                'CADERNO', 'LIVRO', 'GARFO', 'FACA', 'COLHER', 'PRATO',
                'ESPELHO'
            ],
            'paises': [
                'BRASIL', 'ARGENTINA', 'CHILE', 'ALEMANHA', 'ITALIA',
                'ESPANHA', 'MEXICO', 'CHINA', 'PORTUGAL'
            ],
            'animais': [
                'GATO', 'CACHORRO', 'ELEFANTE', 'TIGRE', 'GIRAFA',
                'ZEBRA', 'COELHO', 'PINGUIM', 'TARTARUGA', 'BALEIA',
                'GOLFINHO', 'URSO', 'LOBO'
            ],
            'frutas': [
                'ABACAXI', 'BANANA', 'MANGA', 'MELANCIA', 'PERA',
                'UVA', 'MORANGO', 'KIWI'
            ],
            'pch': [  # Nova categoria: palavras simples (não compostas), em maiúsculo, sem acentos
                'CABECA', 'BRACO', 'PERNA', 'MAO', 'GARGANTA',
                'FARINGE', 'NARIZ', 'BOCA', 'ORELHA', 'CABELO'
            ]
        }

        self.palavra = random.choice(bancoDePalavras[self.categoria])
        self.letras_acertadas = [""] * len(self.palavra)
        self.letras_usadas = set()
        self.erros = 0
        self.tempo_restante = 180

        self.label_palavra.setText(" ".join("_" for _ in self.palavra))
        self.label_letras_usadas.setText("Letras já usadas: ")

        self.atualizar_imagem()
        self.timer_cronometro.start(1000)

        self.btn_reiniciar.show()

        # Esconde os botões e mostra o jogo
        self.widget_categorias.hide()
        self.label_categoria.show()
        self.label_forca.show()
        self.label_palavra.show()
        self.label_letras_usadas.show()
        self.label_tempo.show()

    def atualizar_tempo(self):
        self.tempo_restante -= 1
        minutos = self.tempo_restante // 60
        segundos = self.tempo_restante % 60
        self.label_tempo.setText(f"Tempo restante: {minutos:02d}:{segundos:02d}")

        if self.tempo_restante <= 0:
            self.timer_cronometro.stop()
            self.label_palavra.setText(
                f'<div style="font-size: 32px; letter-spacing: 5px;">'
                f"Tempo esgotado! Você perdeu! A palavra era: {self.palavra.upper()}"
                '</div>'
            )

    def atualizar_imagem(self):
        # CORREÇÃO: Verifica se o arquivo existe e carrega a imagem
        try:
            caminho_img = os.path.join(self.caminho_pasta, f"forca_{self.erros}.png")
            pixmap = QPixmap(caminho_img)
            if pixmap.isNull():
                # Se a imagem não carregar, cria uma placeholder
                pixmap = QPixmap(300, 300)
                pixmap.fill(Qt.white)
            pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label_forca.setPixmap(pixmap)
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")

    def verificar_dedo_botao(self, centro, botoes):
        """Verifica se o dedo está dentro de um botão"""
        x, y = centro[:2]

        for nome, botao in botoes.items():
            rect = botao.geometry()
            bx, by, bw, bh = rect.x(), rect.y(), rect.width(), rect.height()
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
        """Chamado pelo CameraManager a cada frame"""
        if not self.palavra:
            return  # jogo não iniciado

        # Contador FPS (opcional)
        if not hasattr(self, 'frame_count'):
            self.frame_count = 0
            self.last_time = time.time()
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            fps = 30 / (time.time() - self.last_time)
            print(f"FPS aproximado: {fps:.1f}")
            self.last_time = time.time()

        try:
            landmarks = None
            if results.multi_hand_landmarks:
                self.timecursor = time.time()
                for idx, mao in enumerate(results.multi_hand_landmarks):
                    # Desenha landmarks (DESCOMENTADO para ver pontinhos e linhas da mão)
                    mp_draw.draw_landmarks(frame, mao, mp_hands.HAND_CONNECTIONS)

                    # Obtém os Pontos da Mão
                    landmarks = mao.landmark

                    # APPEND MANUAL TEMPORÁRIO à trajetoria (força população, como no seu código original)
                    centro = landmarks[0]
                    coord = (centro.x, centro.y)  # Simples x,y (libras.py pode adicionar z se precisar)
                    self.trajetoria.append(coord)
                    print(f"Debug: Append à trajetoria. Tamanho: {len(self.trajetoria)}")  # Debug: veja se cresce

                    # Controle de gravação / estados (exato do palavras.py)
                    if self.gravando:
                        if movimento_parado(self.trajetoria_suavizada):
                            print("Debug: Movimento parado. Parando gravação.")  # Debug
                            # limpa alguns pontos e marca gravado
                            for i in range(10):
                                if self.trajetoria_suavizada:
                                    self.trajetoria_suavizada.pop()
                            self.gravando = False
                            self.gravou = True
                    elif movimento_andando(self.trajetoria_suavizada):
                        print("Debug: Movimento andando detectado!")  # Debug: deve aparecer ao mover
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
                            print("Debug: Iniciando gravação real.")  # Debug
                            self.gravando = True
                            self.aguardando_inicio = False
                            self.tempo_inicio = None
                            self.trajetoria_suavizada.clear()

                    tamanho = len(self.trajetoria_suavizada)
                    print(f"Debug: Tamanho suavizada: {tamanho}")  # Debug: deve crescer com movimento

                    # Desenha a trajetória e atualiza cursor (exato do palavras.py)
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

                        x = landmarks[9].x  # Ponta do dedo médio
                        y = landmarks[9].y
                        inside_frame = (0.20 <= x <= 0.80 and 0.20 <= y <= 0.80)
                        # print(inside_frame)  # Descomente se quiser ver

                        if inside_frame:
                            self.cursor_label.hide()
                        else:
                            self.cursor_label.move(
                                dedo_x - self.cursor_label.width() // 2,
                                dedo_y - self.cursor_label.height() // 2
                            )
                            self.cursor_label.show()

                        # desenha linhas de trajetória no frame
                        for i in range(1, tamanho):
                            pt1 = self.trajetoria_suavizada[i - 1]['indicador'][:2]
                            pt2 = self.trajetoria_suavizada[i]['indicador'][:2]
                            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

                # Adiciona valores a lista "historico_frames" (exato do palavras.py)
                print(f"Debug: Chamando process_detector. Historico atual: {len(self.historico_frames)}")  # Debug
                self.historico_frames = process_detector(frame, results, self.historico_frames, self.trajetoria,
                                                         self.trajetoria_suavizada)
                print(f"Debug: process_detector concluído. Novo historico: {len(self.historico_frames)}")  # Debug

            elif time.time() - self.timecursor > 0.5:
                self.cursor_label.hide()

            # Quando a gravação terminou, faz a detecção de letra (exato do palavras.py)
            if not self.gravando and self.gravou and landmarks is not None and self.trajetoria_suavizada:
                try:
                    print("Debug: Tentando detectar letra...")  # Debug
                    self.status = "Movimente a Mão Para Iniciar a Gravação"
                    self.tempo_inicio = None
                    self.gravou = False
                    self.aguardando_inicio = False
                    # Detecta a letra
                    self.letra = detectar_letras(self.historico_frames)
                    print(f"Debug: Letra detectada: '{self.letra}'")  # Debug
                finally:
                    # limpa estado depois da tentativa
                    self.rotacao_final = None
                    self.rotacao_inicial = None
                    self.trajetoria_suavizada.clear()

            # Estabilização de letra (copiado do palavras.py, adaptado para o jogo)
            letra_detectada = self.letra
            if not hasattr(self, 'letra_estavel'):
                self.letra_estavel = None
                self.frames_mesma_letra = 0
                self.frames_necessarios = 10
                self.letra_aceita_recentemente = False
                self.ultimo_tempo = 0
                self.intervalo_minimo = 1.0

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
                        # BLOQUEIO DE SÍMBOLOS: Ignora se não for uma letra do alfabeto (A-Z)
                        processar_letra = True  # Flag para controlar o processamento
                        if not self.letra_estavel.isalpha():
                            print(f"Símbolo não é letra válida: '{self.letra_estavel}'. Ignorando.")  # Debug opcional
                            processar_letra = False  # Não processa o jogo
                            self.letra_aceita_recentemente = True  # Marca como "aceito" para evitar spam
                            self.ultimo_tempo = agora
                            self.letra = ""  # Limpa para próxima detecção
                            # Opcional: self.status = "Gesto não é letra válida. Tente uma letra A-Z."

                        # Se for letra válida, processa o jogo
                        if processar_letra:
                            # Integração com o jogo (só para letras válidas A-Z)
                            if self.letra_estavel in self.letras_usadas:
                                print(f"Letra '{self.letra_estavel}' já foi usada.")
                            else:
                                self.letras_usadas.add(self.letra_estavel)
                                self.label_letras_usadas.setText(
                                    "Letras já usadas: " + " ".join(sorted(self.letras_usadas)))

                                if self.letra_estavel in self.palavra.upper():
                                    for i, l in enumerate(self.palavra.upper()):
                                        if l == self.letra_estavel:
                                            self.letras_acertadas[i] = self.letra_estavel
                                    self.label_palavra.setText(
                                        " ".join([l if l else "_" for l in self.letras_acertadas]))
                                    print(f"Debug: Letra '{self.letra_estavel}' acertada!")
                                else:
                                    self.erros += 1
                                    self.atualizar_imagem()
                                    print(f"Debug: Erro com '{self.letra_estavel}'. Erros: {self.erros}")

                                # Verifica vitória/derrota
                                if self.erros >= self.max_erros:
                                    self.label_palavra.setText(f"Você perdeu! A palavra era: {self.palavra.upper()}")
                                    self.timer_cronometro.stop()
                                    self.btn_reiniciar.show()
                                elif "".join(self.letras_acertadas) == self.palavra.upper():
                                    self.label_palavra.setText(f"Você venceu! Parabéns!")
                                    self.timer_cronometro.stop()
                                    self.btn_reiniciar.show()

                            self.letra_aceita_recentemente = True
                            self.ultimo_tempo = agora
                            self.letra = ""

            # --- desenha texto com PIL e atualiza QLabel (exato do palavras.py) ---
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_pil)

            try:
                font_status = ImageFont.truetype("seguiemj.ttf", 30)
                font_letra = ImageFont.truetype("seguiemj.ttf", 40)
            except:
                font_status = ImageFont.load_default()
                font_letra = ImageFont.load_default()

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
            print("Erro em ForcaWindow.process_frame:", e)
            traceback.print_exc()

    def open_firstPage(self):
        self.main_window.switch_to_page(0)
        self.cursor_label.hide()