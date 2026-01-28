from PyQt6.QtCore import QThread, pyqtSignal
from core.sensores.esp32_serial import ESP32Serial
import time

class ESP32Worker(QThread):
    data_received = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, puerto="COM7", baudios=115200, parent=None):
        super().__init__(parent)
        self.puerto = puerto
        self.baudios = baudios
        self._running = False
        self.receptor = ESP32Serial()

    def configurar(self):
        ok = self.receptor.configurar_conexion(self.puerto, self.baudios)
        if not ok:
            self.error.emit("No se pudo configurar el puerto serial.")
        return ok

    def run(self):
        # Intentar configurar 
        try:
            self.receptor.configurar_conexion(self.puerto, self.baudios)
        except Exception as e:
            self.error.emit(f"Error al configurar serial: {e}")

        self._running = True
        while self._running:
            try:
                datos = self.receptor.recibir_datos()
                if datos:
                    # Emitir copia segura de los datos
                    self.data_received.emit(dict(datos))
                # Pequeña pausa para evitar bloqueo completo
                time.sleep(0.1)
            except Exception as e:
                self.error.emit(f"Error lectura serial: {e}")
                time.sleep(0.5)

    def stop(self):
        self._running = False
        try:
            self.receptor.cerrar_conexion()
        except Exception:
            pass
        self.wait()
