# rekey_tick.ps1 — one scheduled tick of the object_id slow-roll repair.
# Registered as a Windows Scheduled Task that fires every minute. Each run:
#   1. runs one batch of rekey_object_zeros.sql (register + backfill)
#   2. logs a timestamped progress line
#   3. when 0 NULL rows remain: final VACUUM ANALYZE, write .done, disable task
#
# No password lives here: psql reads %APPDATA%\postgresql\pgpass.conf
# (localhost:5432:*:postgres:...). Paths derive from $PSScriptRoot so there is
# no hardcoded drive letter in the logic. See README_rekey_2026-06-23.md.

$ErrorActionPreference = 'Stop'
$Batch    = if ($env:REKEY_BATCH) { [int]$env:REKEY_BATCH } else { 4000 }
$TaskName = 'PrometheusRekeyObjectZeros'
$Psql     = if ($env:PROMETHEUS_PSQL) { $env:PROMETHEUS_PSQL } else { 'C:\Program Files\PostgreSQL\17\bin\psql.exe' }
$Sql      = Join-Path $PSScriptRoot 'rekey_object_zeros.sql'
$Log      = Join-Path $PSScriptRoot 'rekey_progress.log'
$Done     = Join-Path $PSScriptRoot 'rekey.done'

$conn = @('-h','localhost','-U','postgres','-d','prometheus_fire','-w')
function Stamp { (Get-Date).ToString('yyyy-MM-dd HH:mm:ss') }

if (Test-Path $Done) { return }  # already finished; no-op

try {
    # one transactional tick
    & $Psql @conn '-1' '-q' '-v' 'ON_ERROR_STOP=1' '-v' "batch=$Batch" '-f' $Sql 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "psql tick exit $LASTEXITCODE" }

    # remaining work
    $remaining = (& $Psql @conn '-tA' '-c' 'SELECT count(*) FROM zeros.object_zeros WHERE object_id IS NULL;').Trim()
    $minted    = (& $Psql @conn '-tA' '-c' 'SELECT count(*) FROM zeros.object_zeros WHERE object_id > 134475;').Trim()
    "$(Stamp)  remaining_null=$remaining  minted=$minted  batch=$Batch" | Add-Content $Log

    if ([int]$remaining -eq 0) {
        "$(Stamp)  ALL ROWS KEYED - running final VACUUM ANALYZE" | Add-Content $Log
        & $Psql @conn '-q' '-c' 'VACUUM ANALYZE zeros.object_zeros;' 2>&1 | Out-Null
        & $Psql @conn '-q' '-c' 'VACUUM ANALYZE xref.object_registry;' 2>&1 | Out-Null
        "$(Stamp)  DONE" | Add-Content $Log
        Set-Content $Done "completed $(Stamp)"
        schtasks /Change /TN $TaskName /DISABLE 2>&1 | Out-Null
    }
}
catch {
    "$(Stamp)  ERROR: $_" | Add-Content $Log
    throw
}
