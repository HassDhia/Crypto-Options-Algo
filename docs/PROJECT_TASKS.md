# Project Tasks (v1.0 Roadmap)

## Task 1 – Infrastructure
- **1-1 GKE Terraform module** – create Kubernetes cluster in `europe-west1` *(done)*
- **1-2 Edge VPS Terraform** – provision AMS1 VPS for latency-critical execution
- **1-3 Helmfile data plane** – deploy Redpanda, Postgres, Redis, Prometheus and Grafana on GKE
- **1-4 CI pipeline** – wire Terraform + Helmfile stages

## Task 2 – Core Services
- **2-1 IV Surface API** – SVI-J surface fit service
- **2-2 Regime Detector** – HMM-based market regime service
- **2-3 RL Tuner** – reinforcement learning parameter tuner

## Task 3 – Trading Agents
- **3-1 Data Ingestor** – Deribit WebSocket → Redpanda
- **3-2 Scout Agent** – opportunity scanner
- **3-3 Risk Agent** – risk caps and limits
- **3-4 Sizing Agent** – Bayesian-Kelly bet size calculator
- **3-5 Execution Agent** – low-latency order execution in AMS1

Each task should be tracked as a GitHub issue and linked in PR descriptions so progress can be aggregated automatically.
