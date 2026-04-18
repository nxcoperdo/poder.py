# Servidor de licencias (MVP)

Este servicio habilita activacion por dispositivo, verificacion periodica y revocacion remota para `Lenguaje.pyw`.

## Requisitos

- Python 3.10+
- Dependencias de `licensing_server/requirements.txt`

## Instalacion

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
python -m pip install -r requirements.txt
```

## Arranque recomendado (sin errores de clave)

Usa el script guiado, asi no se desalinea la clave admin:

### Desde PowerShell

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
powershell -ExecutionPolicy Bypass -File .\start_server.ps1
```

### Desde CMD

```bat
cd /d C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
start_server.cmd
```

El script pedira:

- `LICENSE_SECRET`
- `LICENSE_ADMIN_KEY`

## Panel admin recomendado

### Desde PowerShell

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
powershell -ExecutionPolicy Bypass -File .\start_admin.ps1
```

### Desde CMD

```bat
cd /d C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
start_admin.cmd
```

El panel usa `admin_licencias.ps1` y ahora valida conectividad (`/health`) antes de operar.

## Flujo operativo del vendedor

1. Levantar servidor con `start_server.ps1`.
2. Abrir panel con `start_admin.ps1`.
3. Crear licencia por cliente.
4. Entregar `Lenguaje.pyw` + `requirements.txt` + carpeta `licensing/` + licencia.
5. Revocar por licencia o dispositivo si hay uso indebido.

## Comandos directos (opcional)

Crear licencia:

```powershell
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action create -BaseUrl "http://127.0.0.1:8008" -AdminKey "TU_ADMIN_KEY_REAL" -CustomerName "Cliente Demo" -MaxDevices 1 -ExpiresDays 365
```

Revocar licencia:

```powershell
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action revoke-license -BaseUrl "http://127.0.0.1:8008" -AdminKey "TU_ADMIN_KEY_REAL" -LicenseKey "ACP-XXXXXXXX"
```

Revocar dispositivo:

```powershell
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action revoke-device -BaseUrl "http://127.0.0.1:8008" -AdminKey "TU_ADMIN_KEY_REAL" -LicenseKey "ACP-XXXXXXXX" -DeviceId "device-id-a-revocar"
```

## Error 403 (Prohibido): causa y solucion

Si sale `403` al crear/revocar licencias:

1. La `-AdminKey` del panel no coincide con `LICENSE_ADMIN_KEY` del servidor.
2. Reinicia el servidor despues de cambiar variables.
3. No uses placeholders como `tu-admin-key`; usa tu clave real.

## Nota importante sobre shell

- `Set-ExecutionPolicy`, `Test-Path`, `Remove-Item` son comandos de **PowerShell**.
- Si estas en `cmd.exe`, usa los wrappers `.cmd` o abre PowerShell.

## Nota para soporte

- El cliente final usa `Lenguaje.pyw`, Ollama, Python y una licencia valida.
- `licensing_server/`, `LICENSE_SECRET` y `LICENSE_ADMIN_KEY` se quedan del lado del vendedor.

