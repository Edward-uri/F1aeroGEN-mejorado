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

#Pruebitas
if __name__ == "__main__":
    
    P_INITIAL = 10  
    P_MAX = 20
    P_CRUZA = 0.8  
    P_MUTACION = 0.1

    print("comenzandop")
    
    motor = GeneticEngine(p_initial=P_INITIAL, p_max=P_MAX, p_cruza=P_CRUZA, p_mutacion=P_MUTACION)
    motor.create_population()
    
    print(f"\n[+] Población inicial creada con {P_INITIAL} individuos:")
    for i, ind in enumerate(motor.population):
        print(f"  Individuo {i+1}: {ind.genes}")

    parejas = motor.generate_pairs()
    
    print(f"\n[+] Se formaron {len(parejas)} parejas listas para cruzarse:")