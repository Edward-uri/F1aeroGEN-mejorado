# F1aeroGen
Algoritmo genetico basado en la optimizacion de la configuracion de un auto de Formula 1 

# Contexto de la problemática: 
En el automovilismo de alta competición (Fórmula 1), cada circuito presenta un perfil único de rectas y curvas. Los ingenieros deben configurar el vehículo (setup) antes de la carrera. Una configuración con mucha carga aerodinámica permite tomar curvas rápido, pero hace al coche lento en rectas debido a la resistencia al aire (drag).
# Problemática: 
Encontrar el equilibrio manual entre carga aerodinámica y velocidad punta es ineficiente y propenso a errores humanos. Una mala configuración resulta en tiempos de vuelta altos , consumo excesivo de neumáticos o imposibilidad de realizar adelantamientos, lo que conlleva pérdidas deportivas y económicas para la escudería.
# Nombre largo: 
Sistema de optimización de configuración aerodinámica y mecánica para monoplazas de competición mediante algoritmos genéticos
# Descripcion del proyectó: 
Desarrollo de un sistema basado en algoritmos genéticos que determina la combinación óptima de ángulos de alerones y rigidez de suspensión. El sistema simula una vuelta al circuito y evoluciona los parámetros para reducir el tiempo total, respetando las leyes físicas de fricción y resistencia aerodinámica.

# VARIABLES DE DECISIÓN (17 genes, rangos del setup de F1 25)
- Ángulo de alerón delantero y trasero
- Camber delantero y trasero
- Toe delantero y trasero
- Rigidez de suspensión delantera y trasera
- Barra antivuelco delantera y trasera
- Altura de chasis delantera y trasera (efecto suelo y rake)
- Presión de neumáticos delantera y trasera
- Relación de marchas (aceleración vs velocidad tope)
- Diferencial en aceleración (tracción vs subviraje)
- Reparto de frenada (distancia de frenado)

# VARIABLES A OPTIMIZAR:
- Tiempo de vuelta
- Velocidad punta 
- Estabilidad en curva

# ESTRUCTURA DEL PROYECTO
```
backend/
  main.py              → API FastAPI (la usa el frontend)
  cli.py               → versión de consola (guarda CSV + PNGs)
  test_smoke.py        → chequeo rápido del motor genético
  base_conocimiento/   → CSVs: circuitos, coches, aero, neumáticos
  modulos/
    individual.py         → genes y sus límites (LIMITES_GENES)
    genetic_engine.py     → cruza, mutación, poda con elitismo
    fitness_evaluator.py  → modelo físico y función de aptitud
    stop_criterial.py     → paro por convergencia
    visualizer.py         → las 4 gráficas (PNG base64)
    telemetry_listener.py → captura UDP del juego F1 (2025)
frontend/              → interfaz web (React + Vite)
```

# CÓMO EJECUTAR

**Backend** (requiere Python 3):
```bash
cd backend
python3 -m venv .venv                 # solo la primera vez
.venv/bin/pip install -r requirements.txt   # solo la primera vez
.venv/bin/uvicorn main:app --port 8000
```

**Frontend** (requiere Node):
```bash
cd frontend
npm install    # solo la primera vez
npm run dev    # abre http://localhost:5173
```

**Versión de consola** (sin frontend):
```bash
cd backend && .venv/bin/python cli.py
```

**Prueba rápida del motor:**
```bash
cd backend && .venv/bin/python test_smoke.py
```

# NOTAS
- Para agregar una variable de decisión nueva: agrega su rango en `LIMITES_GENES`
  (`backend/modulos/individual.py`) y su efecto físico en `fitness_evaluator.py`.
  La generación aleatoria y la mutación la toman automáticamente.
- El endpoint `/api/evolucionar` acepta `seed` (resultados reproducibles),
  `paciencia` (paro anticipado si no hay mejora en N generaciones; 0 = desactivado)
  y `seleccion`: `"torneo"` (default, presión selectiva k=3, cómputo lineal) o
  `"todos"` (emparejamiento combinatorio original, útil para comparar métodos).
- Los coeficientes aerodinámicos y la fricción de neumáticos se interpolan
  linealmente entre las filas de los CSVs, así cada grado de alerón tiene un
  efecto distinto (sin mesetas de fitness).
- El tiempo de vuelta se obtiene con un simulador por segmentos
  (`simular_vuelta`): en cada recta el coche acelera (limitado por motor,
  tracción del diferencial y arrastre) y frena al final para entrar a la
  curva. La gráfica de telemetría muestra el perfil real de ese simulador.
