from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QLabel,
    QPushButton, QFileDialog, QGroupBox, QFrame, QDateEdit, QComboBox,
    QCheckBox, QTextEdit, QScrollArea, QWidget
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QDate
from typing import Optional
import os
import datetime


class InsumoDialog(QDialog):

    def __init__(self, data: Optional[dict] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar / Editar Insumo")
        self.setMinimumWidth(820)
        self.setMinimumHeight(650)
        self.data = data.copy() if data else {}
        self.data.setdefault("tipo", self.data.get("tipo", "Medicamento"))

        # area principal

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        scroll.setWidget(container)

        main = QVBoxLayout(container)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(12)

        # top

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["Medicamento", "Dispositivo Médico", "Biológico"])
        idx = self.cmb_tipo.findText(self.data.get("tipo", "Medicamento"))
        if idx >= 0:
            self.cmb_tipo.setCurrentIndex(idx)

        if self.data.get("id"):
            self.cmb_tipo.setDisabled(True)

        self.inp_id = QLineEdit(self.data.get("id", ""))
        self.inp_id.setReadOnly(True)

        top_row.addWidget(QLabel("Tipo:"))
        top_row.addWidget(self.cmb_tipo, 1)
        top_row.addWidget(QLabel("ID:"))
        top_row.addWidget(self.inp_id)

        main.addLayout(top_row)

        # tarjeta datos generales

        grp_general = QGroupBox("Datos generales")
        lay_general = QFormLayout()

        self.inp_nombre = QLineEdit(self.data.get("nombre", ""))
        self.inp_lote = QLineEdit(self.data.get("lote", ""))
        self.inp_registro = QLineEdit(self.data.get("registro_sanitario", ""))

        self.inp_fecha_cad = QDateEdit(calendarPopup=True)
        self.inp_fecha_fab = QDateEdit(calendarPopup=True)

        def parse_date(value):
            try:
                if isinstance(value, QDate):
                    return value
                if isinstance(value, datetime.date):
                    return QDate(value.year, value.month, value.day)
                y, m, d = (int(x) for x in str(value).split("-"))
                return QDate(y, m, d)
            except:
                return QDate.currentDate()

        self.inp_fecha_cad.setDate(parse_date(self.data.get("fecha_caducidad")))
        self.inp_fecha_fab.setDate(parse_date(self.data.get("fecha_fabricacion")))

        lay_general.addRow("Nombre:", self.inp_nombre)
        lay_general.addRow("Lote / Serie:", self.inp_lote)
        lay_general.addRow("Registro sanitario:", self.inp_registro)
        lay_general.addRow("Fecha caducidad:", self.inp_fecha_cad)
        lay_general.addRow("Fecha fabricación:", self.inp_fecha_fab)

        grp_general.setLayout(lay_general)
        main.addWidget(grp_general)

        # tarjeta datos específicos

        grp_specific = QGroupBox("Datos específicos")
        lay_spec = QVBoxLayout()

        # MEDICAMENTO
        box_med = self._build_med_section()

        # DISPOSITIVO MÉDICO
        box_dev = self._build_dev_section()

        # BIOLÓGICO
        box_bio = self._build_bio_section()

        lay_spec.addWidget(box_med)
        lay_spec.addWidget(box_dev)
        lay_spec.addWidget(box_bio)

        grp_specific.setLayout(lay_spec)
        main.addWidget(grp_specific)

        self._sections = {
            "Medicamento": box_med,
            "Dispositivo Médico": box_dev,
            "Biológico": box_bio
        }
        self.cmb_tipo.currentTextChanged.connect(self._on_tipo_changed)
        self._on_tipo_changed(self.cmb_tipo.currentText())

        # tarjeta imagen

        grp_image = QGroupBox("Imagen")
        lay_img = QHBoxLayout()

        self.lbl_image = QLabel()
        self.lbl_image.setFixedSize(300, 200)
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setStyleSheet("border: 1px dashed #ccc;")
        self._update_photo(self.data.get("foto"))

        btn_load = QPushButton("Cargar imagen")
        btn_load.clicked.connect(self._load_photo)

        btn_clear = QPushButton("Quitar imagen")
        btn_clear.clicked.connect(self._clear_photo)

        vimg = QVBoxLayout()
        vimg.addWidget(btn_load)
        vimg.addWidget(btn_clear)
        vimg.addStretch()

        lay_img.addWidget(self.lbl_image)
        lay_img.addLayout(vimg)

        grp_image.setLayout(lay_img)
        main.addWidget(grp_image)

        # botones

        actions = QHBoxLayout()
        actions.addStretch()

        btn_save = QPushButton("Guardar")
        btn_cancel = QPushButton("Cancelar")
        btn_save.clicked.connect(self._on_save)
        btn_cancel.clicked.connect(self.reject)

        actions.addWidget(btn_save)
        actions.addWidget(btn_cancel)

        main.addLayout(actions)

        # contenido
        wrapper = QVBoxLayout(self)
        wrapper.addWidget(scroll)

    # secciones

    def _build_med_section(self):
        frame = QFrame()
        lay = QFormLayout()

        self.inp_gen = QLineEdit(self.data.get("nombre_generico", ""))
        self.inp_com = QLineEdit(self.data.get("nombre_comercial", ""))
        self.inp_forma = QLineEdit(self.data.get("forma_farmaceutica", ""))
        self.inp_conc = QLineEdit(self.data.get("concentracion", ""))
        self.inp_cont = QLineEdit(self.data.get("contenido_neto", ""))
        self.inp_via = QLineEdit(self.data.get("via_administracion", ""))
        self.chk_receta = QCheckBox()
        self.chk_receta.setChecked(bool(self.data.get("requiere_receta")))

        lay.addRow("Nombre genérico:", self.inp_gen)
        lay.addRow("Nombre comercial:", self.inp_com)
        lay.addRow("Forma farmacéutica:", self.inp_forma)
        lay.addRow("Concentración:", self.inp_conc)
        lay.addRow("Contenido neto:", self.inp_cont)
        lay.addRow("Vía administración:", self.inp_via)
        lay.addRow("Requiere receta:", self.chk_receta)

        frame.setLayout(lay)
        return frame

    def _build_dev_section(self):
        frame = QFrame()
        lay = QFormLayout()

        self.inp_marca = QLineEdit(self.data.get("marca", ""))
        self.inp_model = QLineEdit(self.data.get("modelo", ""))
        self.inp_num = QLineEdit(self.data.get("numero_lote", ""))
        self.inp_cond = QLineEdit(self.data.get("condiciones_almacenamiento", ""))
        self.inp_adv = QTextEdit(self.data.get("advertencias", ""))
        self.inp_adv.setFixedHeight(70)

        lay.addRow("Marca:", self.inp_marca)
        lay.addRow("Modelo:", self.inp_model)
        lay.addRow("Número lote:", self.inp_num)
        lay.addRow("Condiciones almacenamiento:", self.inp_cond)
        lay.addRow("Advertencias:", self.inp_adv)

        frame.setLayout(lay)
        return frame

    def _build_bio_section(self):
        frame = QFrame()
        lay = QFormLayout()

        self.inp_fab = QLineEdit(self.data.get("fabricante", ""))
        self.inp_dosis = QLineEdit(self.data.get("dosis", ""))
        self.inp_ind = QTextEdit(self.data.get("indicaciones", ""))
        self.inp_ind.setFixedHeight(70)
        self.inp_cond_bio = QLineEdit(self.data.get("condiciones_conservacion", ""))

        self.inp_fecha_cad_bio = QDateEdit(calendarPopup=True)
        d = self.data.get("fecha_caducidad")
        self.inp_fecha_cad_bio.setDate(QDate.currentDate() if not d else QDate.fromString(d, "yyyy-MM-dd"))

        lay.addRow("Fabricante:", self.inp_fab)
        lay.addRow("Dosis:", self.inp_dosis)
        lay.addRow("Indicaciones:", self.inp_ind)
        lay.addRow("Condiciones conservación:", self.inp_cond_bio)
        lay.addRow("Fecha caducidad:", self.inp_fecha_cad_bio)

        frame.setLayout(lay)
        return frame

    
    # IMAGEN
    
    def _load_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.data["foto"] = path
            self._update_photo(path)

    def _clear_photo(self):
        self.data["foto"] = None
        self._update_photo(None)

    def _update_photo(self, path: Optional[str]):
        if path and os.path.exists(path):
            pm = QPixmap(path).scaled(
                self.lbl_image.width(), self.lbl_image.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_image.setPixmap(pm)
        else:
            self.lbl_image.setText("Sin imagen")
            self.lbl_image.setStyleSheet("color: gray; border: 1px dashed #ccc;")

    
    # MANEJO DE TIPOS
 
    def _on_tipo_changed(self, tipo: str):
        for name, box in self._sections.items():
            box.setVisible(tipo == name)

   
    # GUARDAR

    def _on_save(self):
        if not self.inp_nombre.text().strip():
            self.inp_nombre.setStyleSheet("border: 1px solid red;")
            return

        self.accept()

    def get_data(self):
        out = {
            "id": self.inp_id.text().strip() or None,
            "tipo": self.cmb_tipo.currentText(),
            "nombre": self.inp_nombre.text().strip(),
            "lote": self.inp_lote.text().strip(),
            "registro_sanitario": self.inp_registro.text().strip(),
            "foto": self.data.get("foto"),
        }

        if out["tipo"] == "Medicamento":
            out.update({
                "nombre_generico": self.inp_gen.text().strip(),
                "nombre_comercial": self.inp_com.text().strip(),
                "forma_farmaceutica": self.inp_forma.text().strip(),
                "concentracion": self.inp_conc.text().strip(),
                "contenido_neto": self.inp_cont.text().strip(),
                "via_administracion": self.inp_via.text().strip(),
                "requiere_receta": self.chk_receta.isChecked(),
                "fecha_caducidad": self.inp_fecha_cad.date().toString("yyyy-MM-dd"),
                "fecha_fabricacion": self.inp_fecha_fab.date().toString("yyyy-MM-dd"),
            })

        elif out["tipo"] == "Dispositivo Médico":
            out.update({
                "marca": self.inp_marca.text().strip(),
                "modelo": self.inp_model.text().strip(),
                "numero_lote": self.inp_num.text().strip(),
                "condiciones_almacenamiento": self.inp_cond.text().strip(),
                "advertencias": self.inp_adv.toPlainText().strip(),
                "fecha_caducidad": self.inp_fecha_cad.date().toString("yyyy-MM-dd"),
                "fecha_fabricacion": self.inp_fecha_fab.date().toString("yyyy-MM-dd"),
            })

        else:  # Biológico
            out.update({
                "fabricante": self.inp_fab.text().strip(),
                "dosis": self.inp_dosis.text().strip(),
                "indicaciones": self.inp_ind.toPlainText().strip(),
                "condiciones_conservacion": self.inp_cond_bio.text().strip(),
                "fecha_caducidad": self.inp_fecha_cad_bio.date().toString("yyyy-MM-dd"),
                "fecha_fabricacion": self.inp_fecha_fab.date().toString("yyyy-MM-dd"),
            })

        return out
