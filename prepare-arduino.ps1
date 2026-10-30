$ErrorActionPreference = 'Stop'
$sketchDirectory = Join-Path $PSScriptRoot 'arduino/Iris'
New-Item -ItemType Directory -Force -Path $sketchDirectory | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'firmware/src/main.cpp') -Destination (Join-Path $sketchDirectory 'Iris.ino')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'firmware/include/config.h') -Destination $sketchDirectory
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'firmware/include/audio_codec.h') -Destination $sketchDirectory
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'firmware/include/mic_stream.h') -Destination $sketchDirectory
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'firmware/include/secrets.example.h') -Destination $sketchDirectory
Write-Output 'Open arduino/Iris/Iris.ino. Create secrets.h beside it from secrets.example.h, then enter your Wi-Fi and host address.'
