from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap


class TarjetaDispositivo(QFrame):

    clicked = pyqtSignal(dict)

    def __init__(self, datos: dict, parent=None):
        super().__init__(parent)

        self.setProperty("datos", datos)

        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #0078d4;
            }
            QLabel {
                color: #333333;
            }
        """)

        self.setFixedSize(180, 260)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # nombre
        self.lbl_nombre = QLabel(datos.get("name", "Sin nombre"))
        self.lbl_nombre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nombre.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(self.lbl_nombre)

        # imagen
        self.lbl_foto = QLabel()
        self.lbl_foto.setFixedSize(120, 120)
        self.lbl_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_foto)

        # batería
        self.lbl_bateria = QLabel()
        self.lbl_bateria.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_bateria)

        layout.addStretch(1)

        # botones
        btns = QHBoxLayout()
        btns.setSpacing(5)

        self.btn_toggle = QPushButton()
        self.btn_toggle.setFixedSize(70, 30)

        self.btn_edit = QPushButton("✎")
        self.btn_edit.setFixedSize(40, 30)

        self.btn_del = QPushButton("🗑")
        self.btn_del.setFixedSize(40, 30)

        btns.addWidget(self.btn_toggle)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_del)
        layout.addLayout(btns)

        base_button_style = """
            QPushButton {
                border: none;
                border-radius: 4px;
                font-size: 10pt;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { opacity: 0.9; }
        """

        self.btn_edit.setStyleSheet(base_button_style + "background: #0078d4;")
        self.btn_del.setStyleSheet(base_button_style + "background: #d13438;")

        self.actualizar_visual(datos)

    # actualizar toda la tarjeta
    
    def actualizar_visual(self, datos):
        self.setProperty("datos", datos)

        # nombre
        self.lbl_nombre.setText(datos.get("name", "Sin nombre"))

        # imagen
        foto = datos.get("foto")
        if foto:
            pm = QPixmap(foto).scaled(120, 120,
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
            self.lbl_foto.setPixmap(pm)
            self.lbl_foto.setStyleSheet("")
        else:
            self.lbl_foto.setPixmap(QPixmap())
            self.lbl_foto.setText("Sin imagen")
            self.lbl_foto.setStyleSheet("""
                color: #999999;
                font-style: italic;
                background-color: #f5f5f5;
                border: 1px dashed #e0e0e0;
            """)

        # batería
        self.actualizar_bateria(datos.get("battery", 100))

        # estado
        self.actualizar_estado(datos.get("active", True))

    # actualizar estado individual

    def actualizar_estado(self, active: bool):
        css = """
            QPushButton {{ background: {bg}; }}
            QPushButton:hover {{ background: {hover}; }}
        """
        if active:
            self.btn_toggle.setText("Activo")
            self.btn_toggle.setStyleSheet(css.format(bg="#107c10", hover="#0f6f0e"))
        else:
            self.btn_toggle.setText("Inactivo")
            self.btn_toggle.setStyleSheet(css.format(bg="#d13438", hover="#b12d31"))

    def actualizar_bateria(self, battery_val: int):
        color = "#d13438" if battery_val < 20 else "#107c10"
        self.lbl_bateria.setText(f"Batería: {battery_val}%")
        self.lbl_bateria.setStyleSheet(f"color: {color}; font-weight: bold;")

    # click
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not any(btn.underMouse() for btn in (self.btn_toggle, self.btn_edit, self.btn_del)):
                self.clicked.emit(self.property("datos"))
        super().mousePressEvent(event)
