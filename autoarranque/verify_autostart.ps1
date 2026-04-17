$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "Lenguaje.pyw"
$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$linkPath = Join-Path $startupDir "AsistenteCajaPro.lnk"

Write-Output "SCRIPT: $scriptPath"
Write-Output "LNK:    $linkPath"

if (-not (Test-Path $scriptPath)) {
    Write-Output "ESTADO SCRIPT: NO ENCONTRADO"
    exit 1
}
Write-Output "ESTADO SCRIPT: OK"

if (-not (Test-Path $linkPath)) {
    Write-Output "ESTADO AUTOARRANQUE: NO CONFIGURADO"
    exit 1
}

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($linkPath)
$target = $shortcut.TargetPath

Write-Output "OBJETIVO LNK: $target"

if ($target -ieq $scriptPath) {
    Write-Output "ESTADO AUTOARRANQUE: OK (apunta al script correcto)"
    exit 0
}

Write-Output "ESTADO AUTOARRANQUE: CONFIGURADO PERO APUNTA A OTRA RUTA"
exit 2

