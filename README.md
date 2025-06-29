# Crypto Options Algo 🚀

**Production-grade, AI-assisted BTC-options trading stack**
Low-latency execution in AMS1; Python micro-services on GKE; fully-automated RL parameter tuning.

---

## 🌐 High-Level Architecture

```mermaid
graph LR
    subgraph Edge POP (AMS1)
        A[Execution Agent<br>(Python)]
    end

    subgraph Core Cluster (GKE)
        B[Data Ingestor] --> C[IV Surface API] --> D[Scout Agent<br>(Python)]
        E[Regime Detector] --> F[Risk Agent<br>(Python)]
        D --> F --> G[Sizing Agent<br>(Python)] --> H[Tuner Agent<br>(Python)] --> A
        G -->|trade intent| A
        H -->|RL params| G

        subgraph Infra
            I[Redpanda] & J[Postgres / NocoDB] & K[Redis Param Server]
        end
    end
```

*Full component responsibilities, data contracts, SLOs, and rollout plan live in [`docs/architecture.md`](docs/architecture.md).*

---

## 🗂 Directory Structure

```
.
├── docs/
│   ├── architecture.md
│   ├── contracts.md
│   └── PROJECT_TASKS.md
├── agents/
│   ├── scout-agent/
│   ├── risk-agent/
│   ├── sizing-agent/
│   ├── execution-agent/
│   └── tuner-agent/
├── dashboard/                # React/Typescript UI
├── infra/                   # Terraform + Helm
├── services/                # Data ingestion services
├── common/                  # Shared libraries
├── integration-tests/
├── requirements.txt         # Python dependencies
├── health-check.sh          # System health checks
├── .pre-commit-config.yaml  # lint / fmt hooks
└── .gitignore
```

---

## ⚡ Quick Start (local dev)

```bash
# clone & bootstrap
git clone git@github.com:HassDhia/Crypto-Options-Algo.git
cd Crypto-Options-Algo

# Python services
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run all agents
python -m scout-agent
python -m risk-agent
python -m sizing-agent
python -m tuner-agent
python -m execution-agent

# Start dashboard (separate terminal)
cd dashboard && npm install && npm run dev
```

> **Note:** Cloud infra (GKE + AMS1 VPS) lives under `/infra/terraform`.
> Secrets are injected via GitHub Actions → GCP Secret Manager.

---

## 🖥 Dashboard

The React-based dashboard provides real-time visualization of:
- Scouted trading opportunities
- Executed trades
- Risk alerts
- RL parameter tuning progress
- Sizing signals

Access at `http://localhost:3000` after running `npm run dev` in the dashboard directory.

---

## 🧪 Testing

```bash
# Run unit tests for all components
make test-unit

# Run integration tests (requires Docker)
make test-integration

# Run end-to-end tests (includes dashboard)
make test-e2e

# Clean up test artifacts
make clean
```

Test environment includes:
- All agents and services
- Dashboard UI
- Redpanda (Kafka-compatible)
- PostgreSQL
- Redis
- Test runner container

## 🔁 Continuous Integration

Our CI pipeline runs automatically on every push and pull request. Key features:
- Runs unit tests for all agents and services
- Executes integration tests with service containers
- Performs Helmfile linting for infrastructure definitions
- Builds and pushes multi-arch Docker images on main branch
- Requires all tests to pass before merging to main

Branch protection rules ensure:
- CI workflow must pass before merging
- Branches must be up-to-date with main
- Force pushes are prevented
- Code review is encouraged

Pipeline configuration: [.github/workflows/ci.yml](.github/workflows/ci.yml)
Branch protection: [.github/settings/branch-protection.yml](.github/settings/branch-protection.yml)

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
