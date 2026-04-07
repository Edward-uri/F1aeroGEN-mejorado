import csv
import matplotlib.pyplot as plt


from modulos.genetic_engine import GeneticEngine
from modulos.fitness_evaluator import FitnessEvaluator

def metodo_inicializacion():
    P_INITIAL = 10
    P_MAX = 30
    P_CRUZA = 0.75
    P_MUT_I = 0.30
    P_MUT_GEN = 0.20
    N_GENERACIONES = 25

    # Instanciamos nuestros objetos
    motor = GeneticEngine(P_INITIAL, P_MAX, P_CRUZA, P_MUT_I, P_MUT_GEN)
    evaluador = FitnessEvaluator(pista_id=1, coche_id=1, km_actual=0, compuesto_actual='Blando')
    
    if not evaluador.csv_cargados:
        print("Deteniendo ejecución por falta de Base de Conocimiento.")
        return

    motor.create_population()

    # Listas para la gráfica
    historial_mejor = []
    historial_peor = []
    historial_media = []

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

        # Guardar en CSV  
        with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([gen + 1, mejor_individuo.fitness, round(tiempo_vuelta, 3), mejor_individuo.genes])
        
        # Imprimir en consola los resultados de la generación
        print(f"Generación {gen + 1}:")
        print(f"  Mejor Fitness:  {mejor_individuo.fitness:.4f}")
        print(f"  Mejor Tiempo:   {tiempo_vuelta:.2f} s")
        print(f"  Velocidad Máx:  {(vmax * 3.6):.2f} km/h")  # m/s a km/h
        print(f"  Estabilidad:    {e_curva:.2f} Gs")
        print(f"  Setup Óptimo:   {mejor_individuo.genes}")
        print("-" * 50)

    # --- GRÁFICA DE RENDIMIENTO ---
    plt.figure(figsize=(12, 6))
    plt.plot(historial_mejor, label='Mejor Aptitud (Elitismo)', color='green', linewidth=2)
    plt.plot(historial_media, label='Media de la Población', color='blue', alpha=0.6)
    plt.plot(historial_peor, label='Peor Aptitud', color='red', linestyle='--')

    plt.title('Evolución de Setups de F1 (Maximización de Rendimiento)')
    plt.xlabel('Generaciones')
    plt.ylabel('Puntuación de Aptitud (Velocidad & Estabilidad / Tiempo)')
    plt.legend()
    plt.grid(True)
    
    print("\nEvolución terminada. Revisa la gráfica y el archivo CSV.")
    plt.show()

# Punto de entrada de la aplicación
if __name__ == "__main__":
    metodo_inicializacion()