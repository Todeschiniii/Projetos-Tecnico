from aviso_page import AvisoPage
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer, QThread, Signal
import os
import time
from menu import MenuWindow
from teste import TesteWindow
from camera_manager import CameraManager
from palavras import PalavrasWindow
from jogo import ForcaWindow
from loading_page import LoadingPage

# Thread para iniciar a câmera
class CameraInitThread(QThread):
    finished = Signal()
    def __init__(self, camera_manager):
        super().__init__()
        self.camera_manager = camera_manager

    def run(self):
        self.camera_manager.open_camera()
        time.sleep(1.5)
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Caminho da pasta de imagens
        self.caminho_pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

        # Cursor
        self.cursor_label = QLabel(self)
        pixmap = QPixmap(os.path.join(self.caminho_pasta, "cursor.png")).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.cursor_label.setPixmap(pixmap)
        self.cursor_label.resize(pixmap.size())
        self.cursor_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.cursor_label.setStyleSheet("background: transparent;")
        self.cursor_label.hide()
        self.cursor_label.raise_()

        # Gerenciador de câmera
        self.camera_manager = CameraManager()

        # Cria páginas do stacked
        self.first_window = MenuWindow(self.stacked, cursor_label=self.cursor_label, main_window=self, caminho_pasta=self.caminho_pasta)
        self.teste_window = TesteWindow(self.stacked, cursor_label=self.cursor_label, main_window=self, caminho_pasta=self.caminho_pasta)
        self.forca_window = ForcaWindow(self.stacked, cursor_label=self.cursor_label, main_window=self, caminho_pasta=self.caminho_pasta, camera_manager=self.camera_manager)
        self.palavras_window = PalavrasWindow(self.stacked, cursor_label=self.cursor_label, main_window=self, caminho_pasta=self.caminho_pasta)
        self.loading_page = LoadingPage(caminho_pasta=self.caminho_pasta, parent=self)

        # Adiciona páginas ao stacked
        self.stacked.addWidget(self.first_window)  # índice 0
        self.stacked.addWidget(self.teste_window)  # índice 1
        self.stacked.addWidget(self.forca_window)  # índice 2
        self.stacked.addWidget(self.palavras_window)  # índice 3
        self.stacked.addWidget(self.loading_page)  # índice 4

        self.setStyleSheet("background-color: #5b6092")
        self.showFullScreen()

        # MOSTRA AVISO primeiro
        self.aviso_page = AvisoPage(proxima_tela=self.first_window)
        self.aviso_page.showFullScreen()

        # Quando o aviso fecha, o menu aparece automaticamente
        QTimer.singleShot(10000, self.aviso_page.fechar_aviso)

        # Conecta sinal para atualizar câmera ao trocar de página
        self.stacked.currentChanged.connect(self.on_page_changed)

        # Inicializa câmera na primeira página
        self.on_page_changed(0)
     # dentro de main_windows.py
    def mostrar_aviso(self):
        from aviso_page import AvisoPage  # import só quando realmente for usado
        self.aviso_page = AvisoPage(proxima_tela=self.first_window)
        self.aviso_page.showFullScreen()
    # Callback quando muda de página no stacked
    def on_page_changed(self, index):
        self.camera_manager.stop()
        if index == 0:
            self.camera_manager.set_callback(self.first_window.process_frame)
        elif index == 1:
            self.camera_manager.set_callback(self.teste_window.process_frame)
        elif index == 2:
            self.camera_manager.set_callback(self.forca_window.process_frame)
        elif index == 3:
            self.camera_manager.set_callback(self.palavras_window.process_frame)
        self.camera_manager.start()

    # Método opcional para mostrar o loading em qualquer página
    def switch_to_page(self, page_index):
        self.loading_page.show()
        self.loading_page.raise_()
        self.cursor_label.hide()

        self.thread = CameraInitThread(self.camera_manager)
        self.thread.finished.connect(lambda: (
            self.camera_manager.start(),
            self.stacked.setCurrentIndex(page_index),
            self.cursor_label.show(),
            self.loading_page.setVisible(False)
        ))
        self.thread.start()
