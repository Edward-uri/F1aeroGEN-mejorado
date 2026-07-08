import random
from modulos.individual import Individual, gen_aleatorio

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
                        # Reinicio Aleatorio Limitado dentro de los límites del gen
                        ind.genes[gen_nombre] = gen_aleatorio(gen_nombre)
        return children

    def prune(self, children, evaluator):
        
        # 1. Unimos la población actual y los nuevos hijos
        full_population = self.population + children

        # 2. Evaluamos solo a los individuos nuevos: los padres conservan su fitness
        # ponytail: fitness 0.0 = sin evaluar; los individuos "chocados" se re-evalúan, es idempotente
        for ind in full_population:
            if ind.fitness == 0.0:
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


