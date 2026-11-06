<#
.SYNOPSIS
    Ejecuta generate_ontologies.py una vez por cada combinación de (ranks, palos)
    de la matriz de pruebas del benchmark, y organiza cada .ttl generado dentro de
    una carpeta "decks_<N>_ranks" según su cantidad de ranks.

    generate_ontologies.py es interactivo (usa input() tres veces: nombre, palos,
    ranks), así que este script le pasa las respuestas por stdin en vez de argumentos.
    generate_ontologies.py siempre escribe en <raiz_proyecto>\ontologies\generated_ontologies\
    (ruta calculada a partir de su propia ubicación en disco, sin importar desde
    dónde se invoque), así que -CarpetaSalida debe apuntar a esa misma carpeta.

.PARAMETER ScriptGenerador
    Ruta al script generate_ontologies.py.

.PARAMETER CarpetaSalida
    Carpeta donde generate_ontologies.py escribe los .ttl (generated_ontologies).
    Ahí mismo se crean las subcarpetas decks_<N>_ranks.

.PARAMETER PythonExe
    Ejecutable de Python a usar.

.PARAMETER GruposRangos
    Cantidades de ranks a generar. Cada una crea su propia carpeta decks_<N>_ranks.

.PARAMETER GruposPalos
    Cantidades de palos a generar dentro de cada grupo de ranks.

.PARAMETER SoloListar
    Si se indica, solo imprime las combinaciones que se generarían, sin ejecutar
    generate_ontologies.py ni tocar el disco. Útil para revisar antes de correr.

.EXAMPLE
    # Generar las 24 ontologías con barajas customizadas completas con los valores por defecto en este script
    # (6/13/19/25/31/37 ranks x 4/8/12/16 palos = 24 archivos):
    .\generate_ontologies.ps1
 
.EXAMPLE
    # Revisar qué ontologías con barajas customizadas se generaría sin escribir nada:
    .\generate_ontologies.ps1 -SoloListar
 
.EXAMPLE
    # Generar solo ontologías con barajas customizadas de cierto de rango:
    .\generate_ontologies.ps1 -GruposRangos 6
 
.EXAMPLE
    # Generar solo un par de combinaciones especificas (por ejemplo para testear):
    .\generate_ontologies.ps1 -GruposRangos 13,19 -GruposPalos 4,8
#>

param(
    [string]$ScriptGenerador = ".\generate_ontologies.py",
    [string]$CarpetaSalida = "..\ontologies\generated_ontologies",
    [string]$PythonExe = "python",

    [int[]]$GruposRangos = @(6, 13, 19, 25, 31, 37),
    [int[]]$GruposPalos = @(4, 8, 12, 16),

    [switch]$SoloListar
)

$todosPalos = @(
    "Fuego", "Agua", "Planta", "Electrico", "Normal", "Volador", "Bicho", "Veneno",
    "Tierra", "Roca", "Lucha", "Psiquico", "Fantasma", "Hielo", "Dragon", "Siniestro"
)

$todosRangos = @(
    "Uno", "Dos", "Tres", "Cuatro", "Cinco", "Seis", "Siete", "Ocho", "Nueve", "Diez",
    "Once", "Doce", "Trece", "Catorce", "Quince", "Dieciseis", "Diecisiete", "Dieciocho", "Diecinueve",
    "Veinte", "Veintiuno", "Veintidos", "Veintitres", "Veinticuatro", "Veinticinco",
    "Veintiseis", "Veintisiete", "Veintiocho", "Veintinueve", "Treinta", "Treintayuno",
    "Treintaydos", "Treintaytres", "Treintaycuatro", "Treintaycinco", "Treintayseis", "Treintaysiete"
)

