# System Architecture

```mermaid
graph LR
  WS[Deribit WS or mock] -->|ticks.raw| RP((Redpanda))
  RP -->|ticks.scouted| Scout
  Scout -->|Redis set last_bid| Redis
