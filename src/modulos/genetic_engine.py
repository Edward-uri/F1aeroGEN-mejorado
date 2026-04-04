import random
from individual import Individual 

class GeneticEngine:
    def __init__(self, p_initial, p_max, p_cruza, p_mutacion):
        self.p_initial = p_initial
        self.p_max = p_max
        self.p_cruza = p_cruza
        self.p_mutacion = p_mutacion
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
                    padre1 = self.population[i]
                    padre2 = self.population[j]
                    pairs.append((padre1, padre2))
        return pairs

    def crossover(self, pairs):
        
        #Aplica Cruce Uniforme a las parejas generadas.
        #Por cada pareja, se generan 2 hijos intercambiando los genes individualmente.
        
        children = []
        
        for padre1, padre2 in pairs:
            # Diccionarios vacíos para los genes de los nuevos hijos
            genes_hijo1 = {}
            genes_hijo2 = {}
            
            # Recorremos cada uno de los 6 parámetros (aleron_delantero, camber, etc.)
            # padre1.genes.keys() nos da los nombres de las piezas
            for gen_nombre in padre1.genes.keys():
                
                # Lanzamos una moneda (50% de probabilidad)
                if random.choice([True, False]):
                    # El Hijo 1 toma la pieza del Padre 1, y el Hijo 2 la del Padre 2
                    genes_hijo1[gen_nombre] = padre1.genes[gen_nombre]
                    genes_hijo2[gen_nombre] = padre2.genes[gen_nombre]
                else:
                    # Se invierten los papeles
                    genes_hijo1[gen_nombre] = padre2.genes[gen_nombre]
                    genes_hijo2[gen_nombre] = padre1.genes[gen_nombre]
            
            # Instanciamos a los dos nuevos individuos pasándoles los genes creados
            # Nuestro constructor de Individual() acepta el parámetro 'genes'
            hijo1 = Individual(genes=genes_hijo1)
            hijo2 = Individual(genes=genes_hijo2)
            
            children.append(hijo1)
            children.append(hijo2)
            
        return children


# Pruebitas

if __name__ == "__main__":
    
    P_INITIAL = 5  
    P_MAX = 20
    P_CRUZA = 0.8  
    P_MUTACION = 0.1

    print("logs")
    
    motor = GeneticEngine(p_initial=P_INITIAL, p_max=P_MAX, p_cruza=P_CRUZA, p_mutacion=P_MUTACION)
    motor.create_population()
    
    print(f"\n[+] Población inicial creada con {P_INITIAL} individuos:")
    for i, ind in enumerate(motor.population):
        print(f" Individuo {i+1}: {ind.genes}")

    parejas = motor.generate_pairs()
    print(f"\n[+] Se formaron {len(parejas)} parejas listas para cruzarse.")
    
    #  PROBANDO LA CRUZA 
    hijos = motor.crossover(parejas)
    
    print(f"\n[+] Han nacido {len(hijos)} hijos de la cruza:")
    for i, hijo in enumerate(hijos):
        print(f"  Hijo {i+1}: {hijo.genes}")