param(
    [string]$RunId = ("final_scene_demo_{0}" -f (Get-Date -Format "yyyyMMdd_HHmmss")),
    [int]$Duration = 1800,
    [int]$SyntheticCycles = 80,
    [switch]$NoDocker,
    [switch]$NoLiveInflux,
    [switch]$NoLiveAnalytics,
    [switch]$Continuous,
    [switch]$SkipPostPipeline,
    [string]$Python = "",
    [string]$PowerShell = ""
)

$ErrorActionPreference = "Stop"

function Resolve-CommandName {
    param([string[]]$Names)
    foreach ($Name in $Names) {
        if ([string]::IsNullOrWhiteSpace($Name)) {
            continue
        }
        $Command = Get-Command $Name -ErrorAction SilentlyContinue
        if ($Command) {
            return $Command.Source
        }
    }
    throw "None of these commands were found: $($Names -join ', ')"
}

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ComposeDir = Join-Path $ProjectRoot "infra\pak"
$CollectorHelper = Join-Path $ProjectRoot "scripts\coppeliasim\python\run_final_scene_full_collection.ps1"
$PipelineExporter = Join-Path $ProjectRoot "scripts\data_pipeline\run_pipeline_and_export.ps1"
$LiveAnalytics = Join-Path $ProjectRoot "scripts\data_pipeline\live_analytics_to_influx.py"
$RawPath = Join-Path $ProjectRoot "data\telemetry\vkr_raw\$RunId.jsonl"
$LogsDir = Join-Path $ProjectRoot "logs"
$LiveAnalyticsOut = Join-Path $LogsDir "$RunId.live_analytics.out.log"
$LiveAnalyticsErr = Join-Path $LogsDir "$RunId.live_analytics.err.log"
$PythonExe = Resolve-CommandName @($Python, "python", "python3")
$PowerShellExe = Resolve-CommandName @($PowerShell, "pwsh", "powershell")
$IsWindowsHost = ($PSVersionTable.PSEdition -eq "Desktop") -or ($IsWindows)

Write-Host "VKR PAK demo run"
Write-Host "Project: $ProjectRoot"
Write-Host "Run id: $RunId"
Write-Host "Raw telemetry: $RawPath"
Write-Host ""

if (-not $NoDocker) {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker command was not found. Install Docker Desktop or rerun with -NoDocker."
    }
    Write-Host "Starting InfluxDB and Grafana"
    docker compose -f (Join-Path $ComposeDir "docker-compose.yml") up -d
    Write-Host ""
}

Write-Host "Before collection:"
Write-Host "1. Open CoppeliaSim."
Write-Host "2. Load scenes\pred_final.ttt."
Write-Host "3. Keep simulation stopped until this script says it is waiting for start."
Write-Host ""

$collectorArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $CollectorHelper,
    "-RunId", $RunId,
    "-Duration", $Duration,
    "-Python", $PythonExe
)

if (-not $NoLiveInflux) {
    $collectorArgs += "-InfluxLive"
}

if ($Continuous) {
    $collectorArgs += "-Continuous"
}

$liveAnalyticsProcess = $null
try {
    if ((-not $NoLiveInflux) -and (-not $NoLiveAnalytics)) {
        New-Item -ItemType Directory -Force $LogsDir | Out-Null
        Write-Host "Starting live HI/RUL/NN analytics"
        Write-Host "Live analytics log: $LiveAnalyticsOut"
        $liveAnalyticsArgs = @(
            $LiveAnalytics,
            "--input", $RawPath,
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

    & $PowerShellExe @collectorArgs
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

if (-not $SkipPostPipeline) {
    Write-Host ""
    Write-Host "Running post-run analytics and InfluxDB export"
    & $PowerShellExe -ExecutionPolicy Bypass -File $PipelineExporter -InputPath $RawPath -RunId $RunId -SyntheticCycles $SyntheticCycles -Python $PythonExe
}

Write-Host ""
Write-Host "Done."
Write-Host "Grafana: http://localhost:3000"
Write-Host "InfluxDB: http://localhost:8086"
