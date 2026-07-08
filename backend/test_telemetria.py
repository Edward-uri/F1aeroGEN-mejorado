"""Prueba del listener UDP con paquetes sintéticos en formato F1 25.

Simula una vuelta completa del juego (Lap Data + Car Telemetry + Car Setup)
sin necesidad de tener el juego corriendo.
Uso:  cd backend && python test_telemetria.py
"""
import socket
import struct
import time

from modulos.telemetry_listener import F1TelemetryListener, HEADER_FMT

PUERTO_PRUEBA = 20877


def header(packet_id):
    # formato 2025, jugador = coche 0
    return struct.pack(HEADER_FMT, 2025, 25, 1, 0, 1, packet_id, 99, 0.0, 0, 0, 0, 255)


def paquete_coches(packet_id, bloque_jugador, stride, cola):
    cuerpo = bytearray(stride * 22)
    cuerpo[0:len(bloque_jugador)] = bloque_jugador
    return header(packet_id) + bytes(cuerpo) + cola


def lap_data(last_ms, distancia):
    b = bytearray(57)  # tamaño del bloque LapData en F1 24/25
    struct.pack_into('<I', b, 0, last_ms)
    struct.pack_into('<f', b, 18, distancia)
    return paquete_coches(2, b, 57, b'\x00\x00')


def car_telemetry(vel_kmh):
    b = bytearray(60)
    struct.pack_into('<H', b, 0, vel_kmh)
    return paquete_coches(6, b, 60, b'\x00\x00\x00')


def car_setup():
    b = bytearray(50)  # bloque con engineBraking (F1 24/25)
    b[0], b[1], b[2], b[3] = 22, 26, 80, 55            # alerones, diff on/off
    struct.pack_into('<ffff', b, 4, -3.1, -1.7, 0.05, 0.2)  # cambers, toes
    b[20], b[21] = 30, 8                                # suspensión del/tras
    b[22], b[23] = 15, 9                                # barras antivuelco
    b[24], b[25] = 34, 37                               # alturas
    b[26], b[27], b[28] = 100, 59, 5                    # presión freno, reparto, engine braking
    struct.pack_into('<ffff', b, 29, 21.0, 21.2, 23.0, 23.4)  # presiones RL RR FL FR
    return paquete_coches(5, b, 50, b'\x00\x00\x00\x00')


def main():
    listener = F1TelemetryListener(puerto=PUERTO_PRUEBA)
    listener.start()
    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def envia(paquete):
        tx.sendto(paquete, ('127.0.0.1', PUERTO_PRUEBA))
        time.sleep(0.002)

    # Vuelta completa: 0 → 4000 m acelerando de 150 a 190 km/h
    for i in range(41):
        envia(lap_data(0, i * 100.0))
        envia(car_telemetry(150 + i))

    # Cruce de meta: la distancia cae y el tiempo de vuelta llega después
    envia(lap_data(0, 5.0))
    envia(lap_data(78543, 10.0))
    envia(car_setup())

    time.sleep(0.3)
    listener.stop()

    assert len(listener.vueltas) == 1, f"debió cerrar 1 vuelta, hay {len(listener.vueltas)}"
    vuelta = listener.vueltas[0]
    assert vuelta['tiempo_s'] == 78.543, f"tiempo de vuelta incorrecto: {vuelta['tiempo_s']}"
    assert len(vuelta['trazo']) == 41, f"trazo incompleto: {len(vuelta['trazo'])} puntos"
    assert vuelta['trazo'][0] == (0.0, 150) and vuelta['trazo'][-1] == (4000.0, 190)

    s = listener.setup_capturado
    assert s['aleron_delantero'] == 22 and s['aleron_trasero'] == 26
    assert s['diferencial'] == 80 and s['reparto_frenada'] == 59
    assert s['suspension_delantera'] == 30 and s['barra_antivuelco_trasera'] == 9
    assert s['altura_delantera'] == 34 and s['altura_trasera'] == 37
    assert abs(s['camber_frontal'] + 3.1) < 0.01 and abs(s['toe_trasero'] - 0.2) < 0.01
    assert s['presion_delantera'] == 23.2 and s['presion_trasera'] == 21.1

    assert listener.mejor_vuelta()['tiempo_s'] == 78.543
    estado = listener.estado()
    assert estado['vueltas'][0]['puntos'] == 41 and not estado['escuchando']

    print("OK: prueba del listener UDP pasó (Lap Data + Car Setup + Car Telemetry)")


if __name__ == '__main__':
    main()