if (-not $SoloListar) {
    if (-not (Test-Path $ScriptGenerador)) {
        Write-Error "No se encontro el script generador: $ScriptGenerador"
        exit 1
    }
    New-Item -ItemType Directory -Force -Path $CarpetaSalida | Out-Null

    $utf8SinBom = New-Object System.Text.UTF8Encoding($false)
    [Console]::OutputEncoding = $utf8SinBom
    [Console]::InputEncoding  = $utf8SinBom
    $OutputEncoding = $utf8SinBom
    $env:PYTHONIOENCODING = "utf-8"
    chcp 65001 > $null
}

$maxRangoPedido = ($GruposRangos | Measure-Object -Maximum).Maximum
$maxPaloPedido  = ($GruposPalos  | Measure-Object -Maximum).Maximum
if ($maxRangoPedido -gt $todosRangos.Count) {
    Write-Error "Se pidieron hasta $maxRangoPedido ranks pero el catalogo solo tiene $($todosRangos.Count)."
    exit 1
}
if ($maxPaloPedido -gt $todosPalos.Count) {
    Write-Error "Se pidieron hasta $maxPaloPedido palos pero el catalogo solo tiene $($todosPalos.Count)."
    exit 1
}

$totalCombos = $GruposRangos.Count * $GruposPalos.Count
Write-Host ""
Write-Host "Se van a generar $totalCombos barajas ($($GruposRangos.Count) grupos de ranks x $($GruposPalos.Count) grupos de palos)."
if ($SoloListar) { Write-Host "(-SoloListar activo: no se ejecutara nada, solo se lista)" }
Write-Host ""

$numero = 0
$tInicioTotal = Get-Date

foreach ($nRangos in $GruposRangos) {

    $ranksGrupo  = $todosRangos[0..($nRangos - 1)]
    $carpetaGrupo = Join-Path $CarpetaSalida "decks_${nRangos}_ranks"

    if (-not $SoloListar) {
        New-Item -ItemType Directory -Force -Path $carpetaGrupo | Out-Null
    }

    foreach ($nPalos in $GruposPalos) {
        $numero++

        $palosGrupo   = $todosPalos[0..($nPalos - 1)]
        $nombreBaraja = "deck_${nRangos}r_${nPalos}p"
        $palosLinea   = $palosGrupo -join ", "
        $ranksLinea  = $ranksGrupo -join ", "

        Write-Host "==================================================================="
        Write-Host " [$numero/$totalCombos] $nombreBaraja  ($nPalos palos x $nRangos ranks)"
        Write-Host "==================================================================="

        if ($SoloListar) {
            Write-Host "  Palos  : $palosLinea"
            Write-Host "  Rangos : $ranksLinea"
            Write-Host ""
            continue
        }

        $tInicio = Get-Date

        $respuestas = @($nombreBaraja, $palosLinea, $ranksLinea)
        $respuestas | & $PythonExe $ScriptGenerador

        if ($LASTEXITCODE -ne 0) {
            Write-Warning "  generate_ontologies.py devolvio codigo $LASTEXITCODE para $nombreBaraja. Se omite."
            Write-Host ""
            continue
        }

        $archivoGenerado = Join-Path $CarpetaSalida "$nombreBaraja.ttl"

        if ((Test-Path $archivoGenerado) -and ((Get-Item $archivoGenerado).LastWriteTime -ge $tInicio)) {
            Move-Item -Path $archivoGenerado -Destination $carpetaGrupo -Force
            Write-Host "  Movido a: $(Join-Path $carpetaGrupo "$nombreBaraja.ttl")"
        } else {
            Write-Warning "  No se encontro el archivo esperado: $archivoGenerado"
        }

        Write-Host ""
    }
}

$duracionTotal = (Get-Date) - $tInicioTotal

if ($SoloListar) {
    Write-Host "Listado terminado. Se habrían generado $numero ontologías con barajas customizadas."
} else {
    Write-Host "Proceso terminado. Se generaron $numero ontologías con barajas customizadas en $([math]::Round($duracionTotal.TotalSeconds, 1)) s."
    Write-Host "Organizadas en subcarpetas decks_<N>_ranks dentro de: $CarpetaSalida"
}