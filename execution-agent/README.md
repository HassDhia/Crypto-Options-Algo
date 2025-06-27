# Execution Agent (Python)

**Path:** `execution-agent`

## Overview
Processes trade signals and executes orders through exchange APIs.

## Development
| Purpose          | Command                               |
|------------------|---------------------------------------|
| Local execution  | `python __main__.py`                  |
| Unit tests       | `pytest tests/`                       |
| Integration tests| `pytest integration-tests/`           |
| Build Docker image| `docker build -t execution-agent .`  |

## Configuration
Environment variables:
- `EXCHANGE_API_KEY`: Exchange API key
- `EXCHANGE_SECRET`: Exchange API secret
- `KAFKA_BROKERS`: Comma-separated Kafka brokers

## Input/Output
- **Input:** Kafka topic `trade.signals` (Avro format)
- **Output:** Exchange order executions
