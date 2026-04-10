from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os

from modulos.genetic_engine import GeneticEngine
from modulos.fitness_evaluator import FitnessEvaluator
from modulos.visualizer import Visualizer

app = FastAPI(title="F1AeroGen API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base_conocimiento')


# ─── Modelos ───
class EvolucionRequest(BaseModel):
    pista_id: int = 5
    coche_id: int = 1
    km_actual: int = 0
    compuesto: str = "Blando"
    p_initial: int = 10
    p_max: int = 30
    p_cruza: float = 0.75
    p_mut_i: float = 0.30
    p_mut_gen: float = 0.20
    n_generaciones: int = 25


# ─── Endpoints ───

@app.get("/api/pistas")
def get_pistas():
    df = pd.read_csv(os.path.join(BC_DIR, 'catalog_circuitos.csv'))
    pistas = []
    for _, row in df.iterrows():
        pistas.append({
            "id": int(row['ID_Pista']),
            "nombre": row['Nombre_Pista'],
            "rectas": int(row['Longitud_Rectas_m']),
            "curvas": int(row['Longitud_Curvas_m']),
            "radio_curva": int(row['Radio_Curva_Promedio_m']),
            "densidad": float(row['Densidad_Aire_kg_m3']),
            "altitud": int(row['Altitud_m']),
        })
    return pistas


@app.get("/api/coches")
def get_coches():
    df = pd.read_csv(os.path.join(BC_DIR, 'config_coche.csv'))
    coches = []
    for _, row in df.iterrows():
        coches.append({
            "id": int(row['ID_Coche']),
            "categoria": row['Categoria'],
            "potencia_hp": round(float(row['Potencia_W']) / 745.7),
            "peso_kg": round(float(row['Peso_N']) / 9.81),
            "area_frontal": float(row['Area_Frontal_m2']),
        })
    return coches


@app.post("/api/evolucionar")
def evolucionar(req: EvolucionRequest):
    motor = GeneticEngine(req.p_initial, req.p_max, req.p_cruza, req.p_mut_i, req.p_mut_gen)
    evaluador = FitnessEvaluator(
        pista_id=req.pista_id, coche_id=req.coche_id,
        km_actual=req.km_actual, compuesto_actual=req.compuesto
    )

    if not evaluador.csv_cargados:
        return {"error": "No se pudieron cargar los CSVs de la base de conocimiento."}

    motor.create_population()

    historial_mejor, historial_peor, historial_media = [], [], []
    historial_vmax, historial_ecurva, historial_tlap = [], [], []
    log_generaciones = []

    for gen in range(req.n_generaciones):
        parejas = motor.generate_pairs()
        hijos = motor.crossover(parejas)
        hijos_mutados = motor.mutate(hijos)
        motor.prune(hijos_mutados, evaluador)
        motor.population.sort(key=lambda x: x.fitness, reverse=True)

        mejor = motor.population[0]
        peor = motor.population[-1]
        todos = [ind.fitness for ind in motor.population]
        media = sum(todos) / len(todos)

        historial_mejor.append(mejor.fitness)
        historial_peor.append(peor.fitness)
        historial_media.append(media)

        vmax = evaluador.calcular_vmax(mejor.genes)
        e_curva = evaluador.calcular_estabilidad(mejor.genes)
        t_vuelta = evaluador.calcular_tiempo_vuelta(vmax, e_curva)

        historial_vmax.append(vmax)
        historial_ecurva.append(e_curva)
        historial_tlap.append(t_vuelta)

        log_generaciones.append({
            "gen": gen + 1,
            "fitness": round(mejor.fitness, 4),
            "tiempo": round(t_vuelta, 2),
            "vmax_kmh": round(vmax * 3.6, 2),
            "estabilidad": round(e_curva, 2),
        })

    # Mejor individuo final
    campeon = motor.population[0]
    vmax_f = evaluador.calcular_vmax(campeon.genes)
    ecurva_f = evaluador.calcular_estabilidad(campeon.genes)
    tlap_f = evaluador.calcular_tiempo_vuelta(vmax_f, ecurva_f)

    # Config base para comparar
    genes_base = {
        "aleron_delantero": 25, "aleron_trasero": 25,
        "barra_estabilizadora": 10, "camber_frontal": -3.0,
        "toe_frontal": 0.25, "altura_chasis": 25
    }
    from modulos.individual import Individual
    ind_base = Individual(genes=genes_base.copy())
    evaluador.evaluate(ind_base)
    vmax_base = evaluador.calcular_vmax(genes_base)
    ecurva_base = evaluador.calcular_estabilidad(genes_base)
    tlap_base = evaluador.calcular_tiempo_vuelta(vmax_base, ecurva_base)

    # Generar las 4 gráficas como base64
    graficas = {
        "variables": Visualizer.plot_evolucion_variables(historial_vmax, historial_ecurva, historial_tlap),
        "aptitud": Visualizer.plot_convergencia(historial_mejor, historial_media, historial_peor),
        "telemetria": Visualizer.plot_telemetria_simulada(evaluador, genes_base, campeon.genes, evaluador.nombre_pista),
        "mapa_calor": Visualizer.plot_mapa_calor_aero(evaluador, campeon.genes),
    }

    return {
        "mejor_individuo": campeon.genes,
        "fitness": round(campeon.fitness, 4),
        "tiempo_vuelta": round(tlap_f, 2),
        "vmax_kmh": round(vmax_f * 3.6, 2),
        "estabilidad": round(ecurva_f, 2),
        "config_base": {
            "fitness": round(ind_base.fitness, 4),
            "tiempo_vuelta": round(tlap_base, 2),
            "vmax_kmh": round(vmax_base * 3.6, 2),
            "estabilidad": round(ecurva_base, 2),
        },
        "log": log_generaciones,
        "graficas": graficas,
        "nombre_pista": evaluador.nombre_pista,
    }
