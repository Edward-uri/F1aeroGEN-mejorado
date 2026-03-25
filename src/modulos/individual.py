import random

class Individual:
    
    def __init__(self, genes=None):
        if genes:
            self.genes = genes
        else:
            self.genes = self._generate_random_genes()
        
        self.fitness = 0.0

    def _generate_random_genes(self):
        """
        Genera los 6 genes iniciales respetando los límites mecánicos del contexto.
        """
        return {
            "aleron_delantero": random.randint(1, 50),         # x1: [1 a 50]
            "aleron_trasero": random.randint(1, 50),           # x2: [1 a 50]
            "barra_estabilizadora": random.randint(1, 21),     # x3: [1 a 21]
            "camber_frontal": round(random.uniform(-3.50, -2.50), 2), # x4: [-3.50 a -2.50]
            "toe_frontal": round(random.uniform(0.0, 0.50), 2),       # x5: [0.0 a 0.50]
            "altura_chasis": random.randint(1, 50)             # x6: [1 a 50]
        }

    def __str__(self):
        """
        Formato de impresión para que sea fácil leerlo en la consola.
        """
        return f"Individuo(Fitness: {self.fitness:.4f} | Setup: {self.genes})"