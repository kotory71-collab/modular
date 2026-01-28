from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QCheckBox, QFormLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class DispositivoDialog(QDialog):
    def __init__(self, datos=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar / Editar dispositivo")
        self.setMinimumWidth(400)
        self.datos = datos or {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        form = QFormLayout()
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(10)

        # ID
        self.inp_id = QLineEdit(self.datos.get("id", ""))
        self.inp_id.setReadOnly(True)
        form.addRow("ID:", self.inp_id)

        # Nombre
        self.inp_name = QLineEdit(self.datos.get("name", ""))
        form.addRow("Nombre:", self.inp_name)

        # Conexiones
        self.inp_connections = QLineEdit(self.datos.get("connections", ""))
        form.addRow("Conexiones:", self.inp_connections)

        # Ubicación
        self.inp_location = QLineEdit(self.datos.get("location", ""))
        form.addRow("Ubicación:", self.inp_location)

        # Activo
        self.chk_active = QCheckBox()
        self.chk_active.setChecked(self.datos.get("active", True))
        form.addRow("Activo:", self.chk_active)

        layout.addLayout(form)

        # FOTO
        photo_box = QHBoxLayout()
        self.photo_path = self.datos.get("foto", "")
        self.lbl_photo = QLabel()
        self.lbl_photo.setFixedSize(150, 150)
        self._update_photo(self.photo_path)
        photo_box.addWidget(self.lbl_photo)

        btn_foto = QPushButton("Cargar foto")
        btn_foto.clicked.connect(self.cargar_foto)
        photo_box.addWidget(btn_foto)
        photo_box.addStretch()
        layout.addLayout(photo_box)

        # BOTONES
        buttons = QHBoxLayout()
        btn_save = QPushButton("Guardar")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)

    def cargar_foto(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.photo_path = path
            self._update_photo(path)

    def _update_photo(self, path):
        if path:
            pm = QPixmap(path).scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_photo.setPixmap(pm)
        else:
            self.lbl_photo.setText("Sin imagen")
            self.lbl_photo.setStyleSheet("""
                color: gray; 
                font-style: italic;
                border: 1px dashed #aaa;
                qproperty-alignment: AlignCenter;
            """)

    def get_datos(self):
        return {
            "id": self.inp_id.text(),
            "name": self.inp_name.text(),
            "connections": self.inp_connections.text(),
            "location": self.inp_location.text(),
            "active": self.chk_active.isChecked(),
            "battery": self.datos.get("battery", 100),
            "foto": self.photo_path,
            "temp_amb": self.datos.get("temp_amb"),
            "humedad": self.datos.get("humedad"),
            "golpe": self.datos.get("golpe"),
            "luz": self.datos.get("luz"),
            "temp_sonda": self.datos.get("temp_sonda"),
            "punto_condensacion": self.datos.get("punto_condensacion"),
        }
