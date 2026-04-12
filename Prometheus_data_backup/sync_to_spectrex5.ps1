# Sync Prometheus to SPECTREX5 share (mapped as Z:\)
# Run from PowerShell: .\sync_to_spectrex5.ps1

$src = "F:\Prometheus"
$dst = "Z:\"

Write-Host "=== Syncing $src -> $dst ===" -ForegroundColor Cyan
Write-Host "Started: $(Get-Date)"

# Directories to skip
$excludeDirs = @('.git', 'node_modules', '__pycache__', '.mypy_cache')

# Get all items, filter out excluded dirs
$items = Get-ChildItem -Path $src -Recurse -Force -ErrorAction SilentlyContinue | Where-Object {
    $dominated = $false
    foreach ($ex in $excludeDirs) {
        if ($_.FullName -match "\\$ex(\\|$)") { $dominated = $true; break }
    }
    -not $dominated -and $_.Extension -ne '.pyc'
}

$totalFiles = ($items | Where-Object { -not $_.PSIsContainer }).Count
Write-Host "Files to copy: $totalFiles"

$copied = 0
$errors = 0

foreach ($item in $items) {
    $relativePath = $item.FullName.Substring($src.Length)
    $destPath = Join-Path $dst $relativePath

    try {
        if ($item.PSIsContainer) {
            if (-not (Test-Path $destPath)) {
                New-Item -ItemType Directory -Path $destPath -Force | Out-Null
            }
        } else {
            $destDir = Split-Path $destPath -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item -Path $item.FullName -Destination $destPath -Force
            $copied++
            if ($copied % 500 -eq 0) {
                Write-Host "  $copied / $totalFiles files copied..."
            }
        }
    } catch {
        $errors++
        if ($errors -le 10) {
            Write-Host "  ERROR: $relativePath - $_" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Copied: $copied files"
Write-Host "Errors: $errors"
Write-Host "Finished: $(Get-Date)"
