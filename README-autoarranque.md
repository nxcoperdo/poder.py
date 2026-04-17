# Autoarranque descontinuado

Este archivo quedó solo como referencia histórica. El proyecto ya no usa autoarranque.

## Estado actual

- La aplicación principal es `Lenguaje.pyw`.
- La documentación activa está en `README.md`.
- Las hotkeys del programa se usan con el script abierto manualmente.

## Motivo de la descontinuación

Se decidió no continuar con el autoarranque porque, al cerrar el script con `F10`, Ollama puede seguir ejecutándose en segundo plano.

Eso significa que el modelo puede mantener un consumo moderado de memoria incluso cuando la ventana principal ya se cerró, lo cual no es ideal en equipos con poca RAM o recursos limitados.

## Recomendación

No uses los scripts de autoarranque anteriores. Consulta `README.md` para instalación, dependencias y uso.



