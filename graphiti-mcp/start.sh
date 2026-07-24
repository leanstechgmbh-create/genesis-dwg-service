#!/usr/bin/env bash
# Startet nginx (Geheimpfad-Proxy) + Graphiti-MCP-Server in einem Container.
set -euo pipefail

: "${MCP_PATH_SECRET:?MCP_PATH_SECRET fehlt — GitHub-Secret GRAPHITI_MCP_PATH_SECRET setzen (siehe GRAPHITI_SETUP.md)}"
: "${NEO4J_URI:?NEO4J_URI fehlt — GitHub-Secret GRAPHITI_NEO4J_URI setzen (siehe GRAPHITI_SETUP.md)}"
: "${NEO4J_PASSWORD:?NEO4J_PASSWORD fehlt — GitHub-Secret GRAPHITI_NEO4J_PASSWORD setzen (siehe GRAPHITI_SETUP.md)}"
: "${OPENAI_API_KEY:?OPENAI_API_KEY fehlt — GitHub-Secret GRAPHITI_OPENAI_API_KEY setzen (siehe GRAPHITI_SETUP.md)}"

# Cloud Run schickt Traffic an $PORT — dort lauscht nginx.
LISTEN_PORT="${PORT:-8080}"
export LISTEN_PORT
envsubst '${LISTEN_PORT} ${MCP_PATH_SECRET}' \
  < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# PORT entfernen, damit der MCP-Server auf seinem Standard 8000 bleibt
# und nicht mit nginx kollidiert.
unset PORT

cd /app/mcp
UV_BIN="$(command -v uv || echo /root/.local/bin/uv)"
"$UV_BIN" run --no-sync main.py &
MCP_PID=$!

nginx -g 'daemon off;' &
NGINX_PID=$!

# Stirbt einer der beiden Prozesse, beendet sich der Container —
# Cloud Run startet ihn dann frisch.
wait -n "$MCP_PID" "$NGINX_PID"
exit 1
