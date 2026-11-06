<#
.SYNOPSIS
    Ejecuta generate_split_instances.py una vez por cada ontologia .ttl
    encontrada dentro de generated_ontologies. A diferencia de
    generar_complete_instances.ps1, cada ejecución produce 10 archivos (uno por
    tipo de mano, 4 manos) en vez de 1 archivos y 40 manos, asi que cada baraja recibe su propia subcarpeta:

        CarpetaSalida\instances_decks_<N>_ranks\<nombre_baraja>\instances_<nombre_baraja>_<tipo>.ttl

.PARAMETER ScriptInstancias
    Ruta al script generate_split_instances.py.

.PARAMETER CarpetaOntologias
    Carpeta raiz donde buscar los .ttl de las barajas
    customizadas a procesar.

.PARAMETER CarpetaSalida
    Carpeta raiz donde se guardan los archivos generados, replicando la misma
    estructura de subcarpetas que CarpetaOntologias, mas una subcarpeta extra
    por baraja (ya que cada una produce 10 archivos, uno por tipo de mano).

.PARAMETER PythonExe
    Ejecutable de Python a usar.

.PARAMETER Filtro
    Patron de nombre de archivo a procesar. Por defecto procesa todos los .ttl
    encontrados.

.PARAMETER Forzar
    Si se indica, regenera instances aunque ya existan los 10 archivos de esa
    baraja.

.PARAMETER SoloListar
    Si se indica, solo lista que .ttl se procesarian y donde quedaria cada
    salida, sin ejecutar nada.

.EXAMPLE
    # Desde la carpeta instances\, procesa las 24 ontologies customizadas:
    .\generar_split_instances.ps1

.EXAMPLE
    # Revisar que se haria sin ejecutar nada:
    .\generar_split_instances.ps1 -SoloListar

.EXAMPLE
    # Generar instances de solo ontologías con barajas customizadas de cierto de rango:
    .\generar_split_instances.ps1 -Filtro "deck_6r_*"

.EXAMPLE
    # Regenerar todo de nuevo aunque ya existan instances:
    .\generar_split_instances.ps1 -Forzar
#>

param(
    [string]$ScriptInstancias = ".\generate_split_instances.py",
    [string]$CarpetaOntologias = "..\ontologies\generated_ontologies",
    [string]$CarpetaSalida = "..\instances\split_instances",
    [string]$PythonExe = "python",
    [string]$Filtro = "*.ttl",
    [switch]$Forzar,
    [switch]$SoloListar
)

$tiposMano = @(
    "carta_alta", "par", "doble_par", "trio", "escalera",
    "color", "full", "poker", "escalera_color", "escalera_real"
)

if (-not (Test-Path $ScriptInstancias)) {
    Write-Error "No se encontro el script generador: $ScriptInstancias"
    exit 1
}
if (-not (Test-Path $CarpetaOntologias)) {
    Write-Error "No se encontro la carpeta de ontologies: $CarpetaOntologias"
    exit 1
}

$scriptAbsoluto = (Resolve-Path $ScriptInstancias).Path
$ontologiesAbsoluto = (Resolve-Path $CarpetaOntologias).Path

$archivos = Get-ChildItem -Path $ontologiesAbsoluto -Recurse -Filter $Filtro | Sort-Object FullName

if ($archivos.Count -eq 0) {
    Write-Warning "No se encontraron archivos .ttl en $ontologiesAbsoluto con el filtro '$Filtro'."
    exit 0
}

Write-Host ""
Write-Host "Se encontraron $($archivos.Count) ontologies para procesar ($($tiposMano.Count) archivos cada una)."
if ($SoloListar) { Write-Host "(-SoloListar activo: no se ejecutara nada, solo se lista)" }
Write-Host ""

$numero = 0
$barajasGeneradas = 0
$omitidas = 0
$fallidas = 0
$tInicioTotal = Get-Date

foreach ($archivo in $archivos) {
    $numero++

    $subcarpetaRelativa = $archivo.DirectoryName.Substring($ontologiesAbsoluto.Length).Trim('\', '/')
    $nombreBase = [System.IO.Path]::GetFileNameWithoutExtension($archivo.Name)

    $carpetaGrupo = if ($subcarpetaRelativa) { Join-Path $CarpetaSalida "instances_$subcarpetaRelativa" } else { $CarpetaSalida }
    $carpetaBaraja = Join-Path $carpetaGrupo $nombreBase

    $archivosEsperados = $tiposMano | ForEach-Object { Join-Path $carpetaBaraja "instances_${nombreBase}_$_.ttl" }
    $completo = -not ($archivosEsperados | Where-Object { -not (Test-Path $_) })

    Write-Host "[$numero/$($archivos.Count)] $($archivo.Name)"

    if ($completo -and (-not $Forzar)) {
        Write-Host "  Ya existen los $($tiposMano.Count) archivos, se omite (usa -Forzar para regenerar): $carpetaBaraja"
        $omitidas++
        Write-Host ""
        continue
    }

    if ($SoloListar) {
        Write-Host "  Se generarian $($tiposMano.Count) archivos en: $carpetaBaraja"
        Write-Host ""
        continue
    }

    New-Item -ItemType Directory -Force -Path $carpetaBaraja | Out-Null

    Push-Location $carpetaBaraja
    try {
        & $PythonExe $scriptAbsoluto $archivo.FullName
        $codigoSalida = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    $completoAhora = -not ($archivosEsperados | Where-Object { -not (Test-Path $_) })

    if ($codigoSalida -ne 0) {
        Write-Warning "  generate_split_instances.py devolvio codigo $codigoSalida para $($archivo.Name)."
        $fallidas++
    } elseif ($completoAhora) {
        Write-Host "  Generados los $($tiposMano.Count) archivos en: $carpetaBaraja"
        $barajasGeneradas++
    } else {
        $faltantes = ($archivosEsperados | Where-Object { -not (Test-Path $_) }).Count
        Write-Warning "  Faltan $faltantes de $($tiposMano.Count) archivos esperados en: $carpetaBaraja"
        $fallidas++
    }

    Write-Host ""
}

$duracionTotal = (Get-Date) - $tInicioTotal

if ($SoloListar) {
    Write-Host "Listado terminado. Se procesarian $($archivos.Count) ontologies ($($archivos.Count * $tiposMano.Count) archivos en total)."
} else {
    Write-Host "Proceso terminado. Se generaron instances divididas para $barajasGeneradas barajas (de $($archivos.Count)), $($barajasGeneradas * $tiposMano.Count) archivos en total, en $([math]::Round($duracionTotal.TotalSeconds, 1)) s."
    if ($omitidas -gt 0) { Write-Host "  Omitidas (ya existian): $omitidas" }
    if ($fallidas -gt 0) { Write-Host "  Fallidas: $fallidas" }
    Write-Host "Organizadas en subcarpetas instances_decks_<N>_ranks\<nombre_baraja> dentro de: $CarpetaSalida"
}