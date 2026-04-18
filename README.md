# AsistenteCajaPro

Asistente flotante para Windows orientado actualmente a aprendizaje de **Python con ciclos** y logica de repeticion.

## Aviso principal: uso educativo y responsabilidad del usuario

Este asistente fue desarrollado con fines educativos y de aprendizaje. No esta permitido su uso para plagio, suplantacion, fraude academico o cualquier actividad indebida en evaluaciones.

Los desarrolladores no se hacen responsables por sanciones, perjuicios o consecuencias academicas, disciplinarias o legales derivadas del uso inapropiado de la herramienta.

## Alcance actual del proyecto

- Se elimina el flujo de distribucion con `.exe`.
- El canal oficial de ejecucion es **solo** `Lenguaje.pyw`.
- Se mantiene activo todo el sistema de licencias (activacion, verificacion periodica y revocacion remota).

## Atajos de la aplicacion

- `F7`: consulta con el texto del portapapeles.
- `F8`: oculta la ventana.
- `F9`: vuelve a mostrar la ventana.
- `F10`: cierra el programa.

## Licenciamiento comercial

El sistema usa validacion remota para controlar distribucion del script.

- Activacion obligatoria con clave de licencia.
- Licencia asociada al equipo (huella de dispositivo).
- Revalidacion periodica (default: `24` horas).
- Gracia offline configurable (default: `72` horas).
- Revocacion remota por licencia o por equipo.

Variables de entorno del cliente:

- `LICENSE_API_URL` (default: `http://127.0.0.1:8008`)
- `LICENSE_CHECK_HOURS` (default: `24`)
- `LICENSE_GRACE_HOURS` (default: `72`)

## Instalacion y uso para cliente final

### Requisitos del cliente

- Windows 10/11
- Python 3.10+
- Ollama instalado
- Modelo `llama3` descargado
- Conexion a internet para activacion de licencia

### Pasos del cliente

1. Instalar Python desde https://www.python.org/downloads/
2. Instalar Ollama desde https://ollama.com/download
3. Abrir PowerShell y descargar modelo:

```powershell
ollama pull llama3
```

4. Instalar dependencias del proyecto:

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder
python -m pip install -r requirements.txt
```

5. Ejecutar el asistente:

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder
python Lenguaje.pyw
```

6. Ingresar la licencia cuando la aplicacion lo solicite.

## Instalacion para vendedor/desarrollador

### 1) Requisitos

- Python 3.10+
- Ollama instalado y corriendo en `http://localhost:11434`

### 2) Dependencias de app

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder
python -m pip install -r requirements.txt
```

### 3) Ejecutar desde codigo

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder
python Lenguaje.pyw
```

## Servidor de licencias (obligatorio para activar)

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\start_server.ps1
```

Si prefieres CMD:

```bat
cd /d C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
start_server.cmd
```

Crear licencia por API (opcional):

```powershell
$headers = @{ "x-admin-key" = "TU_ADMIN_KEY_REAL" }
$body = @{ customer_name = "Cliente Demo"; max_devices = 1; expires_days = 365 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8008/admin/create_license" -Headers $headers -ContentType "application/json" -Body $body
```

## Panel de ventas y revocaciones

Usa `licensing_server/admin_licencias.ps1`.

Modo menu:

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
powershell -ExecutionPolicy Bypass -File .\start_admin.ps1
```

Si prefieres CMD:

```bat
cd /d C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
start_admin.cmd
```

Modo no interactivo:

```powershell
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action create -BaseUrl "http://127.0.0.1:8008" -AdminKey "TU_ADMIN_KEY_REAL" -CustomerName "Cliente Demo" -MaxDevices 1 -ExpiresDays 365
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action revoke-license -BaseUrl "http://127.0.0.1:8008" -AdminKey "TU_ADMIN_KEY_REAL" -LicenseKey "ACP-XXXXXXXX"
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action revoke-device -BaseUrl "http://127.0.0.1:8008" -AdminKey "TU_ADMIN_KEY_REAL" -LicenseKey "ACP-XXXXXXXX" -DeviceId "device-id-a-revocar"
```

## Solucion rapida de errores comunes

- `403 Prohibido` al crear licencias: la clave del panel no coincide con `LICENSE_ADMIN_KEY` del servidor.
- Comandos como `Set-ExecutionPolicy`/`Test-Path` no se reconocen: estabas en `cmd.exe`, no en PowerShell.
- Solucion simple: usa `start_server.cmd` y `start_admin.cmd` desde CMD.

## Entrega comercial

Carpeta recomendada: `ENTREGA/`.

Contenido de entrega al cliente:

- `Lenguaje.pyw`
- `requirements.txt`
- `licensing/`
- `ENTREGA/INSTRUCCIONES_CLIENTE.md`
- `ENTREGA/LICENCIA_CLIENTE.txt`

No compartir con clientes:

- `licensing_server/`
- `LICENSE_SECRET`
- `LICENSE_ADMIN_KEY`
- base de datos de licencias

## Estructura del proyecto

- `Lenguaje.pyw`: aplicacion principal
- `licensing/`: cliente local de licencias
- `licensing_server/`: API de activacion/revocacion
- `licensing_server/admin_licencias.ps1`: panel administrativo
- `licensing_server/start_server.ps1`: arranque guiado de servidor
- `licensing_server/start_admin.ps1`: arranque guiado de panel
- `licensing_server/start_server.cmd`: wrapper para CMD
- `licensing_server/start_admin.cmd`: wrapper para CMD
- `ENTREGA/`: documentos para entrega comercial
- `operaciones a futuro/`: hoja de ruta

## Referencias y creditos

Este proyecto integra **Ollama** para ejecucion local de modelos de lenguaje.

El desarrollo tecnico y segmentacion principal del script fueron realizados por **Alejandro Bautista**.

Se reconoce la contribucion integral de **Nicolas Perdomo** como responsable de la implementacion practica y consolidacion operativa del proyecto, incluyendo la evolucion funcional del asistente (ocultar/mostrar), la implementacion del licenciamiento por dispositivo con activacion online, verificacion periodica y revocacion remota, la creacion del panel administrativo de licencias, la actualizacion completa de la documentacion tecnica y comercial, y el soporte de operacion para instalacion, venta y despliegue.


