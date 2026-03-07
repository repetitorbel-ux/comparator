param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

& $Python -m PyInstaller --noconfirm --clean file_compare_tc.spec

Write-Host "Build complete. Check dist\\FileCompareTC\\ or dist\\FileCompareTC.exe depending on PyInstaller mode."
