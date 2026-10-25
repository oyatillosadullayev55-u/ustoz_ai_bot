FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATABASE_PATH=/app/data/ustoz_ai.db

WORKDIR /app

RUN groupadd --system --gid 10001 ustozai \
    && useradd --system --uid 10001 --gid ustozai --create-home ustozai

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=ustozai:ustozai . .

RUN mkdir -p /app/data /app/logs \
    && chown -R ustozai:ustozai /app/data /app/logs

USER ustozai

EXPOSE 8080

CMD ["python", "bot.py"]
