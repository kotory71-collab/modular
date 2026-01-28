# ui/users/users_card.py
from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from ui.users.users_view import UserViewDialog


class UserCard(QFrame):

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setProperty("data", data)
        self.data = data
        self.setStyleSheet("""
            QFrame { background: white; border: 1px solid #e0e0e0; border-radius: 8px; }
            QLabel { color: #222; }
            QPushButton { padding: 4px 8px; border-radius: 6px; }
        """)
        self.setFixedSize(260, 180)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # nombre y rol
        self.lbl_name = QLabel(self._full_name(data))
        self.lbl_name.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_name)

        # foto y datos
        inner = QHBoxLayout()
        self.lbl_photo = QLabel()
        self.lbl_photo.setFixedSize(64, 64)
        self._update_photo(data.get("foto"))
        inner.addWidget(self.lbl_photo)

        info = QVBoxLayout()
        self.lbl_user = QLabel(f"Usuario: {data.get('usuario','')}")
        self.lbl_phone = QLabel(f"Tel: {data.get('telefono','')}")
        self.lbl_email = QLabel(f"Email: {data.get('email','')}")
        info.addWidget(self.lbl_user)
        info.addWidget(self.lbl_phone)
        info.addWidget(self.lbl_email)
        inner.addLayout(info)

        layout.addLayout(inner)

        # RFC y estado documentos
        self.lbl_rfc = QLabel(f"RFC: {data.get('rfc','')}")
        self.lbl_docs = QLabel(f"Docs: {data.get('estado_documentos','Pendiente')}")
        layout.addWidget(self.lbl_rfc)
        layout.addWidget(self.lbl_docs)

        layout.addStretch()

        # botones
        btns = QHBoxLayout()
        self.btn_edit = QPushButton("Editar")
        self.btn_edit.setStyleSheet("background: #0078d4; color: white;")
        self.btn_del = QPushButton("Eliminar")
        self.btn_del.setStyleSheet("background: #d13438; color: white;")
        self.btn_preview_history = QPushButton("Historial")
        self.btn_preview_history.setStyleSheet("background: #666; color: white;")

        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_preview_history)
        btns.addWidget(self.btn_del)
        layout.addLayout(btns)

    # Vista detallada al hacer clic
    def mousePressEvent(self, event):
        dlg = UserViewDialog(self.data, self)
        dlg.exec()

    def _full_name(self, d):
        return f"{d.get('nombre','')} {d.get('apellido','')}".strip()

    def _update_photo(self, path):
        if path:
            try:
                pm = QPixmap(path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.lbl_photo.setPixmap(pm)
            except Exception:
                self.lbl_photo.setText("No foto")
        else:
            self.lbl_photo.setText("Sin foto")
            self.lbl_photo.setStyleSheet("color: #999; font-style: italic;")

    def update_visual(self, data: dict):
        self.data = data
        self.setProperty("data", data)
        self.lbl_name.setText(self._full_name(data))
        self.lbl_user.setText(f"Usuario: {data.get('usuario','')}")
        self.lbl_phone.setText(f"Tel: {data.get('telefono','')}")
        self.lbl_email.setText(f"Email: {data.get('email','')}")
        self.lbl_rfc.setText(f"RFC: {data.get('rfc','')}")
        self.lbl_docs.setText(f"Docs: {data.get('estado_documentos','Pendiente')}")
        self._update_photo(data.get("foto"))
