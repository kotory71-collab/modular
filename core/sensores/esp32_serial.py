import json
import time
import math
import random
import threading
import serial
from queue import Queue
from typing import Dict, Union

class ESP32Serial:
    CAMPOS = ["ID", "T_Amb", "T_Sonda", "Hum", "Luz", "Rocío", "Bat", "Acc"]

    def __init__(self):
        self.ser = None
        self.simulacion = False
        self._sim_nodos = [0, 1, 2]
        self._cola_sim = Queue()
        self._hilos_sim = []
        self._stop_event = threading.Event()

    def configurar_conexion(self, puerto: Union[str, int], baudios: Union[int, float]) -> bool:
        if puerto == -1 and baudios == -1:
            print("[INFO] Modo de simulación activado.")
            self.simulacion = True
            self._iniciar_simulacion()
            return True
        try:
            self.ser = serial.Serial(puerto, baudios, timeout=1)
            self.simulacion = False
            return True
        except serial.SerialException as e:
            print(f"[ERROR] No se pudo abrir el puerto {puerto}: {e}")
            return False

    def recibir_datos(self) -> Dict[str, Union[int, float]]:
        if self.simulacion:
            try:
                return self._cola_sim.get(timeout=1)
            except:
                return {}

        if not self.ser or not self.ser.is_open:
            raise ConnectionError("Puerto serial no configurado o cerrado.")

        try:
            linea = self.ser.readline().decode().strip()
            if linea:
                datos_raw = json.loads(linea)
                return self._normalizar_datos(datos_raw)
            else:
                return {}
        except json.JSONDecodeError:
            print("[ADVERTENCIA] Error al decodificar JSON.")
            return {}

    def _normalizar_datos(self, datos_raw: dict) -> Dict[str, Union[int, float]]:
        datos_norm = {}
        for campo in self.CAMPOS:
            clave_json = self._mapear_clave(campo)
            datos_norm[campo] = datos_raw.get(clave_json, -255)
        return datos_norm

    def _mapear_clave(self, campo: str) -> str:
        return {
            "ID": "id", "T_Amb": "ta", "T_Sonda": "ts", "Hum": "h",
            "Luz": "lz", "Rocío": "roc", "Bat": "bat", "Acc": "a"
        }.get(campo, campo)

    def _iniciar_simulacion(self):
        self._stop_event.clear()
        for nodo_id in self._sim_nodos:
            hilo = threading.Thread(target=self._hilo_sim_nodo, args=(nodo_id,))
            hilo.daemon = True
            hilo.start()
            self._hilos_sim.append(hilo)

    def _hilo_sim_nodo(self, nodo_id: int):
        fase_base = random.uniform(0, 2 * math.pi)
        contador = 0
        while not self._stop_event.is_set():
            t_actual = time.time()
            fase = fase_base + contador * 0.1

            T_Amb = 22 + 3 * math.sin(fase)
            T_Sonda = T_Amb + 2 + 0.5 * math.sin(fase + 1.5)
            Hum = 45 + 10 * math.sin(fase - 1)
            Luz = 300 + 150 * math.sin(fase + 0.5)
            Rocio = T_Sonda - ((100 - Hum) / 5.0)
            Bat = 80 + 10 * math.sin(fase / 2)
            Acc = 0.3 + 0.2 * math.sin(fase * 3.1 + nodo_id) + random.uniform(-0.05, 0.05)  # m/s²

            datos = {
                "ID": nodo_id,
                "T_Amb": round(T_Amb, 2),
                "T_Sonda": round(T_Sonda, 2),
                "Hum": round(Hum, 2),
                "Luz": round(Luz, 2),
                "Rocío": round(Rocio, 2),
                "Bat": round(Bat, 2),
                "Acc": round(Acc, 3)
            }

            self._cola_sim.put(datos)
            contador += 1
            intervalo = 10 + random.uniform(-2, 2)
            time.sleep(intervalo)

    def enviar_texto(self, mensaje: str) -> bool:
        if self.simulacion:
            print(f"[SIMULACIÓN] Enviando: {mensaje}")
            return True
        if not self.ser or not self.ser.is_open:
            raise ConnectionError("Puerto serial no configurado o cerrado.")
        try:
            self.ser.write(mensaje.encode())
            return True
        except serial.SerialTimeoutException:
            print("[ERROR] Timeout al enviar mensaje.")
            return False

    def recibir_texto(self) -> str:
        if self.simulacion:
            return "[SIMULACIÓN] texto recibido"
        if not self.ser or not self.ser.is_open:
            raise ConnectionError("Puerto serial no configurado o cerrado.")
        try:
            return self.ser.readline().decode().strip()
        except Exception as e:
            print(f"[ERROR] Al recibir texto: {e}")
            return ""

    def cerrar_conexion(self):
        self._stop_event.set()
        if self.ser and self.ser.is_open:
            self.ser.close()

# Prueba

lista = []

#sensor = ESP32Serial()

'''
if sensor.configurar_conexion('COM7', 115200):
#if sensor.configurar_conexion(-1, -1):
    while True:      
        datos = sensor.recibir_datos()
        if datos:
            lista.append(datos["T_Amb"])
        if len(lista) >= 5:
            print(lista)
            lista = []
'''
            


if __name__ == "__main__":
    receptor = ESP32Serial()
    if receptor.configurar_conexion('COM7', 115200):  
    #if receptor.configurar_conexion(-1, -1):  # Activar simulación
        try:
            while True:
                datos = receptor.recibir_datos()
                if datos:
                    print("Datos:", datos)
        except KeyboardInterrupt:
            receptor.cerrar_conexion()
            print("\n[INFO] Programa terminado por el usuario.")
