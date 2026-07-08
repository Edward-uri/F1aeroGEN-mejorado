class StopCriteria:
    """Criterio de paro por convergencia: detiene el AG si el mejor fitness
    no mejora durante `paciencia` generaciones seguidas.

    Con paciencia=0 se desactiva y el AG corre todas las generaciones máximas.
    """

    def __init__(self, paciencia=10, tolerancia=1e-6):
        self.paciencia = paciencia
        self.tolerancia = tolerancia
        self.mejor_fitness = float('-inf')
        self.generaciones_sin_mejora = 0

    def convergio(self, fitness_actual):
        """Registra el mejor fitness de la generación y devuelve True si hay que parar."""
        if fitness_actual > self.mejor_fitness + self.tolerancia:
            self.mejor_fitness = fitness_actual
            self.generaciones_sin_mejora = 0
        else:
            self.generaciones_sin_mejora += 1

        return self.paciencia > 0 and self.generaciones_sin_mejora >= self.paciencia
