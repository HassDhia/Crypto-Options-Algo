# Crypto Options Algo 🚀

**Production-grade, AI-assisted BTC-options trading stack**
Low-latency execution in AMS1; Python / TypeScript / Go micro-services on GKE; fully-automated RL parameter tuning.

---

## 🌐 High-Level Architecture

```mermaid
graph LR
    subgraph Edge POP (AMS1)
        A[Execution Agent<br>(Go)]
    end

    subgraph Core Cluster (GKE)
        B[Data Ingestor] --> C[IV Surface API] --> D[Scout Agent]
        E[Regime Detector] --> F[Risk Agent]
        D --> F --> G[Sizing Agent] --> A
        G -->|trade intent| A

        subgraph Infra
            H[Redpanda] & I[Postgres / NocoDB] & J[Redis Param Server]
        end
    end
````

*Full component responsibilities, data contracts, SLOs, and rollout plan live in [`docs/architecture.md`](docs/architecture.md).*

---

## 🗂 Directory Structure (initial scaffold)

```
.
├── docs/
│   └── architecture.md        # ← paste the full spec here (next commit)
├── scout-agent/               # TypeScript
├── risk-agent/                # TypeScript
├── sizing-agent/              # TypeScript
├── execution-agent/           # Go
├── requirements.txt           # Python deps (IV Surface, Regime Detector, RL-Tuner)
├── package.json               # npm workspaces root
├── go.work                    # Go workspace (optional)
├── .pre-commit-config.yaml    # lint / fmt hooks
└── .gitignore
```

*(Agent folders are empty for now; CI skips their build until code lands.)*

---

## ⚡ Quick Start (local dev)

```bash
# clone & bootstrap
git clone git@github.com:HassDhia/Crypto-Options-Algo.git
cd Crypto-Options-Algo

# Python services
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# TS agents
npm ci --workspaces
npm run test --workspaces

# Go execution agent
cd execution-agent && go run ./cmd/sim   # connects to Deribit testnet
```

> **Note:** Cloud infra (GKE + AMS1 VPS) lives under `/infra/terraform`.
> Secrets are injected via GitHub Actions → GCP Secret Manager.

---

## 🧪 Testing

The project includes a comprehensive testing system:

```bash
# Run unit tests for all components
make test-unit

# Run integration tests (requires Docker)
make test-integration

# Clean up test artifacts
make clean
```

The integration test environment uses Docker Compose to spin up:
- Redpanda (Kafka-compatible message broker)
- PostgreSQL database
- Redis parameter server
- All agents and services
- A test runner container

## 🛠 CI / CD

| Stage             | Tooling                                          |
| ----------------- | ------------------------------------------------ |
| **Build**         | GitHub Actions (`docker buildx`)                 |
| **Test**          | Jest, PyTest, golangci-lint, Integration Tests   |
| **Deploy**        | Helm + Terraform (`gke-dev` → `gke-prod`)        |
| **Observability** | Prometheus & Grafana dashboards auto-provisioned |

---

## 🤝 Contributing

1. **Fork** → feature branch → PR.
2. Run `pre-commit run --all-files`; lint must pass.
3. Merge into **`main`** auto-deploys to staging (`gke-dev`).

---

**MIT License** • © 2025 Hass Dhia
