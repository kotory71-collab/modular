# ui/dashboard/dashboard_window.py
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton,
    QStackedWidget, QSizePolicy, QGridLayout, QLabel
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QEvent
from PyQt6.QtGui import QCursor

from ui.widgets.sensor_card import SensorCard
from core.sensores.esp32_worker import ESP32Worker
from ui.devices.devices_window import DevicesPage
from ui.users.users_page import UsersPage
from ui.insumos.insumos_page import InsumosPage



class Dashboard(QWidget):
    def __init__(self, user_role: str, on_logout):
        super().__init__()
        self.user_role = user_role
        self.on_logout = on_logout

        # QUITADO: modo oscuro
        self.dark_mode = False

        # Dimensiones menú
        self.menu_expanded_width = 240
        self.menu_collapsed_width = 0
        self.menu_sensitive_area = 20
        self.menu_pinned = False

        self.setWindowTitle("Dashboard - Monitoreo de Insumos")
        self.resize(1360, 820)

        # Aplicar estilo claro
        self.apply_theme()

        self.setObjectName("root")

        # ------------------------------
        #  PRIMERO INICIAMOS EL WORKER
        # ------------------------------
        self.worker = ESP32Worker(puerto="COM7", baudios=115200)
        self.worker.data_received.connect(self.on_sensor_data)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()

        # ---------------- Layout principal ----------------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # CONTENEDOR DEL MENÚ
        self.menu_container = QFrame()
        self.menu_container.setObjectName("menuContainer")
        self.menu_container.setFixedWidth(self.menu_collapsed_width)

        menu_container_layout = QHBoxLayout(self.menu_container)
        menu_container_layout.setContentsMargins(0, 0, 0, 0)
        menu_container_layout.setSpacing(0)

        # Sidebar
        self.sidebar = self._build_sidebar()
        self.sidebar.setMinimumWidth(self.menu_expanded_width)
        menu_container_layout.addWidget(self.sidebar)

        # Botón toggle
        self.toggle_button = QPushButton("☰")
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(10, 30, 70, 0.9);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2196F3;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_menu)
        self.toggle_button.show()


        menu_container_layout.addWidget(self.toggle_button)
        menu_container_layout.addStretch()

        # STACK DE PÁGINAS
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # ----------------------------
        #  PÁGINAS (worker YA EXISTE)
        # ----------------------------
        self.page_dashboard = self._build_dashboard_page()

        #  Módulo Dispositivos REAL
        self.page_devices = DevicesPage(esp32_worker=self.worker)

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self._placeholder_page("Rutas y Transporte"))
        self.stack.addWidget(InsumosPage())
        self.stack.addWidget(self.page_devices)
        self.stack.addWidget(UsersPage())
        self.stack.addWidget(self._placeholder_page("Historial y Reportes"))
        self.stack.addWidget(self._placeholder_page("Alertas y Notificaciones"))
        

        main_layout.addWidget(self.menu_container)
        main_layout.addWidget(self.stack, 1)

        # Animación menú
        self.menu_animation = QPropertyAnimation(self.menu_container, b"maximumWidth")
        self.menu_animation.setDuration(300)
        self.menu_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Timer auto ocultar
        self.hide_menu_timer = QTimer()
        self.hide_menu_timer.setSingleShot(True)
        self.hide_menu_timer.setInterval(500)
        self.hide_menu_timer.timeout.connect(self.auto_hide_menu)

        self.stack.installEventFilter(self)
        self.setMouseTracking(True)
        self.stack.setMouseTracking(True)

    # ----------------------------------------------------------------------
    # -------------------------- DISEÑO SIN MODO OSCURO ---------------------
    # ----------------------------------------------------------------------
    def apply_theme(self):
        """Modo claro fijo"""
        self.setStyleSheet("""
            QWidget#root {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                           stop:0 #f4f6fa, stop:1 #e8ecf3);
                color: #222;
            }
            QFrame#sidebar {
                background: rgba(255,255,255,0.8);
                border-top-right-radius: 16px;
                border-bottom-right-radius: 16px;
            }
            QPushButton.menuBtn {
                background: transparent;
                color: #222;
                padding: 10px 18px;
                font-size: 15px;
                border-radius: 8px;
                text-align: left;
            }
            QPushButton.menuBtn:hover {
                background: rgba(0,0,0,0.08);
            }
            QFrame.card {
                background: rgba(255,255,255,0.9);
                border-radius: 12px;
                border: 1px solid rgba(0,0,0,0.05);
            }
        """)

    # ----------------------------------------------------------------------
    # ---------------------------- SIDEBAR ---------------------------------
    # ----------------------------------------------------------------------
    def _build_sidebar(self):
        menu = QFrame()
        menu.setObjectName("sidebar")

        layout = QVBoxLayout(menu)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.btn_pin = QPushButton("Fijar menú")
        self.btn_pin.setFixedSize(100, 34)
        self.btn_pin.clicked.connect(self._toggle_pin)
        layout.addWidget(self.btn_pin)

        buttons = [
            ("Dashboard", 0),
            ("Rutas y Transporte", 1),
            ("Insumos Médicos", 2),
            ("Dispositivos", 3),
            ("Usuarios", 4),
            ("Historial & Reportes", 5),
            ("Alertas & Notificaciones", 6),
            ("Configuración", 7),
        ]

        for text, index in buttons:
            btn = QPushButton(text)
            btn.setProperty("class", "menuBtn")
            btn.clicked.connect(lambda _, i=index: self.stack.setCurrentIndex(i))
            layout.addWidget(btn)

        layout.addStretch()

        self.btn_logout = QPushButton("Cerrar sesión")
        self.btn_logout.setProperty("class", "menuBtn")
        self.btn_logout.clicked.connect(self._logout)
        layout.addWidget(self.btn_logout)

        return menu

    # ----------------------------------------------------------------------
    # --------------------------- PÁGINAS ----------------------------------
    # ----------------------------------------------------------------------
    def _build_dashboard_page(self):
        page = QFrame()
        page.setObjectName("page")
        g = QGridLayout(page)
        g.setContentsMargins(24, 24, 24, 24)
        g.setSpacing(20)

        self.cards = {
            "T_Amb": SensorCard("Temperatura Ambiente", "°C"),
            "T_Sonda": SensorCard("Temp. Sonda", "°C"),
            "Hum": SensorCard("Humedad", "%"),
            "Luz": SensorCard("Luz", "lx"),
            "Rocío": SensorCard("Punto de Condensación", "°C"),
            "Bat": SensorCard("Batería", "%"),
            "Acc": SensorCard("Aceleración", "g")
        }

        keys = list(self.cards.keys())
        cols = 4
        rows = (len(keys) + cols - 1) // cols
        idx = 0

        for r in range(rows):
            for c in range(cols):
                if idx >= len(keys):
                    break
                g.addWidget(self.cards[keys[idx]], r, c)
                idx += 1

        return page

    def _placeholder_page(self, text):
        w = QFrame()
        layout = QVBoxLayout(w)
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 22px;")
        layout.addStretch()
        layout.addWidget(lbl)
        layout.addStretch()
        return w

    # ----------------------------------------------------------------------
    # ------------------ MANEJO DEL MENÚ LATERAL ---------------------------
    # ----------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if obj == self.stack and event.type() == QEvent.Type.MouseMove:
            if not self.menu_pinned:
                if event.pos().x() < self.menu_sensitive_area:
                    self.show_menu()
                else:
                    if self.menu_container.maximumWidth() > 0:
                        self.hide_menu_timer.start()
        return super().eventFilter(obj, event)

    def toggle_menu(self):
        if self.menu_container.maximumWidth() == 0:
            self.show_menu()
        else:
            self.hide_menu()

    def auto_hide_menu(self):
        if not self.menu_pinned and self.menu_container.maximumWidth() > 0:
            self.hide_menu()

    def show_menu(self):
        self.hide_menu_timer.stop()
        self.menu_animation.stop()
        self.menu_animation.setStartValue(self.menu_container.maximumWidth())
        self.menu_animation.setEndValue(self.menu_expanded_width + 40)
        self.menu_animation.start()
        self.toggle_button.hide()

    def hide_menu(self):
        if not self.menu_pinned:
            self.menu_animation.stop()
            self.menu_animation.setStartValue(self.menu_container.maximumWidth())
            self.menu_animation.setEndValue(0)
            self.menu_animation.finished.connect(self._on_menu_hidden)
            self.menu_animation.start()

    def _on_menu_hidden(self):
        if self.menu_container.maximumWidth() == 0:
            self.toggle_button.show()
        self.menu_animation.finished.disconnect(self._on_menu_hidden)

    def _toggle_pin(self):
        self.menu_pinned = not self.menu_pinned
        self.btn_pin.setText("Fijar menú" if not self.menu_pinned else "Menú fijado")
        if self.menu_pinned and self.menu_container.maximumWidth() == 0:
            self.show_menu()
        if not self.menu_pinned:
            self.hide_menu_timer.start()

    # ----------------------------------------------------------------------
    # --------------------------- SENSORES ---------------------------------
    # ----------------------------------------------------------------------
    def on_sensor_data(self, datos: dict):
        mapping = {
            "T_Amb": "T_Amb",
            "T_Sonda": "T_Sonda",
            "Hum": "Hum",
            "Luz": "Luz",
            "Rocío": "Rocío",
            "Bat": "Bat",
            "Acc": "Acc"
        }
        for k_src, k_card in mapping.items():
            if k_src in datos:
                self.cards[k_card].update_value(datos[k_src])

    def on_worker_error(self, mensaje: str):
        print("[ESP32 Worker] ", mensaje)

    def _logout(self):
        try:
            if self.worker and self.worker.isRunning():
                self.worker.stop()
        except:
            pass
        if callable(self.on_logout):
            self.on_logout()

    def closeEvent(self, event):
        try:
            if self.worker and self.worker.isRunning():
                self.worker.stop()
        except:
            pass
        event.accept()
