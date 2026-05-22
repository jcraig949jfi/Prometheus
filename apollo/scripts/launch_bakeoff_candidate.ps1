#requires -Version 5.1
<#
.SYNOPSIS
Launch one bake-off candidate: alt LLM server + Apollo with candidate config.

.PARAMETER Candidate
Short name: phi4mini | granite2b | dscoder13b

.EXAMPLE
.\launch_bakeoff_candidate.ps1 -Candidate phi4mini
#>
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("phi4mini","granite2b","dscoder13b")]
    [string]$Candidate
)

$ErrorActionPreference = "Stop"
$PythonExe = "C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe"
$ApolloDir = "D:\Prometheus\apollo"
$ModelPath = "$ApolloDir\.hf_cache\$Candidate"
$ConfigPath = "$ApolloDir\configs\config_bakeoff_$Candidate.yaml"
$RunDir = "$ApolloDir\run_v2d2b_$Candidate"
$AltLog = "$RunDir\alt_llm_server.log"
$ApolloLog = "$RunDir\apollo_launch.log"

if (-not (Test-Path $ModelPath)) {
    Write-Error "Model not found: $ModelPath"
    exit 1
}
if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config not found: $ConfigPath"
    exit 1
}

# 1. Set env vars
$env:AGORA_POSTGRES_HOST = "192.168.1.176"
$env:AGORA_POSTGRES_PASSWORD = "prometheus"
$env:AGORA_REDIS_HOST = "192.168.1.176"
$env:AGORA_REDIS_PASSWORD = "prometheus"
$env:PROMETHEUS_MACHINE = "M2"
$env:PYTHONPATH = "D:\Prometheus"
$env:LLM_ALT_MODEL_NAME = $ModelPath
$env:LLM_ALT_PORT = "8801"
$env:LLM_ALT_LOAD_IN_8BIT = "1"

Write-Host "Starting alt LLM server: $ModelPath on port 8801"
"=== alt server start $(Get-Date -Format o) | model=$ModelPath ===" | Out-File -Encoding utf8 -Append $AltLog

# 2. Start alt LLM server in background
Set-Location $ApolloDir
$altProc = Start-Process -PassThru -FilePath $PythonExe `
    -ArgumentList "src\llm_server_alt.py" `
    -RedirectStandardOutput $AltLog -RedirectStandardError "$AltLog.err" `
    -NoNewWindow

Write-Host "Alt server PID: $($altProc.Id) — waiting for /health..."

# 3. Wait for /health to return ok (up to 5 minutes for model load)
$deadline = (Get-Date).AddMinutes(5)
$ready = $false
while ((Get-Date) -lt $deadline) {
    try {
        $h = Invoke-RestMethod -Uri "http://localhost:8801/health" -TimeoutSec 5
        if ($h.status -eq "ok") {
            Write-Host "Alt server ready: $($h.model) | VRAM=$($h.vram_allocated_gb)GB / $($h.vram_total_gb)GB"
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 3
    }
}

if (-not $ready) {
    Write-Error "Alt server did not become ready in 5 min. Killing."
    Stop-Process -Id $altProc.Id -Force -ErrorAction SilentlyContinue
    exit 2
}

# 4. Launch Apollo
"=== apollo bakeoff start $(Get-Date -Format o) | candidate=$Candidate ===" | Out-File -Encoding utf8 -Append $ApolloLog
Write-Host "Launching Apollo with config: $ConfigPath"

$apolloProc = Start-Process -PassThru -FilePath $PythonExe `
    -ArgumentList "src\apollo.py", "--config", $ConfigPath `
    -RedirectStandardOutput $ApolloLog -RedirectStandardError "$ApolloLog.err" `
    -NoNewWindow

Write-Host "Apollo PID: $($apolloProc.Id)"
Write-Host ""
Write-Host "To monitor: Get-Content $ApolloLog -Wait -Tail 20"
Write-Host "To stop:    Stop-Process -Id $($apolloProc.Id) -Force ; Stop-Process -Id $($altProc.Id) -Force"
Write-Host ""
Write-Host "Apollo PID file: $RunDir\bakeoff.pids"
"$($apolloProc.Id) $($altProc.Id)" | Out-File -Encoding utf8 "$RunDir\bakeoff.pids"
