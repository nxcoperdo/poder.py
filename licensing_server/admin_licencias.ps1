param(
    [string]$BaseUrl = "http://127.0.0.1:8008",
    [string]$AdminKey = "",
    [ValidateSet("menu", "health", "create", "revoke-license", "revoke-device")]
    [string]$Action = "menu",
    [string]$CustomerName = "",
    [int]$MaxDevices = 1,
    [int]$ExpiresDays = 365,
    [string]$LicenseKey = "",
    [string]$DeviceId = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Normalize-BaseUrl {
    param([string]$Url)
    if (-not $Url) {
        return "http://127.0.0.1:8008"
    }
    return $Url.Trim().TrimEnd("/")
}

function Get-AdminHeaders {
    param([string]$Key)
    return @{ "x-admin-key" = $Key }
}

function Invoke-LicenseApi {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri,
        [hashtable]$Headers,
        [object]$Body
    )

    try {
        if ($null -ne $Body) {
            return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -ContentType "application/json" -Body ($Body | ConvertTo-Json)
        }

        return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers
    }
    catch {
        $status = "desconocido"
        $detail = $_.Exception.Message

        if ($_.Exception.Response) {
            try {
                $status = [int]$_.Exception.Response.StatusCode
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $raw = $reader.ReadToEnd()
                if ($raw) {
                    $detail = $raw
                }
            }
            catch {
                $detail = $_.Exception.Message
            }
        }

        if ($status -eq 403) {
            Write-Host "Error API (status=403): acceso denegado." -ForegroundColor Red
            Write-Host "Verifica que -AdminKey sea EXACTAMENTE la misma que LICENSE_ADMIN_KEY del servidor." -ForegroundColor Yellow
            Write-Host "Si cambiaste variables, reinicia el servidor de licencias." -ForegroundColor Yellow
            if ($detail) {
                Write-Host "Detalle: $detail" -ForegroundColor DarkYellow
            }
            exit 1
        }

        Write-Host "Error API (status=$status): $detail" -ForegroundColor Red
        exit 1
    }
}

function Ensure-AdminKey {
    param([string]$Key)

    $normalized = ""
    if ($Key) {
        $normalized = $Key.Trim()
    }

    if (-not $normalized) {
        $entered = Read-Host "Ingresa LICENSE_ADMIN_KEY"
        $entered = $entered.Trim()
        if (-not $entered) {
            Write-Host "No se ingreso clave administrativa." -ForegroundColor Red
            exit 1
        }
        return $entered
    }

    return $normalized
}

function Ensure-ServerHealth {
    param([string]$Url)
    try {
        $result = Invoke-RestMethod -Method Get -Uri "$Url/health"
        if ($result.status -ne "ok") {
            Write-Host "El servidor no respondio status=ok en /health." -ForegroundColor Red
            exit 1
        }
    }
    catch {
        Write-Host "No se pudo conectar al servidor de licencias en $Url" -ForegroundColor Red
        Write-Host "Levanta el servidor antes de usar el panel." -ForegroundColor Yellow
        exit 1
    }
}

function Show-Health {
    param([string]$Url)
    $result = Invoke-LicenseApi -Method "Get" -Uri "$Url/health"
    Write-Host "Servidor: $($result.status)" -ForegroundColor Green
}

function Create-License {
    param(
        [string]$Url,
        [string]$Key,
        [string]$Name,
        [int]$Devices,
        [int]$Days
    )

    if (-not $Name) {
        $Name = Read-Host "Nombre del cliente"
    }

    if ([string]::IsNullOrWhiteSpace($Name)) {
        Write-Host "CustomerName es obligatorio." -ForegroundColor Red
        exit 1
    }

    if ($Devices -lt 1) {
        Write-Host "MaxDevices debe ser >= 1" -ForegroundColor Red
        exit 1
    }

    if ($Days -lt 1) {
        Write-Host "ExpiresDays debe ser >= 1" -ForegroundColor Red
        exit 1
    }

    $headers = Get-AdminHeaders -Key $Key
    $body = @{
        customer_name = $Name
        max_devices   = $Devices
        expires_days  = $Days
    }

    $result = Invoke-LicenseApi -Method "Post" -Uri "$Url/admin/create_license" -Headers $headers -Body $body

    Write-Host "Licencia creada correctamente:" -ForegroundColor Green
    Write-Host "  Cliente      : $($result.customer_name)"
    Write-Host "  License Key  : $($result.license_key)" -ForegroundColor Yellow
    Write-Host "  Max Devices  : $($result.max_devices)"
    Write-Host "  Expires At   : $($result.expires_at)"
}

