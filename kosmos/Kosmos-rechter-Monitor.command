#!/bin/bash
# ===========================================================
#  LEANS Kosmos — Vollbild auf dem rechten Monitor (macOS)
#
#  Falls er auf dem falschen Bildschirm aufgeht:
#  X unten auf die Breite deines LINKEN Monitors setzen.
#  Danach im Fenster einmal F drücken für echtes Vollbild.
# ===========================================================

X=1920

SEITE="$(cd "$(dirname "$0")" && pwd)/index.html"
URL="file://$SEITE"

if [ -d "/Applications/Google Chrome.app" ]; then
  open -na "Google Chrome" --args --app="$URL" --window-position=$X,0 --start-fullscreen --new-window
elif [ -d "/Applications/Microsoft Edge.app" ]; then
  open -na "Microsoft Edge" --args --app="$URL" --window-position=$X,0 --start-fullscreen --new-window
else
  echo "Weder Chrome noch Edge gefunden — index.html von Hand öffnen."
  open "$URL"
fi
