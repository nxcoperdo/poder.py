# AsistenteCajaPro

Asistente flotante para Windows orientado actualmente a aprendizaje de **Python con ciclos** y lógica de repetición.

## Aviso principal: uso educativo y responsabilidad del usuario

Este asistente fue desarrollado con fines educativos y de aprendizaje. No está permitido su uso para plagio, suplantación, fraude académico o cualquier actividad indebida en evaluaciones.

Los desarrolladores no se hacen responsables por sanciones, perjuicios o consecuencias académicas, disciplinarias o legales derivadas del uso inapropiado de la herramienta.

## Cambios documentados en esta versión

- Se implementó licenciamiento por dispositivo con activación online.
- Se agregó verificación periódica de licencia y modo gracia offline.
- Se agregó revocación remota por licencia o por dispositivo.
- Se añadió panel de administración en `licensing_server/admin_licencias.ps1`.
- Se preparó carpeta de entrega comercial en `entrega final/`.

## Atajos de la aplicación

- `F7`: consulta con el texto del portapapeles.
- `F8`: oculta la ventana.
- `F9`: vuelve a mostrar la ventana.
- `F10`: cierra el programa.

## Licenciamiento comercial

El sistema actual usa validación remota para controlar distribución.

- Activación obligatoria con clave de licencia.
- Licencia asociada al equipo (huella de dispositivo).
- Revalidación periódica (default: `24` horas).
- Gracia offline configurable (default: `72` horas).
- Revocación remota por licencia o por equipo.

Variables de entorno del cliente:

- `LICENSE_API_URL` (default: `http://127.0.0.1:8008`)
- `LICENSE_CHECK_HOURS` (default: `24`)
- `LICENSE_GRACE_HOURS` (default: `72`)

## Instalación para cliente final (compra)

Si entregas el `AsistenteCajaPro.exe`, el cliente **no necesita instalar Python ni librerías** del proyecto.

### Requisitos del cliente

- Windows 10/11
- Ollama instalado
- Modelo `llama3` descargado
- Conexión a internet para activación de licencia

### Pasos del cliente

1. Instalar Ollama desde https://ollama.com/download
2. Descargar modelo:

```powershell
ollama pull llama3
```

3. Ejecutar `AsistenteCajaPro.exe`
4. Ingresar la licencia cuando la aplicación lo solicite

## Instalación para vendedor/desarrollador (código fuente)

### 1) Requisitos

- Python 3.10+
- Ollama instalado y corriendo en `http://localhost:11434`

### 2) Dependencias de app

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder
python -m pip install -r requirements.txt
```

### 3) Ejecutar desde código

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder
python Lenguaje.pyw
```

## Servidor de licencias (obligatorio para activar)

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
python -m pip install -r requirements.txt
$env:LICENSE_SECRET = "cambia-esta-clave-secreta"
$env:LICENSE_ADMIN_KEY = "cambia-esta-admin-key"
python -m uvicorn app:app --host 0.0.0.0 --port 8008
```

Crear licencia por API:

```powershell
$headers = @{ "x-admin-key" = "cambia-esta-admin-key" }
$body = @{ customer_name = "Cliente Demo"; max_devices = 1; expires_days = 365 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8008/admin/create_license" -Headers $headers -ContentType "application/json" -Body $body
```

## Panel de ventas y revocaciones

Usa `licensing_server/admin_licencias.ps1`.

Modo menú:

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -BaseUrl "http://127.0.0.1:8008" -AdminKey "cambia-esta-admin-key"
```

Modo no interactivo:

```powershell
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action create -BaseUrl "http://127.0.0.1:8008" -AdminKey "cambia-esta-admin-key" -CustomerName "Cliente Demo" -MaxDevices 1 -ExpiresDays 365
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action revoke-license -BaseUrl "http://127.0.0.1:8008" -AdminKey "cambia-esta-admin-key" -LicenseKey "ACP-XXXXXXXX"
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action revoke-device -BaseUrl "http://127.0.0.1:8008" -AdminKey "cambia-esta-admin-key" -LicenseKey "ACP-XXXXXXXX" -DeviceId "device-id-a-revocar"
```

## Build de ejecutable para entrega

Build automática:

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder
powershell -ExecutionPolicy Bypass -File .\build\build.ps1
```

Si aparece error de `pip` no reconocido, usar build manual:

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder
python -m pip install pyarmor pyinstaller
pyarmor gen -O dist_obf Lenguaje.pyw licensing
python -m PyInstaller --onefile --noconsole --name AsistenteCajaPro dist_obf\Lenguaje.pyw
```

Resultado esperado: `dist\AsistenteCajaPro.exe`.

## Entrega comercial

Carpeta recomendada: `entrega final/`.

Contenido de entrega al cliente:

- `AsistenteCajaPro.exe`
- `INSTRUCCIONES_CLIENTE.md`
- `LICENCIA_CLIENTE.txt`
- `CONTENIDO_ENTREGA.txt`

No compartir con clientes:

- código fuente
- `licensing_server/`
- `LICENSE_SECRET`
- `LICENSE_ADMIN_KEY`
- base de datos de licencias

## Estructura del proyecto

- `Lenguaje.pyw`: aplicación principal
- `licensing/`: cliente local de licencias
- `licensing_server/`: API de activación/revocación
- `licensing_server/admin_licencias.ps1`: panel administrativo
- `build/build.ps1`: script de build
- `entrega final/`: paquete documental para venta
- `operaciones a futuro/`: hoja de ruta

## Referencias y créditos

Este proyecto integra **Ollama** para ejecución local de modelos de lenguaje.

El desarrollo técnico y segmentación principal del script fueron realizados por **Alejandro Bautista**.

Se reconoce la contribución integral de **Nicolás Perdomo** como responsable de la implementación práctica y consolidación operativa del proyecto, incluyendo la evolución funcional del asistente (ocultar/mostrar), la implementación del licenciamiento por dispositivo con activación online, verificación periódica y revocación remota, la creación del panel administrativo de licencias, la estructuración de la carpeta de entrega comercial, la definición del flujo de build y empaquetado `.exe`, la actualización completa de la documentación técnica y comercial, y el soporte de operación para instalación, venta y despliegue.


