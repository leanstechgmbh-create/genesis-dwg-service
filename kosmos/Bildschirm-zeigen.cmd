@echo off
title Bildschirm zeigen

REM ===========================================================
REM  Ein Klick: Bild vom rechten Monitor ins Google Drive.
REM  Danach kann Claude hineinschauen.
REM
REM  Es wird nur der rechte Bildschirm aufgenommen, nichts sonst,
REM  und immer in dieselbe Datei — es sammelt sich nichts an.
REM ===========================================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bildschirm.ps1"

if errorlevel 1 (
  echo.
  echo   Das hat nicht geklappt. Dann bitte mit der Windows-Taste + Druck
  echo   ein Bild machen und in den Chat ziehen.
  echo.
)

pause
