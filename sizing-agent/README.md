# Sizing Agent (Python)

**Path:** `sizing-agent`

## Overview
Calculates optimal position sizes based on market conditions and risk parameters.

## Development
| Purpose          | Command                               |
|------------------|---------------------------------------|
| Local execution  | `python __main__.py`                  |
| Unit tests       | `pytest tests/`                       |
| Integration tests| `pytest integration-tests/`           |
| Build Docker image| `docker build -t sizing-agent .`     |

## Configuration
Environment variables:
- `REDIS_HOST`: Redis server host
- `REDIS_PORT`: Redis server port
- `KAFKA_BROKERS`: Comma-separated Kafka brokers

## Input/Output
- **Input:** Market data (Redis) and risk parameters
- **Output:** Position sizing signals (Kafka topic `size.signals`)
