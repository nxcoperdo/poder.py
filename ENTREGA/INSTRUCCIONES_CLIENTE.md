# Instrucciones para el cliente

Gracias por adquirir AsistenteCajaPro.

## Aviso principal: uso educativo y responsabilidad del usuario

Este asistente fue desarrollado con fines educativos y de aprendizaje. No esta permitido su uso para plagio, suplantacion, fraude academico o cualquier actividad indebida en evaluaciones.

Los desarrolladores no se hacen responsables por sanciones, perjuicios o consecuencias academicas, disciplinarias o legales derivadas del uso inapropiado de la herramienta.

## Contenido de la entrega

- `Lenguaje.pyw`
- `requirements.txt`
- `licensing/`
- `INSTRUCCIONES_CLIENTE.md`
- `LICENCIA_CLIENTE.txt`

## Requisitos

- Windows 10/11
- Python 3.10+
- Ollama instalado
- Modelo `llama3` descargado
- Conexion a internet para activar licencia
- URL del servidor de licencias entregada por el vendedor

## Instalacion

1. Instalar Ollama desde https://ollama.com/download
2. Abrir PowerShell y ejecutar:

```powershell
ollama pull llama3
```

3. Abrir una terminal en la carpeta de entrega e instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

4. Verificar que `Lenguaje.pyw` y la carpeta `licensing/` esten en la misma carpeta.

5. Configurar la URL del servidor de licencias (si el vendedor te dio una distinta a localhost):

```powershell
$env:LICENSE_API_URL = "http://127.0.0.1:8008"
```

6. Ejecutar:

```powershell
python Lenguaje.pyw
```

7. Ingresar la licencia cuando el sistema la solicite

## Nota sobre terminal

- Si usas `cmd.exe`, puedes ejecutar tambien:

```bat
set LICENSE_API_URL=http://127.0.0.1:8008
python Lenguaje.pyw
```

## Uso rapido

- `F7`: consulta con el texto del portapapeles
- `F8`: oculta ventana
- `F9`: muestra ventana
- `F10`: cierra programa

## Soporte

Si tienes problemas de activacion o licencia, contacta al vendedor con:

- Captura del error
- Fecha y hora del intento
- Nombre de cliente y licencia

## Referencias y creditos

Este proyecto integra **Ollama** para ejecucion local de modelos de lenguaje.

El desarrollo tecnico y segmentacion principal del script fueron realizados por **Alejandro Bautista**.

Se reconoce la contribucion integral de **Nicolas Perdomo** como responsable de la implementacion practica y consolidacion operativa del proyecto, incluyendo la evolucion funcional del asistente (ocultar/mostrar), la implementacion del licenciamiento por dispositivo con activacion online, verificacion periodica y revocacion remota, la creacion del panel administrativo de licencias, la actualizacion completa de la documentacion tecnica y comercial, y el soporte de operacion para instalacion, venta y despliegue.

