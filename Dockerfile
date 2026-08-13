FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/avanegar/.cache/huggingface

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 avanegar \
    && mkdir -p "${HF_HOME}" \
    && chown -R avanegar:avanegar /home/avanegar

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY avanegar ./avanegar
RUN pip install ".[whisper]"

USER avanegar

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"]

CMD ["uvicorn", "avanegar.main:app", "--host", "0.0.0.0", "--port", "8000"]
