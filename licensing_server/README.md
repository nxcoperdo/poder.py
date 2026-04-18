# Servidor de licencias (MVP)

Este servicio habilita activación por dispositivo, verificación periódica y revocación remota para `Lenguaje.pyw` y `AsistenteCajaPro.exe`.

## Requisitos

- Python 3.10+
- Dependencias de `licensing_server/requirements.txt`

## Instalacion

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
python -m pip install -r requirements.txt
```

## Variables recomendadas

```powershell
$env:LICENSE_SECRET = "cambia-esta-clave-secreta"
$env:LICENSE_ADMIN_KEY = "cambia-esta-admin-key"
$env:LICENSE_CHECK_HOURS = "24"
$env:LICENSE_GRACE_HOURS = "72"
```

Recomendación: usar valores fuertes y no compartirlos con clientes.

## Ejecucion

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
python -m uvicorn app:app --host 0.0.0.0 --port 8008
```

## Flujo operativo del vendedor

1. Levantar servidor de licencias.
2. Crear licencia para cada cliente.
3. Entregar `.exe` + licencia (no entregar backend).
4. Revocar por licencia o dispositivo ante uso indebido.

## Crear una licencia (admin)

```powershell
$headers = @{ "x-admin-key" = "cambia-esta-admin-key" }
$body = @{ customer_name = "Cliente Demo"; max_devices = 1; expires_days = 365 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8008/admin/create_license" -Headers $headers -ContentType "application/json" -Body $body
```

## Revocar una licencia

```powershell
$headers = @{ "x-admin-key" = "cambia-esta-admin-key" }
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8008/admin/revoke/license/ACP-XXXXXXXX" -Headers $headers
```

## Revocar un dispositivo

```powershell
$headers = @{ "x-admin-key" = "cambia-esta-admin-key" }
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8008/admin/revoke/device/ACP-XXXXXXXX/device-id-a-revocar" -Headers $headers
```

## Script admin con menu

Tambien puedes administrar licencias con `admin_licencias.ps1`.

### Modo menu (interactivo)

```powershell
cd C:\Users\ASUS\OneDrive\Desktop\poder\licensing_server
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -BaseUrl "http://127.0.0.1:8008" -AdminKey "cambia-esta-admin-key"
```

### Modo comando (no interactivo)

Health:

```powershell
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action health -BaseUrl "http://127.0.0.1:8008"
```

Crear licencia:

```powershell
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action create -BaseUrl "http://127.0.0.1:8008" -AdminKey "cambia-esta-admin-key" -CustomerName "Cliente Demo" -MaxDevices 1 -ExpiresDays 365
```

Revocar licencia completa:

```powershell
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action revoke-license -BaseUrl "http://127.0.0.1:8008" -AdminKey "cambia-esta-admin-key" -LicenseKey "ACP-XXXXXXXX"
```

Revocar un dispositivo:

```powershell
powershell -ExecutionPolicy Bypass -File .\admin_licencias.ps1 -Action revoke-device -BaseUrl "http://127.0.0.1:8008" -AdminKey "cambia-esta-admin-key" -LicenseKey "ACP-XXXXXXXX" -DeviceId "device-id-a-revocar"
```

## Nota para soporte

- El cliente final solo necesita `AsistenteCajaPro.exe`, Ollama y una licencia válida.
- Python, `requirements.txt`, backend y claves administrativas se quedan del lado del vendedor.

