# ===========================================================
#  Macht ein Bild vom RECHTEN Monitor und legt es im Google
#  Drive ab, damit Claude hineinschauen kann.
#
#  Wird von "Bildschirm-zeigen.cmd" aufgerufen — dieses Skript
#  nicht einzeln starten.
# ===========================================================

Add-Type -AssemblyName System.Windows.Forms, System.Drawing

# --- rechten Monitor bestimmen ---
$rechts = [System.Windows.Forms.Screen]::AllScreens | Sort-Object { $_.Bounds.X } | Select-Object -Last 1
$b = $rechts.Bounds

# --- Bild aufnehmen ---
$bild = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$stift = [System.Drawing.Graphics]::FromImage($bild)
$stift.CopyFromScreen($b.X, $b.Y, 0, 0, $bild.Size)

# --- Ablageort suchen: Google Drive, sonst Desktop ---
$kandidaten = @()
foreach ($laufwerk in 'G', 'H', 'I', 'J', 'K') {
    $kandidaten += "${laufwerk}:\Meine Ablage"
    $kandidaten += "${laufwerk}:\My Drive"
}
$kandidaten += Join-Path $env:USERPROFILE 'Google Drive\Meine Ablage'
$kandidaten += Join-Path $env:USERPROFILE 'Google Drive\My Drive'
$kandidaten += Join-Path $env:USERPROFILE 'Meine Ablage'

$ziel = $null
foreach ($ort in $kandidaten) {
    if (Test-Path -LiteralPath $ort) {
        $ziel = Join-Path $ort 'Leans Tech GmbH\LEANS Kosmos'
        break
    }
}

$imDrive = $true
if (-not $ziel) {
    $ziel = [Environment]::GetFolderPath('Desktop')
    $imDrive = $false
}
if (-not (Test-Path -LiteralPath $ziel)) {
    New-Item -ItemType Directory -Path $ziel -Force | Out-Null
}

# --- speichern ---
$datei = Join-Path $ziel 'bildschirm.png'
$bild.Save($datei, [System.Drawing.Imaging.ImageFormat]::Png)
$stift.Dispose()
$bild.Dispose()

Write-Host ""
Write-Host "  Rechter Monitor: $($b.Width)x$($b.Height), beginnt bei X=$($b.X)"
Write-Host "  Bild: $datei"
Write-Host ""
if ($imDrive) {
    Write-Host "  Liegt im Google Drive. Sag Claude kurz Bescheid," -ForegroundColor Green
    Write-Host "  sobald der Drive-Haken am Ordner gruen ist." -ForegroundColor Green
} else {
    Write-Host "  Google Drive nicht als Laufwerk gefunden." -ForegroundColor Yellow
    Write-Host "  Das Bild liegt auf dem Desktop — bitte in den Chat ziehen." -ForegroundColor Yellow
}
Write-Host ""
