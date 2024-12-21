FROM python:3.10-slim

WORKDIR /app

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    git \
    libavcodec-extra \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten installieren
COPY requirements.txt .

# Pip Cache löschen und Pakete neu installieren
RUN pip cache purge && \
    pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Anwendungscode kopieren
COPY src/ ./src/
COPY data/ ./data/

# Port freigeben
EXPOSE 8000

# Standardbefehl
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 