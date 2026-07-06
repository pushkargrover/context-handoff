# doctor.ps1 - Relay preflight self-check (Windows).
# Reports which Relay capabilities are available on THIS machine.
$ErrorActionPreference = 'SilentlyContinue'
Write-Host "=== Relay doctor ==="
Write-Host "OS         : $([System.Environment]::OSVersion.VersionString)"
Write-Host "PowerShell : $($PSVersionTable.PSVersion)"
Write-Host ""

# Core handoff triggers - if this script runs, PowerShell is available.
Write-Host "[ OK ] Core handoff triggers (auto handoff at token budget, /handoff)"

# git -> Repository State depth
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    Write-Host "[ OK ] git found ($((& git --version)))  ->  handoffs include Repository State"
} else {
    Write-Host "[ -- ] git not found              ->  handoffs omit the Repository State section"
}

# Ollama -> local mode + auto-recovery
$url = if ($env:RELAY_OLLAMA_URL) { $env:RELAY_OLLAMA_URL.TrimEnd('/') } else { 'http://localhost:11434' }
try {
    $tags = Invoke-RestMethod -Uri "$url/api/tags" -Method Get -TimeoutSec 4
    $models = (@($tags.models) | ForEach-Object { $_.name }) -join ', '
    if (-not $models) { $models = '(none pulled - run: ollama pull gemma4)' }
    Write-Host "[ OK ] Ollama reachable at $url"
    Write-Host "        models: $models"
    Write-Host "        ->  /handoff-local, relay-recover, and 429 auto-recovery enabled"
} catch {
    Write-Host "[ -- ] Ollama not reachable at $url"
    Write-Host "        ->  local mode + auto-recovery disabled (install: https://ollama.com)"
}

Write-Host ""
Write-Host "Core triggers work with zero of the optional pieces above; git and Ollama only add capabilities."
