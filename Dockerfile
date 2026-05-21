# ---- Stage 1: builder ----
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/app/.local -r requirements.txt

# ---- Stage 2: runtime ----
FROM python:3.12-slim AS runtime

RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser \
    && mkdir -p /app/data && chown -R appuser:appuser /app

RUN touch /app/data/users.txt /app/data/previous_data.json

WORKDIR /app

COPY --from=builder /app/.local /app/.local

COPY tradeparse.py config.ini ./
COPY config/ ./config/
COPY bot/ ./bot/
COPY parsing/ ./parsing/
COPY db/ ./db/
COPY logger/ ./logger/
COPY entrypoint.sh ./entrypoint.sh

RUN chmod +x entrypoint.sh

ENV PATH="/app/.local/bin:$PATH"
ENV PYTHONPATH="/app/.local/lib/python3.12/site-packages"
ENV PYTHONUNBUFFERED=1

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "tradeparse.py"]
