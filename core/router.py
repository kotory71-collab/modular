from ui.login.login_window import LoginWindow
from ui.dashboard.dashboard_window import Dashboard

class Router:
    def __init__(self, app):
        self.app = app
        self.ventana_login = None
        self.dashboard = None

    def mostrar_login(self):
        if self.dashboard:
            self.dashboard.close()
            self.dashboard = None
            
        if self.ventana_login:
            self.ventana_login.close()
            
        self.ventana_login = LoginWindow(self.ir_a_dashboard)
        self.ventana_login.show()

    def ir_a_dashboard(self, rol):
        """
        Se ejecuta cuando el login es correcto.
        """
        if self.ventana_login:
            self.ventana_login.close()
            self.ventana_login = None

        # Creamos el dashboard
        self.dashboard = Dashboard(rol, self.mostrar_login)
        self.dashboard.show()

    def logout(self):
        """
        Se ejecuta cuando el usuario cierra sesión desde Dashboard.
        """
        if self.dashboard:
            self.dashboard.close()
            self.dashboard = None

        # Volvemos al login
        self.mostrar_login()