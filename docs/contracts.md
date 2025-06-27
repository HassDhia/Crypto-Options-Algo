# Schema Contracts

## Message Schemas

### ticks.raw (WebSocket → Redpanda)
```json
{
  "type": "record",
  "name": "Tick",
  "fields": [
    {"name": "instrument", "type": "string"},
    {"name": "bid", "type": "double"},
    {"name": "ask", "type": "double"},
    {"name": "timestamp", "type": "long"}
  ]
}
```

### ticks.scouted (Redpanda → Scout)
```json
{
  "type": "record",
  "name": "ScoutedTick",
  "fields": [
    {"name": "instrument", "type": "string"},
    {"name": "bid", "type": "double"},
    {"name": "ask", "type": "double"},
    {"name": "timestamp", "type": "long"},
    {"name": "scout_processed_at", "type": "long"}
  ]
}
```

### risk.alerts (Risk → Execution)
```json
{
  "type": "record",
  "name": "RiskAlert",
  "fields": [
    {"name": "instrument", "type": "string"},
    {"name": "risk_level", "type": {"type": "enum", "name": "RiskLevel", "symbols": ["LOW", "MEDIUM", "HIGH"]}},
    {"name": "recommended_action", "type": {"type": "enum", "name": "Action", "symbols": ["HOLD", "REDUCE", "CLOSE"]}},
    {"name": "timestamp", "type": "long"}
  ]
}
```

### size.signals (Sizing → Execution)
```json
{
  "type": "record",
  "name": "SizeSignal",
  "fields": [
    {"name": "instrument", "type": "string"},
    {"name": "size", "type": "double"},
    {"name": "timestamp", "type": "long"}
  ]
}
```

## Redis Data Structures

### last_bid:{instrument}
- Type: String
- Value: Last bid price (float)
- TTL: 1 hour

## API Contracts

### Scout Agent API
- **Input:** Consumes ticks.raw from Redpanda
- **Output:** Writes to Redis (last_bid keys), produces ticks.scouted

### Risk Agent API
- **Input:** Reads Redis market data
- **Output:** Produces risk.alerts

### Sizing Agent API
- **Input:** Reads Redis market data and risk parameters
- **Output:** Produces size.signals

### Execution Agent API
- **Input:** Consumes size.signals and risk.alerts
- **Output:** Executes orders via exchange API
