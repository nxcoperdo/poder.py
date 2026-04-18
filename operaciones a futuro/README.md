# Operaciones a futuro

Esta carpeta existe para dejar documentada la evolución prevista del proyecto.

## Estado actual resumido

- El proyecto está activo con licenciamiento por dispositivo y validación remota.
- La distribucion comercial actual se realiza con `Lenguaje.pyw`.
- La instalación quedó separada por perfil:
  - cliente final (`Lenguaje.pyw` + `requirements.txt` + Ollama + licencia)
  - vendedor/desarrollador (codigo fuente + servidor de licencias)

## Objetivos a futuro

1. A futuro, la idea es que el asistente deje de responder solo con código Python y pueda funcionar de forma más abierta, para responder distintos tipos de preguntas y temas.

2. Se plantea implementar la conmutación manual del esquema cromático del overlay, con el objetivo de optimizar la legibilidad y la accesibilidad visual en entornos con fondos claros y oscuros.
   Este tema se consultará entre desarrolladores y usuarios para definir la mejor forma de implementarlo.

3. Evaluar un paquete instalador para el flujo `.pyw` (sin empaquetado `.exe`) para facilitar despliegue sin romper el modelo de licencia actual.

4. Definir estrategia de actualización para clientes actuales cuando se publique la versión libre (v2), manteniendo trazabilidad comercial y continuidad de soporte.
   Esta línea nace como propuesta inicial y será consultada con los desarrolladores antes de cerrar el modelo final de migración, versiones y condiciones de actualización.

## Estado actual

- El proyecto sigue enfocado en Python.
- La prioridad actual sigue siendo la lógica con ciclos y ejercicios relacionados.
- Esta carpeta solo deja constancia del plan de expansión.

## Nota

No modifica el comportamiento del programa. Solo sirve como referencia documental para los siguientes pasos del proyecto.

Para instrucciones de instalación y operación actualizada, consultar `README.md`.

