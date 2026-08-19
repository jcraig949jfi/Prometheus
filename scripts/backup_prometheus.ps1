# Prometheus backup job — DECISION 2 (2026-08-17: "Z: now + cloud later"), amended
# 2026-08-18: Z: not mounted on M1, so the reachable target is E:\prometheus_backup
# (different physical disk, ~1TB free). Z:/cloud remains a parked follow-up.
#
# What this protects and why:
#   - prometheus_fire, prometheus_sci  -> pg_dump -Fc  (NOT in git; the irreplaceable set)
#   - lmfdb (363GB) EXCLUDED           -> re-downloadable mirror
#   - repo tracked files EXCLUDED      -> GitHub remote is their offsite already
# Retention: keep the 6 most recent dump sets, delete older.
# Registered as Windows Scheduled Task "PrometheusBackupWeekly" (pattern:
# PrometheusRekeyObjectZeros, the job that ran 8h unattended in June).
#
# Manual run:  powershell -NoProfile -ExecutionPolicy Bypass -File F:\Prometheus\scripts\backup_prometheus.ps1

$ErrorActionPreference = "Stop"
$PgDump  = "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
$BackupRoot = "E:\prometheus_backup\pg"
$PgHost  = "localhost"   # server is local on M1; localhost matches pgpass.conf. The .202
                         # form found no pgpass entry -> silent password prompt -> eternal
                         # 0-byte hang (diagnosed 2026-08-18).
$PgUser  = "postgres"   # password from %APPDATA%\postgresql\pgpass.conf
$Stamp   = Get-Date -Format "yyyyMMdd_HHmmss"
$Dest    = Join-Path $BackupRoot $Stamp
$Log     = Join-Path $BackupRoot "backup_log.txt"

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Add-Content $Log "[$Stamp] backup starting -> $Dest"

foreach ($db in @("prometheus_fire", "prometheus_sci")) {
    $out = Join-Path $Dest "$db.dump"
    & $PgDump -h $PgHost -U $PgUser -Fc -f $out $db
    if ($LASTEXITCODE -ne 0) {
        Add-Content $Log "[$Stamp] FAILED: $db (exit $LASTEXITCODE)"
        throw "pg_dump failed for $db"
    }
    $sz = [math]::Round((Get-Item $out).Length / 1MB, 1)
    Add-Content $Log "[$Stamp] OK: $db -> $sz MB"
}

# retention: keep newest 6 sets
$sets = Get-ChildItem $BackupRoot -Directory | Sort-Object Name -Descending
if ($sets.Count -gt 6) {
    $sets | Select-Object -Skip 6 | ForEach-Object {
        Add-Content $Log "[$Stamp] retention: removing $($_.Name)"
        Remove-Item $_.FullName -Recurse -Force
    }
}
Add-Content $Log "[$Stamp] backup complete"
Write-Host "backup complete -> $Dest"
