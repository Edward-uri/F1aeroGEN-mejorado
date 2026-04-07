import random
import csv
import matplotlib.pyplot as plt
from individual import Individual 
from fitness_evaluator import FitnessEvaluator

class GeneticEngine:
    def __init__(self, p_initial, p_max, p_cruza, p_mut_i, p_mut_gen):
        self.p_initial = p_initial
        self.p_max = p_max
        self.p_cruza = p_cruza
        self.p_mut_i = p_mut_i
        self.p_mut_gen = p_mut_gen
        self.population = [] 

    def create_population(self):
        for _ in range(self.p_initial):
            nuevo_individuo = Individual() 
            self.population.append(nuevo_individuo)
    
    def generate_pairs(self):
        pairs = []
        for i in range(len(self.population)):
            for j in range(i + 1, len(self.population)):
                if random.random() <= self.p_cruza:
                    pairs.append((self.population[i], self.population[j]))
        return pairs

    def crossover(self, pairs):
        children = []
        for padre1, padre2 in pairs:
            genes_hijo1, genes_hijo2 = {}, {}
            for gen_nombre in padre1.genes.keys():
                if random.choice([True, False]):
                    genes_hijo1[gen_nombre] = padre1.genes[gen_nombre]
                    genes_hijo2[gen_nombre] = padre2.genes[gen_nombre]
                else:
                    genes_hijo1[gen_nombre] = padre2.genes[gen_nombre]
                    genes_hijo2[gen_nombre] = padre1.genes[gen_nombre]
            
            children.append(Individual(genes=genes_hijo1))
            children.append(Individual(genes=genes_hijo2))
        return children

    def mutate(self, children):
        for ind in children:
            if random.random() <= self.p_mut_i:
                for gen_nombre in ind.genes.keys():
                    if random.random() <= self.p_mut_gen:
                        # Reinicio Aleatorio Limitado
                        if gen_nombre == "aleron_delantero" or gen_nombre == "aleron_trasero":
                            ind.genes[gen_nombre] = random.randint(1, 50)
                        elif gen_nombre == "barra_estabilizadora":
                            ind.genes[gen_nombre] = random.randint(1, 21)
                        elif gen_nombre == "camber_frontal":
                            ind.genes[gen_nombre] = round(random.uniform(-3.50, -2.50), 2)
                        elif gen_nombre == "toe_frontal":
                            ind.genes[gen_nombre] = round(random.uniform(0.0, 0.50), 2)
                        elif gen_nombre == "altura_chasis":
                            ind.genes[gen_nombre] = random.randint(1, 50)
        return children

    def prune(self, children, evaluator):
        
        # 1. Unimos la población actual y los nuevos hijos
        full_population = self.population + children

        # 2. Evaluamos físicamente a todos los individuos
        for ind in full_population:
            evaluator.evaluate(ind)

        # 3. Ordenamos de MAYOR a MENOR aptitud (queremos maximizar el fitness)
        full_population.sort(key=lambda x: x.fitness, reverse=True)

        # 4. ELITISMO: Rescatamos al campeón indiscutible
        next_generation = [full_population.pop(0)]

        # 5. Dividimos a los perdedores en 3 particiones de calidad
        n = len(full_population)
        if n > 0:
            part1 = full_population[: n // 3]
            part2 = full_population[n // 3 : (2 * n) // 3]
            part3 = full_population[(2 * n) // 3 :]
            partitions = [part1, part2, part3]

            # 6. Llenamos los espacios restantes hasta P_MAX
            while len(next_generation) < self.p_max:
                available = [p for p in partitions if p]
                if not available:
                    break
                
                chosen_partition = random.choice(available)
                idx = random.randint(0, len(chosen_partition) - 1)
                # Lo sacamos de la partición y lo metemos a la nueva generación
                next_generation.append(chosen_partition.pop(idx))

        self.population = next_generation
        return self.population


def main():
    P_INITIAL = 10
    P_MAX = 30
    P_CRUZA = 0.75
    P_MUT_I = 0.30
    P_MUT_GEN = 0.20
    N_GENERACIONES = 25

    motor = GeneticEngine(P_INITIAL, P_MAX, P_CRUZA, P_MUT_I, P_MUT_GEN)
    evaluador = FitnessEvaluator(pista_id=1,coche_id=1, km_actual=0, compuesto_actual='Blando')
    
    if not evaluador.csv_cargados:
        print("Deteniendo ejecución por falta de Base de Conocimiento.")
        return

    motor.create_population()

    # 2. Listas para la gráfica
    historial_mejor = []
    historial_peor = []
    historial_media = []

    # 3. Preparar archivo CSV de reporte
    nombre_archivo = 'evolucion_setups_f1.csv'
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Generacion', 'Mejor_Fitness', 'Tiempo_Vuelta_Segundos', 'Mejor_Setup'])

    print("INICIANDO EVOLUCIÓN DE SETUPS F1...\n")
    print(f" Pista a evaluar: {evaluador.nombre_pista}")

    # --- CICLO EVOLUTIVO ---
    for gen in range(N_GENERACIONES):
        parejas = motor.generate_pairs()
        hijos = motor.crossover(parejas)
        hijos_mutados = motor.mutate(hijos)
        
        # Poda y evaluación
        motor.prune(hijos_mutados, evaluador)

        # Extraemos métricas (la población ya está ordenada por la poda)
        # OJO: La población la ordenamos internamente en el prune, pero debemos 
        # re-ordenar por si las dudas (el orden se altera al añadir de las particiones)
        motor.population.sort(key=lambda x: x.fitness, reverse=True)
        
        mejor_individuo = motor.population[0]
        peor_individuo = motor.population[-1]
        
        todos_los_fitness = [ind.fitness for ind in motor.population]
        media_fit = sum(todos_los_fitness) / len(todos_los_fitness)

        historial_mejor.append(mejor_individuo.fitness)
        historial_peor.append(peor_individuo.fitness)
        historial_media.append(media_fit)

        # Calculamos el tiempo de vuelta real para el print y el CSV
        vmax = evaluador.calcular_vmax(mejor_individuo.genes)
        e_curva = evaluador.calcular_estabilidad(mejor_individuo.genes)
        tiempo_vuelta = evaluador.calcular_tiempo_vuelta(vmax, e_curva)

        # Guardar en CSV  
        with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([gen + 1, mejor_individuo.fitness, round(tiempo_vuelta, 3), mejor_individuo.genes])
        
        print(f"Generación {gen + 1}:")
        print(f"  Mejor Fitness:  {mejor_individuo.fitness:.4f}")
        print(f"  Mejor Tiempo:   {tiempo_vuelta:.2f} s")
        print(f"  Velocidad Máx:  {(vmax * 3.6):.2f} km/h")  # Convertido de m/s a km/h
        print(f"  Estabilidad:    {e_curva:.2f} Gs")        # Fuerzas G soportadas
        print(f"  Setup Óptimo:   {mejor_individuo.genes}")
        print("-" * 50)

    # --- GRÁFICA DE RENDIMIENTO ---
    plt.figure(figsize=(12, 6))
    # Aquí buscamos MAXIMIZAR la aptitud
    plt.plot(historial_mejor, label='Mejor Aptitud (Elitismo)', color='green', linewidth=2)
    plt.plot(historial_media, label='Media de la Población', color='blue', alpha=0.6)
    plt.plot(historial_peor, label='Peor Aptitud', color='red', linestyle='--')

    plt.title('Evolución de Setups de F1 (Maximización de Rendimiento)')
    plt.xlabel('Generaciones')
    plt.ylabel('Puntuación de Aptitud (Velocidad & Estabilidad / Tiempo)')
    plt.legend()
    plt.grid(True)
    
    print("\n Evolución terminada. Revisa la gráfica y el archivo CSV.")
    plt.show()

if __name__ == "__main__":
    main()