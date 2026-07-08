## **1\. Método de Selección de Padres (Torneo Determinista, k=3)**

Para la fase de selección y formación de parejas reproductivas, el sistema implementa **Selección por Torneo**: para elegir a cada padre se toman *k=3* individuos al azar de la población y gana el de mayor aptitud. Se forman `población/2` parejas por generación, y cada pareja se consolida según la **Probabilidad de Cruza (`p_cruza`)**.

**Justificación técnica:**

* **Presión selectiva controlada:** Los individuos más aptos tienen mayor probabilidad de reproducirse, pero cualquier individuo puede ganar su torneo si le tocan rivales débiles. Esto acelera la convergencia sin eliminar la diversidad genética (un torneo de k=3 es presión moderada; valores altos de k harían la selección casi elitista).
* **Costo computacional lineal:** El número de parejas escala con el tamaño de la población (O(n)), no con sus combinaciones (O(n²)). En la práctica esto redujo el cómputo por corrida ~12× respecto al método combinatorio, y a presupuesto de cómputo igual (más generaciones en el mismo tiempo) el torneo alcanza mejor aptitud final.

**Método alternativo conservado — Emparejamiento Combinatorio Probabilístico (All-vs-All):** el sistema conserva el método original, seleccionable con el parámetro `seleccion="todos"`, en el que cada par posible de individuos tiene probabilidad `p_cruza` de reproducirse sin considerar su aptitud. Maximiza la exploración de sinergias mecánicas entre setups dispares, a costa de un número de evaluaciones cuadrático y de no ejercer ninguna presión selectiva en el emparejamiento (toda la presión recae en la poda). Mantener ambos métodos permite compararlos experimentalmente.

## **2\. Método de Reproducción (Cruce Uniforme / Uniform Crossover)**

Para la fase de reproducción, el proyecto descarta las cruzas aritméticas o de punto único en favor del **Cruce Uniforme**. Este método trata a cada uno de los 17 genes del monoplaza (Alerones, Camber y Toe por eje, Suspensión, Barras Antivuelco, Alturas de chasis, Presiones de neumáticos, Relación de marchas, Diferencial y Reparto de frenada) como bloques de construcción independientes.

**Mecanismo de acción:** Por cada pareja seleccionada, se generan 2 descendientes (Hijos). El algoritmo evalúa cada gen de forma individual y, mediante una distribución probabilística del 50% ("lanzar una moneda"), decide si el *Hijo 1* hereda esa pieza mecánica específica del *Padre 1* o del *Padre 2*. El *Hijo 2* recibe invariablemente la pieza del padre no seleccionado.

**Justificación técnica y coherencia física:**

* **Garantía de Validez del Cromosoma (Hard Constraints):** Dado que el simulador exige rangos de variables estrictos y tipos de datos heterogéneos (enteros para aerodinámica y flotantes para geometría de neumáticos), promediar valores matemáticamente arrojaría individuos nulos (por ejemplo, un alerón de valor `25.5°`, lo cual es imposible de configurar en el simulador). El Cruce Uniforme garantiza que solo se hereden valores legales que ya estaban validados en la generación previa.  
* **Modularidad Realista:** Este operador genético imita fielmente el trabajo en los *boxes* de Fórmula 1, donde los mecánicos pueden intercambiar el alerón frontal entero del Coche A y montarlo en el chasis del Coche B, sin alterar las propiedades atómicas de dicha pieza.  
* **Alta Capacidad Exploratoria:** Al no depender del orden en el que están programados los parámetros en el código, el Cruce Uniforme elimina el sesgo posicional, permitiendo una recombinación macroestructural altamente eficiente.

**3\. Método de Mutación (Híbrida: Reinicio Aleatorio Limitado \+ Creep)**

Para inyectar diversidad genética y evitar que la población se estanque en mínimos locales (convergencia prematura), se implementó un operador de mutación híbrido que combina **Reinicio Aleatorio Limitado** (exploración) con **Mutación Creep** (explotación).

**Mecanismo de acción:** Se evalúa mediante un sistema de doble probabilidad:

1. **Probabilidad de Individuo (`p_mut_i`):** Determina si el hijo recién creado sufrirá alguna mutación.  
2. **Probabilidad de Gen (`p_mut_gen`):** Si el individuo muta, se evalúa cada uno de sus 17 parámetros de manera independiente para decidir cuál pieza específica será alterada.

Cuando un gen es seleccionado para mutar, se decide con probabilidad 50/50 entre dos operadores:

* **Reinicio Aleatorio Limitado:** se genera un *nuevo valor aleatorio estrictamente dentro de los límites físicos* permitidos para esa pieza. Permite saltos exploratorios masivos (p. ej. pasar de un alerón de 5° a uno de 45° en una generación).
* **Mutación Creep:** se perturba el valor actual hasta ±10% del rango del gen, recortando al límite si se excede. Realiza el *ajuste fino* alrededor de soluciones que ya funcionan — exactamente lo que un reinicio puro no puede hacer, y la razón por la que la versión anterior del algoritmo se estancaba una vez cerca del óptimo.

**Justificación técnica y coherencia física:**

* **Heterogeneidad Estricta:** El cromosoma del monoplaza está compuesto por magnitudes heterogéneas. Intercambiar una magnitud angular flotante (Camber: \-3.00°) con una magnitud escalar entera (Altura: 25 mm) generaría "individuos muertos". El Reinicio Aleatorio respeta el dominio de cada variable.  
* **Exploración de Fronteras:** Al generar un valor completamente nuevo dentro del límite de la pieza (en lugar de solo sumar o restar un pequeño porcentaje), se permite que el algoritmo dé "saltos" exploratorios masivos. Por ejemplo, pasar de un alerón descargado (5°) a uno de máxima carga (45°) en una sola generación para probar configuraciones disruptivas.

**4\. Método de Poda y Selección de Supervivientes (Elitismo \+ Particionado Estocástico)**

Para la transición generacional (Poda), se diseñó un método híbrido que equilibra la explotación de las mejores soluciones con la exploración del espacio de búsqueda, garantizando que la población no supere el límite máximo ($P\_{max}$).

**Mecanismo de acción:**

1. **Evaluación Global:** Se unifican los padres y los hijos mutados en una superpoblación. Todos son evaluados por la Función de Aptitud (que premia la velocidad/estabilidad y castiga los tiempos altos).  
2. **Elitismo Puro:** Se extrae al individuo con la calificación más alta y se le garantiza un pase directo a la siguiente generación.  
3. **Particionado Estocástico (Ruleta por Tercios):** El resto de la población se ordena por aptitud y se divide en tres bloques (Alta, Media y Baja aptitud). Para llenar los cupos restantes hasta $P\_{max}$, se elige aleatoriamente un bloque y luego un individuo al azar dentro de ese bloque.

**Justificación técnica:**

* **Monotonicidad del Rendimiento:** El uso de Elitismo asegura que el mejor tiempo de vuelta histórico *nunca se pierda* por culpa de una mutación desfavorable o un cruce ineficiente. La gráfica de aptitud máxima siempre será ascendente o plana, nunca descendente.  
* **Mantenimiento de Diversidad Genética:** Si solo escogiéramos a los mejores individuos absolutos, la población sufriría de "convergencia prematura" (todos los coches terminarían siendo idénticos en pocas generaciones). Al dividir a los perdedores en bloques y darles una oportunidad aleatoria de sobrevivir, permitimos que "genes recesivos" (como un alerón extraño que por sí solo es malo, pero cruzado con otro chasis podría ser brillante) sobrevivan y aporten variedad genética.

