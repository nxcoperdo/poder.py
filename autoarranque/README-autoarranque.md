# Autoarranque descontinuado

Este archivo quedó solo como referencia histórica. El proyecto ya no usa autoarranque.

## Estado actual

- La aplicacion actual se ejecuta como script en `Lenguaje.pyw`.
- La documentación activa está en `README.md`.
- Las hotkeys se usan con la app abierta manualmente (`F7`, `F8`, `F9`, `F10`).

## Motivo de la descontinuación

Se decidió retirar el esquema de autoarranque debido a que `F10` solo finaliza la interfaz principal del script, pero no garantiza la terminación completa de los procesos asociados a Ollama, que pueden permanecer activos en segundo plano.

En sistemas con recursos limitados, especialmente equipos con baja disponibilidad de RAM, este comportamiento puede generar un consumo sostenido de memoria que resulta poco conveniente para el rendimiento general del sistema.

Además, el modelo operativo actual prioriza control de licencias, apertura manual de la aplicación y activación bajo demanda.

## Recomendación

No uses los scripts de autoarranque anteriores.

Consulta `README.md` para:

- instalacion de cliente final con `Lenguaje.pyw`
- instalación de vendedor/desarrollador
- operación del panel de licencias y revocaciones



