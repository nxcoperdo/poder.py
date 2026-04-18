param(
    [string]$BaseUrl = "http://127.0.0.1:8008",
    [string]$AdminKey = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $AdminKey) {
    $AdminKey = Read-Host "Ingresa LICENSE_ADMIN_KEY"
}

$AdminKey = $AdminKey.Trim()
if (-not $AdminKey) {
    Write-Host "No se ingreso clave administrativa." -ForegroundColor Red
    exit 1
}

$scriptPath = Join-Path $PSScriptRoot "admin_licencias.ps1"
if (-not (Test-Path $scriptPath)) {
    Write-Host "No se encontro admin_licencias.ps1" -ForegroundColor Red
    exit 1
}

powershell -ExecutionPolicy Bypass -File $scriptPath -BaseUrl $BaseUrl -AdminKey $AdminKey

