param(
    [string]$RunId = "final_scene_full_01",
    [int]$Duration = 1800,
    [int]$SyntheticCycles = 80,
    [switch]$InfluxLive,
    [switch]$LiveAnalytics,
    [switch]$Continuous,
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"

function Resolve-PythonCommand {
    param([string]$Preferred)
    foreach ($Name in @($Preferred, "python", "python3")) {
        if ([string]::IsNullOrWhiteSpace($Name)) {
            continue
        }
        $Command = Get-Command $Name -ErrorAction SilentlyContinue
        if ($Command) {
            return $Command.Source
        }
    }
    throw "Python was not found. Install Python 3 and make sure python or python3 is on PATH."
}

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$OutputPath = Join-Path $ProjectRoot "data\telemetry\vkr_raw\$RunId.jsonl"
$Collector = Join-Path $PSScriptRoot "collect_final_scene_telemetry.py"
$LiveAnalyticsScript = Join-Path $ProjectRoot "scripts\data_pipeline\live_analytics_to_influx.py"
$LogsDir = Join-Path $ProjectRoot "logs"
$LiveAnalyticsOut = Join-Path $LogsDir "$RunId.live_analytics.out.log"
$LiveAnalyticsErr = Join-Path $LogsDir "$RunId.live_analytics.err.log"
$PythonExe = Resolve-PythonCommand $Python
$IsWindowsHost = ($PSVersionTable.PSEdition -eq "Desktop") -or ($IsWindows)

Write-Host "VKR final scene telemetry collection"
Write-Host "Run id: $RunId"
Write-Host "Output: $OutputPath"
Write-Host ""
Write-Host "1. Keep CoppeliaSim open with scenes\pred_final.ttt."
Write-Host "2. Start this script while simulation is STOPPED."
Write-Host "3. Wait for: Waiting for CoppeliaSim simulation start."
Write-Host "4. Press Play in CoppeliaSim."
if ($Continuous) {
    Write-Host "5. Continuous mode is enabled: the script runs until Duration seconds or Ctrl+C."
} else {
    Write-Host "5. The script stops automatically after cycle_complete or Duration seconds."
}
Write-Host "6. Use -InfluxLive to stream raw telemetry directly to InfluxDB/Grafana during simulation."
Write-Host "7. Use -LiveAnalytics together with -InfluxLive to stream HI/RUL/NN panels during simulation."
Write-Host ""

$CollectorArgs = @(
    $Collector,
    "--duration", $Duration,
    "--run-id", $RunId,
    "--output", $OutputPath,
    "--wait-for-simulation"
)

if (-not $Continuous) {
    $CollectorArgs += "--stop-on-phase"
    $CollectorArgs += "cycle_complete"
    $CollectorArgs += "--stop-delay"
    $CollectorArgs += "0.2"
}

if ($InfluxLive) {
    $CollectorArgs += "--influx-live"
}

$liveAnalyticsProcess = $null
try {
    if ($InfluxLive -and $LiveAnalytics) {
        New-Item -ItemType Directory -Force $LogsDir | Out-Null
        Write-Host "Starting live HI/RUL/NN analytics"
        Write-Host "Live analytics log: $LiveAnalyticsOut"
        $liveAnalyticsArgs = @(
            $LiveAnalyticsScript,
            "--input", $OutputPath,
            "--run-id", $RunId,
            "--synthetic-cycles", $SyntheticCycles,
            "--wait-for-input",
            "--idle-timeout", "45"
        )
        $startArgs = @{
            FilePath = $PythonExe
            ArgumentList = $liveAnalyticsArgs
            WorkingDirectory = $ProjectRoot
            RedirectStandardOutput = $LiveAnalyticsOut
            RedirectStandardError = $LiveAnalyticsErr
            PassThru = $true
        }
        if ($IsWindowsHost) {
            $startArgs["WindowStyle"] = "Hidden"
        }
        $liveAnalyticsProcess = Start-Process @startArgs
        Write-Host ""
    }

    & $PythonExe @CollectorArgs
}
finally {
    if ($liveAnalyticsProcess -and -not $liveAnalyticsProcess.HasExited) {
        Write-Host "Stopping live analytics"
        Start-Sleep -Seconds 3
        if (-not $liveAnalyticsProcess.HasExited) {
            Stop-Process -Id $liveAnalyticsProcess.Id -Force
        }
    }
}
