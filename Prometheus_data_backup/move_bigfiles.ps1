$src = "F:\bigfiles"
$dst = "H:\bigfiles"

if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Path $dst | Out-Null }

Get-ChildItem -Path $src -File | ForEach-Object {
    $dstFile = Join-Path $dst $_.Name
    if (Test-Path $dstFile) {
        $dstSize = (Get-Item $dstFile).Length
        if ($dstSize -ge $_.Length) {
            Write-Host "Same/larger exists, deleting source: $($_.Name)"
            Remove-Item $_.FullName
        } else {
            Write-Host "Partial exists, replacing: $($_.Name)"
            Remove-Item $dstFile
            Move-Item -Path $_.FullName -Destination $dstFile
        }
    } else {
        Write-Host "Moving: $($_.Name)"
        Move-Item -Path $_.FullName -Destination $dstFile
    }
    Start-Sleep -Seconds 2
}

Write-Host "Done."
