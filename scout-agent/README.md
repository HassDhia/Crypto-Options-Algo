# Scout Agent (Python)

**Path:** `scout-agent`

## Overview
Processes market ticks from Redpanda and updates Redis with latest bid prices.

## Development
| Purpose          | Command                               |
|------------------|---------------------------------------|
| Local execution  | `python __main__.py`                  |
| Unit tests       | `pytest tests/`                       |
| Integration tests| `pytest integration-tests/`           |
| Build Docker image| `docker build -t scout-agent .`      |

## Configuration
Environment variables:
- `REDIS_HOST`: Redis server host
- `REDIS_PORT`: Redis server port
- `KAFKA_BROKERS`: Comma-separated Kafka brokers

## Input/Output
- **Input:** Kafka topic `ticks.raw` (Avro format)
- **Output:** Redis keys `last_bid:{instrument}`
