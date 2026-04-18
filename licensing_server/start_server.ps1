param(
    [string]$ServerHost = "127.0.0.1",
    [int]$Port = 8008,
    [string]$LicenseSecret = "",
    [string]$AdminKey = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $LicenseSecret) {
    $LicenseSecret = Read-Host "Ingresa LICENSE_SECRET"
}

if (-not $AdminKey) {
    $AdminKey = Read-Host "Ingresa LICENSE_ADMIN_KEY"
}

$LicenseSecret = $LicenseSecret.Trim()
$AdminKey = $AdminKey.Trim()

if (-not $LicenseSecret -or -not $AdminKey) {
    Write-Host "LICENSE_SECRET y LICENSE_ADMIN_KEY son obligatorios." -ForegroundColor Red
    exit 1
}

$env:LICENSE_SECRET = $LicenseSecret
$env:LICENSE_ADMIN_KEY = $AdminKey

Write-Host "Servidor de licencias iniciando en http://$ServerHost`:$Port" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener." -ForegroundColor DarkCyan

python -m uvicorn app:app --host $ServerHost --port $Port

