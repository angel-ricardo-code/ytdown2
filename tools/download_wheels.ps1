<#
Run this on a machine with Internet access to download all wheels required by requirements.txt
Usage:
  .\tools\download_wheels.ps1 -OutDir C:\path\to\wheelhouse
#>

param(
    [string]$OutDir = "$(Join-Path $PSScriptRoot 'wheelhouse')"
)

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

Write-Host "Downloading wheels into $OutDir"
py -3 -m pip download -r requirements.txt -d $OutDir
Write-Host "Done. Copy the '$OutDir' folder to the target machine and run the installer script."
