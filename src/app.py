import csv

from modulos.genetic_engine import GeneticEngine
from modulos.fitness_evaluator import FitnessEvaluator
from modulos.visualizer import Visualizer

def metodo_inicializacion():
    P_INITIAL = 10
    P_MAX = 30
    P_CRUZA = 0.75
    P_MUT_I = 0.30
    P_MUT_GEN = 0.20
    N_GENERACIONES = 25

    # Instanciamos nuestros objetos
    motor = GeneticEngine(P_INITIAL, P_MAX, P_CRUZA, P_MUT_I, P_MUT_GEN)
    evaluador = FitnessEvaluator(pista_id=5, coche_id=1, km_actual=0, compuesto_actual='Blando')
    
    if not evaluador.csv_cargados:
        print("Deteniendo ejecución por falta de Base de Conocimiento.")
        return

    motor.create_population()

    # Listas para las gráficas
    historial_mejor = []
    historial_peor = []
    historial_media = []
    historial_vmax = []
    historial_ecurva = []
    historial_tlap = []

    # Preparar archivo CSV de reporte
    nombre_archivo = 'evolucion_setups_f1.csv'
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Generacion', 'Mejor_Fitness', 'Tiempo_Vuelta_Segundos', 'Mejor_Setup'])

    # --- IMPRESIÓN DE INICIO ---
    print("INICIANDO EVOLUCIÓN DE SETUPS F1...\n")
    print(f"Pista a evaluar: {evaluador.nombre_pista}")
    print(f"Densidad del aire: {evaluador.RHO} kg/m³")
    print(f"Desgaste actual: {evaluador.km_actual} km (Compuesto {evaluador.compuesto_actual})")
    print("-" * 50 + "\n")

    # --- CICLO EVOLUTIVO ---
    for gen in range(N_GENERACIONES):
        parejas = motor.generate_pairs()
        hijos = motor.crossover(parejas)
        hijos_mutados = motor.mutate(hijos)
        
        # Poda y evaluación
        motor.prune(hijos_mutados, evaluador)

        # Extraemos métricas y ordenamos
        motor.population.sort(key=lambda x: x.fitness, reverse=True)
        
        mejor_individuo = motor.population[0]
        peor_individuo = motor.population[-1]
        
        todos_los_fitness = [ind.fitness for ind in motor.population]
        media_fit = sum(todos_los_fitness) / len(todos_los_fitness)

        historial_mejor.append(mejor_individuo.fitness)
        historial_peor.append(peor_individuo.fitness)
        historial_media.append(media_fit)

        # Calculamos métricas reales para el print y el CSV
        vmax = evaluador.calcular_vmax(mejor_individuo.genes)
        e_curva = evaluador.calcular_estabilidad(mejor_individuo.genes)
        tiempo_vuelta = evaluador.calcular_tiempo_vuelta(vmax, e_curva)

        historial_vmax.append(vmax)
        historial_ecurva.append(e_curva)
        historial_tlap.append(tiempo_vuelta)

        # Guardar en CSV  
        with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([gen + 1, mejor_individuo.fitness, round(tiempo_vuelta, 3), mejor_individuo.genes])
        
        # Imprimir en consola los resultados de la generación
        print(f"Generación {gen + 1}:")
        print(f"  Mejor Fitness:  {mejor_individuo.fitness:.4f}")
        print(f"  Mejor Tiempo:   {tiempo_vuelta:.2f} s")
        print(f"  Velocidad Máx:  {(vmax * 3.6):.2f} km/h")
        print(f"  Estabilidad:    {e_curva:.2f} Gs")
        print(f"  Setup Óptimo:   {mejor_individuo.genes}")
        print("-" * 50)

    print("\n[V] Evolución terminada. Resultados guardados en el CSV.")
    
    # --- MOSTRAR LAS 4 GRÁFICAS DEL PROYECTO ---
    print("\nGenerando Gráficas de Resultados (cierra una ventana para ver la siguiente)...")
    
    # 1. Gráfica de evolución de las variables de optimización (Vmax, Ecurva, Tlap)
    Visualizer.plot_evolucion_variables(historial_vmax, historial_ecurva, historial_tlap)
    
    # 2. Gráfica de evolución de la aptitud (Fitness)
    Visualizer.plot_convergencia(historial_mejor, historial_media, historial_peor)

    # 3. Telemetría Simulada: Velocidad vs Distancia (Base vs AG)
    genes_base = {
        "aleron_delantero": 25, "aleron_trasero": 25,
        "barra_estabilizadora": 10, "camber_frontal": -3.0,
        "toe_frontal": 0.25, "altura_chasis": 25
    }
    Visualizer.plot_telemetria_simulada(
        evaluador, genes_base, mejor_individuo.genes,
        nombre_pista=evaluador.nombre_pista
    )

    # 4. Mapa de Calor de Carga Aerodinámica 
    Visualizer.plot_mapa_calor_aero(evaluador, mejor_individuo.genes)


# Punto de entrada de la aplicación
if __name__ == "__main__":
    metodo_inicializacion()