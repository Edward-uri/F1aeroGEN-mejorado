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
