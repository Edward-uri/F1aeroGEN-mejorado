import math
import numpy as np
import pandas as pd
import os

# Carpeta de la base de conocimiento, resuelta desde la raíz del backend
BC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'base_conocimiento')


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

        # se inyecta la densidad del aire según la altitud del circuito!
        self.RHO = pista['Densidad_Aire_kg_m3']

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
        """Interpola la fricción base según el desgaste y le suma la mejora por Camber."""
        mu_base_llanta = np.interp(self.km_actual, self._llanta_km, self._llanta_mu)

        # El camber negativo mejora el agarre lateral de la llanta
        mu_real = mu_base_llanta + (0.05 * abs(genes['camber_frontal']))
        return mu_real

    def calcular_vmax(self, genes):
        cd_delantero, _ = self._obtener_coeficientes_aero(genes['aleron_delantero'])
        cd_trasero, _ = self._obtener_coeficientes_aero(genes['aleron_trasero'])

        # Drag total = Chasis + Alerón Del + Alerón Tras + Penalización por Toe Frontal (fricción extra)
        cd_total = self.CD_BASE + cd_delantero + cd_trasero + (0.1 * genes['toe_frontal'])

        # Vmax = raíz_cúbica( 2*P / (rho * A * Cd) )
        vmax = math.pow((2 * self.P) / (self.RHO * self.A * cd_total), 1.0/3.0)
        return vmax

    def calcular_estabilidad(self, genes):
        _, cl_delantero = self._obtener_coeficientes_aero(genes['aleron_delantero'])
        _, cl_trasero = self._obtener_coeficientes_aero(genes['aleron_trasero'])

        cl_total = self.CL_BASE + cl_delantero + cl_trasero

        # Carga aerodinámica (L) = 0.5 * rho * V^2 * A * Cl
        L = 0.5 * self.RHO * (self.V_REF_CURVA**2) * self.A * cl_total

        # Obtenemos la fricción real sumando el desgaste de llantas y el camber
        mu = self._obtener_friccion_llanta(genes)

        # E_curva = mu * (Peso + L) / Peso
        e_curva = (mu * (self.PESO + L)) / self.PESO
        return e_curva

    def calcular_tiempo_vuelta(self, vmax, e_curva):
        # Tiempo en rectas (penalizando un 15% por el tiempo de aceleración)
        t_rectas = self.d_rectas / (vmax * 0.85)

        # Velocidad máxima posible en curva antes de superar las Fuerzas G soportadas
        v_curva_limite = math.sqrt(e_curva * self.GRAVEDAD * self.r_curva)

        # Tiempo en curvas
        t_curvas = self.d_curvas / v_curva_limite

        t_lap = t_rectas + t_curvas
        return t_lap

    def evaluate(self, individual):

        genes = individual.genes

        # Si la altura del chasis es muy baja, ocurre el "efecto suelo" y el coche choca.
        if genes['altura_chasis'] < 5:
            individual.fitness = 0.0
            return 0.0

        # Calculamos los 3 pilares de la aptitud
        vmax = self.calcular_vmax(genes)
        e_curva = self.calcular_estabilidad(genes)
        t_lap = self.calcular_tiempo_vuelta(vmax, e_curva)

        penalizacion = 1.0
        if e_curva < 2.0:
            penalizacion = 0.5  # Se reduce la calificación a la mitad

        # Queremos minimizar el tiempo de vuelta (por eso está dividiendo) y maximizar la velocidad y estabilidad. aca se checa cual es mejor mediamte esto
        fitness_final = (1.0 / (1.0 + t_lap)) * vmax * e_curva * penalizacion

        individual.fitness = fitness_final

        return fitness_final
