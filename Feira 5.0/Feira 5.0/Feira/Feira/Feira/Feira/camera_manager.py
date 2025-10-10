from PySide6.QtCore import QTimer
import cv2
import mediapipe as mp
import numpy as np

class CameraManager:
    def __init__(self):
        # Inicializa a Câmera
        self.cap = None

        # Inicialização do MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.mp_draw = mp.solutions.drawing_utils

        # função que será chamada por cada página
        self.callback = None

        # Timer para processar frames periodicamente
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.show_rectangle = True

    def set_callback(self, func):
        """Define a função que vai receber os frames"""
        self.callback = func

    def open_camera(self):
        """Abre apenas o dispositivo da câmera, sem iniciar QTimer"""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)

    def start(self):
        """Inicia o loop de frames"""
        self.open_camera()
        self.timer.start(30)  # 30ms

    def stop(self):
        self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def process_frame(self):
        """Processa cada frame da câmera"""
        if not self.cap.isOpened() or self.callback is None:
            return  # Evita erros de frame vazio ou callback None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        h, w, _ = frame.shape
        
        # 🔥 entrega os dados para a página ativa
        self.callback(ret, frame, results, self.mp_hands, self.mp_draw)
