import math
import numpy as np
import pandas as pd
import os

# Carpeta de la base de conocimiento, resuelta desde la raíz del backend
BC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'base_conocimiento')

# Velocidad tope del motor (m/s) con relación de marchas 1.0; una relación
# corta (>1) recorta este tope a cambio de mejor aceleración.
# ponytail: calibrado para que el recorte muerda en setups de poca ala
# (vmax aero ~63-68 m/s); si se cambia la potencia del coche, recalibrar.
V_TOPE_MOTOR = 72.0

# El radio promedio del CSV sobreestima la velocidad de paso por curva real
# (chicanes y horquillas van mucho más lento que la curva "promedio")
FACTOR_APEX = 0.85


class FitnessEvaluator:
    def __init__(self, pista_id, coche_id, km_actual, compuesto_actual):

        # Variables de estado de la simulación
        self.km_actual = km_actual
        self.compuesto_actual = compuesto_actual

        self.df_circuitos = pd.read_csv(os.path.join(BC_DIR, 'catalog_circuitos.csv'))
        self.df_aero = pd.read_csv(os.path.join(BC_DIR, 'perfiles_aero.csv'))
        self.df_llantas = pd.read_csv(os.path.join(BC_DIR, 'deg_neumaticos.csv'))
        self.df_coche = pd.read_csv(os.path.join(BC_DIR, 'config_coche.csv'))

        # --- 1. EXTRAER DATOS DEL COCHE ---
        coches = self.df_coche[self.df_coche['ID_Coche'] == coche_id]
        if coches.empty:
            raise ValueError(f"El coche con ID {coche_id} no existe en config_coche.csv")
        coche = coches.iloc[0]
        self.P = coche['Potencia_W']
        self.A = coche['Area_Frontal_m2']
        self.PESO = coche['Peso_N']
        self.GRAVEDAD = coche['Gravedad_m_s2']
        self.CD_BASE = coche['Cd_Base']
        self.CL_BASE = coche['Cl_Base']
        self.V_REF_CURVA = coche['V_Ref_Curva_m_s']

        # --- 2. EXTRAER DATOS DE LA PISTA ---
        pistas = self.df_circuitos[self.df_circuitos['ID_Pista'] == pista_id]
        if pistas.empty:
            raise ValueError(f"La pista con ID {pista_id} no existe en catalog_circuitos.csv")
        pista = pistas.iloc[0]
        self.nombre_pista = pista['Nombre_Pista']
        self.d_rectas = pista['Longitud_Rectas_m']
        self.d_curvas = pista['Longitud_Curvas_m']
        self.r_curva = pista['Radio_Curva_Promedio_m']
        self.RUGOSIDAD = pista['Rugosidad_Asfalto']  # 0.85 (lisa) a 1.20 (rugosa)

        # se inyecta la densidad del aire según la altitud del circuito!
        self.RHO = pista['Densidad_Aire_kg_m3']

        # La vuelta se modela como n_pares segmentos (recta + curva). El número
        # de curvas se estima de la longitud total de curva y el radio promedio
        # (arco de ~90° por curva): Mónaco ≈ 20 curvas, Monza ≈ 8.
        self.n_pares = max(3, min(20, round(self.d_curvas / (self.r_curva * math.pi / 2))))
        self.long_recta_seg = self.d_rectas / self.n_pares
        self.long_curva_seg = self.d_curvas / self.n_pares

        # --- 3. VALIDAR COMPUESTO DE NEUMÁTICO ---
        if compuesto_actual not in self.df_llantas['Compuesto_Neumatico'].values:
            disponibles = ', '.join(self.df_llantas['Compuesto_Neumatico'].unique())
            raise ValueError(f"Compuesto '{compuesto_actual}' no existe. Disponibles: {disponibles}")

        # --- 4. TABLAS PARA INTERPOLACIÓN ---
        # El CSV de aero va en pasos de ~5° pero los genes son enteros 1-50:
        # interpolar hace que cada grado tenga coeficientes distintos (sin
        # interpolación, ángulos vecinos colapsan al mismo valor y el fitness
        # se llena de mesetas que estancan la convergencia).
        df_aero_ord = self.df_aero.sort_values('Angulo_Aleron_Grados')
        self._aero_angulos = df_aero_ord['Angulo_Aleron_Grados'].to_numpy(dtype=float)
        self._aero_cd = df_aero_ord['Coeficiente_Drag_Cd'].to_numpy(dtype=float)
        self._aero_cl = df_aero_ord['Coeficiente_Downforce_Cl'].to_numpy(dtype=float)

        df_llanta = self.df_llantas[self.df_llantas['Compuesto_Neumatico'] == compuesto_actual].sort_values('Kilometro')
        self._llanta_km = df_llanta['Kilometro'].to_numpy(dtype=float)
        self._llanta_mu = df_llanta['Coeficiente_Friccion_Mu'].to_numpy(dtype=float)

    def _obtener_coeficientes_aero(self, angulo):
        """Interpola los coeficientes aerodinámicos para un ángulo de alerón."""
        cd = np.interp(angulo, self._aero_angulos, self._aero_cd)
        cl = np.interp(angulo, self._aero_angulos, self._aero_cl)
        return cd, cl

    def _obtener_friccion_llanta(self, genes):
        """Interpola la fricción base según el desgaste y le suma camber y presiones."""
        mu_base_llanta = np.interp(self.km_actual, self._llanta_km, self._llanta_mu)

        # El camber negativo mejora el agarre lateral en ambos ejes
        mu_real = mu_base_llanta + (0.05 * abs(genes['camber_frontal'])) \
                                 + (0.05 * abs(genes['camber_trasero']))

        # Presión baja = mayor huella de contacto = más agarre (a cambio de
        # más resistencia a la rodadura, que se cobra en calcular_vmax)
        mu_real += 0.02 * ((25.0 - genes['presion_delantera']) + (23.0 - genes['presion_trasera']))
        return mu_real

    def _carga_aero_suelo(self, genes):
        """Cl extra por efecto suelo y rake (alturas del chasis)."""
        # Efecto suelo: cuanto más bajo el coche, más carga genera el difusor
        altura_promedio = (genes['altura_delantera'] + genes['altura_trasera']) / 2.0
        cl_suelo = 0.8 * (50 - altura_promedio) / 20.0  # 0 a 50mm, 0.8 a 30mm

        # Rake positivo (trasera más alta) inclina el difusor y suma carga;
        # rake negativo (nariz arriba) la pierde
        rake = genes['altura_trasera'] - genes['altura_delantera']
        cl_rake = 0.02 * rake
        return cl_suelo + cl_rake

    def _factor_suspension(self, genes):
        """Factor de agarre [<=1] según rigidez de suspensión/barras vs rugosidad.

        Pista lisa (Monza, 0.85) premia suspensión dura; pista rugosa
        (Mónaco, 1.20) premia suspensión blanda que absorba los baches.
        El desbalance entre barras antivuelco genera sub/sobreviraje.
        """
        rigidez = ((genes['suspension_delantera'] - 1) / 40.0
                   + (genes['suspension_trasera'] - 1) / 40.0
                   + (genes['barra_antivuelco_delantera'] - 1) / 20.0
                   + (genes['barra_antivuelco_trasera'] - 1) / 20.0) / 4.0

        rigidez_ideal = 1.0 - (self.RUGOSIDAD - 0.85) / 0.35
        rigidez_ideal = min(1.0, max(0.0, rigidez_ideal))

        desbalance_barras = abs((genes['barra_antivuelco_delantera'] - 1) / 20.0
                                - (genes['barra_antivuelco_trasera'] - 1) / 20.0)

        # hasta -12% de agarre por rigidez equivocada, hasta -5% por desbalance
        return 1.0 - 0.12 * abs(rigidez - rigidez_ideal) - 0.05 * desbalance_barras

    def _cd_total(self, genes):
        """Coeficiente de arrastre total del setup."""
        cd_delantero, _ = self._obtener_coeficientes_aero(genes['aleron_delantero'])
        cd_trasero, _ = self._obtener_coeficientes_aero(genes['aleron_trasero'])

        # Chasis + Alerones + arrastre por Toe en ambos ejes
        cd_total = self.CD_BASE + cd_delantero + cd_trasero \
            + 0.1 * (genes['toe_frontal'] + genes['toe_trasero'])

        # El rake positivo genera carga extra pero también arrastre
        rake = genes['altura_trasera'] - genes['altura_delantera']
        cd_total += 0.01 * max(0, rake)

        # Presión baja = más resistencia a la rodadura
        cd_total += 0.03 * ((25.0 - genes['presion_delantera']) + (23.0 - genes['presion_trasera']))
        return cd_total

    def _potencia_efectiva(self, genes):
        """Marchas cortas mantienen el motor en su banda de potencia (hasta +10%)."""
        return self.P * (0.90 + 0.10 * (genes['relacion_marchas'] - 0.85) / 0.30)

    def calcular_vmax(self, genes):
        # Equilibrio aerodinámico: Vmax = raíz_cúbica( 2*P / (rho * A * Cd) )
        p_ef = self._potencia_efectiva(genes)
        v_aero = math.pow((2 * p_ef) / (self.RHO * self.A * self._cd_total(genes)), 1.0/3.0)

        # Tope por régimen del motor: la relación corta corta la velocidad final
        v_tope = V_TOPE_MOTOR / genes['relacion_marchas']
        return min(v_aero, v_tope)

    def calcular_estabilidad(self, genes):
        _, cl_delantero = self._obtener_coeficientes_aero(genes['aleron_delantero'])
        _, cl_trasero = self._obtener_coeficientes_aero(genes['aleron_trasero'])

        cl_total = self.CL_BASE + cl_delantero + cl_trasero + self._carga_aero_suelo(genes)

        # Carga aerodinámica (L) = 0.5 * rho * V^2 * A * Cl
        L = 0.5 * self.RHO * (self.V_REF_CURVA**2) * self.A * cl_total

        # Fricción real: desgaste + camber + presiones, ajustada por la
        # afinación de suspensión contra la rugosidad de la pista
        mu = self._obtener_friccion_llanta(genes) * self._factor_suspension(genes)

        # E_curva = mu * (Peso + L) / Peso
        e_curva = (mu * (self.PESO + L)) / self.PESO

        # Diferencial muy bloqueado = subviraje a mitad de curva (hasta -6%);
        # su recompensa es la tracción a la salida (ver simular_vuelta)
        e_curva *= 1.0 - 0.06 * (genes['diferencial'] - 50) / 50.0
        return e_curva

    def simular_vuelta(self, genes, dx=5.0):
        """Simula la vuelta segmento a segmento con aceleración y frenado.

        En cada recta el coche sale de la curva anterior, acelera (limitado por
        motor, tracción del diferencial y arrastre) y frena al final para entrar
        a la siguiente curva. Devuelve (t_lap, trazo) donde trazo es una lista
        de puntos (distancia_m, velocidad_ms) para graficar telemetría.
        """
        m = self.PESO / self.GRAVEDAD
        vmax = self.calcular_vmax(genes)
        e_curva = self.calcular_estabilidad(genes)
        v_curva = min(FACTOR_APEX * math.sqrt(e_curva * self.GRAVEDAD * self.r_curva), vmax)

        # Frenada: la capacidad de agarre total frena el coche; un reparto
        # lejos del ideal (58% delantero) desperdicia parte de esa capacidad
        eficiencia_reparto = 1.0 - 0.01 * abs(genes['reparto_frenada'] - 58)
        a_freno = e_curva * self.GRAVEDAD * eficiencia_reparto

        # Tracción a la salida de curva: el diferencial abierto patina (menos
        # aceleración disponible), el bloqueado transmite todo el par
        mu = self._obtener_friccion_llanta(genes) * self._factor_suspension(genes)
        a_traccion = mu * self.GRAVEDAD * (0.55 + 0.45 * (genes['diferencial'] - 50) / 50.0)

        p_ef = self._potencia_efectiva(genes)
        cd_total = self._cd_total(genes)

        t_total, dist = 0.0, 0.0
        trazo = [(0.0, v_curva)]

        for _ in range(self.n_pares):
            # ── Recta: acelerar y frenar al final ──
            D, v, x = self.long_recta_seg, v_curva, 0.0
            while x < D:
                # ¿ya hay que frenar para llegar a v_curva al final?
                d_freno = (v*v - v_curva*v_curva) / (2 * a_freno) if v > v_curva else 0.0
                if D - x <= d_freno:
                    break
                a_motor = p_ef / (m * v)
                a_drag = 0.5 * self.RHO * self.A * cd_total * v * v / m
                a = min(a_motor, a_traccion) - a_drag
                paso = min(dx, D - x)
                v = min(math.sqrt(max(v*v + 2*a*paso, 1.0)), vmax)
                t_total += paso / v
                x += paso
                trazo.append((dist + x, v))
            if v > v_curva:
                # ponytail: el tramo final se aproxima como frenada pura (error O(dx))
                t_total += (v - v_curva) / a_freno + max(0.0, (D - x) - d_freno) / v
                trazo.append((dist + D, v_curva))
            dist += D

            # ── Curva: velocidad constante al límite de agarre ──
            t_total += self.long_curva_seg / v_curva
            dist += self.long_curva_seg
            trazo.append((dist, v_curva))

        return t_total, trazo

    def calcular_tiempo_vuelta(self, genes):
        return self.simular_vuelta(genes)[0]

    def evaluate(self, individual):

        genes = individual.genes

        # Restricción dura: por debajo de 32mm el fondo plano toca el asfalto
        # a alta velocidad (el efecto suelo premia ir bajo, esto pone el límite)
        if min(genes['altura_delantera'], genes['altura_trasera']) < 32:
            individual.fitness = 0.0
            return 0.0

        # Calculamos los 3 pilares de la aptitud
        vmax = self.calcular_vmax(genes)
        e_curva = self.calcular_estabilidad(genes)
        t_lap = self.calcular_tiempo_vuelta(genes)

        penalizacion = 1.0
        if e_curva < 2.0:
            penalizacion = 0.5  # Se reduce la calificación a la mitad

        # Queremos minimizar el tiempo de vuelta (por eso está dividiendo) y maximizar la velocidad y estabilidad. aca se checa cual es mejor mediamte esto
        fitness_final = (1.0 / (1.0 + t_lap)) * vmax * e_curva * penalizacion

        individual.fitness = fitness_final

        return fitness_final
