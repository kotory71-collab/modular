# ui/users/users_form.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton,
    QFileDialog, QHBoxLayout, QCheckBox, QDateEdit, QMessageBox, QComboBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QDate
import re
from typing import Optional
import os


class UserDialog(QDialog):

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar / Editar usuario")
        self.setMinimumWidth(520)
        self.data = data or {}

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Datos personales
        self.inp_nombre = QLineEdit(self.data.get("nombre", ""))
        self.inp_apellido = QLineEdit(self.data.get("apellido", ""))
        self.inp_usuario = QLineEdit(self.data.get("usuario", ""))
        self.inp_telefono = QLineEdit(self.data.get("telefono", ""))
        self.inp_email = QLineEdit(self.data.get("email", ""))

        # Rol con las 3 opciones
        self.inp_rol = QComboBox()
        self.inp_rol.addItems(["Administrador", "Supervisor", "Chofer"])
        # si viene rol, seleccionarla
        if "rol" in self.data and isinstance(self.data["rol"], str):
            idx = self.inp_rol.findText(self.data["rol"])
            if idx >= 0:
                self.inp_rol.setCurrentIndex(idx)

        self.inp_rfc = QLineEdit(self.data.get("rfc", ""))  # RFC

        form.addRow("Nombre:", self.inp_nombre)
        form.addRow("Apellido:", self.inp_apellido)
        form.addRow("Usuario:", self.inp_usuario)
        form.addRow("Teléfono:", self.inp_telefono)
        form.addRow("Email:", self.inp_email)
        form.addRow("Rol:", self.inp_rol)
        form.addRow("RFC:", self.inp_rfc)

        # Info médica / operativa
        self.inp_tipo_sangre = QLineEdit(self.data.get("tipo_sangre", ""))
        self.inp_alergias = QLineEdit(self.data.get("alergias", ""))
        self.inp_enfermedades = QLineEdit(self.data.get("enfermedades", ""))
        self.inp_notas = QLineEdit(self.data.get("notas_medicas", ""))
        self.chk_apto = QCheckBox()
        self.chk_apto.setChecked(bool(self.data.get("apto_operar", False)))

        form.addRow("Tipo de sangre:", self.inp_tipo_sangre)
        form.addRow("Alergias:", self.inp_alergias)
        form.addRow("Enfermedades:", self.inp_enfermedades)
        form.addRow("Notas médicas:", self.inp_notas)
        form.addRow("Apto para operar:", self.chk_apto)

        layout.addLayout(form)

        # Foto y documentos (INE / Licencia)
        docs_layout = QHBoxLayout()
        # foto
        vfoto = QVBoxLayout()
        self.lbl_photo = QLabel()
        self.lbl_photo.setFixedSize(120, 120)
        self._update_photo(self.data.get("foto"))
        btn_photo = QPushButton("Cargar foto")
        btn_photo.clicked.connect(self._load_photo)
        vfoto.addWidget(self.lbl_photo)
        vfoto.addWidget(btn_photo)
        docs_layout.addLayout(vfoto)

        # INE
        v1 = QVBoxLayout()
        self.lbl_ine = QLabel(self._short_name(self.data.get("ine")))
        btn_ine = QPushButton("Subir INE")
        btn_ine.clicked.connect(self._load_ine)
        v1.addWidget(self.lbl_ine)
        v1.addWidget(btn_ine)
        docs_layout.addLayout(v1)

        # Licencia
        v2 = QVBoxLayout()
        self.lbl_lic = QLabel(self._short_name(self.data.get("licencia")))
        btn_lic = QPushButton("Subir licencia")
        btn_lic.clicked.connect(self._load_lic)
        v2.addWidget(self.lbl_lic)
        v2.addWidget(btn_lic)

        # Número y expiración
        self.inp_lic_num = QLineEdit(self.data.get("licencia_num", ""))
        self.inp_lic_exp = QDateEdit()
        self.inp_lic_exp.setCalendarPopup(True)
        if self.data.get("licencia_exp"):
            try:
                y, m, d = (int(x) for x in str(self.data.get("licencia_exp")).split("-"))
                self.inp_lic_exp.setDate(QDate(y, m, d))
            except Exception:
                self.inp_lic_exp.setDate(QDate.currentDate())
        else:
            self.inp_lic_exp.setDate(QDate.currentDate())

        v2.addWidget(QLabel("Núm. licencia:"))
        v2.addWidget(self.inp_lic_num)
        v2.addWidget(QLabel("Vence:"))
        v2.addWidget(self.inp_lic_exp)
        docs_layout.addLayout(v2)

        layout.addLayout(docs_layout)

        # Botones
        btns = QHBoxLayout()
        self.btn_save = QPushButton("Guardar")
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        # Validaciones en tiempo real
        self.inp_email.textChanged.connect(self._validate_email)
        self.inp_telefono.textChanged.connect(self._validate_phone)
        self.inp_rfc.textChanged.connect(self._validate_rfc)

    # Utilidades de carga y visualización

    def _short_name(self, path: Optional[str]) -> str:
        if not path:
            return "No subido"
        return (path.split(os.path.sep)[-1])[:32]

    def _load_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar foto", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.data["foto"] = path
            self._update_photo(path)

    def _load_ine(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar INE", "", "PDF, imágenes (*.pdf *.png *.jpg *.jpeg)")
        if path:
            self.data["ine"] = path
            self.lbl_ine.setText(self._short_name(path))

    def _load_lic(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Licencia", "", "PDF, imágenes (*.pdf *.png *.jpg *.jpeg)")
        if path:
            self.data["licencia"] = path
            self.lbl_lic.setText(self._short_name(path))

    def _update_photo(self, path):
        if path:
            try:
                pm = QPixmap(path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.lbl_photo.setPixmap(pm)
            except Exception:
                self.lbl_photo.setText("No foto")
        else:
            self.lbl_photo.setText("Sin foto")

    # Validaciones

    def _validate_email(self):
        text = self.inp_email.text().strip()
        if not text:
            self.inp_email.setStyleSheet("")
            return
        ok = re.match(r"^[^@]+@[^@]+\.[^@]+$", text) is not None
        self.inp_email.setStyleSheet("" if ok else "border: 1px solid #d13438;")

    def _validate_phone(self):
        text = self.inp_telefono.text().strip()
        if not text:
            self.inp_telefono.setStyleSheet("")
            return
        ok = re.match(r"^[0-9\-\+\s]{7,20}$", text) is not None
        self.inp_telefono.setStyleSheet("" if ok else "border: 1px solid #d13438;")

    def _validate_rfc(self):
        text = self.inp_rfc.text().strip().upper()
        if not text:
            self.inp_rfc.setStyleSheet("")
            return
        # RFC 12 o 13 caracteres alfanuméricos
        ok = re.match(r"^[A-Z0-9]{12,13}$", text) is not None
        self.inp_rfc.setStyleSheet("" if ok else "border: 1px solid #d13438;")

    # guardar

    def _on_save(self):
        # validacion nombre
        if not self.inp_nombre.text().strip():
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            return
        # email
        if self.inp_email.text().strip() and not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.inp_email.text().strip()):
            QMessageBox.warning(self, "Validación", "Email inválido.")
            return

        self.accept()

    def get_data(self) -> dict:
        return {
            "id": self.data.get("id"),
            "nombre": self.inp_nombre.text().strip(),
            "apellido": self.inp_apellido.text().strip(),
            "usuario": self.inp_usuario.text().strip(),
            "telefono": self.inp_telefono.text().strip(),
            "email": self.inp_email.text().strip(),
            "rol": self.inp_rol.currentText(),
            "rfc": self.inp_rfc.text().strip().upper(),
            "tipo_sangre": self.inp_tipo_sangre.text().strip(),
            "alergias": self.inp_alergias.text().strip(),
            "enfermedades": self.inp_enfermedades.text().strip(),
            "notas_medicas": self.inp_notas.text().strip(),
            "apto_operar": self.chk_apto.isChecked(),
            "foto": self.data.get("foto"),
            "ine": self.data.get("ine"),
            "licencia": self.data.get("licencia"),
            "licencia_num": self.inp_lic_num.text().strip(),
            "licencia_exp": self.inp_lic_exp.date().toString("yyyy-MM-dd"),
            "estado_documentos": "Validado" if (self.data.get("ine") and self.data.get("licencia")) else "Pendiente",
            "history": self.data.get("history", [])
        }
