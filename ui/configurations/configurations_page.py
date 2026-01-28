import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QHBoxLayout, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt

try:
    from core.sensores.esp32_serial import ESP32Serial
except ImportError:
    ESP32Serial = None


CONFIG_FILE = "configurations.json"


class ConfigurationsPage(QWidget):
    def __init__(self, role="admin"):
        super().__init__()
        self.role = role
        self.setup_ui()
        self.load_config()
        self.apply_permissions()

    # configuración UI
    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        #seccion 1: preferencias generales
        self.general_frame = self._create_section("Preferencias generales")
        general_layout = QFormLayout(self.general_frame.inner_frame)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Claro", "Oscuro", "Automático"])

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Español", "Inglés"])

        general_layout.addRow("Tema:", self.theme_combo)
        general_layout.addRow("Idioma:", self.language_combo)

        scroll_layout.addWidget(self.general_frame)

        #seccion 2: conexión de dispositivos
        self.device_frame = self._create_section("Conexión de dispositivos (ESP32 / USB Serial)")
        device_layout = QFormLayout(self.device_frame.inner_frame)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Ej. COM3 o /dev/ttyUSB0")

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "115200", "230400"])

        self.test_button = QPushButton("Probar conexión")
        self.test_button.setStyleSheet("background-color: #2980b9; color: white; padding: 5px;")
        self.test_button.clicked.connect(self.test_connection)

        device_layout.addRow("Puerto Serial:", self.port_input)
        device_layout.addRow("Baudrate:", self.baudrate_combo)
        device_layout.addRow(self.test_button)

        scroll_layout.addWidget(self.device_frame)

        #seccion 3: notificaciones y alertas
        self.notif_frame = self._create_section("Notificaciones y alertas")
        notif_layout = QFormLayout(self.notif_frame.inner_frame)

        self.enable_alerts = QCheckBox("Activar predicciones de alertas")
        self.sound_alerts = QCheckBox("Alertas sonoras")
        self.email_alerts = QCheckBox("Enviar alertas al correo registrado")

        notif_layout.addRow(self.enable_alerts)
        notif_layout.addRow(self.sound_alerts)
        notif_layout.addRow(self.email_alerts)

        scroll_layout.addWidget(self.notif_frame)

        #seccion 4: ajustes de cuenta
        self.user_frame = self._create_section("Ajustes de cuenta")
        user_layout = QFormLayout(self.user_frame.inner_frame)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de usuario")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Teléfono")

        user_layout.addRow("Usuario:", self.username_input)
        user_layout.addRow("Teléfono:", self.phone_input)

        scroll_layout.addWidget(self.user_frame)

        #botones guardar/cancelar
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.save_btn = QPushButton("Guardar cambios")
        self.cancel_btn = QPushButton("Cancelar")

        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px;")
        self.cancel_btn.setStyleSheet("background-color: #c0392b; color: white; padding: 8px;")

        self.save_btn.clicked.connect(self.save_config)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)

        scroll_layout.addLayout(btn_layout)

    # permisos según rol
    def apply_permissions(self):
        """Oculta secciones según rol."""
        if self.role == "chofer":
            self.general_frame.hide()
            self.device_frame.hide()

        elif self.role == "supervisor":
            self.device_frame.hide()

        # Admin ve todo

    # guardar y cargar configuraciones
    def load_config(self):
        """Carga configuraciones desde JSON."""
        if not os.path.exists(CONFIG_FILE):
            return

        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)

            self.theme_combo.setCurrentText(cfg.get("tema", "Claro"))
            self.language_combo.setCurrentText(cfg.get("idioma", "Español"))
            self.port_input.setText(cfg.get("puerto", ""))
            self.baudrate_combo.setCurrentText(cfg.get("baudrate", "115200"))
            self.enable_alerts.setChecked(cfg.get("predicciones", False))
            self.sound_alerts.setChecked(cfg.get("alertas_sonoras", True))
            self.email_alerts.setChecked(cfg.get("alertas_email", False))
            self.username_input.setText(cfg.get("usuario", ""))
            self.phone_input.setText(cfg.get("telefono", ""))

        except Exception as e:
            print("[ERROR] No se pudo cargar configuraciones:", e)

    def save_config(self):
        """Guarda configuraciones en JSON."""
        cfg = {
            "tema": self.theme_combo.currentText(),
            "idioma": self.language_combo.currentText(),
            "puerto": self.port_input.text(),
            "baudrate": self.baudrate_combo.currentText(),
            "predicciones": self.enable_alerts.isChecked(),
            "alertas_sonoras": self.sound_alerts.isChecked(),
            "alertas_email": self.email_alerts.isChecked(),
            "usuario": self.username_input.text(),
            "telefono": self.phone_input.text(),
        }

        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(cfg, f, indent=4)

            QMessageBox.information(self, "Guardado", "Configuraciones guardadas correctamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{e}")


    # PROBAR CONEXIÓN ESP32
    def test_connection(self):
        if ESP32Serial is None:
            QMessageBox.warning(self, "Error", "Módulo ESP32Serial no encontrado.")
            return

        port = self.port_input.text().strip()

        if not port:
            QMessageBox.warning(self, "Error", "Debes colocar un puerto COM válido.")
            return

        try:
            esp = ESP32Serial(port)
            if esp.connected:
                QMessageBox.information(self, "Éxito", f"Conexión exitosa al dispositivo en {port}")
                esp.close()
            else:
                QMessageBox.critical(self, "Error", f"No se pudo conectar al puerto {port}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al conectar:\n{e}")

    # utilidades
    def _create_section(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #CCCCCC;
                border-radius: 10px;
                padding: 10px;
                margin-top: 10px;
            }
        """)

        layout = QVBoxLayout(frame)

        label = QLabel(title)
        label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(label)

        inner_frame = QFrame()
        inner_layout = QVBoxLayout(inner_frame)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(inner_frame)

        frame.inner_frame = inner_frame
        return frame
