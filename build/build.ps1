param(
    # Ruta raíz del proyecto para ejecutar la build desde cualquier ubicación.
    [string]$ProjectRoot = "C:\Users\ASUS\OneDrive\Desktop\poder"
)

# Fuerza errores tempranos para evitar builds incompletas silenciosas.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $ProjectRoot
try {
    # Dependencias de ofuscación y empaquetado ejecutable.
    pip install pyarmor pyinstaller

    # Limpia artefactos previos antes de generar una build nueva.
    if (Test-Path "dist_obf") { Remove-Item "dist_obf" -Recurse -Force }
    if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
    if (Test-Path "build") { Remove-Item "build" -Recurse -Force }

    # Ofusca código fuente y luego genera el ejecutable final.
    pyarmor gen -O dist_obf Lenguaje.pyw licensing
    pyinstaller --onefile --noconsole --name AsistenteCajaPro dist_obf\Lenguaje.pyw

    Write-Host "Build completa. Ejecutable en dist\AsistenteCajaPro.exe"
}
finally {
    Pop-Location
}

