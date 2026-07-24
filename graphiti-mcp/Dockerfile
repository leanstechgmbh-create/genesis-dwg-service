# Graphiti-MCP-Server (Gedaechtnis/Wissensgraph) fuer Cloud Run.
# Basis: offizielles Standalone-Image von getzep/graphiti (nur MCP-Server,
# ohne eingebettete DB). Davor haengt ein nginx mit Geheimpfad, weil
# claude.ai-Custom-Connectors keine Auth-Header mitschicken koennen.
FROM zepai/knowledge-graph-mcp:standalone

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base \
    && rm -rf /var/lib/apt/lists/*

COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY config.yaml /app/mcp/config/config.yaml
COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV CONFIG_PATH=/app/mcp/config/config.yaml \
    GRAPHITI_TELEMETRY_ENABLED=false

EXPOSE 8080
ENTRYPOINT ["/bin/bash", "/start.sh"]
