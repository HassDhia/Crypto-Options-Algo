# Risk Agent (Python)

**Path:** `risk-agent`

## Overview
The Risk Agent enforces hard risk limits such as maximum notional exposure and maximum position size. It consumes scouted trade candidates from the `ticks.scouted` topic, checks proposed trades against configured risk limits, and publishes risk alerts to `risk.alerts` for any violations.

## Development
| Purpose          | Command                               |
|------------------|---------------------------------------|
| Local execution  | `python __main__.py`                  |
| Unit tests       | `pytest tests/`                       |
| Integration tests| `pytest integration-tests/`           |
| Build Docker image| `docker build -t risk-agent .`       |

## Configuration
Environment variables:
- `REDIS_HOST`: Redis server host (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `RISK_LIMITS_JSON`: JSON string of risk limits with properties:
  - `max_notional`: Maximum notional exposure per trade
  - `max_position_contracts`: Maximum contracts per position

## Input/Output
- **Input:** Redis portfolio data
- **Output:** Risk violation alerts (Kafka topic `risk.alerts`)
