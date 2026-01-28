from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from functools import partial
import csv

from ui.devices.devices_card import TarjetaDispositivo
from ui.devices.devices_form import DispositivoDialog
from core.sensores.esp32_worker import ESP32Worker


class DevicesPage(QWidget):
    def __init__(self, esp32_worker=None, esp32_puerto=-1, esp32_baudios=-1, parent=None):
        super().__init__(parent)

        self.devices: list[dict] = []
        self.device_cards: dict[str, TarjetaDispositivo] = {}

        self.external_worker = esp32_worker is not None
        self.worker = esp32_worker

        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 11pt;
                color: #222;
            }
            QLineEdit, QTableWidget {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(12)

        # top

        barra = QHBoxLayout(spacing=8)
        self.search_input = QLineEdit(placeholderText="Buscar dispositivo…")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_devices)
        barra.addWidget(self.search_input)

        self.btn_toggle_view = QPushButton("Cambiar a Tabla", clicked=self.toggle_view)
        barra.addWidget(self.btn_toggle_view)

        self.btn_add = QPushButton("Agregar dispositivo", clicked=self.agregar_dispositivo_en_linea)
        barra.addWidget(self.btn_add)

        self.btn_export = QPushButton("Exportar a CSV", clicked=self.exportar_csv)
        barra.addWidget(self.btn_export)

        barra.addStretch()
        root.addLayout(barra)

        # tarjetas y tabla

        self.main_container = QWidget()
        main_layout = QVBoxLayout(self.main_container)

        self.scroll = QScrollArea(widgetResizable=True)
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.scroll.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll)

        self.table = QTableWidget()
        self.table.setColumnCount(14)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Conexiones", "Ubicación", "Batería (%)", "Estado",
            "Temp Amb", "Humedad", "Golpe", "Luz", "Temp Sonda", "Punto Cond.",
            "Acción", "Eliminar"
        ])
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        self.table.hide()
        main_layout.addWidget(self.table)

        root.addWidget(self.main_container)

        # tiempo

        self.timer = QTimer(self, timeout=self.alertas)
        self.timer.start(5000)

        self.battery_timer = QTimer(self)
        self.battery_timer.timeout.connect(self._auto_reduce_battery)
        self.battery_timer.start(30000)  # 30 segundo

        # worker ESP32

        if not self.external_worker:
            self.worker = ESP32Worker(esp32_puerto, esp32_baudios, parent=self)
            self.worker.error.connect(self._on_worker_error)
            self.worker.data_received.connect(self._handle_esp32_data)
            self.worker.configurar()
            self.worker.start()
        else:
            self.worker.data_received.connect(self._handle_esp32_data)
            self.worker.error.connect(self._on_worker_error)

    # funciones del worker

    def _on_worker_error(self, msg: str):
        print("[ESP32 Worker]:", msg)

    def _handle_esp32_data(self, data: dict):
        if "ID" not in data:
            return

        dev_id = str(data["ID"])
        idx = self._idx(dev_id)

        if idx != -1 and not self.devices[idx].get("active", True):
            return

        if idx == -1:
            nuevo = dict(
                id=dev_id,
                name=f"Dispositivo {dev_id}",
                connections=data.get("connections", ""),
                location=data.get("location", ""),
                battery=int(data.get("battery", 100)),
                active=True,
                foto=None,
                temp_amb=data.get("T_Amb"),
                humedad=data.get("Hum"),
                golpe=data.get("golpe"),
                luz=data.get("Luz"),
                temp_sonda=data.get("T_Sonda"),
                punto_condensacion=data.get("Rocío")
            )
            self.devices.append(nuevo)
            self.actualizar_vistas()
            return

        d = self.devices[idx]

        # actualizar campos
        campos = {
            "name": "name",
            "connections": "connections",
            "location": "location",
            "battery": "battery",
            "T_Amb": "temp_amb",
            "Hum": "humedad",
            "golpe": "golpe",
            "Luz": "luz",
            "T_Sonda": "temp_sonda",
            "Rocío": "punto_condensacion",
        }

        for key_in, key_out in campos.items():
            if key_in in data:
                d[key_out] = data[key_in]

        self.actualizar_vistas()

    # crud de dispositivos

    def agregar_dispositivo_en_linea(self):
        new_id = f"DVC-{len(self.devices)+1}"
        self.devices.append({
            "id": new_id,
            "name": f"Dispositivo {len(self.devices)+1}",
            "connections": "",
            "location": "",
            "battery": 100,
            "active": True,
            "foto": None,
            "temp_amb": None,
            "humedad": None,
            "golpe": None,
            "luz": None,
            "temp_sonda": None,
            "punto_condensacion": None
        })
        self.actualizar_vistas()

    def editar_dispositivo_por_id(self, dev_id: str):
        idx = self._idx(dev_id)
        if idx == -1:
            return

        dlg = DispositivoDialog(self.devices[idx], parent=self)
        if dlg.exec():
            self.devices[idx] = dlg.get_datos()
            self.actualizar_vistas()

    def eliminar_dispositivo_por_id(self, dev_id: str):
        idx = self._idx(dev_id)
        if idx == -1:
            return

        if QMessageBox.question(
            self, "Eliminar dispositivo",
            f"¿Seguro que deseas eliminar '{self.devices[idx]['name']}'?"
        ) != QMessageBox.StandardButton.Yes:
            return

        self.devices.pop(idx)
        self.actualizar_vistas()

    def toggle_device_status_por_id(self, dev_id: str):
        idx = self._idx(dev_id)
        if idx == -1:
            return
        d = self.devices[idx]
        d["active"] = not d["active"]
        self.actualizar_vistas()

    # tarjetas y tablas
    def _actualizar_tarjetas(self):
        ids_existentes = {d["id"] for d in self.devices}

        # eliminar tarjetas viejas
        for dev_id in list(self.device_cards.keys()):
            if dev_id not in ids_existentes:
                card = self.device_cards.pop(dev_id)
                self.cards_layout.removeWidget(card)
                card.deleteLater()

        # refrescar o crear tarjetas
        for i, d in enumerate(self.devices):
            dev_id = d["id"]

            if dev_id not in self.device_cards:
                card = TarjetaDispositivo(d, parent=self.cards_container)
                self.device_cards[dev_id] = card

                card.btn_edit.clicked.connect(partial(self.editar_dispositivo_por_id, dev_id))
                card.btn_del.clicked.connect(partial(self.eliminar_dispositivo_por_id, dev_id))
                card.btn_toggle.clicked.connect(partial(self.toggle_device_status_por_id, dev_id))
            else:
                card = self.device_cards[dev_id]

            card.actualizar_visual(d)

            row, col = divmod(i, 3)
            self.cards_layout.addWidget(card, row, col)

    def _actualizar_tabla(self):
        self.table.setRowCount(len(self.devices))

        for row, d in enumerate(self.devices):
            self.table.setItem(row, 0, QTableWidgetItem(d["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(d["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(d["connections"]))
            self.table.setItem(row, 3, QTableWidgetItem(d["location"]))
            self.table.setItem(row, 4, QTableWidgetItem(f"{d['battery']}%"))

            estado = QTableWidgetItem("Activo" if d["active"] else "Inactivo")
            estado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, estado)

            for col, key in enumerate(["temp_amb", "humedad", "golpe", "luz",
                                       "temp_sonda", "punto_condensacion"], start=6):
                self.table.setItem(row, col, QTableWidgetItem(str(d.get(key, "--"))))

            btn_toggle = QPushButton("Desactivar" if d["active"] else "Activar")
            btn_toggle.clicked.connect(partial(self.toggle_device_status_por_id, d["id"]))
            self.table.setCellWidget(row, 12, btn_toggle)

            btn_del = QPushButton("Eliminar")
            btn_del.clicked.connect(partial(self.eliminar_dispositivo_por_id, d["id"]))
            self.table.setCellWidget(row, 13, btn_del)

    def actualizar_vistas(self):
        self._actualizar_tarjetas()
        self._actualizar_tabla()

    # alertas
    def alertas(self):
        for d in self.devices:
            if d["battery"] == 0 and d.get("active"):
                QMessageBox.critical(self, "Dispositivo apagado",
                                     f"{d['name']} se quedó sin batería.")
                d["active"] = False

    # bateria automática
    def _auto_reduce_battery(self):
        for d in self.devices:
            if d.get("active"):
                actual = d.get("battery", 100)
                if isinstance(actual, int):
                    d["battery"] = max(0, actual - 1)

        self.actualizar_vistas()

    # utilidades
    def _idx(self, dev_id):
        for i, d in enumerate(self.devices):
            if d["id"] == dev_id:
                return i
        return -1

    def filter_devices(self, text):
        text = text.lower()
        for card in self.device_cards.values():
            datos = card.property("datos") or {}
            visible = any(text in str(v).lower() for v in datos.values())
            card.setVisible(visible)

        for row in range(self.table.rowCount()):
            visible = any(
                text in (self.table.item(row, col).text().lower()
                         if self.table.item(row, col) else "")
                for col in range(self.table.columnCount())
            )
            self.table.setRowHidden(row, not visible)

    def toggle_view(self):
        mostrando_cards = self.scroll.isVisible()
        self.scroll.setVisible(not mostrando_cards)
        self.table.setVisible(mostrando_cards)

        self.btn_toggle_view.setText(
            "Cambiar a Tarjetas" if mostrando_cards else "Cambiar a Tabla"
        )

    def exportar_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "", "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Nombre", "Conexiones", "Ubicación", "Batería",
                "Activo", "Temp Amb", "Hum", "Golpe",
                "Luz", "Temp Sonda", "Punto Cond."
            ])
            for d in self.devices:
                writer.writerow([
                    d["id"], d["name"], d["connections"], d["location"],
                    d["battery"], "Sí" if d["active"] else "No",
                    d["temp_amb"], d["humedad"], d["golpe"],
                    d["luz"], d["temp_sonda"], d["punto_condensacion"]
                ])

    def closeEvent(self, event):
        if not self.external_worker and self.worker and self.worker.isRunning():
            self.worker.stop()
        super().closeEvent(event)
