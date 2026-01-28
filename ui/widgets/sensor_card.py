from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class SensorCard(QWidget):
    def __init__(self, titulo: str, unidad: str = ""):
        super().__init__()
        self.titulo = titulo
        self.unidad = unidad

        self.setMinimumHeight(140)
        self.setMaximumHeight(160)

        # --- Estilo para modo CLARO ---
        self.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border-radius: 14px;
                border: 1px solid #dddddd;
            }
            QLabel.titulo {
                color: #333;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel.valor {
                color: #000;
                font-size: 30px;
                font-weight: 700;
            }
            QLabel.unidad {
                color: #555;
                font-size: 12px;
            }
        """)

        # Layout principal
        main = QVBoxLayout()
        main.setContentsMargins(16, 12, 16, 12)
        main.setSpacing(6)

        # Título
        self.lbl_titulo = QLabel(self.titulo)
        self.lbl_titulo.setObjectName("titulo")
        self.lbl_titulo.setProperty("class", "titulo")
        self.lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Valor + unidad
        val_layout = QHBoxLayout()
        self.lbl_valor = QLabel("--")
        self.lbl_valor.setObjectName("valor")
        self.lbl_valor.setProperty("class", "valor")

        self.lbl_unidad = QLabel(self.unidad)
        self.lbl_unidad.setObjectName("unidad")
        self.lbl_unidad.setProperty("class", "unidad")
        self.lbl_unidad.setAlignment(Qt.AlignmentFlag.AlignBottom)

        val_layout.addWidget(self.lbl_valor)
        val_layout.addWidget(self.lbl_unidad)
        val_layout.addStretch()

        main.addWidget(self.lbl_titulo)
        main.addLayout(val_layout)

        self.setLayout(main)

    def update_value(self, value):
        """Actualiza el valor mostrado en la tarjeta."""
        try:
            if isinstance(value, float):
                texto = f"{value:.2f}"
            else:
                texto = str(value)
        except Exception:
            texto = str(value)

        self.lbl_valor.setText(texto)
