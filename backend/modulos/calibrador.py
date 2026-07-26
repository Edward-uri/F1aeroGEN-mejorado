"""Calibración del modelo físico contra vueltas reales capturadas por UDP.

Método (2 grados de libertad, uno por régimen del coche):
1. Velocidad punta: k = vmax_real / vmax_simulada (percentil 95 del trazo).
   Se aplica a la potencia (k³, porque vmax ~ P^(1/3)) y al tope del motor
   (k), preservando el trade-off de la relación de marchas en la escala nueva.
2. Agarre: bisección sobre el factor de e_curva hasta que el tiempo simulado
   con el setup capturado reproduce el tiempo real de la vuelta.

Los factores se guardan por pista en base_conocimiento/calibracion.json y
FitnessEvaluator los aplica automáticamente al crearse.
"""
import json
import os

from modulos.individual import LIMITES_GENES

RUTA_CALIBRACION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'base_conocimiento', 'calibracion.json')


def cargar_calibraciones(ruta=RUTA_CALIBRACION):
    try:
        with open(ruta) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def calibracion_de_pista(pista_id, ruta=RUTA_CALIBRACION):
    return cargar_calibraciones(ruta).get(str(pista_id))


def guardar_calibracion(pista_id, factores, ruta=RUTA_CALIBRACION):
    todas = cargar_calibraciones(ruta)
    todas[str(pista_id)] = factores
    with open(ruta, 'w') as f:
        json.dump(todas, f, indent=2)


def borrar_calibracion(pista_id, ruta=RUTA_CALIBRACION):
    todas = cargar_calibraciones(ruta)
    if todas.pop(str(pista_id), None) is None:
        return False
    with open(ruta, 'w') as f:
        json.dump(todas, f, indent=2)
    return True


def genes_desde_setup(setup):
    """Convierte el setup capturado del juego en un cromosoma válido del AG."""
    genes = dict(setup)
    genes.setdefault('relacion_marchas', 1.0)  # el juego no expone marchas
    for nombre, (minimo, maximo, tipo) in LIMITES_GENES.items():
        valor = genes.get(nombre, (minimo + maximo) / 2)
        valor = max(minimo, min(maximo, valor))
        genes[nombre] = int(round(valor)) if tipo is int else float(valor)
    return {nombre: genes[nombre] for nombre in LIMITES_GENES}


def calibrar_con_vuelta(evaluador, genes, trazo, tiempo_real):
    """Ajusta los factores CAL_* del evaluador para reproducir la vuelta real.

    El evaluador debe crearse con usar_calibracion=False (factores en 1.0);
    se modifica in situ. Devuelve (factores, métricas).
    """
    vmax_sim_antes = evaluador.calcular_vmax(genes)
    tiempo_sim_antes = evaluador.calcular_tiempo_vuelta(genes)

    # 1. Escala de velocidad punta (potencia y tope del motor)
    velocidades = sorted(v / 3.6 for _, v in trazo)  # km/h → m/s
    vmax_real = velocidades[int(len(velocidades) * 0.95)]
    k = max(0.5, min(2.5, vmax_real / vmax_sim_antes))
    evaluador.CAL_POTENCIA = k ** 3
    evaluador.CAL_TOPE = k

    # 2. Agarre por bisección: más agarre = curvas más rápidas = menos tiempo
    lo, hi = 0.2, 5.0
    for _ in range(40):
        evaluador.CAL_AGARRE = (lo + hi) / 2
        if evaluador.calcular_tiempo_vuelta(genes) > tiempo_real:
            lo = evaluador.CAL_AGARRE
        else:
            hi = evaluador.CAL_AGARRE
    evaluador.CAL_AGARRE = round((lo + hi) / 2, 4)
    evaluador.calibrado = True

    tiempo_sim_despues = evaluador.calcular_tiempo_vuelta(genes)
    factores = {
        'potencia': round(evaluador.CAL_POTENCIA, 4),
        'tope': round(evaluador.CAL_TOPE, 4),
        'agarre': evaluador.CAL_AGARRE,
        'tiempo_real_s': tiempo_real,
    }
    metricas = {
        'tiempo_sim_antes_s': round(tiempo_sim_antes, 2),
        'tiempo_sim_despues_s': round(tiempo_sim_despues, 2),
        'vmax_real_kmh': round(vmax_real * 3.6, 1),
        'vmax_sim_antes_kmh': round(vmax_sim_antes * 3.6, 1),
        'error_pct': round((tiempo_sim_despues - tiempo_real) / tiempo_real * 100, 2),
    }
    return factores, metricas
