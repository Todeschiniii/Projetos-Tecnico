from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import QRect, Qt

class LoadingButton(QPushButton):
    def __init__(self, text, parent = None):
        super().__init__(text, parent)
        self.progresso = 0.0 # 0.0 → vazio, 1.0 → chei
        self.texto = text # guarda o texto
        self.setFont(QFont("Arial", 40, QFont.Bold)) # fonte grande
        self.setMinimumHeight(100)

    def set_progress(self, valor):
        """Atualiza progresso de preenchimento azul"""
          # Garante que o progresso sempre fique dentro do intervalo [0.0, 1.0]
        self.progresso = max(0.0, min(1.0, valor))
        self.update() # Força repetir

    def paintEvent(self, event):
        # Desenha fundo preto
        # Cria um objeto QPainter que permite desenhar manualmente no botão
        painter = QPainter(self)
        # Ativa o modo "antialiasing", que suaviza bordas e cantos arredondados para não ficarem serrilhados
        painter.setRenderHint(QPainter.Antialiasing)
        # Define o pincel (brush) para preencher o fundo do botão de preto.
        painter.setBrush(QColor(0, 0, 0, 0)) # Fundo Transparente
        # Define a cor da "caneta" (pen), que desenha as bordas.
        painter.setPen(Qt.NoPen)  
        # Desenha um retângulo arredondado ocupando toda a área do botão,
        # usando o fundo preto e a borda branca definidos acima.
        painter.drawRoundedRect(self.rect(), 20, 20)
        
        if self.progresso > 0:
            # Calcula a altura proporcional ao progresso (0% → 0, 100% → altura total do botão).
            altura = int(self.height() * self.progresso)
             # Define um retângulo que começa de baixo pra cima, crescendo conforme o progresso.
            # - x=0 (lado esquerdo)
            # - y = parte de baixo do botão até o ponto proporcional ao progresso
            # - largura = largura total do botão
            # - altura = altura proporcional calculada acima
            rect = QRect(0, self.height() - altura, self.width(), altura)

            # Preenche esse retângulo com azul, simulando a "barra de carregamento".
            painter.setBrush(QColor(0, 0, 0)) # azul
            # Desenha com curvatura
            painter.drawRoundedRect(rect, 20, 20)

        # Texto sempre por cima
        painter.setPen(QColor(255, 255, 255)) # Branco
        painter.drawText(self.rect(), Qt.AlignCenter, self.texto)
