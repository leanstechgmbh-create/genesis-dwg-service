@echo off
setlocal enabledelayedexpansion
title LEANS Kosmos

REM ===========================================================
REM  Startet den Kosmos auf dem RECHTEN Monitor.
REM
REM  Der rechte Bildschirm wird selbst ermittelt — normalerweise
REM  ist hier nichts einzustellen.
REM
REM  Nur falls es doch daneben geht: unten MANUELL auf die Breite
REM  des LINKEN Monitors setzen, z. B.  set "MANUELL=1920"
REM    1920 = Full HD links   2560 = WQHD links   3840 = 4K links
REM ===========================================================

set "MANUELL="

set "SEITE=%~dp0index.html"
set "SEITE=%SEITE:\=/%"
set "URL=file:///%SEITE%#vollbild"

REM ---------- Bildschirm bestimmen ----------
set "X=1920"
set "Y=0"
set "BREITE="
set "HOEHE="

if defined MANUELL (
  set "X=%MANUELL%"
) else (
  for /f "tokens=1-4" %%a in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; $s = [System.Windows.Forms.Screen]::AllScreens ^| Sort-Object { $_.Bounds.X } ^| Select-Object -Last 1; '{0} {1} {2} {3}' -f $s.Bounds.X, $s.Bounds.Y, $s.Bounds.Width, $s.Bounds.Height" 2^>nul') do (
    set "X=%%a"
    set "Y=%%b"
    set "BREITE=%%c"
    set "HOEHE=%%d"
  )
)

REM ---------- Browser suchen ----------
set "BROWSER="
for %%B in (chrome.exe msedge.exe) do (
  if not defined BROWSER (
    for /f "delims=" %%P in ('where %%B 2^>nul') do if not defined BROWSER set "BROWSER=%%P"
  )
)

if not defined BROWSER (
  if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "BROWSER=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
)
if not defined BROWSER (
  if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "BROWSER=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
)
if not defined BROWSER (
  if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "BROWSER=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
)

if not defined BROWSER (
  echo.
  echo   Weder Chrome noch Edge gefunden.
  echo   Dann bitte index.html von Hand oeffnen und F11 druecken.
  echo.
  pause
  exit /b 1
)

REM ---------- Starten ----------
echo   Rechter Monitor: X=!X!  Y=!Y!  !BREITE!x!HOEHE!

if defined BREITE (
  start "" "%BROWSER%" --app="%URL%" --window-position=!X!,!Y! --window-size=!BREITE!,!HOEHE! --new-window
) else (
  start "" "%BROWSER%" --app="%URL%" --window-position=!X!,!Y! --start-fullscreen --new-window
)

REM Fenster geht auf, Fenster ist da: einmal ins Bild klicken -> Vollbild.
exit /b 0
