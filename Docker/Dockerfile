FROM ghcr.io/astral-sh/uv:0.6.14-python3.10-bookworm


WORKDIR /app/src


RUN apt-get update && apt-get install -y \
    build-essential \
    libavif-dev pkg-config \
    libjpeg-dev \
    gcc unzip zip \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* 
       

COPY src/requirements.txt /app/requirements.txt



RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r /app/requirements.txt --system


COPY src/ /app/src/


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 



