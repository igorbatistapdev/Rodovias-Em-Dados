# Configuracao opcional. Executar na raiz do projeto:
# powershell -ExecutionPolicy Bypass -File .\scripts\configurar_windows.ps1
$ErrorActionPreference = 'Continue'
$project = Split-Path $PSScriptRoot -Parent
Set-Location $project
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host 'O inicializador py nao foi encontrado; instale Python 3.13 em python.org ou winget.'
    exit 1
}
$python13 = & py -3.13 --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Python 3.13 nao foi encontrado. Para instalar com winget:' -ForegroundColor Yellow
    Write-Host 'winget install --id Python.Python.3.13 --exact --source winget'
    exit 1
}
Write-Host "Python detectado: $python13"
$ErrorActionPreference = 'Stop'
& py -3.13 -m venv .venv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$exe = Join-Path $project '.venv\Scripts\python.exe'
& $exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Ambiente pronto. Para executar:' -ForegroundColor Green
Write-Host '.\.venv\Scripts\python.exe scripts/run_pipeline.py'
