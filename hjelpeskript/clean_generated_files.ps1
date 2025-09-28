#!/usr/bin/env powershell
<#
.SYNOPSIS
    Sletter maskingenererte filer som automatisk kan gjenopprettes.

.DESCRIPTION
    Dette scriptet sletter alle maskingenererte filer og kataloger som kan 
    automatisk gjenopprettes ved bygg, testing eller kjøring av koden:
    
    - Python bytecode (.pyc filer og __pycache__ kataloger)
    - Build artifakter (dist/, build/, *.egg-info/)
    - Test cache (.pytest_cache/, .coverage)
    - IDE/Editor filer (.vscode/, *.swp, *.swo, *~)
    - Temporære filer (*.tmp, *.temp, *.log)
    - Automatisk genererte visualiseringsfiler (*.png fra demos)

.PARAMETER DryRun
    Viser hva som ville blitt slettet uten å faktisk slette noe.

.PARAMETER Verbose
    Viser detaljert output under slettingen.

.EXAMPLE
    .\clean_generated_files.ps1
    Sletter alle maskingenererte filer.

.EXAMPLE  
    .\clean_generated_files.ps1 -DryRun
    Viser hva som ville blitt slettet uten å gjøre endringer.

.EXAMPLE
    .\clean_generated_files.ps1 -Verbose
    Sletter filer med detaljert output.
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Verbose
)

# Få absolut sti til script-katalogen (prosjektrot)
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "🧹 Renser maskingenererte filer i: $ProjectRoot" -ForegroundColor Cyan
Write-Host ""

# Definer maskingenererte filer og kataloger som kan slettes
$ItemsToClean = @{
    "Python bytecode" = @(
        "**\__pycache__",
        "**\*.pyc", 
        "**\*.pyo",
        "**\*.pyd"
    )
    "Build artifakter" = @(
        "dist",
        "build", 
        "*.egg-info",
        "**\*.egg-info"
    )
    "Test og coverage cache" = @(
        ".pytest_cache",
        ".coverage",
        ".coverage.*",
        "htmlcov",
        ".tox"
    )
    "IDE og editor filer" = @(
        ".vscode\settings.json",
        "*.swp",
        "*.swo", 
        "*~",
        ".DS_Store",
        "Thumbs.db"
    )
    "Temporære filer" = @(
        "*.tmp",
        "*.temp",
        "*.log",
        "**\*.tmp",
        "**\*.temp"
    )
    "Demo visualiseringsfiler" = @(
        "*_hx_demo.png",
        "*_hx_demo.html",
        "my_hx.*",
        "static_hx.png",
        "interactive_hx.html"
    )
}

$TotalItemsFound = 0
$TotalItemsDeleted = 0
$TotalSizeFreed = 0

# Funksjon for å beregne størrelse av fil eller katalog
function Get-ItemSize {
    param([string]$Path)
    
    if (Test-Path $Path -PathType Container) {
        # Katalog - summer alle filer rekursivt
        $size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum
        return [math]::Max(0, $size)
    } else {
        # Fil
        return (Get-Item $Path -ErrorAction SilentlyContinue).Length
    }
}

# Funksjon for å formatere filstørrelse
function Format-FileSize {
    param([long]$Size)
    
    if ($Size -lt 1024) { return "$Size B" }
    elseif ($Size -lt 1MB) { return "{0:N1} KB" -f ($Size / 1KB) }  
    elseif ($Size -lt 1GB) { return "{0:N1} MB" -f ($Size / 1MB) }
    else { return "{0:N1} GB" -f ($Size / 1GB) }
}

# Gå gjennom hver kategori
foreach ($Category in $ItemsToClean.Keys) {
    Write-Host "📂 $Category" -ForegroundColor Yellow
    
    $CategoryItemsFound = 0
    $CategoryItemsDeleted = 0
    $CategorySizeFreed = 0
    
    foreach ($Pattern in $ItemsToClean[$Category]) {
        try {
            # Finn matchende filer/kataloger
            $Items = Get-ChildItem -Path $Pattern -Force -ErrorAction SilentlyContinue
            
            foreach ($Item in $Items) {
                $CategoryItemsFound++
                $TotalItemsFound++
                
                # Beregn størrelse før sletting
                $ItemSize = Get-ItemSize -Path $Item.FullName
                $CategorySizeFreed += $ItemSize
                $TotalSizeFreed += $ItemSize
                
                if ($DryRun) {
                    Write-Host "   [DRY RUN] Ville slettet: $($Item.FullName) ($(Format-FileSize $ItemSize))" -ForegroundColor Gray
                } else {
                    if ($Verbose) {
                        Write-Host "   Sletter: $($Item.FullName) ($(Format-FileSize $ItemSize))" -ForegroundColor Gray
                    }
                    
                    if ($Item.PSIsContainer) {
                        Remove-Item -Path $Item.FullName -Recurse -Force -ErrorAction SilentlyContinue
                    } else {
                        Remove-Item -Path $Item.FullName -Force -ErrorAction SilentlyContinue
                    }
                    
                    # Verifiser at elementet ble slettet
                    if (-not (Test-Path $Item.FullName)) {
                        $CategoryItemsDeleted++
                        $TotalItemsDeleted++
                    }
                }
            }
        } catch {
            # Ignorer feil (f.eks. filer som ikke finnes eller er låst)
            continue
        }
    }
    
    if ($CategoryItemsFound -eq 0) {
        Write-Host "   ✅ Ingen filer funnet" -ForegroundColor Green
    } else {
        if ($DryRun) {
            Write-Host "   📊 Fant $CategoryItemsFound element(er) ($(Format-FileSize $CategorySizeFreed))" -ForegroundColor Cyan
        } else {
            Write-Host "   ✅ Slettet $CategoryItemsDeleted av $CategoryItemsFound element(er) ($(Format-FileSize $CategorySizeFreed))" -ForegroundColor Green
        }
    }
    
    Write-Host ""
}

# Sammendrag
Write-Host "📊 SAMMENDRAG" -ForegroundColor Magenta
Write-Host "─────────────────────────────────────────" -ForegroundColor Gray

if ($DryRun) {
    Write-Host "🔍 DRY RUN - Ingen filer ble slettet" -ForegroundColor Yellow
    Write-Host "📁 Fant totalt: $TotalItemsFound element(er)" -ForegroundColor Cyan
    Write-Host "💾 Ville frigjort: $(Format-FileSize $TotalSizeFreed)" -ForegroundColor Cyan
} else {
    Write-Host "✅ Slettet totalt: $TotalItemsDeleted av $TotalItemsFound element(er)" -ForegroundColor Green
    Write-Host "💾 Frigjort diskplass: $(Format-FileSize $TotalSizeFreed)" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔄 For å gjenopprette filene:" -ForegroundColor Blue
Write-Host "   • Python bytecode: Kjør python-koden på nytt" -ForegroundColor Gray
Write-Host "   • Build artifakter: Kjør 'python -m build' eller 'pip install -e .'" -ForegroundColor Gray
Write-Host "   • Test cache: Kjør 'pytest' på nytt" -ForegroundColor Gray
Write-Host "   • Demo filer: Kjør visualiseringsdemoene på nytt" -ForegroundColor Gray

if ($DryRun) {
    Write-Host ""
    Write-Host "💡 Kjør uten -DryRun parameteren for å faktisk slette filene." -ForegroundColor Yellow
}