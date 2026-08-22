# F1aeroGEN

Sistema de optimización de la configuración de un monoplaza de Fórmula 1 mediante algoritmos genéticos.

## Problema

Cada circuito exige un equilibrio diferente entre carga aerodinámica, velocidad punta, estabilidad y comportamiento en curvas. Ajustar manualmente estas variables puede ser lento y propenso a errores.

## Solución

El proyecto utiliza un algoritmo genético para explorar configuraciones de un monoplaza y buscar combinaciones que reduzcan el tiempo de vuelta, considerando variables aerodinámicas y mecánicas.

### Variables de decisión

- ángulo del alerón delantero;
- ángulo del alerón trasero;
- dureza de la suspensión;
- relación de marchas.

### Objetivos de optimización

- reducir el tiempo de vuelta;
- mejorar la velocidad punta;
- mantener la estabilidad en curva;
- respetar restricciones físicas de fricción y resistencia aerodinámica.

## Estructura

- `backend/`: lógica de optimización y simulación;
- `frontend/`: interfaz para visualizar configuraciones y resultados;
- `src/`: implementación principal;
- `imagenes/`: recursos visuales;
- `evolucion_setups_f1.csv`: datos de configuraciones evaluadas.

## Ejecución local

Revisa los archivos `backend/`, `frontend/` y `src/` para identificar el flujo de ejecución correspondiente a cada parte del sistema. Las dependencias y comandos pueden variar entre los componentes.

## Nota sobre el origen

Este repositorio parte de una base forked y contiene trabajo de adaptación y mejora. La atribución del proyecto original se conserva en GitHub.

## Estado

Proyecto experimental de optimización y simulación.

## Autor

Eduardo Uriel Chavez Diaz — [@Edward-uri](https://github.com/Edward-uri)
