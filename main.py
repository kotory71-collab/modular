from PyQt6.QtWidgets import QApplication
from core.router import Router
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)

    router = Router(app)
    router.mostrar_login()

    sys.exit(app.exec())
