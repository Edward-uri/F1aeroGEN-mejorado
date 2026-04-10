# Patrón de Tarjetas (Cards)

Las tarjetas se usan para selección de pistas y coches.

- **Fondo**: `var(--bg-card)` con `backdrop-filter: blur(12px)`.
- **Imagen**: Contenedor con `height: 160px` y `overflow: hidden`. Efecto zoom `scale(1.1)` en hover.
- **Selección**: Borde de `1px solid var(--accent)` y `box-shadow` interno.
- **Iconos**: Usar `lucide-react` con tamaño 14-16px para estadísticas secundarias.
