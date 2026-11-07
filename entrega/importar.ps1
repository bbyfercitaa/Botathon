param(
    [string]$AutomateC = "C:\Program Files\Blue Prism Limited\Blue Prism Automate\AutomateC.exe",
    [Parameter(Mandatory = $true)][string]$User,
    [Parameter(Mandatory = $true)][string]$Password,
    [string]$DbConName = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $AutomateC)) {
    throw "No existe AutomateC en: $AutomateC"
}

function Invoke-AutomateC {
    param([string[]]$Arguments)
    $base = @()
    if ($DbConName) { $base += @("/dbconname", $DbConName) }
    & $AutomateC @Arguments @base /user $User $Password
    if ($LASTEXITCODE -ne 0) {
        throw "AutomateC fallo con: $($Arguments -join ' ')"
    }
}

$archivos = @(
    "01_MS_Excel_VBO.xml",
    "02_Ingesta_BaseContratos.xml",
    "03_Ingesta_Planificacion.xml"
)

foreach ($archivo in $archivos) {
    $ruta = Join-Path $PSScriptRoot $archivo
    if (-not (Test-Path -LiteralPath $ruta)) {
        throw "Falta el archivo: $ruta"
    }
    Write-Host "Importando $archivo..."
    Invoke-AutomateC @("/import", $ruta, "/overwrite")
}

foreach ($proceso in @("Ingesta_BaseContratos", "Ingesta_Planificacion")) {
    Write-Host "Publicando $proceso..."
    Invoke-AutomateC @("/publish", $proceso)
}

Write-Host ""
Write-Host "Listo. Recuerda ajustar las rutas (vRuta, vSalida...) en Process Studio."