function Revoke-License {
    param(
        [string]$Url,
        [string]$Key,
        [string]$TargetLicense
    )

    if (-not $TargetLicense) {
        $TargetLicense = Read-Host "LicenseKey a revocar"
    }

    if ([string]::IsNullOrWhiteSpace($TargetLicense)) {
        Write-Host "LicenseKey es obligatorio." -ForegroundColor Red
        exit 1
    }

    $headers = Get-AdminHeaders -Key $Key
    $result = Invoke-LicenseApi -Method "Post" -Uri "$Url/admin/revoke/license/$TargetLicense" -Headers $headers

    Write-Host "Licencia revocada: $($result.license_key)" -ForegroundColor Yellow
}

function Revoke-Device {
    param(
        [string]$Url,
        [string]$Key,
        [string]$TargetLicense,
        [string]$TargetDevice
    )

    if (-not $TargetLicense) {
        $TargetLicense = Read-Host "LicenseKey"
    }

    if (-not $TargetDevice) {
        $TargetDevice = Read-Host "DeviceId"
    }

    if ([string]::IsNullOrWhiteSpace($TargetLicense) -or [string]::IsNullOrWhiteSpace($TargetDevice)) {
        Write-Host "LicenseKey y DeviceId son obligatorios." -ForegroundColor Red
        exit 1
    }

    $headers = Get-AdminHeaders -Key $Key
    $result = Invoke-LicenseApi -Method "Post" -Uri "$Url/admin/revoke/device/$TargetLicense/$TargetDevice" -Headers $headers

    Write-Host "Dispositivo revocado:" -ForegroundColor Yellow
    Write-Host "  LicenseKey: $($result.license_key)"
    Write-Host "  DeviceId  : $($result.device_id)"
}

function Show-Menu {
    Write-Host ""
    Write-Host "=== ADMIN LICENCIAS ===" -ForegroundColor Cyan
    Write-Host "1) Health servidor"
    Write-Host "2) Crear licencia"
    Write-Host "3) Revocar licencia completa"
    Write-Host "4) Revocar dispositivo"
    Write-Host "5) Salir"
    Write-Host ""
}

if ($Action -eq "menu") {
    $BaseUrl = Normalize-BaseUrl -Url $BaseUrl
    Ensure-ServerHealth -Url $BaseUrl
    $admin = Ensure-AdminKey -Key $AdminKey

    while ($true) {
        Show-Menu
        $option = Read-Host "Selecciona una opcion"

        switch ($option) {
            "1" { Show-Health -Url $BaseUrl }
            "2" { Create-License -Url $BaseUrl -Key $admin -Name $CustomerName -Devices $MaxDevices -Days $ExpiresDays }
            "3" { Revoke-License -Url $BaseUrl -Key $admin -TargetLicense $LicenseKey }
            "4" { Revoke-Device -Url $BaseUrl -Key $admin -TargetLicense $LicenseKey -TargetDevice $DeviceId }
            "5" { exit 0 }
            default { Write-Host "Opcion invalida." -ForegroundColor Red }
        }
    }
}

switch ($Action) {
    "health" {
        $BaseUrl = Normalize-BaseUrl -Url $BaseUrl
        Show-Health -Url $BaseUrl
        exit 0
    }
    "create" {
        $BaseUrl = Normalize-BaseUrl -Url $BaseUrl
        Ensure-ServerHealth -Url $BaseUrl
        $admin = Ensure-AdminKey -Key $AdminKey
        Create-License -Url $BaseUrl -Key $admin -Name $CustomerName -Devices $MaxDevices -Days $ExpiresDays
        exit 0
    }
    "revoke-license" {
        $BaseUrl = Normalize-BaseUrl -Url $BaseUrl
        Ensure-ServerHealth -Url $BaseUrl
        $admin = Ensure-AdminKey -Key $AdminKey
        Revoke-License -Url $BaseUrl -Key $admin -TargetLicense $LicenseKey
        exit 0
    }
    "revoke-device" {
        $BaseUrl = Normalize-BaseUrl -Url $BaseUrl
        Ensure-ServerHealth -Url $BaseUrl
        $admin = Ensure-AdminKey -Key $AdminKey
        Revoke-Device -Url $BaseUrl -Key $admin -TargetLicense $LicenseKey -TargetDevice $DeviceId
        exit 0
    }
}

