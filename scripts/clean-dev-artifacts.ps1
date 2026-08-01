param(
    [switch]$Execute
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

$dirNames = @("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "coverage")
$dirTargets = Get-ChildItem -Path $repoRoot -Recurse -Force -Directory |
    Where-Object { $dirNames -contains $_.Name }

$fileTargets = Get-ChildItem -Path $repoRoot -Recurse -Force -File -Filter "*.pyc"

Write-Host "Repositorio: $repoRoot"
Write-Host ""
Write-Host "Directorios candidatos:" -ForegroundColor Yellow
$dirTargets | ForEach-Object { Write-Host $_.FullName }
Write-Host ""
Write-Host "Archivos candidatos (*.pyc):" -ForegroundColor Yellow
$fileTargets | ForEach-Object { Write-Host $_.FullName }
Write-Host ""

if (-not $Execute) {
    Write-Host "Modo simulacion. No se elimino nada." -ForegroundColor Cyan
    Write-Host "Para ejecutar limpieza real:"
    Write-Host "  pwsh ./scripts/clean-dev-artifacts.ps1 -Execute"
    exit 0
}

$dirTargets | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
$fileTargets | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Limpieza completada." -ForegroundColor Green
