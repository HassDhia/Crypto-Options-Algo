# Ingestor

**Path:** `services/ingestor`
**Language:** python

| Purpose          | Value                                             |
|------------------|---------------------------------------------------|
| Input            | Deribit WebSocket                                 |
| Output           | Redpanda topic `raw_ticks`                         |
| Local dev loop   | `poetry run python -m ingest.deribit_ws`          |
| Unit test cmd    | `pytest -q`                                       |
| Build image      | `docker buildx bake .`                            |
| Helm chart       | `services/ingestor/chart/`                         |
