---
name: f1-design-system
description: Sistema de diseño y directrices visuales para F1 AeroGen. Úsalo para mejorar interfaces, crear nuevos componentes o asegurar que el estilo de "alto rendimiento" y "glassmorphism" se mantenga profesional y presentable en todo el proyecto.
---

# F1 AeroGen Design System

Este skill proporciona el marco de trabajo para mantener una interfaz de alta gama, inspirada en la telemetría de Fórmula 1 y el diseño de videojuegos de carreras modernos.

## Principios de Diseño

1. **Estética de Alto Rendimiento**: Uso de colores vibrantes sobre fondos profundos, tipografía técnica y líneas dinámicas.
2. **Glassmorphism**: Paneles translúcidos con desenfoque (`blur(12px)`) y bordes sutiles para dar profundidad.
3. **Motion-First**: Cada transición debe sentirse fluida y deliberada, utilizando `framer-motion`.
4. **Claridad de Telemetría**: La información crítica (fitness, tiempo, V-max) debe destacar con iconos y tipografía de gran peso.

## Tokens de Diseño

- **Fondo**: `#08080c` (con gradientes radiales sutiles).
- **Acento Primario**: `#ff1e1e` (Rojo F1) con `box-shadow` de brillo.
- **Acento Secundario**: `#ff9d00` (Oro/Naranja) para advertencias o estados especiales.
- **Tipografía**:
  - `Chakra Petch`: Títulos y valores numéricos (técnico/racing).
  - `Plus Jakarta Sans`: Texto de lectura y etiquetas (moderno/limpio).

## Componentes y Patrones

Consulta los archivos en `references/` para detalles técnicos:
- **Tarjetas de Selección**: [CARDS.md](references/CARDS.md)
- **Paneles de Configuración**: [PANELS.md](references/PANELS.md)
- **Visualización de Resultados**: [RESULTS.md](references/RESULTS.md)
- **Animaciones y Transiciones**: [MOTION.md](references/MOTION.md)

## Cuándo usar este Skill

- Al agregar una nueva página o sección al simulador.
- Cuando el usuario pida "pulir" o "estilizar" un componente existente.
- Para asegurar que los iconos de `lucide-react` sean consistentes.
- Al refactorizar estilos para usar variables CSS o Tailwind (si se solicita).
