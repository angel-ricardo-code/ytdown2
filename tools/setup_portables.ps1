<#
Setup portables: Python embeddable, FFmpeg static, yt-dlp.exe

This script will:
 - create tools/portable
 - download the chosen zips/exes if missing
 - extract archives
 - attempt to bootstrap pip into the embeddable Python

Run in PowerShell from the repository root:
  .\tools\setup_portables.ps1
#>

param()

Set-StrictMode -Version Latest

$base = Join-Path $PSScriptRoot "portable"
if (-not (Test-Path $base)) { New-Item -ItemType Directory -Path $base | Out-Null }

$files = @{
    python_zip = @{ url = 'https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip'; dest = Join-Path $base 'python-embed.zip' }
    ffmpeg_zip = @{ url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'; dest = Join-Path $base 'ffmpeg.zip' }
    yt_dlp = @{ url = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe'; dest = Join-Path $base 'yt-dlp.exe' }
    get_pip = @{ url = 'https://bootstrap.pypa.io/get-pip.py'; dest = Join-Path $base 'get-pip.py' }
}

Function Download-IfMissing($url, $dest) {
    if (Test-Path $dest) { Write-Host "Exists: $dest"; return }
    Write-Host "Downloading $url -> $dest"
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
}

foreach ($k in $files.Keys) {
    $entry = $files[$k]
    Download-IfMissing $entry.url $entry.dest
}

# Extract python embeddable
$pyDir = Join-Path $base 'python'
if (-not (Test-Path $pyDir)) {
    Write-Host "Extracting Python embed to $pyDir"
    Expand-Archive -LiteralPath $files.python_zip.dest -DestinationPath $pyDir -Force
}

# Extract ffmpeg (take first ffmpeg.exe found)
$ffDir = Join-Path $base 'ffmpeg'
if (-not (Test-Path $ffDir)) {
    Write-Host "Extracting FFmpeg to $ffDir"
    Expand-Archive -LiteralPath $files.ffmpeg_zip.dest -DestinationPath $ffDir -Force
}

# Try to ensure pip in embeddable Python
$pythonExe = Get-ChildItem -Path $pyDir -Filter 'python.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $pythonExe) {
    Write-Warning "python.exe not found in the embedded distribution. Pip bootstrap may fail."
} else {
    $py = $pythonExe.FullName
    Write-Host "Found python: $py"
    Write-Host "Attempting to run ensurepip..."
    & $py -m ensurepip 2>&1 | Write-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ensurepip failed, attempting get-pip.py"
        & $py $files.get_pip.dest 2>&1 | Write-Host
    }
}

Write-Host "Portable setup complete. Binaries located in: $base"
