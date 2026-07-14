<#
Run on the offline/airgapped machine after copying the wheelhouse folder here.
Usage:
  .\tools\install_from_wheels.ps1 -WheelDir .\wheelhouse
#>

param(
    [string]$WheelDir = "$(Join-Path $PSScriptRoot 'wheelhouse')"
)

if (-not (Test-Path $WheelDir)) { Write-Error "Wheel dir '$WheelDir' not found."; exit 1 }

Write-Host "Installing from wheels in $WheelDir"
py -3 -m pip install --no-index --find-links $WheelDir -r requirements.txt
Write-Host "Installation completed (if dependencies are satisfied)."
