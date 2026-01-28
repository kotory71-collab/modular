from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton,
                             QMessageBox, QLabel, QFrame, QHBoxLayout, QSizePolicy)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from core.api_simulada import validate_user
import os

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión")
        self.on_login_success = on_login_success
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1e3c72, stop:1 #2a5298);
                color: #fff;
                font-family: Segoe UI, sans-serif;
            }
            QLabel#title {
                font-size: 26px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 20px;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border-radius: 6px;
                border: none;
                background-color: #ffffff;
                color: #000;
            }
            QPushButton {
                background-color: #00c853;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00b248;
            }
            QPushButton#exitButton {
                background-color: #c62828;
            }
            QPushButton#exitButton:hover {
                background-color: #b71c1c;
            }
        """)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.left_container = QWidget()
        self.right_container = QWidget()
        self.left_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.right_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.layout.addWidget(self.left_container)
        self.layout.addWidget(self.right_container)

        self.build_left()
        self.build_right()
        self.showFullScreen()

    def build_left(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), r'C:\Users\kurof\OneDrive\Desktop\prueba\ui\widgets\img/logo.png')
        if os.path.exists(logo_path):
            logo.setPixmap(QPixmap(logo_path).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo)

        title = QLabel("Sistema de Monitoreo Médico")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.left_container.setLayout(layout)

    def build_right(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_frame = QFrame()
        form_layout = QFormLayout()
        form_layout.setSpacing(20)

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.role = QComboBox()
        self.role.addItems(["Administrador", "Chofer", "Supervisor"])

        form_layout.addRow("Usuario:", self.username)
        form_layout.addRow("Contraseña:", self.password)
        form_layout.addRow("Rol:", self.role)

        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.login_btn = QPushButton("Iniciar Sesión")
        self.login_btn.clicked.connect(self.attempt_login)
        buttons_layout.addWidget(self.login_btn)

        self.exit_btn = QPushButton("Salir")
        self.exit_btn.setObjectName("exitButton")
        self.exit_btn.clicked.connect(self.confirm_exit)
        buttons_layout.addWidget(self.exit_btn)

        layout.addLayout(buttons_layout)

        self.right_container.setLayout(layout)

    def attempt_login(self):
        user = self.username.text()
        pwd = self.password.text()
        role = self.role.currentText()

        if validate_user(user, pwd, role):
            # LLAMAMOS AL ROUTER
            self.on_login_success(role)
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Credenciales incorrectas")

    def confirm_exit(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar salida")
        msg.setText("¿Estás seguro que deseas salir?")
        msg.setIcon(QMessageBox.Icon.Question)

        yes_btn = QPushButton("Sí")
        no_btn = QPushButton("No")

        msg.addButton(yes_btn, QMessageBox.ButtonRole.AcceptRole)
        msg.addButton(no_btn, QMessageBox.ButtonRole.RejectRole)

        msg.setDefaultButton(no_btn)

        ret = msg.exec()

        if msg.clickedButton() == yes_btn:
            self.close()