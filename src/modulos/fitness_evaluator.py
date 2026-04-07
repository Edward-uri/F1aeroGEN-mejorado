import math
import pandas as pd

class FitnessEvaluator:
    def __init__(self, pista_id, coche_id, km_actual, compuesto_actual):
        
        # Variables de estado de la simulación
        self.km_actual = km_actual
        self.compuesto_actual = compuesto_actual

        try:
            self.df_circuitos = pd.read_csv('src/base_conocimiento/catalog_circuitos.csv')
            self.df_aero = pd.read_csv('src/base_conocimiento/perfiles_aero.csv')
            self.df_llantas = pd.read_csv('src/base_conocimiento/deg_neumaticos.csv')
            self.df_coche = pd.read_csv('src/base_conocimiento/config_coche.csv')
            
            # --- 1. EXTRAER DATOS DEL COCHE ---
            coche = self.df_coche[self.df_coche['ID_Coche'] == coche_id].iloc[0]
            self.P = coche['Potencia_W']
            self.A = coche['Area_Frontal_m2']
            self.PESO = coche['Peso_N']
            self.GRAVEDAD = coche['Gravedad_m_s2']
            self.CD_BASE = coche['Cd_Base']
            self.CL_BASE = coche['Cl_Base']
            self.V_REF_CURVA = coche['V_Ref_Curva_m_s']

            # --- 2. EXTRAER DATOS DE LA PISTA ---
            pista = self.df_circuitos[self.df_circuitos['ID_Pista'] == pista_id].iloc[0]
            self.nombre_pista = pista['Nombre_Pista']
            self.d_rectas = pista['Longitud_Rectas_m']
            self.d_curvas = pista['Longitud_Curvas_m']
            self.r_curva = pista['Radio_Curva_Promedio_m']
            
            # se inyecta la densidad del aire según la altitud del circuito!
            self.RHO = pista['Densidad_Aire_kg_m3'] 
            
            self.csv_cargados = True
            
        except FileNotFoundError as e:
            print(f"Aviso: No se encontró un archivo CSV ({e}).")
            print("Asegúrate de tener la carpeta 'src/base_conocimiento' con los 4 archivos.")
            self.csv_cargados = False

    def _obtener_coeficientes_aero(self, angulo):
        """Busca en el CSV de aerodinámica los coeficientes para un ángulo específico."""
        if self.csv_cargados:
            # Encuentra la fila con el ángulo más cercano al gen del individuo
            idx = (abs(self.df_aero['Angulo_Aleron_Grados'] - angulo)).idxmin()
            fila = self.df_aero.iloc[idx]
            return fila['Coeficiente_Drag_Cd'], fila['Coeficiente_Downforce_Cl']
        return 0.92, 2.10 # Valores de respaldo (fallback)

    def _obtener_friccion_llanta(self, genes):
        """Busca en el CSV de llantas la fricción base y le suma la mejora por Camber."""
        if self.csv_cargados:
            # Filtramos por compuesto y encontramos el kilometraje más cercano
            df_filtrado = self.df_llantas[self.df_llantas['Compuesto_Neumatico'] == self.compuesto_actual]
            idx = (abs(df_filtrado['Kilometro'] - self.km_actual)).idxmin()
            mu_base_llanta = df_filtrado.loc[idx, 'Coeficiente_Friccion_Mu']
        else:
            mu_base_llanta = 1.45 # Valor de respaldo
            
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