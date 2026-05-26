param(
    [string]$InputPath = "data\telemetry\vkr_raw\final_scene_full_02.jsonl",
    [string]$RunId = "final_scene_full_02",
    [int]$SyntheticCycles = 80,
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

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Pipeline = Join-Path $ProjectRoot "scripts\data_pipeline\run_file_pipeline.py"
$Exporter = Join-Path $ProjectRoot "scripts\data_pipeline\export_to_influx.py"
$PythonExe = Resolve-PythonCommand $Python

Write-Host "Running VKR file pipeline"
Write-Host "Input: $InputPath"
Write-Host "Run id: $RunId"

& $PythonExe $Pipeline --inputs $InputPath --run-id $RunId --cycles $SyntheticCycles

Write-Host ""
Write-Host "Exporting latest pipeline outputs to InfluxDB"
& $PythonExe $Exporter --timestamp-mode align-end
