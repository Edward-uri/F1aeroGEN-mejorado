"""Chequeo mínimo del motor genético. Uso:  cd backend && python test_smoke.py"""
import random

from modulos.genetic_engine import GeneticEngine
from modulos.fitness_evaluator import FitnessEvaluator
from modulos.individual import LIMITES_GENES, gen_creep
from modulos.stop_criterial import StopCriteria


def main():
    random.seed(42)
    evaluador = FitnessEvaluator(pista_id=1, coche_id=1, km_actual=0, compuesto_actual='Blando')
    motor = GeneticEngine(10, 30, 0.75, 0.30, 0.20)
    motor.create_population()
    for ind in motor.population:
        evaluador.evaluate(ind)

    mejores = []
    for _ in range(5):
        hijos = motor.mutate(motor.crossover(motor.generate_pairs()))
        motor.prune(hijos, evaluador)
        motor.population.sort(key=lambda x: x.fitness, reverse=True)
        mejores.append(motor.population[0].fitness)

    # La población respeta el límite máximo
    assert len(motor.population) <= 30, f"población excede p_max: {len(motor.population)}"

    # El elitismo garantiza que el mejor fitness nunca empeora
    assert all(b >= a for a, b in zip(mejores, mejores[1:])), f"el mejor fitness empeoró: {mejores}"
    assert mejores[-1] > 0, "el campeón no tiene fitness positivo"

    # Los genes del campeón respetan sus límites
    for nombre, (minimo, maximo, _tipo) in LIMITES_GENES.items():
        valor = motor.population[0].genes[nombre]
        assert minimo <= valor <= maximo, f"gen {nombre}={valor} fuera de [{minimo}, {maximo}]"

    # IDs inválidos fallan con mensaje claro, no con IndexError
    for kwargs in [dict(pista_id=999, coche_id=1), dict(pista_id=1, coche_id=999)]:
        try:
            FitnessEvaluator(km_actual=0, compuesto_actual='Blando', **kwargs)
            assert False, f"debió rechazar {kwargs}"
        except ValueError:
            pass

    # El criterio de paro converge tras N generaciones sin mejora
    paro = StopCriteria(paciencia=3)
    assert not paro.convergio(1.0)
    assert not paro.convergio(1.0)
    assert not paro.convergio(1.0)
    assert paro.convergio(1.0), "debió converger a la 3a generación sin mejora"

    # La mutación creep respeta límites y tipos
    for _ in range(200):
        for nombre, (minimo, maximo, tipo) in LIMITES_GENES.items():
            valor = gen_creep(nombre, minimo if random.random() < 0.5 else maximo)
            assert minimo <= valor <= maximo, f"creep de {nombre}={valor} fuera de rango"
            assert isinstance(valor, tipo), f"creep de {nombre} devolvió {type(valor).__name__}"

    # La interpolación aero distingue ángulos que antes colapsaban al mismo valor
    cd23, cl23 = evaluador._obtener_coeficientes_aero(23)
    cd27, cl27 = evaluador._obtener_coeficientes_aero(27)
    assert cd23 != cd27 and cl23 != cl27, "ángulos 23 y 27 deben tener coeficientes distintos"

    # --- Física de los genes nuevos (ningún gen muerto) ---
    from modulos.individual import Individual
    base = {
        "aleron_delantero": 25, "aleron_trasero": 25,
        "camber_frontal": -3.0, "camber_trasero": -1.5,
        "toe_frontal": 0.25, "toe_trasero": 0.25,
        "suspension_delantera": 21, "suspension_trasera": 21,
        "barra_antivuelco_delantera": 11, "barra_antivuelco_trasera": 11,
        "altura_delantera": 40, "altura_trasera": 42,
        "presion_delantera": 23.75, "presion_trasera": 21.75,
        "relacion_marchas": 1.0, "diferencial": 75, "reparto_frenada": 60,
    }

    # Restricción dura: altura < 32mm toca el suelo → fitness 0
    tocando = Individual(genes={**base, "altura_delantera": 30})
    assert evaluador.evaluate(tocando) == 0.0, "altura 30mm debió dar fitness 0"

    # Efecto suelo: coche más bajo (legal) genera más estabilidad
    e_bajo = evaluador.calcular_estabilidad({**base, "altura_delantera": 33, "altura_trasera": 33})
    e_alto = evaluador.calcular_estabilidad({**base, "altura_delantera": 48, "altura_trasera": 48})
    assert e_bajo > e_alto, "el efecto suelo debe premiar ir bajo"

    # Presiones bajas: más agarre pero menos velocidad punta
    bajas = {**base, "presion_delantera": 22.5, "presion_trasera": 20.5}
    altas = {**base, "presion_delantera": 25.0, "presion_trasera": 23.0}
    assert evaluador.calcular_estabilidad(bajas) > evaluador.calcular_estabilidad(altas)
    assert evaluador.calcular_vmax(bajas) < evaluador.calcular_vmax(altas)

    # Rugosidad: en Monza (lisa) gana suspensión dura, en Mónaco (rugosa) la blanda
    dura = {**base, "suspension_delantera": 41, "suspension_trasera": 41,
            "barra_antivuelco_delantera": 21, "barra_antivuelco_trasera": 21}
    blanda = {**base, "suspension_delantera": 1, "suspension_trasera": 1,
              "barra_antivuelco_delantera": 1, "barra_antivuelco_trasera": 1}
    ev_monza = evaluador  # pista_id=1 es Monza
    ev_monaco = FitnessEvaluator(pista_id=2, coche_id=1, km_actual=0, compuesto_actual='Blando')
    assert ev_monza._factor_suspension(dura) > ev_monza._factor_suspension(blanda)
    assert ev_monaco._factor_suspension(blanda) > ev_monaco._factor_suspension(dura)

    # Desbalance de barras antivuelco penaliza
    desbalanceada = {**base, "barra_antivuelco_delantera": 21, "barra_antivuelco_trasera": 1}
    assert ev_monza._factor_suspension(base) > ev_monza._factor_suspension(desbalanceada)

    # --- Física de la fase 2 (transmisión y frenos) ---
    # Relación corta: el tope del motor recorta la Vmax en un setup de poca ala
    poca_ala = {**base, "aleron_delantero": 5, "aleron_trasero": 5}
    assert evaluador.calcular_vmax({**poca_ala, "relacion_marchas": 1.15}) \
         < evaluador.calcular_vmax({**poca_ala, "relacion_marchas": 0.85}), \
        "la relación corta debe recortar la velocidad punta"

    # Diferencial bloqueado: subvira (menos estabilidad) pero acelera mejor
    assert evaluador.calcular_estabilidad({**base, "diferencial": 50}) \
         > evaluador.calcular_estabilidad({**base, "diferencial": 100})

    # Reparto de frenada lejos del ideal (58%) alarga la vuelta.
    # Se prueba en Mónaco: en Monza el setup base pasa las curvas a Vmax
    # y nunca frena, así que ahí el reparto (correctamente) no influye.
    assert ev_monaco.calcular_tiempo_vuelta({**base, "reparto_frenada": 58}) \
         < ev_monaco.calcular_tiempo_vuelta({**base, "reparto_frenada": 70})

    # El simulador recorre la pista completa y devuelve un trazo coherente
    t_lap, trazo = evaluador.simular_vuelta(base)
    assert t_lap > 0
    assert abs(trazo[-1][0] - (evaluador.d_rectas + evaluador.d_curvas)) < 1.0, \
        "el trazo debe cubrir la longitud total de la pista"
    assert all(v > 0 for _, v in trazo), "ninguna velocidad del trazo puede ser <= 0"

    # --- Calibración contra una vuelta "real" sintética ---
    from modulos import calibrador
    ev_cal = FitnessEvaluator(pista_id=5, coche_id=1, km_actual=0,
                              compuesto_actual='Blando', usar_calibracion=False)
    t_sim, trazo_sim = ev_cal.simular_vuelta(base)
    # "vuelta real": el mismo coche, 15% más rápido en el trazo y 10% en tiempo
    trazo_real = [(d, v * 3.6 * 1.15) for d, v in trazo_sim]  # a km/h, como el listener
    t_real = t_sim / 1.10
    factores, metricas = calibrador.calibrar_con_vuelta(ev_cal, base, trazo_real, t_real)
    assert 1.05 < factores['tope'] < 1.20, f"factor de tope fuera de rango: {factores['tope']}"
    assert abs(factores['potencia'] - factores['tope'] ** 3) < 0.01, "potencia debe ser tope³"
    assert abs(metricas['error_pct']) < 1.0, \
        f"tras calibrar, el tiempo simulado debe reproducir el real: {metricas}"

    # El setup del juego se convierte en cromosoma válido (clamp + marchas por defecto)
    genes_juego = calibrador.genes_desde_setup({'aleron_delantero': 0, 'camber_frontal': -5.0})
    assert genes_juego['aleron_delantero'] == 1 and genes_juego['camber_frontal'] == -3.5
    assert genes_juego['relacion_marchas'] == 1.0 and len(genes_juego) == len(LIMITES_GENES)

    # Persistencia: guardar / cargar / borrar en un archivo temporal
    import os
    import tempfile
    ruta_tmp = os.path.join(tempfile.gettempdir(), 'calibracion_test.json')
    calibrador.guardar_calibracion(5, factores, ruta=ruta_tmp)
    assert calibrador.calibracion_de_pista(5, ruta=ruta_tmp)['agarre'] == factores['agarre']
    assert calibrador.borrar_calibracion(5, ruta=ruta_tmp)
    assert calibrador.calibracion_de_pista(5, ruta=ruta_tmp) is None
    os.remove(ruta_tmp)

    # El método de selección original sigue disponible
    motor_todos = GeneticEngine(6, 10, 0.75, 0.30, 0.20, seleccion="todos")
    motor_todos.create_population()
    for ind in motor_todos.population:
        evaluador.evaluate(ind)
    motor_todos.prune(motor_todos.mutate(motor_todos.crossover(motor_todos.generate_pairs())), evaluador)
    assert motor_todos.population[0].fitness > 0

    print("OK: smoke test del motor genético pasó")


if __name__ == '__main__':
    main()
