import random

# Límites físicos/reglamentarios de cada gen: (mínimo, máximo, tipo).
# Único lugar donde se definen los rangos: la generación aleatoria y la
# mutación leen de aquí, así que agregar un gen nuevo solo requiere una línea.
LIMITES_GENES = {
    "aleron_delantero":     (1, 50, int),
    "aleron_trasero":       (1, 50, int),
    "barra_estabilizadora": (1, 21, int),
    "camber_frontal":       (-3.50, -2.50, float),
    "toe_frontal":          (0.0, 0.50, float),
    "altura_chasis":        (1, 50, int),
}


def gen_aleatorio(nombre):
    """Genera un valor aleatorio válido para el gen, respetando su rango y tipo."""
    minimo, maximo, tipo = LIMITES_GENES[nombre]
    if tipo is int:
        return random.randint(minimo, maximo)
    return round(random.uniform(minimo, maximo), 2)


def gen_creep(nombre, valor_actual):
    """Mutación creep: perturba el valor actual hasta ±10% del rango del gen.

    A diferencia del reinicio aleatorio (salto exploratorio), el creep hace
    ajuste fino alrededor de un valor que ya funciona (explotación local).
    """
    minimo, maximo, tipo = LIMITES_GENES[nombre]
    delta = (maximo - minimo) * 0.10
    nuevo = valor_actual + random.uniform(-delta, delta)
    nuevo = max(minimo, min(maximo, nuevo))  # se recorta a los límites del gen
    if tipo is int:
        return int(round(nuevo))
    return round(nuevo, 2)


class Individual:

    def __init__(self, genes=None):
        if genes:
            self.genes = genes
        else:
            self.genes = {nombre: gen_aleatorio(nombre) for nombre in LIMITES_GENES}

        self.fitness = 0.0

    def __str__(self):
        return f"Individuo(Fitness: {self.fitness:.4f} | Setup: {self.genes})"
