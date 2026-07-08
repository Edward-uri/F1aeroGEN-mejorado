"""Escucha la telemetría UDP del juego F1 (formatos 2023-2025, header de 29 bytes).

En el juego: Ajustes → Telemetría → UDP activado, IP de esta máquina, puerto 20777.
El canal es de solo lectura: el juego transmite y aquí solo escuchamos.

Paquetes decodificados (solo el coche del jugador):
- 2 Lap Data:      distancia recorrida en la vuelta y tiempo de la última vuelta
- 5 Car Setup:     setup aplicado en el juego, mapeado a los nombres de nuestros genes
- 6 Car Telemetry: velocidad (km/h) para construir el trazo velocidad vs distancia
"""
import socket
import struct
import threading
import time

HEADER_FMT = '<HBBBBBQfIIBB'
HEADER_SIZE = struct.calcsize(HEADER_FMT)  # 29 bytes

PACKET_LAP_DATA = 2
PACKET_CAR_SETUP = 5
PACKET_CAR_TELEMETRY = 6

MAX_VUELTAS = 20


class F1TelemetryListener:

    def __init__(self, puerto=20777):
        self.puerto = puerto
        self.sock = None
        self.thread = None
        self.escuchando = False

        self.formato_paquete = None    # 2023/2024/2025, informativo
        self.distancia_actual = 0.0    # lapDistance real del juego (m)
        self.muestras = 0
        self.vueltas = []              # [{'tiempo_s': float|None, 'trazo': [(m, km/h), ...]}]
        self.setup_capturado = None    # setup del juego con nombres de genes
        self._trazo_actual = []
        self._ms_antes_del_cierre = 0
        self._last_ms_anterior = 0

    # ── decodificación ──

    @staticmethod
    def _bloque_jugador(data, header):
        """(offset, stride) del bloque del coche del jugador.

        El stride por coche se infiere del tamaño del paquete (22 coches +
        cola de <22 bytes), así el mismo código sirve para F1 23/24/25 sin
        hardcodear tamaños de estructura por versión.
        """
        stride = (len(data) - HEADER_SIZE) // 22
        return HEADER_SIZE + header[10] * stride, stride

    def _procesar(self, data):
        if len(data) < HEADER_SIZE:
            return
        try:
            header = struct.unpack_from(HEADER_FMT, data)
        except struct.error:
            return
        self.formato_paquete = header[0]
        packet_id = header[5]
        if packet_id == PACKET_LAP_DATA:
            self._leer_lap_data(data, header)
        elif packet_id == PACKET_CAR_SETUP:
            self._leer_setup(data, header)
        elif packet_id == PACKET_CAR_TELEMETRY:
            self._leer_telemetria(data, header)

    def _leer_lap_data(self, data, header):
        offset, _ = self._bloque_jugador(data, header)
        # offsets estables desde F1 23: lastLapTimeInMS @0 (u32), lapDistance @18 (float)
        last_ms = struct.unpack_from('<I', data, offset)[0]
        distancia = struct.unpack_from('<f', data, offset + 18)[0]

        # Cierre de vuelta: la distancia cae bruscamente al cruzar la meta
        if distancia < self.distancia_actual - 500 and self._trazo_actual:
            self.vueltas.append({'tiempo_s': None, 'trazo': self._trazo_actual})
            del self.vueltas[:-MAX_VUELTAS]
            self._trazo_actual = []
            self._ms_antes_del_cierre = self._last_ms_anterior
        self.distancia_actual = distancia

        # El tiempo de la vuelta cerrada llega cuando el juego refresca lastLapTime
        if self.vueltas and self.vueltas[-1]['tiempo_s'] is None \
                and last_ms > 0 and last_ms != self._ms_antes_del_cierre:
            self.vueltas[-1]['tiempo_s'] = round(last_ms / 1000.0, 3)
        self._last_ms_anterior = last_ms

    def _leer_telemetria(self, data, header):
        offset, _ = self._bloque_jugador(data, header)
        vel_kmh = struct.unpack_from('<H', data, offset)[0]  # speed @0 (u16, km/h)
        if self.distancia_actual >= 0:  # negativa = todavía no cruza la línea de salida
            self._trazo_actual.append((round(self.distancia_actual, 1), vel_kmh))
            self.muestras += 1

    def _leer_setup(self, data, header):
        offset, stride = self._bloque_jugador(data, header)
        # engineBraking se agregó en F1 24 (bloque de 50 bytes); en F1 23 mide 49
        off_presiones = offset + (29 if stride >= 50 else 28)
        rl, rr, fl, fr = struct.unpack_from('<ffff', data, off_presiones)

        def u8(i):
            return data[offset + i]

        def f32(i):
            return struct.unpack_from('<f', data, offset + i)[0]

        self.setup_capturado = {
            'aleron_delantero': u8(0), 'aleron_trasero': u8(1),
            'diferencial': u8(2),                     # % on-throttle
            'camber_frontal': round(f32(4), 2), 'camber_trasero': round(f32(8), 2),
            'toe_frontal': round(f32(12), 2), 'toe_trasero': round(f32(16), 2),
            'suspension_delantera': u8(20), 'suspension_trasera': u8(21),
            'barra_antivuelco_delantera': u8(22), 'barra_antivuelco_trasera': u8(23),
            'altura_delantera': u8(24), 'altura_trasera': u8(25),
            'reparto_frenada': u8(27),                # % al eje delantero
            'presion_delantera': round((fl + fr) / 2, 2),
            'presion_trasera': round((rl + rr) / 2, 2),
        }

    # ── ciclo de vida ──

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.puerto))
        self.sock.settimeout(1.0)
        self.escuchando = True
        self.thread = threading.Thread(target=self._escuchar, daemon=True)
        self.thread.start()

    def _escuchar(self):
        while self.escuchando:
            try:
                data, _ = self.sock.recvfrom(2048)
                self._procesar(data)
            except socket.timeout:
                continue
            except OSError:
                break

    def stop(self):
        self.escuchando = False
        if self.thread:
            self.thread.join()
        if self.sock:
            self.sock.close()
            self.sock = None

    # ── consultas ──

    def mejor_vuelta(self):
        """La vuelta completa más rápida capturada, o None."""
        completas = [v for v in self.vueltas if v['tiempo_s']]
        return min(completas, key=lambda v: v['tiempo_s']) if completas else None

    def estado(self):
        return {
            'escuchando': self.escuchando,
            'puerto': self.puerto,
            'formato_paquete': self.formato_paquete,
            'muestras': self.muestras,
            'distancia_actual': round(self.distancia_actual, 1),
            'vueltas': [
                {'num': i + 1, 'tiempo_s': v['tiempo_s'], 'puntos': len(v['trazo'])}
                for i, v in enumerate(self.vueltas)
            ],
            'setup': self.setup_capturado,
        }


if __name__ == "__main__":
    listener = F1TelemetryListener()
    listener.start()
    print(f"[UDP] Escuchando telemetría de F1 en el puerto {listener.puerto}. CTRL+C para detener.")
    try:
        while True:
            time.sleep(1)
            e = listener.estado()
            print(f"Dist: {e['distancia_actual']:.0f} m | muestras: {e['muestras']} | "
                  f"vueltas: {len(e['vueltas'])}", end='\r')
    except KeyboardInterrupt:
        listener.stop()
        print(f"\n[UDP] Detenido. Estado final: {len(listener.vueltas)} vueltas capturadas.")
