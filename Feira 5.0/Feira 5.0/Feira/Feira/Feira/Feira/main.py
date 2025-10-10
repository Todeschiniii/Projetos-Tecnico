import sys
from PySide6.QtWidgets import QApplication
from main_windows import MainWindow

# Esse bloco garante que o código só será executado
# quando rodar esse arquivo diretamente (python main.py)
# e não quando ele for importado por outro módulo.
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # sys.argv permite passar argumentos pelo terminal (ex: modo debug).
    # Mesmo que você não passe nada, o padrão é sys.argv.

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
    # Inicia o loop de eventos da aplicação (fica rodando até fechar a janela).
    # sys.exit garante que quando a janela for fechada, o programa termina 100%,
    # sem ficar nenhum processo fantasma aberto.
