# F1AeroGen  
## Sistema de optimización de configuración aerodinámica y mecánica para monoplazas de competición mediante algoritmos genéticos

---

## 1. Contexto de la problemática

En el automovilismo de alta competición (Fórmula 1), cada circuito presenta un perfil único de rectas y curvas.  
Los ingenieros deben configurar el vehículo (**setup**) antes de la carrera.  
Una configuración con mucha carga aerodinámica permite tomar curvas más rápido, pero hace al coche lento en rectas debido a la resistencia al aire (*drag*).

---

## 2. Problemática

Encontrar el equilibrio manual entre carga aerodinámica y velocidad punta es ineficiente y propenso a errores humanos.  
Una mala configuración puede producir:

- Tiempos de vuelta altos.  
- Consumo excesivo de neumáticos.  
- Dificultad o imposibilidad de realizar adelantamientos.

Todo esto se traduce en pérdidas deportivas y económicas para la escudería.

---

## 3. Nombre del proyecto

- **Nombre largo:**  
  Sistema de optimización de configuración aerodinámica y mecánica para monoplazas de competición mediante algoritmos genéticos.

- **Nombre corto:**  
  **F1AeroGen**

---

## 4. Descripción del proyecto

Desarrollo de un sistema basado en **algoritmos genéticos** que determina la combinación óptima de:

- Ángulos de alerones.  
- Rigidez de suspensión.  
- Relación de marchas.

El sistema simula una vuelta al circuito y evoluciona los parámetros para reducir el tiempo total, respetando las leyes físicas de fricción y resistencia aerodinámica.  
La búsqueda se realiza en función de las características del circuito y las condiciones ambientales del día de la carrera.

---

## 5. Variables de decisión

- Ángulo de alerón delantero.  
- Ángulo de alerón trasero.  
- Dureza de suspensión.  
- Relación de marchas.

---

## 6. Variables a optimizar

- Tiempo de vuelta.  
- Velocidad punta.  
- Estabilidad en curva.

---

## 7. Objetivos de optimización

- Minimizar el **tiempo de vuelta**.  
- Maximizar la **velocidad punta**.  
- Maximizar la **estabilidad en curva** (seguridad y control del vehículo).

---

## 8. Base de conocimiento

- **Catálogo de circuitos homologados**  
  Lista con la topología de las pistas, incluyendo:
  - Longitud de recta principal.  
  - Radio de curvas lentas.  
  - Radio de curvas rápidas.  
  - Rugosidad del asfalto.

- **Curvas de degradación de neumáticos**  
  Datos históricos de cuánto agarre pierde un neumático (Blando/Medio/Duro) por kilómetro recorrido, en función de la temperatura.

- **Perfiles aerodinámicos**  
  Tabla que correlaciona ángulos de alerón (0°–40°) con sus respectivos coeficientes de:
  - *Drag* (resistencia).  
  - *Downforce* (carga aerodinámica).

---

## 9. Entradas al sistema

- **Archivo de pista objetivo**  
  Archivo específico del circuito que se va a correr (topología y características del trazado).

- **Condiciones atmosféricas (variables de entorno)**  
  - Temperatura del aire (afecta la densidad del aire y, por tanto, la aerodinámica).  
  - Temperatura de pista (afecta el comportamiento y degradación de los neumáticos).

- **Límites reglamentarios (FIA)**  
  Archivo con valores mínimos y máximos permitidos para la temporada actual, por ejemplo:
  - Altura mínima del chasis.  
  - Límites de ángulo de alerón.  
  - Rangos permitidos de otros parámetros mecánicos.

---

## 10. Salidas esperadas del sistema

- **Hoja de setup óptimo (tabla)**  
  Listado detallado con la configuración ganadora:
  - Ángulos exactos de alerones.  
  - Presión de neumáticos.  
  - Altura del chasis.  
  - Otros parámetros relevantes.  
  Incluye el **tiempo de vuelta estimado** para ese setup.

- **Gráfica de convergencia**  
  Evolución de la aptitud (fitness) de la población a lo largo de las generaciones del algoritmo genético, mostrando cómo el sistema va mejorando el tiempo de vuelta.

- **Gráfica de telemetría comparativa**  
  Gráfico de **Velocidad vs. Distancia** que superpone:
  - La vuelta del “mejor individuo” (setup óptimo).  
  - Una “configuración base” (setup inicial o estándar).  

  Esto permite visualizar en qué zonas del circuito se gana tiempo (rectas, curvas lentas, curvas rápidas, frenadas, etc.).

- **Mapa de calor de carga aerodinámica**  
  Visualización 2D que muestra el equilibrio del coche:
  - Tendencia a **subviraje** (faltante de giro del eje delantero).  
  - Tendencia a **sobreviraje** (exceso de giro del eje trasero).  

  El mapa se genera a partir de los ángulos de alerón elegidos y la distribución de carga aerodinámica.

---