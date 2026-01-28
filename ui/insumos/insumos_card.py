from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from typing import Optional


class InsumoCard(QFrame):

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setProperty("data", data)
        self._data = data

        self.setStyleSheet("""
            QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 8px; }
            QLabel { color: #222; }
            QPushButton { padding: 4px 8px; border-radius: 6px; }
        """)
        self.setFixedSize(220, 240)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Título
        self.lbl_title = QLabel(data.get("nombre", "Sin nombre"))
        self.lbl_title.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_title)

        # Foto / placeholder
        self.lbl_img = QLabel()
        self.lbl_img.setFixedSize(160, 100)
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_image(self._data.get("foto"))
        layout.addWidget(self.lbl_img, 0, Qt.AlignmentFlag.AlignHCenter)

        # Resumen 
        self.lbl_sub = QLabel(self._subtitle())
        layout.addWidget(self.lbl_sub)

        # detalles cortos
        self.lbl_row1 = QLabel(self._short_row1())
        self.lbl_row2 = QLabel(self._short_row2())
        layout.addWidget(self.lbl_row1)
        layout.addWidget(self.lbl_row2)

        layout.addStretch()

        # botones
        btns = QHBoxLayout()
        self.btn_edit = QPushButton("Editar")
        self.btn_del = QPushButton("Eliminar")
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_del)
        layout.addLayout(btns)

    def _subtitle(self) -> str:
        t = self._data.get("tipo", "")
        return t

    def _short_row1(self) -> str:
        # mostrar lote / modelo / fabricante según tipo
        t = self._data.get("tipo", "")
        if t == "Medicamento":
            return f"Lote: {self._data.get('lote','')}"
        if t == "Dispositivo Médico":
            return f"Marca/Modelo: {self._data.get('marca','')} {self._data.get('modelo','')}"
        return f"Fabricante: {self._data.get('fabricante','')}"

    def _short_row2(self) -> str:
        t = self._data.get("tipo", "")
        if t == "Medicamento":
            return f"Cad: {self._data.get('fecha_caducidad','')}"
        if t == "Dispositivo Médico":
            return f"Fabr: {self._data.get('fecha_fabricacion','')}"
        return f"Dosis: {self._data.get('dosis','')}"

    def _update_image(self, path: Optional[str]):
        if path:
            try:
                pm = QPixmap(path).scaled(160, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.lbl_img.setPixmap(pm)
            except Exception:
                self.lbl_img.setText("Sin imagen")
        else:
            self.lbl_img.setText("Sin imagen")
            self.lbl_img.setStyleSheet("color: #999; font-style: italic;")

    def update_visual(self, data: dict):
        self._data = data
        self.setProperty("data", data)
        self.lbl_title.setText(data.get("nombre", "Sin nombre"))
        self.lbl_sub.setText(self._subtitle())
        self.lbl_row1.setText(self._short_row1())
        self.lbl_row2.setText(self._short_row2())
        self._update_image(data.get("foto"))
