import socket
import struct
import threading
import time

class F1TelemetryListener:
 
    def __init__(self, ip='0.0.0.0', port=20777):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)
        self.listening = False
        self.thread = None
        
        self.distancia_actual = 0.0
        self.telemetria_procesada = [] 
        self.ultimo_tiempo = None

    def _unpack_header(self, data):
 
        try:
            return struct.unpack('<HBBBB B Q f II BB', data[:29])
        except struct.error:
            return None

    def _escuchar(self):
        print(f"[UDP] Escuchando telemetría de F1 en {self.ip}:{self.port}")
        self.ultimo_tiempo = time.time()
        
        while self.listening:
            try:
                data, _ = self.sock.recvfrom(2048)
                header = self._unpack_header(data)
                
                if header is None: continue
                
                packet_id = header[5]
                player_car_index = header[10]
                
                if packet_id == 6:
                    offset = 29 + (player_car_index * 60)
                    
                    if len(data) >= offset + 2:
                        speed_bytes = data[offset : offset+2]
                        vel_kmh = struct.unpack('<H', speed_bytes)[0]
                        
                        tiempo_actual = time.time()
                        dt = tiempo_actual - self.ultimo_tiempo
                        self.ultimo_tiempo = tiempo_actual
                        
                        vel_ms = vel_kmh / 3.6
                        self.distancia_actual += (vel_ms * dt)
                        
                        if vel_kmh > 0 or self.distancia_actual > 0:
                            self.telemetria_procesada.append((self.distancia_actual, vel_kmh))
                            
            except socket.timeout:
                continue 
            except Exception as e:
                print(f"[UDP] Error decodificando frame: {e}")

    def start(self):
        self.listening = True
        self.telemetria_procesada = []
        self.distancia_actual = 0.0
        self.ultimo_tiempo = time.time()
        self.thread = threading.Thread(target=self._escuchar, daemon=True)
        self.thread.start()

    def stop(self):
        self.listening = False
        if self.thread:
            self.thread.join()
        if self.sock:
            self.sock.close()
            
        print(f"\n[UDP] Sensor detenido. Muestras guardadas: {len(self.telemetria_procesada)}")
        
        import csv
        with open('telemetria_capturada.csv', mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Distancia_Mts", "Velocidad_KMH"])
            for d, v in self.telemetria_procesada:
                writer.writerow([round(d, 3), v])
                
        return self.telemetria_procesada

if __name__ == "__main__":
    listener = F1TelemetryListener()
    listener.start()
    print("Corre el juego y acelera tu monoplaza. Presiona CTRL+C para detener y ver resultados.")
    try:
        while True:
            time.sleep(1)
            if listener.telemetria_procesada:
                d, v = listener.telemetria_procesada[-1]
                print(f"Dist. recorrida: {d:.1f} m  |  Velocidad actual: {v} km/h", end='\r')
    except KeyboardInterrupt:
        distancia = listener.stop()
        print(f"\nDistancia total registrada: {distancia[-1][0]:.2f} metros." if distancia else "Sin datos.")
