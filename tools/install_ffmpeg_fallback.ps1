<#
Fallback installer for ffmpeg that tries several strategies:
 - If a portable build is downloadable, fetch and extract to tools/portable/ffmpeg
 - If downloads fail (no network), print manual steps and alternative mirrors

Run: .\tools\install_ffmpeg_fallback.ps1
#>

param()

Set-StrictMode -Version Latest

$base = Join-Path $PSScriptRoot 'portable'
if (-not (Test-Path $base)) { New-Item -ItemType Directory -Path $base | Out-Null }

function Try-Download($url, $out) {
    try {
        Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing -ErrorAction Stop
        return $true
    } catch {
        Write-Host "Download failed: $url"
        return $false
    }
}

$candidates = @(
    'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
    'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z',
    'https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z'
)

$tmp = Join-Path $env:TEMP 'ffmpeg_download'
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
New-Item -ItemType Directory -Path $tmp | Out-Null

$downloaded = $false
foreach ($u in $candidates) {
    $out = Join-Path $tmp ([IO.Path]::GetFileName($u))
    if (Try-Download $u $out) { $downloaded = $true; $archive = $out; break }
}

if ($downloaded) {
    Write-Host "Extracting $archive"
    try {
        Expand-Archive -LiteralPath $archive -DestinationPath $base -Force
    } catch {
        Write-Host "Extraction failed (maybe 7z). Please extract manually and place ffmpeg.exe under tools\portable\ffmpeg\bin"
    }
    Write-Host "Busca ffmpeg.exe en $base y muévelo a tools\portable\ffmpeg\bin si es necesario"
} else {
    Write-Host "No fue posible descargar automáticamente ffmpeg desde mirrors preconfigurados."
    Write-Host "Por favor descarga manualmente uno de estos enlaces y descomprímelo en tools\\portable\\ffmpeg\\bin:"
    Write-Host " - https://www.gyan.dev/ffmpeg/builds/"
    Write-Host " - https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    Write-Host " - https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z"
}

Write-Host "Después de colocar ffmpeg.exe en tools\portable\ffmpeg\bin, ejecuta: ffmpeg -version para verificar."
