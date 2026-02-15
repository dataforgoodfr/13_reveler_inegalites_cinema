FROM python:3.11-slim

#RUN pip install --no-cache-dir "uv~=0.1"
RUN pip install "uv~=0.1"

#RUN --mount=from=uv,source=/uv,target=./uv \
#    ./uv venv /opt/venv
    
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    cmake \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN uv pip install --system -r requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
RUN uv pip install --system torch torchvision --index-url https://download.pytorch.org/whl/cu118
#RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

RUN bash install/download_models.sh

#ENTRYPOINT ["python", "main.py"]
