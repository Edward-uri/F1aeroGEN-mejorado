import random

# Límites físicos/reglamentarios de cada gen: (mínimo, máximo, tipo).
# Único lugar donde se definen los rangos: la generación aleatoria y la
# mutación leen de aquí, así que agregar un gen nuevo solo requiere una línea.
# Rangos tomados de la pantalla de setup del juego F1 25.
LIMITES_GENES = {
    # Aerodinámica
    "aleron_delantero":           (1, 50, int),
    "aleron_trasero":             (1, 50, int),
    # Geometría de suspensión
    "camber_frontal":             (-3.50, -2.50, float),
    "camber_trasero":             (-2.00, -1.00, float),
    "toe_frontal":                (0.0, 0.50, float),
    "toe_trasero":                (0.0, 0.50, float),
    # Suspensión
    "suspension_delantera":       (1, 41, int),
    "suspension_trasera":         (1, 41, int),
    "barra_antivuelco_delantera": (1, 21, int),
    "barra_antivuelco_trasera":   (1, 21, int),
    "altura_delantera":           (30, 50, int),   # mm; por debajo de 32 el coche toca el suelo
    "altura_trasera":             (30, 50, int),
    # Neumáticos
    "presion_delantera":          (22.5, 25.0, float),  # psi
    "presion_trasera":            (20.5, 23.0, float),  # psi
    # Transmisión y frenos
    "relacion_marchas":           (0.85, 1.15, float),  # >1 = marchas cortas: mejor aceleración, menor tope
    "diferencial":                (50, 100, int),        # % bloqueo en aceleración: tracción vs subviraje
    "reparto_frenada":            (50, 70, int),         # % de frenada al eje delantero
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
