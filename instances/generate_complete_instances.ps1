<#
.SYNOPSIS
    Ejecuta generador_instances.py una vez por cada ontologia .ttl encontrada
    dentro de la carpeta generated_ontologies, y guarda cada
    instances_*.ttl resultante en una carpeta paralela que refleja la misma
    estructura de subcarpetas (decks_<N>_ranks).

.PARAMETER ScriptInstancias
    Ruta al script generador_instances.py.

.PARAMETER CarpetaOntologias
    Carpeta raiz donde buscar los .ttl de las barajas
    customizadas a procesar.

.PARAMETER CarpetaSalida
    Carpeta raiz donde se guardan los instances_*.ttl generados, replicando
    la misma estructura de subcarpetas que CarpetaOntologias.

.PARAMETER PythonExe
    Ejecutable de Python a usar.

.PARAMETER Filtro
    Patron de nombre de archivo a procesar. Por defecto
    procesa todos los .ttl encontrados.

.PARAMETER Forzar
    Si se indica, regenera instances aunque el archivo de salida ya exista.
    Por defecto se omiten los que ya tienen su instances_*.ttl (la generacion
    usa random, asi que no se pisan resultados existentes sin pedirlo explicitamente).

.PARAMETER SoloListar
    Si se indica, solo lista que .ttl se procesarian y donde quedaria cada
    salida, sin ejecutar nada.

.EXAMPLE
    # Desde la carpeta instances\, procesa las 24 ontologies customizadas:
    .\generar_complete_instances.ps1

.EXAMPLE
    # Revisar que se haria sin ejecutar nada:
    .\generar_complete_instances.ps1 -SoloListar

.EXAMPLE
    # Generar instances de solo ontologías con barajas customizadas de cierto de rango:
    .\generar_complete_instances.ps1 -Filtro "deck_6r_*"

.EXAMPLE
    # Regenerar todo de nuevo aunque ya existan instances:
    .\generar_complete_instances.ps1 -Forzar
#>

param(
    [string]$ScriptInstancias = ".\generate_complete_instances.py",
    [string]$CarpetaOntologias = "..\ontologies\generated_ontologies",
    [string]$CarpetaSalida = "..\instances\complete_instances",
    [string]$PythonExe = "python",
    [string]$Filtro = "*.ttl",
    [switch]$Forzar,
    [switch]$SoloListar
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
Write-Host "Se encontraron $($archivos.Count) ontologies para procesar."
if ($SoloListar) { Write-Host "(-SoloListar activo: no se ejecutara nada, solo se lista)" }
Write-Host ""

$numero = 0
$generados = 0
$omitidos = 0
$fallidos = 0
$tInicioTotal = Get-Date

foreach ($archivo in $archivos) {
    $numero++

    $subcarpetaRelativa = $archivo.DirectoryName.Substring($ontologiesAbsoluto.Length).Trim('\', '/')

    $nombreBase = [System.IO.Path]::GetFileNameWithoutExtension($archivo.Name)
    $carpetaDestino = if ($subcarpetaRelativa) { Join-Path $CarpetaSalida "instances_$subcarpetaRelativa" } else { $CarpetaSalida }
    $archivoDestino = Join-Path $carpetaDestino "instances_$nombreBase.ttl"

    Write-Host "[$numero/$($archivos.Count)] $($archivo.Name)"

    if ((Test-Path $archivoDestino) -and (-not $Forzar)) {
        Write-Host "  Ya existe, se omite (usa -Forzar para regenerar): $archivoDestino"
        $omitidos++
        Write-Host ""
        continue
    }

    if ($SoloListar) {
        Write-Host "  Se generaria en: $archivoDestino"
        Write-Host ""
        continue
    }

    New-Item -ItemType Directory -Force -Path $carpetaDestino | Out-Null

    Push-Location $carpetaDestino
    try {
        & $PythonExe $scriptAbsoluto $archivo.FullName
        $codigoSalida = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    if ($codigoSalida -ne 0) {
        Write-Warning "  generate_complete_instances.py devolvio codigo $codigoSalida para $($archivo.Name)."
        $fallidos++
    } elseif (Test-Path $archivoDestino) {
        Write-Host "  Generado: $archivoDestino"
        $generados++
    } else {
        Write-Warning "  No se encontro el archivo esperado: $archivoDestino"
        $fallidos++
    }

    Write-Host ""
}

$duracionTotal = (Get-Date) - $tInicioTotal

if ($SoloListar) {
    Write-Host "Listado terminado. Se procesarian $($archivos.Count) archivos."
} else {
    Write-Host "Proceso terminado. Se generaron $generados instances (de $($archivos.Count) ontologies) en $([math]::Round($duracionTotal.TotalSeconds, 1)) s."
    if ($omitidos -gt 0) { Write-Host "  Omitidos (ya existian): $omitidos" }
    if ($fallidos -gt 0) { Write-Host "  Fallidos: $fallidos" }
    Write-Host "Organizadas en subcarpetas instances_decks_<N>_ranks dentro de: $CarpetaSalida"
}