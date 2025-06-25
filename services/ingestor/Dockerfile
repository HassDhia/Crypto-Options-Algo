FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry && poetry install --no-root
COPY ingest /app/ingest
CMD ["poetry", "run", "python", "-m", "ingest.deribit_ws"]
