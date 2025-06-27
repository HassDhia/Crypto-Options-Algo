# Risk Agent (Python)

**Path:** `risk-agent`

## Overview
Monitors portfolio risk and enforces risk limits.

## Development
| Purpose          | Command                               |
|------------------|---------------------------------------|
| Local execution  | `python __main__.py`                  |
| Unit tests       | `pytest tests/`                       |
| Integration tests| `pytest integration-tests/`           |
| Build Docker image| `docker build -t risk-agent .`       |

## Configuration
Environment variables:
- `REDIS_HOST`: Redis server host
- `REDIS_PORT`: Redis server port
- `RISK_LIMITS_JSON`: JSON string of risk limits

## Input/Output
- **Input:** Redis portfolio data
- **Output:** Risk violation alerts (Kafka topic `risk.alerts`)
