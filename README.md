# AsistenteCajaPro

Asistente flotante para Windows que lee el portapapeles y consulta Ollama con una hotkey global.

## Qué hace

- `F7`: toma el texto del portapapeles y consulta a Ollama.
- `F8`: oculta la ventana.
- `F9`: vuelve a mostrar la ventana.
- `F10`: cierra el programa.

## Requisitos

- Windows 10 o Windows 11
- Python 3.10 o superior
- Ollama instalado y funcionando en `http://localhost:11434`
- Conexión local al servicio de Ollama

## Librerías de Python

Las dependencias del proyecto están en `requirements.txt`:

- `requests`
- `keyboard`
- `pyperclip`

## Instalación paso a paso

### 1) Instalar Python

Si no lo tienes instalado:

1. Descarga Python desde https://www.python.org/downloads/
2. Durante la instalación marca **Add Python to PATH**
3. Verifica en PowerShell:

```powershell
python --version
pip --version
```

### 2) Instalar Ollama

1. Descarga Ollama para Windows desde:
   https://ollama.com/download
2. Ejecuta el instalador y completa la instalación
3. Abre una terminal y verifica que esté disponible:

```powershell
ollama --version
```

4. Descarga el modelo que usa el script:

```powershell
ollama pull llama3
```

5. Asegúrate de que Ollama esté corriendo antes de usar `Lenguaje.pyw`.
   Si hace falta, abre la app de Ollama o ejecuta el servicio local.

### 3) Instalar dependencias del proyecto

En la carpeta del proyecto ejecuta:

```powershell
pip install -r requirements.txt
```

Si prefieres usar un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 4) Ejecutar el asistente

Desde la carpeta del proyecto:

```powershell
python Lenguaje.pyw
```

## Uso

1. Abre `Lenguaje.pyw`.
2. Copia texto al portapapeles.
3. Pulsa `F7` para consultar a Ollama.
4. Usa `F8` para esconder la ventana y `F9` para volver a verla.
5. Usa `F10` para salir.

## Notas

- El script espera que Ollama responda en `http://localhost:11434/api/generate`.
- Si aparece `Error: Verifica Ollama`, confirma que Ollama esté instalado, abierto y que el modelo `llama3` esté descargado.
- En algunos equipos, la hotkey global `keyboard` puede requerir ejecutar PowerShell o Python con permisos adecuados.

## Estructura del proyecto

- `Lenguaje.pyw`: aplicación principal
- `requirements.txt`: dependencias Python
- `README.md`: guía de instalación y uso


