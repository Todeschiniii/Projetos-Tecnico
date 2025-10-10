from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, QTimer


class AvisoPage(QWidget):
    def __init__(self, proxima_tela=None, caminho_imagem=None):
        super().__init__()
        
        self.proxima_tela = proxima_tela  # Armazena a tela que vai abrir depois do aviso
        self.setWindowTitle("Aviso")
        self.setStyleSheet("background-color: black;")  # Background preto
        
        # Layout vertical centralizado
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Label "ATENÇÃO"
        self.label_atencao = QLabel("ATENÇÃO")
        self.label_atencao.setAlignment(Qt.AlignCenter)
        self.label_atencao.setStyleSheet("color: red;")
        font_atencao = QFont("Arial", 60, QFont.Bold)
        self.label_atencao.setFont(font_atencao)
        
        # Label de instruções
        texto_instrucoes = (
            "Faça os movimentos de forma lenta e constante!\n"
            "Nosso programa ainda é um protótipo! Podem ocorrer Bugs!\n"
            "Tabela com as LIBRAS disponíveis no computador ao lado!\n"
            "Obrigado por testar nosso programa! ❤❤❤"
        )
        self.label_instrucoes = QLabel(texto_instrucoes)
        self.label_instrucoes.setAlignment(Qt.AlignCenter)
        self.label_instrucoes.setStyleSheet("color: white;")
        font_instrucao = QFont("Arial", 30, QFont.Bold)
        self.label_instrucoes.setFont(font_instrucao)
        
        # Label para imagem (se fornecida)
        self.label_imagem = QLabel()
        self.label_imagem.setAlignment(Qt.AlignCenter)
        if caminho_imagem:  # Só carrega se um caminho foi passado
            pixmap = QPixmap(caminho_imagem)
            if not pixmap.isNull():
                # Ajusta a imagem para caber no tamanho da janela mantendo proporção
                self.label_imagem.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Adiciona widgets ao layout
        layout.addWidget(self.label_atencao)
        layout.addSpacing(20)  # Espaço entre títulos e instruções
        layout.addWidget(self.label_instrucoes)
        layout.addSpacing(20)  # Espaço entre instruções e imagem
        layout.addWidget(self.label_imagem)
        
        self.setLayout(layout)
        self.resize(600, 500)  # Tamanho inicial da janela
        
        # Timer para fechar após 25 segundos
        QTimer.singleShot(25000, self.fechar_aviso)
    
    def fechar_aviso(self):
        self.close()
        if self.proxima_tela:
            self.proxima_tela.show()