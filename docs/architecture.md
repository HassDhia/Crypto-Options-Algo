# System Architecture

```mermaid
graph LR
  WS[Deribit WS or mock] -->|ticks.raw| RP((Redpanda))
  RP -->|ticks.scouted| Scout
  Scout -->|Redis set last_bid| Redis
  Redis -->|market data| Risk
  Redis -->|market data| Sizing
  Risk -->|risk signals| Execution
  Sizing -->|size signals| Execution
  Execution -->|orders| Exchange
  Exchange -->|fills| WS

## Components

### Ingestor Service
- Connects to Deribit WebSocket
- Publishes raw ticks to Redpanda (ticks.raw)

### Scout Agent
- Consumes ticks.raw
- Updates Redis with latest bid prices
- Publishes processed ticks (ticks.scouted)

### Risk Agent
- Monitors portfolio exposure
- Enforces risk limits
- Publishes risk alerts (risk.alerts)

### Sizing Agent
- Calculates position sizes
- Considers market conditions and risk
- Publishes size signals (size.signals)

### Execution Agent
- Processes trade signals
- Manages order execution
- Handles exchange communication

## Data Flow
1. Market data enters via WebSocket
2. Processed through pipeline (Scout → Risk → Sizing → Execution)
3. Orders executed on exchange
4. Cycle repeats with new market data
