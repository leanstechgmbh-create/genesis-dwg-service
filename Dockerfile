FROM python:3.11-slim

# Build-Tools fuer LibreDWG
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git pkg-config libpcre2-dev perl \
 && rm -rf /var/lib/apt/lists/*

# LibreDWG bauen — WICHTIG: -Wno-error, sonst bricht der Build an einer Warnung ab (genau das ist vorher passiert)
RUN git clone --depth 1 --branch 0.13.3 https://github.com/LibreDWG/libredwg.git /tmp/libredwg \
 && cd /tmp/libredwg && mkdir build && cd build \
 && cmake .. -DLIBREDWG_LIBONLY=OFF -DBUILD_SHARED_LIBS=ON -DDISABLE_BINDINGS=ON \
      -DCMAKE_C_FLAGS="-Wno-error -w" -DCMAKE_BUILD_TYPE=Release \
 && make -j"$(nproc)" && make install && ldconfig \
 && rm -rf /tmp/libredwg

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py slack_bot.py dwg_core.py ./
COPY mailer/ ./mailer/
COPY website/ ./website/

ENV PORT=8080
EXPOSE 8080
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
