# Prometheus Status Dashboard
# Run with: powershell -ExecutionPolicy Bypass -File "F:\Prometheus\scripts\status.ps1"

$width = 72

function Write-Header {
    param([string]$title)
    $line = "=" * $width
    $inner = " $title "
    $pad = [math]::Max(0, [math]::Floor(($width - $inner.Length) / 2))
    $padR = $width - $inner.Length - $pad
    Write-Host ""
    Write-Host $line -ForegroundColor Cyan
    Write-Host (" " * $pad + $inner + " " * $padR) -ForegroundColor White -BackgroundColor DarkBlue
    Write-Host $line -ForegroundColor Cyan
}

function Write-Divider {
    Write-Host ("-" * $width) -ForegroundColor DarkGray
}

function Format-Uptime {
    param([datetime]$startTime)
    $span = (Get-Date) - $startTime
    if ($span.TotalDays -ge 1) { return "{0}d {1}h {2}m" -f [int]$span.TotalDays, $span.Hours, $span.Minutes }
    if ($span.TotalHours -ge 1) { return "{0}h {1}m {2}s" -f [int]$span.TotalHours, $span.Minutes, $span.Seconds }
    return "{0}m {1}s" -f $span.Minutes, $span.Seconds
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host ""
Write-Host ("  PROMETHEUS STATUS DASHBOARD  --  " + $timestamp) -ForegroundColor Yellow
Write-Host ("=" * $width) -ForegroundColor Cyan

# GPU
Write-Header "  GPU  "

try {
    $gpuFields = "name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw"
    $gpuRaw = & nvidia-smi --query-gpu=$gpuFields --format=csv,noheader,nounits 2>$null

    if ($gpuRaw) {
        $gpuLines = $gpuRaw -split "`n" | Where-Object { $_.Trim() -ne "" }
        $gpuIndex = 0
        foreach ($line in $gpuLines) {
            $parts = $line -split "," | ForEach-Object { $_.Trim() }
            $gpuName   = $parts[0]
            $vramUsed  = $parts[1]
            $vramTotal = $parts[2]
            $gpuUtil   = $parts[3]
            $gpuTemp   = $parts[4]
            $gpuPower  = $parts[5]

            if ($gpuLines.Count -gt 1) {
                Write-Host ("  GPU " + $gpuIndex + " : " + $gpuName) -ForegroundColor Green
            } else {
                Write-Host ("  GPU     : " + $gpuName) -ForegroundColor Green
            }

            $vramPct = if (($vramTotal -as [double]) -gt 0) { [math]::Round(($vramUsed / $vramTotal) * 100, 1) } else { "?" }
            Write-Host ("  VRAM    : {0} / {1} MB  ({2}%)" -f $vramUsed, $vramTotal, $vramPct)
            Write-Host ("  Util    : {0}%" -f $gpuUtil)
            Write-Host ("  Temp    : {0} C" -f $gpuTemp)

            $powerDisplay = if ($gpuPower -match "^\d") { ("{0} W" -f [math]::Round(($gpuPower -as [double]), 1)) } else { "N/A" }
            Write-Host ("  Power   : " + $powerDisplay)
            $gpuIndex++
            if ($gpuIndex -lt $gpuLines.Count) { Write-Divider }
        }
    } else {
        Write-Host "  nvidia-smi returned no output." -ForegroundColor DarkYellow
    }
} catch {
    Write-Host ("  nvidia-smi not found or failed: " + $_) -ForegroundColor DarkYellow
}

# CPU
Write-Header "  CPU  "

try {
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    $loadPct = $cpu.LoadPercentage
    Write-Host ("  CPU     : " + $cpu.Name.Trim()) -ForegroundColor Green
    Write-Host ("  Load    : " + $loadPct + "%")
    Write-Host ("  Cores   : " + $cpu.NumberOfCores + " physical / " + $cpu.NumberOfLogicalProcessors + " logical")
} catch {
    Write-Host ("  Failed to query CPU: " + $_) -ForegroundColor Red
}

# MEMORY
Write-Header "  MEMORY  "

try {
    $os = Get-CimInstance Win32_OperatingSystem
    $totalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $freeGB  = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $usedGB  = [math]::Round($totalGB - $freeGB, 2)
    $usedPct = [math]::Round(($usedGB / $totalGB) * 100, 1)

    Write-Host ("  Total   : " + $totalGB + " GB") -ForegroundColor Green
    Write-Host ("  Used    : " + $usedGB + " GB  (" + $usedPct + "%)")
    Write-Host ("  Free    : " + $freeGB + " GB")
} catch {
    Write-Host ("  Failed to query memory: " + $_) -ForegroundColor Red
}

# PROMETHEUS PYTHON PROCESSES
Write-Header "  PROMETHEUS PYTHON PROCESSES  "

try {
    $allPyProcs = Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'python3.exe'" -ErrorAction SilentlyContinue
    $promProcs = $allPyProcs | Where-Object {
        $cl = $_.CommandLine
        $cl -and ($cl -match "F:\\\\Prometheus" -or $cl -match "F:/Prometheus" -or $cl -imatch "prometheus")
    }

    if ($promProcs -and @($promProcs).Count -gt 0) {
        Write-Host ("  {0,-8}  {1,-35}  {2,-12}  {3}" -f "PID", "Script", "Uptime", "CPU Time") -ForegroundColor Cyan
        Write-Divider
        foreach ($proc in $promProcs) {
            try {
                $psObj = Get-Process -Id $proc.ProcessId -ErrorAction SilentlyContinue
                $cmdLine = $proc.CommandLine

                $scriptName = "unknown"
                if ($cmdLine -match 'python[3]?\.exe[^"]*\s+"?([^"\s]+\.py)"?') {
                    $scriptName = [System.IO.Path]::GetFileName($Matches[1])
                } elseif ($cmdLine -match 'python[3]?\.exe\s+(-[mc]\s+\S+)') {
                    $scriptName = $Matches[1]
                } elseif ($cmdLine -match 'python[3]?\.exe\s+"?([^"\s]+)"?') {
                    $scriptName = [System.IO.Path]::GetFileName($Matches[1])
                }
                if ($scriptName.Length -gt 35) { $scriptName = $scriptName.Substring(0, 32) + "..." }

                $uptime  = if ($psObj) { Format-Uptime $psObj.StartTime } else { "?" }
                $cpuTime = if ($psObj) { $psObj.TotalProcessorTime.ToString("hh\:mm\:ss") } else { "?" }

                Write-Host ("  {0,-8}  {1,-35}  {2,-12}  {3}" -f $proc.ProcessId, $scriptName, $uptime, $cpuTime)
            } catch {
                Write-Host ("  {0,-8}  (error reading process)" -f $proc.ProcessId) -ForegroundColor DarkYellow
            }
        }
    } else {
        Write-Host "  No Prometheus Python processes running." -ForegroundColor DarkYellow
    }
} catch {
    Write-Host ("  Failed to query processes: " + $_) -ForegroundColor Red
}

# ALL PYTHON PROCESSES
Write-Header "  ALL PYTHON PROCESSES  "

try {
    $allPy = Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'python3.exe'" -ErrorAction SilentlyContinue

    if ($allPy -and @($allPy).Count -gt 0) {
        Write-Host ("  {0,-8}  {1}" -f "PID", "Command Line") -ForegroundColor Cyan
        Write-Divider
        foreach ($proc in ($allPy | Sort-Object ProcessId)) {
            $cmd = $proc.CommandLine
            if (-not $cmd) { $cmd = "(no command line available)" }
            if ($cmd.Length -gt 60) { $cmd = $cmd.Substring(0, 57) + "..." }
            Write-Host ("  {0,-8}  {1}" -f $proc.ProcessId, $cmd)
        }
        Write-Host ""
        Write-Host ("  Total Python processes: " + @($allPy).Count) -ForegroundColor DarkGray
    } else {
        Write-Host "  No Python processes running." -ForegroundColor DarkYellow
    }
} catch {
    Write-Host ("  Failed to query processes: " + $_) -ForegroundColor Red
}

Write-Host ""
Write-Host ("=" * $width) -ForegroundColor Cyan
Write-Host ""
