from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QPushButton
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class UserViewDialog(QDialog):


    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalles del Usuario")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)

        # Nombre completo
        lbl_name = QLabel(f"<b>{data.get('nombre','')} {data.get('apellido','')}</b>")
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_name)

        # Foto
        photo = QLabel()
        photo.setFixedSize(150, 150)
        if data.get("foto"):
            try:
                pm = QPixmap(data["foto"]).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation)
                photo.setPixmap(pm)
            except:
                photo.setText("Sin foto")
        else:
            photo.setText("Sin foto")

        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(photo)
        h.addStretch()
        layout.addLayout(h)

        # Datos
        def add_label(titulo, valor):
            lbl = QLabel(f"<b>{titulo}:</b> {valor}")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(lbl)

        add_label("Usuario", data.get("usuario", ""))
        add_label("Rol", data.get("rol", ""))
        add_label("RFC", data.get("rfc", ""))
        add_label("Teléfono", data.get("telefono", ""))
        add_label("Email", data.get("email", ""))
        add_label("Tipo de sangre", data.get("tipo_sangre", ""))
        add_label("Alergias", data.get("alergias", ""))
        add_label("Enfermedades", data.get("enfermedades", ""))
        add_label("Notas médicas", data.get("notas_medicas", ""))
        add_label("Apto para operar", "Sí" if data.get("apto_operar") else "No")
        add_label("Estado documentos", data.get("estado_documentos", "Pendiente"))
        add_label("INE", "Subido" if data.get("ine") else "No")
        add_label("Licencia", "Subida" if data.get("licencia") else "No")

        # Botón cerrar
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
