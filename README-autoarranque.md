# Autoarranque descontinuado

Este archivo quedó solo como referencia histórica. El proyecto ya no usa autoarranque.

## Estado actual

- La aplicación principal es `Lenguaje.pyw`.
- La documentación activa está en `README.md`.
- Las hotkeys del programa se usan con el script abierto manualmente.

## Motivo de la descontinuación

Se decidió retirar el esquema de autoarranque debido a que `F10` solo finaliza la interfaz principal del script, pero no garantiza la terminación completa de los procesos asociados a Ollama, que pueden permanecer activos en segundo plano.

En sistemas con recursos limitados, especialmente equipos con baja disponibilidad de RAM, este comportamiento puede generar un consumo sostenido de memoria que resulta poco conveniente para el rendimiento general del sistema.

## Recomendación

No uses los scripts de autoarranque anteriores. Consulta `README.md` para instalación, dependencias y uso.



