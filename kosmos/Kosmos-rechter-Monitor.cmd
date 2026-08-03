@echo off
setlocal enabledelayedexpansion
title LEANS Kosmos

REM ===========================================================
REM  Startet den Kosmos im Vollbild auf dem RECHTEN Monitor.
REM
REM  Falls er auf dem falschen Bildschirm aufgeht:
REM  X unten auf die Breite deines LINKEN Monitors setzen.
REM    1920 = Full HD links   (Standard)
REM    2560 = WQHD links
REM    3840 = 4K links
REM  Zwei Monitore nebeneinander, rechter ist der zweite.
REM ===========================================================

set X=1920

set "SEITE=%~dp0index.html"
set "SEITE=%SEITE:\=/%"
set "URL=file:///%SEITE%"

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

start "" "%BROWSER%" --app="%URL%" --window-position=%X%,0 --start-fullscreen --new-window
exit /b 0
