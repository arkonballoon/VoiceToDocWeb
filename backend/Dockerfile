FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# Python und System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    build-essential \
    ffmpeg \
    git \
    libavcodec-extra \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten installieren
COPY requirements.txt .

# PyTorch mit CUDA 12.2-Support installieren
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Andere Abhängigkeiten installieren
RUN pip3 install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY src/ ./src/
COPY data/ ./data/

# Port freigeben
EXPOSE 8000

# Standardbefehl
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 
