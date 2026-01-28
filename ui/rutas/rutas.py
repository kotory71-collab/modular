from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QComboBox, QGroupBox, QMessageBox,
    QSplitter, QSizePolicy, QPlainTextEdit, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal


class RoutesPage(QWidget):

    truck_updated = pyqtSignal(dict)  
    route_assigned = pyqtSignal(int, int)  
    route_unassigned = pyqtSignal(int)  

    def __init__(self, role: str = "admin", user_id: int | None = None, parent=None):
        super().__init__(parent)
        self.role = role
        self.user_id = user_id

        # Datos de ejemplo
        # Cada camión: id, placas, tipo, chofer_id, estado ('bodega'|'ruta'), carga
        self.trucks = [
            {"id": 1, "plates": "ABC-123", "type": "Refrigerado", "driver_id": 101, "status": "bodega", "load": "Vacío"},
            {"id": 2, "plates": "XYZ-789", "type": "Seco", "driver_id": 102, "status": "ruta", "load": "Vacunas - Lote 2025A"},
            {"id": 3, "plates": "LMN-456", "type": "Refrigerado", "driver_id": 103, "status": "bodega", "load": "Insumos médicos"},
        ]

        # Rutas de ejemplo: id, nombre, origen, destino
        self.routes = [
            {"id": 1, "name": "Ruta CDMX - Puebla", "origin": "CDMX", "destination": "Puebla", "eta": "2h"},
            {"id": 2, "name": "Ruta CDMX - Toluca", "origin": "CDMX", "destination": "Toluca", "eta": "1h"},
        ]

        # asignacion de caminones a rutas
        self.assignments = {2: 1}  # asignacion inicial: camión 2 a ruta 1

        self._build_ui()
        self._load_tables()
        self._apply_role_restrictions()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # panel izquierdo
        left = QWidget()
        left_layout = QVBoxLayout(left)

        # Filtro de búsqueda y tipo
        filter_box = QGroupBox("Filtros / Buscar")
        fb_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por placas, chofer o tipo...")
        self.search_input.textChanged.connect(self._on_search)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "bodega", "ruta"]) 
        self.status_filter.currentTextChanged.connect(self._on_search)
        fb_layout.addWidget(self.search_input)
        fb_layout.addWidget(self.status_filter)
        filter_box.setLayout(fb_layout)

        left_layout.addWidget(filter_box)

        # Tabla de camiones
        self.trucks_table = QTableWidget(0, 6)
        self.trucks_table.setHorizontalHeaderLabels(["ID", "Placas", "Tipo", "Chofer ID", "Estado", "Carga"])
        self.trucks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trucks_table.setSelectionBehavior(self.trucks_table.SelectionBehavior.SelectRows)
        self.trucks_table.itemSelectionChanged.connect(self._on_truck_selected)
        left_layout.addWidget(QLabel("Camiones"))
        left_layout.addWidget(self.trucks_table)

        # Botones de acción
        actions = QWidget()
        act_layout = QHBoxLayout(actions)
        self.btn_add_truck = QPushButton("Registrar camión")
        self.btn_add_truck.clicked.connect(self._open_add_truck)
        self.btn_assign_route = QPushButton("Asignar ruta")
        self.btn_assign_route.clicked.connect(self._assign_route_to_selected)
        self.btn_unassign_route = QPushButton("Quitar asignación")
        self.btn_unassign_route.clicked.connect(self._unassign_route_from_selected)
        act_layout.addWidget(self.btn_add_truck)
        act_layout.addWidget(self.btn_assign_route)
        act_layout.addWidget(self.btn_unassign_route)
        left_layout.addWidget(actions)

        # Tabla de rutas
        self.routes_table = QTableWidget(0, 5)
        self.routes_table.setHorizontalHeaderLabels(["ID", "Nombre", "Origen", "Destino", "ETA"])
        self.routes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(QLabel("Rutas"))
        left_layout.addWidget(self.routes_table)

        # Formulario rápido
        self.detail_box = QGroupBox("Detalle / Edición rápida")
        db_layout = QFormLayout()
        self.detail_id = QLabel("-")
        self.detail_plates = QLineEdit()
        self.detail_type = QLineEdit()
        self.detail_driver = QLineEdit()
        self.detail_status = QComboBox()
        self.detail_status.addItems(["bodega", "ruta"]) 
        self.detail_load = QPlainTextEdit()
        db_layout.addRow("ID:", self.detail_id)
        db_layout.addRow("Placas:", self.detail_plates)
        db_layout.addRow("Tipo:", self.detail_type)
        db_layout.addRow("Chofer ID:", self.detail_driver)
        db_layout.addRow("Estado:", self.detail_status)
        db_layout.addRow("Carga:", self.detail_load)
        save_btn = QPushButton("Guardar cambios")
        save_btn.clicked.connect(self._save_truck_edits)
        db_layout.addRow(save_btn)
        self.detail_box.setLayout(db_layout)
        left_layout.addWidget(self.detail_box)

        splitter.addWidget(left)

        # panel de mapa
        right = QWidget()
        right_layout = QVBoxLayout(right)

        # Resumen rápido
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        right_layout.addWidget(QLabel("Resumen"))
        right_layout.addWidget(self.summary_label)

        # mapa
        self.map_placeholder = QLabel("[Mapa - reemplazar por widget de mapa si se requiere]")
        self.map_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_placeholder.setMinimumHeight(300)
        self.map_placeholder.setStyleSheet("border: 1px solid #999; background: #fafafa;")
        right_layout.addWidget(self.map_placeholder)

        # Detalle asignación
        self.assignment_label = QLabel("Asignaciones:")
        self.assignment_label.setWordWrap(True)
        right_layout.addWidget(self.assignment_label)

        splitter.addWidget(right)
        splitter.setSizes([700, 400])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def _load_tables(self):
        # Camiones
        self.trucks_table.setRowCount(0)
        for t in self.trucks:
            if self.role == 'driver' and self.user_id is not None:
                if t.get('driver_id') != self.user_id:
                    continue
            row = self.trucks_table.rowCount()
            self.trucks_table.insertRow(row)
            self.trucks_table.setItem(row, 0, QTableWidgetItem(str(t['id'])))
            self.trucks_table.setItem(row, 1, QTableWidgetItem(t['plates']))
            self.trucks_table.setItem(row, 2, QTableWidgetItem(t['type']))
            self.trucks_table.setItem(row, 3, QTableWidgetItem(str(t['driver_id'])))
            self.trucks_table.setItem(row, 4, QTableWidgetItem(t['status']))
            self.trucks_table.setItem(row, 5, QTableWidgetItem(t['load']))

        # Rutas
        self.routes_table.setRowCount(0)
        for r in self.routes:
            row = self.routes_table.rowCount()
            self.routes_table.insertRow(row)
            self.routes_table.setItem(row, 0, QTableWidgetItem(str(r['id'])))
            self.routes_table.setItem(row, 1, QTableWidgetItem(r['name']))
            self.routes_table.setItem(row, 2, QTableWidgetItem(r['origin']))
            self.routes_table.setItem(row, 3, QTableWidgetItem(r['destination']))
            self.routes_table.setItem(row, 4, QTableWidgetItem(r['eta']))

        self._refresh_summary()
        self._refresh_assignments_text()

    def _apply_role_restrictions(self):
        if self.role == 'driver':
            # Chofer sólo ve su camión, no puede editar ni asignar
            self.btn_add_truck.setVisible(False)
            self.btn_assign_route.setVisible(False)
            self.btn_unassign_route.setVisible(False)
            self.detail_box.setVisible(False)
            self.search_input.setEnabled(False)
            self.status_filter.setEnabled(False)
        elif self.role == 'supervisor':
            # Supervisor puede ver todo pero no registrar camiones
            self.btn_add_truck.setVisible(False)
            self.btn_assign_route.setVisible(True)
            self.btn_unassign_route.setVisible(True)
        else:  
            self.btn_add_truck.setVisible(True)
            self.btn_assign_route.setVisible(True)
            self.btn_unassign_route.setVisible(True)

    def _on_search(self):
        term = self.search_input.text().lower()
        status = self.status_filter.currentText()
        filtered = []
        for t in self.trucks:
            if self.role == 'driver' and self.user_id is not None and t.get('driver_id') != self.user_id:
                continue
            if status != 'Todos' and t['status'] != status:
                continue
            if term:
                if term in t['plates'].lower() or term in t['type'].lower() or term in str(t['driver_id']):
                    filtered.append(t)
            else:
                filtered.append(t)

        # recargar tabla
        self.trucks_table.setRowCount(0)
        for t in filtered:
            row = self.trucks_table.rowCount()
            self.trucks_table.insertRow(row)
            self.trucks_table.setItem(row, 0, QTableWidgetItem(str(t['id'])))
            self.trucks_table.setItem(row, 1, QTableWidgetItem(t['plates']))
            self.trucks_table.setItem(row, 2, QTableWidgetItem(t['type']))
            self.trucks_table.setItem(row, 3, QTableWidgetItem(str(t['driver_id'])))
            self.trucks_table.setItem(row, 4, QTableWidgetItem(t['status']))
            self.trucks_table.setItem(row, 5, QTableWidgetItem(t['load']))

    def _on_truck_selected(self):
        items = self.trucks_table.selectedItems()
        if not items:
            return
        row = items[0].row()
        truck_id = int(self.trucks_table.item(row, 0).text())
        truck = next((t for t in self.trucks if t['id'] == truck_id), None)
        if not truck:
            return
        self.detail_id.setText(str(truck['id']))
        self.detail_plates.setText(truck['plates'])
        self.detail_type.setText(truck['type'])
        self.detail_driver.setText(str(truck['driver_id']))
        self.detail_status.setCurrentText(truck['status'])
        self.detail_load.setPlainText(truck['load'])

        # Actualizar mapa
        assign = self.assignments.get(truck_id)
        route_info = "Sin ruta asignada"
        if assign:
            r = next((x for x in self.routes if x['id'] == assign), None)
            if r:
                route_info = f"Asignado a: {r['name']} ({r['origin']} → {r['destination']}) ETA: {r['eta']}"
        self.map_placeholder.setText(f"Camión {truck['plates']}\nEstado: {truck['status']}\n{route_info}\nCarga: {truck['load']}")

    def _open_add_truck(self):
        # Diálogo simple para agregar un camión
        dlg = QWidget()
        dlg.setWindowTitle("Registrar nuevo camión")
        layout = QFormLayout(dlg)
        plates = QLineEdit()
        ttype = QLineEdit()
        driver = QLineEdit()
        status = QComboBox(); status.addItems(["bodega", "ruta"]) 
        load = QPlainTextEdit()
        save = QPushButton("Guardar")

        def do_save():
            new_id = max([t['id'] for t in self.trucks]) + 1 if self.trucks else 1
            try:
                driver_id = int(driver.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "Chofer ID debe ser numérico")
                return
            new = {
                'id': new_id,
                'plates': plates.text(),
                'type': ttype.text(),
                'driver_id': driver_id,
                'status': status.currentText(),
                'load': load.toPlainText()
            }
            self.trucks.append(new)
            self.truck_updated.emit(new)
            self._load_tables()
            dlg.close()

        save.clicked.connect(do_save)
        layout.addRow("Placas:", plates)
        layout.addRow("Tipo:", ttype)
        layout.addRow("Chofer ID:", driver)
        layout.addRow("Estado:", status)
        layout.addRow("Carga:", load)
        layout.addRow(save)
        dlg.setLayout(layout)
        dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
        dlg.setMinimumWidth(300)
        dlg.show()

    def _assign_route_to_selected(self):
        items = self.trucks_table.selectedItems()
        if not items:
            QMessageBox.information(self, "Selecciona", "Selecciona un camión para asignar una ruta")
            return
        row = items[0].row()
        truck_id = int(self.trucks_table.item(row, 0).text())

        # selección de ruta
        route_sel_items = self.routes_table.selectedItems()
        if route_sel_items:
            route_id = int(self.routes_table.item(route_sel_items[0].row(), 0).text())
        else:
            # ruta disponible
            route_id = self.routes[0]['id'] if self.routes else None

        if route_id is None:
            QMessageBox.warning(self, "No hay rutas", "No existen rutas registradas para asignar")
            return

        self.assignments[truck_id] = route_id
        self.route_assigned.emit(truck_id, route_id)
        self._refresh_assignments_text()
        self._load_tables()

    def _unassign_route_from_selected(self):
        items = self.trucks_table.selectedItems()
        if not items:
            QMessageBox.information(self, "Selecciona", "Selecciona un camión para quitar la asignación")
            return
        row = items[0].row()
        truck_id = int(self.trucks_table.item(row, 0).text())
        if truck_id in self.assignments:
            del self.assignments[truck_id]
            self.route_unassigned.emit(truck_id)
            self._refresh_assignments_text()
            self._load_tables()
        else:
            QMessageBox.information(self, "Sin asignación", "El camión no tenía ruta asignada")

    def _save_truck_edits(self):
        tid = self.detail_id.text()
        if tid == '-' or not tid:
            QMessageBox.warning(self, "Error", "Selecciona primero un camión")
            return
        truck = next((t for t in self.trucks if str(t['id']) == tid), None)
        if not truck:
            QMessageBox.warning(self, "Error", "Camión no encontrado")
            return
        try:
            driver_id = int(self.detail_driver.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Chofer ID debe ser numérico")
            return
        truck['plates'] = self.detail_plates.text()
        truck['type'] = self.detail_type.text()
        truck['driver_id'] = driver_id
        truck['status'] = self.detail_status.currentText()
        truck['load'] = self.detail_load.toPlainText()
        self.truck_updated.emit(truck)
        self._load_tables()
        QMessageBox.information(self, "Guardado", "Cambios guardados")

    def _refresh_summary(self):
        total = len([t for t in self.trucks if not (self.role == 'driver' and self.user_id and t.get('driver_id') != self.user_id)])
        en_ruta = len([t for t in self.trucks if t['status'] == 'ruta'])
        en_bodega = len([t for t in self.trucks if t['status'] == 'bodega'])
        self.summary_label.setText(f"Total camiones: {total}\nEn ruta: {en_ruta}\nEn bodega: {en_bodega}")

    def _refresh_assignments_text(self):
        lines = []
        for truck_id, route_id in self.assignments.items():
            truck = next((t for t in self.trucks if t['id'] == truck_id), None)
            route = next((r for r in self.routes if r['id'] == route_id), None)
            if truck and route:
                lines.append(f"{truck['plates']} → {route['name']} ({route['origin']}→{route['destination']})")
        if not lines:
            self.assignment_label.setText("Asignaciones: ninguna")
        else:
            self.assignment_label.setText("Asignaciones:\n" + "\n".join(lines))

    # Métodos públicos
    def set_role(self, role: str, user_id: int | None = None):
        self.role = role
        self.user_id = user_id
        self._apply_role_restrictions()
        self._load_tables()

    def add_route(self, name: str, origin: str, destination: str, eta: str):
        new_id = max([r['id'] for r in self.routes]) + 1 if self.routes else 1
        self.routes.append({"id": new_id, "name": name, "origin": origin, "destination": destination, "eta": eta})
        self._load_tables()
