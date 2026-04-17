$ErrorActionPreference = "Stop"

$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$linkPath = Join-Path $startupDir "AsistenteCajaPro.lnk"

if (Test-Path $linkPath) {
    Remove-Item $linkPath -Force
    Write-Output "OK: Autoarranque eliminado."
    Write-Output "LNK ELIMINADO: $linkPath"
} else {
    Write-Output "INFO: No existia autoarranque para eliminar."
    Write-Output "LNK: $linkPath"
}

