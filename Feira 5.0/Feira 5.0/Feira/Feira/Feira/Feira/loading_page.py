from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt
import os

class LoadingPage(QWidget):
    def __init__(self, caminho_pasta, parent=None):
        super().__init__(parent)

        # Centraliza e ocupa a tela toda
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)  # faz o GIF preencher o espaço
        layout.addWidget(self.label)

        # Carrega a animação (GIF)
        gif_path = os.path.join(caminho_pasta, "loading.gif")
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.label.setMovie(self.movie)
            self.movie.start()
        else:
            print(f"Arquivo não encontrado: {gif_path}")

        # Começa escondido, mas preparado para tela cheia
        self.hide()
