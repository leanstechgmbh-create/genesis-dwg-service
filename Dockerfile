FROM python:3.11-slim

# Build-Tools + libredwg-Abhängigkeiten (alles automatisch beim Image-Build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git pkg-config \
    libpcre2-dev perl \
 && rm -rf /var/lib/apt/lists/*

# LibreDWG aus Quelle bauen (DWG<->DXF Konverter) - laeuft im Cloud Build, kein manueller Download
RUN git clone --depth 1 --branch 0.13.3 https://github.com/LibreDWG/libredwg.git /tmp/libredwg \
 && cd /tmp/libredwg && mkdir build && cd build \
 && cmake .. -DLIBREDWG_LIBONLY=OFF -DBUILD_SHARED_LIBS=ON \
 && make -j"$(nproc)" && make install && ldconfig \
 && rm -rf /tmp/libredwg

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

ENV PORT=8080
EXPOSE 8080
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
