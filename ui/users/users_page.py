# ui/users/users_page.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt
from functools import partial
import csv
import os
from typing import Optional

from ui.users.users_card import UserCard
from ui.users.users_form import UserDialog


class UsersPage(QWidget):

    def __init__(self, current_role: str = "Administrador", parent=None):
        super().__init__(parent)
        self.current_role = current_role

        # datos de ejemplo
        self.users: list[dict] = []
        self.user_cards: dict[str, UserCard] = {}

        self.setStyleSheet("""
            QWidget { background: #ffffff; font-family: 'Segoe UI'; color: #222; }
            QLineEdit { border: 1px solid #d0d0d0; padding: 6px; border-radius: 6px; }
            QPushButton { background: #e6e6e6; border: 1px solid #ccc; padding: 6px 10px; border-radius: 6px; }
            QPushButton:hover { background:#dedede; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        #  mensaje de acceso denegado
        if self.current_role.lower() != "administrador":
            lbl = QLabel("Acceso denegado. Solo usuarios con rol 'Administrador' pueden ver este módulo.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addStretch()
            layout.addWidget(lbl)
            layout.addStretch()
            return

        # Top 
        top = QHBoxLayout()
        self.search_input = QLineEdit(placeholderText="Buscar usuario por nombre, usuario, RFC o teléfono…")
        self.search_input.textChanged.connect(self.filter_users)
        top.addWidget(self.search_input)

        self.btn_toggle_view = QPushButton("Cambiar a Tabla")
        self.btn_toggle_view.clicked.connect(self.toggle_view)
        top.addWidget(self.btn_toggle_view)

        self.btn_add = QPushButton("Agregar usuario")
        self.btn_add.clicked.connect(self.add_user_inline)
        top.addWidget(self.btn_add)

        self.btn_export = QPushButton("Exportar CSV")
        self.btn_export.clicked.connect(self.export_csv)
        top.addWidget(self.btn_export)

        #  descargar fotos
        self.btn_download_photos = QPushButton("Descargar fotos")
        self.btn_download_photos.clicked.connect(self.descargar_fotos)
        top.addWidget(self.btn_download_photos)

        top.addStretch()
        layout.addLayout(top)

        # Main cartas y tablas
        self.main_container = QWidget()
        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # tarjetas area
        self.scroll = QScrollArea(widgetResizable=True)
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setContentsMargins(8, 8, 8, 8)
        self.cards_layout.setSpacing(12)
        self.scroll.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll)

        # Tabla
        self.table = QTableWidget()
        headers = [
            "ID", "Nombre", "Usuario", "Teléfono", "Correo", "Rol", "RFC",
            "INE", "Licencia", "Estado documentos", "Acción", "Eliminar"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        self.table.hide()
        main_layout.addWidget(self.table)

        layout.addWidget(self.main_container)

        # incializar vacio
        self._next_id = 1

    # CRUD
    def add_user_inline(self):
        # ficha basica
        uid = f"USR-{self._next_id:03d}"
        self._next_id += 1
        user = {
            "id": uid,
            "nombre": f"Usuario {uid}",
            "apellido": "",
            "usuario": f"usuario{self._next_id}",
            "telefono": "",
            "email": "",
            "rol": "Chofer",
            "rfc": "",
            "tipo_sangre": "",
            "alergias": "",
            "enfermedades": "",
            "notas_medicas": "",
            "apto_operar": False,
            "foto": None,
            "ine": None,
            "licencia": None,
            "licencia_num": None,
            "licencia_exp": None,
            "estado_documentos": "Pendiente",
            "history": []
        }
        self.users.append(user)
        self.actualizar_vistas()

    def edit_user_by_id(self, user_id: str):
        idx = self._find_idx(user_id)
        if idx == -1:
            return
        current = self.users[idx]
        dlg = UserDialog(current, parent=self)
        if dlg.exec():
            new = dlg.get_data()
            # guardar en historial
            current.setdefault("history", []).append({
                "when": __import__("datetime").datetime.now().isoformat(),
                "prev": {k: current.get(k) for k in ("nombre", "apellido", "usuario", "telefono", "email", "rol", "rfc")}
            })
            # actualizar datos
            self.users[idx].update(new)
            # actualizar estado documentos
            self.users[idx]["estado_documentos"] = self._compute_doc_status(self.users[idx])
            # actualizar tarjeta si existe
            uid = self.users[idx]["id"]
            if uid in self.user_cards:
                self.user_cards[uid].update_visual(self.users[idx])
            self.actualizar_vistas()

    def delete_user_by_id(self, user_id: str):
        idx = self._find_idx(user_id)
        if idx == -1:
            return
        if QMessageBox.question(self, "Eliminar usuario", f"¿Eliminar {self.users[idx]['nombre']}?") != QMessageBox.StandardButton.Yes:
            return
        
        self.users.pop(idx)
        self.actualizar_vistas()

    # Actualizar vistas
    def _actualizar_tarjetas(self):
        ids = {u["id"] for u in self.users}
        # eliminar tarjetas obsoletas
        for uid in list(self.user_cards.keys()):
            if uid not in ids:
                card = self.user_cards.pop(uid)
                self.cards_layout.removeWidget(card)
                card.deleteLater()

        for i, u in enumerate(self.users):
            uid = u["id"]
            if uid not in self.user_cards:
                card = UserCard(u, parent=self)
                self.user_cards[uid] = card
                card.btn_edit.clicked.connect(partial(self.edit_user_by_id, uid))
                card.btn_del.clicked.connect(partial(self.delete_user_by_id, uid))
                card.btn_preview_history.clicked.connect(partial(self._show_history, uid))
            else:
                card = self.user_cards[uid]

            card.update_visual(u)

            row, col = divmod(i, 3)
            self.cards_layout.addWidget(card, row, col)

    def _actualizar_tabla(self):
        self.table.setRowCount(len(self.users))
        for row, u in enumerate(self.users):
            self.table.setItem(row, 0, QTableWidgetItem(u.get("id", "")))
            nombre = f"{u.get('nombre','')} {u.get('apellido','')}".strip()
            self.table.setItem(row, 1, QTableWidgetItem(nombre))
            self.table.setItem(row, 2, QTableWidgetItem(u.get("usuario", "")))
            self.table.setItem(row, 3, QTableWidgetItem(u.get("telefono", "")))
            self.table.setItem(row, 4, QTableWidgetItem(u.get("email", "")))
            self.table.setItem(row, 5, QTableWidgetItem(u.get("rol", "")))
            self.table.setItem(row, 6, QTableWidgetItem(u.get("rfc", "")))
            self.table.setItem(row, 7, QTableWidgetItem("Sí" if u.get("ine") else "No"))
            self.table.setItem(row, 8, QTableWidgetItem("Sí" if u.get("licencia") else "No"))
            self.table.setItem(row, 9, QTableWidgetItem(u.get("estado_documentos", "Pendiente")))

            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(partial(self.edit_user_by_id, u["id"]))
            self.table.setCellWidget(row, 10, btn_edit)

            btn_del = QPushButton("Eliminar")
            btn_del.clicked.connect(partial(self.delete_user_by_id, u["id"]))
            self.table.setCellWidget(row, 11, btn_del)

    def actualizar_vistas(self):
        self._actualizar_tarjetas()
        self._actualizar_tabla()

    # Herramientas y utilidades

    def _find_idx(self, user_id: str) -> int:
        for i, u in enumerate(self.users):
            if u.get("id") == user_id:
                return i
        return -1

    def _compute_doc_status(self, user: dict) -> str:
        # validar estado documentos
        if user.get("ine") and user.get("licencia"):
            return "Validado"
        return "Pendiente"

    def filter_users(self, text: str):
        text = text.lower()
        for card in self.user_cards.values():
            datos = card.property("data") or {}
            full = " ".join([
                datos.get("nombre",""), datos.get("apellido",""),
                datos.get("usuario",""), datos.get("rfc",""),
                datos.get("telefono","")
            ]).lower()
            card.setVisible(text in full)
        # tabla
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)

    def toggle_view(self):
        cards_visible = self.scroll.isVisible()
        self.scroll.setVisible(not cards_visible)
        self.table.setVisible(cards_visible)
        self.btn_toggle_view.setText("Cambiar a Tarjetas" if cards_visible else "Cambiar a Tabla")

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar CSV", "", "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Nombre","Usuario","Tel","Email","Rol","RFC","EstadoDocs"])
            for u in self.users:
                nombre = f"{u.get('nombre','')} {u.get('apellido','')}".strip()
                writer.writerow([u.get("id"), nombre, u.get("usuario"), u.get("telefono"), u.get("email"), u.get("rol"), u.get("rfc"), u.get("estado_documentos")])
        QMessageBox.information(self, "Exportar CSV", "Archivo CSV guardado correctamente.")

    def descargar_fotos(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino")
        if not carpeta:
            return

        fotos_copiadas = 0
        for u in self.users:
            foto = u.get("foto")
            if foto and os.path.exists(foto):
                # nombre destino
                ext = os.path.splitext(foto)[1] or ".jpg"
                nombre_archivo = f"{u.get('usuario','usuario')}_{u.get('id')}{ext}"
                destino = os.path.join(carpeta, nombre_archivo)
                try:
                    with open(foto, "rb") as fsrc, open(destino, "wb") as fdst:
                        fdst.write(fsrc.read())
                    fotos_copiadas += 1
                except Exception:
                    pass

        if fotos_copiadas == 0:
            QMessageBox.information(self, "Descargar fotos", "No hay fotos para descargar.")
        else:
            QMessageBox.information(self, "Descargar fotos", f"Se descargaron {fotos_copiadas} fotos correctamente.")

    def _show_history(self, uid: str):
        idx = self._find_idx(uid)
        if idx == -1:
            return
        history = self.users[idx].get("history", [])
        if not history:
            QMessageBox.information(self, "Historial", "No hay historial para este usuario.")
            return
        text = "\n\n".join([f"{h['when']}\n{h['prev']}" for h in history])
        QMessageBox.information(self, "Historial", text)
