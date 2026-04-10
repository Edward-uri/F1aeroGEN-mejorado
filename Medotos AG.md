## **1\. Método de Generación de Parejas (Emparejamiento Combinatorio Probabilístico)**

Para la fase de selección y formación de parejas reproductivas, el sistema implementa un **Emparejamiento Combinatorio Probabilístico (All-vs-All Pairing)**. En lugar de limitar la cruza estrictamente a los individuos de mayor aptitud (lo cual podría causar convergencia prematura), este método evalúa todas las combinaciones posibles dentro de la población poblacional.

**Mecanismo de acción:** El algoritmo iterativo recorre la población asegurando que el *Individuo A* tenga la oportunidad de emparejarse con el *Individuo B* sin generar pares duplicados ni emparejamientos consigo mismo. La decisión final de consolidar la pareja está dictada por el hiper parámetro de **Probabilidad de Cruza (`p_cruza`)**, típicamente configurado entre 0.7 y 0.9.

**Justificación técnica:**

* **Mantenimiento de la Diversidad Genética:** Al permitir que individuos con aptitudes medias participen en la cruza, se preservan "piezas" mecánicas (genes) que podrían ser invaluables en generaciones futuras, evitando que el algoritmo se estanque en mínimos locales.  
* **Exploración de Sinergias:** En la dinámica de vehículos, un reglaje no es lineal. Un alerón de un individuo "lento" podría ser la pieza perfecta para la suspensión de un individuo "inestable". Este método fomenta la experimentación máxima de sinergias mecánicas en la fase inicial de búsqueda.

## **2\. Método de Reproducción (Cruce Uniforme / Uniform Crossover)**

Para la fase de reproducción, el proyecto descarta las cruzas aritméticas o de punto único en favor del **Cruce Uniforme**. Este método trata a cada uno de los 6 genes del monoplaza (Alerones, Barra Estabilizadora, Camber, Toe y Altura) como bloques de construcción independientes.

**Mecanismo de acción:** Por cada pareja seleccionada, se generan 2 descendientes (Hijos). El algoritmo evalúa cada gen de forma individual y, mediante una distribución probabilística del 50% ("lanzar una moneda"), decide si el *Hijo 1* hereda esa pieza mecánica específica del *Padre 1* o del *Padre 2*. El *Hijo 2* recibe invariablemente la pieza del padre no seleccionado.

**Justificación técnica y coherencia física:**

* **Garantía de Validez del Cromosoma (Hard Constraints):** Dado que el simulador exige rangos de variables estrictos y tipos de datos heterogéneos (enteros para aerodinámica y flotantes para geometría de neumáticos), promediar valores matemáticamente arrojaría individuos nulos (por ejemplo, un alerón de valor `25.5°`, lo cual es imposible de configurar en el simulador). El Cruce Uniforme garantiza que solo se hereden valores legales que ya estaban validados en la generación previa.  
* **Modularidad Realista:** Este operador genético imita fielmente el trabajo en los *boxes* de Fórmula 1, donde los mecánicos pueden intercambiar el alerón frontal entero del Coche A y montarlo en el chasis del Coche B, sin alterar las propiedades atómicas de dicha pieza.  
* **Alta Capacidad Exploratoria:** Al no depender del orden en el que están programados los parámetros en el código, el Cruce Uniforme elimina el sesgo posicional, permitiendo una recombinación macroestructural altamente eficiente.

**3\. Método de Mutación (Reinicio Aleatorio Limitado / Bounded Random Resetting)**

Para inyectar diversidad genética y evitar que la población se estanque en mínimos locales (convergencia prematura), se implementó un operador de mutación basado en **Reinicio Aleatorio Limitado**.

**Mecanismo de acción:** Se evalúa mediante un sistema de doble probabilidad:

1. **Probabilidad de Individuo (`p_mut_i`):** Determina si el hijo recién creado sufrirá alguna mutación.  
2. **Probabilidad de Gen (`p_mut_gen`):** Si el individuo muta, se evalúa cada uno de sus 6 parámetros de manera independiente para decidir cuál pieza específica será alterada.

Cuando un gen es seleccionado para mutar, no se intercambia con otro gen del mismo individuo (lo cual corrompería los tipos de datos), sino que se genera un *nuevo valor aleatorio estrictamente dentro de los límites físicos y matemáticos* permitidos para esa pieza específica.

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

