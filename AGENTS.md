# 🤖 AGENTS.md — Working on Crypto‑Options‑Algo

This document is the **single source of truth** for every engineer who touches a
micro‑service (“agent”) in the BTC‑options trading stack.  
If you read **nothing else** before opening a PR, read this.

| 🔗 Quick Links                                   | What for                                         |
|-------------------------------------------------|--------------------------------------------------|
| [`docs/PROJECT_TASKS.md`](docs/PROJECT_TASKS.md) | The master Kanban‑ready task list (v1.0 roadmap) |
| `.pre‑commit‑config.yaml`                       | Auto‑lint / fmt rules enforced on every commit   |
| `.github/workflows/ci.yml`                      | CI matrix (lint → test → multi‑arch Docker)      |
| `docker‑compose.dev.yml`                        | Spin‑up of ALL agents + Redpanda + Postgres      |
| `proto/`, `avro/`                               | Cross‑lang message contracts                     |

---

## 1 • Repo Layout Cheat‑Sheet

```

services/
├─ ingestor/        # Python + asyncio (Deribit WS → Kafka)
├─ iv_surface/      # Python + FastAPI (SVI‑J surface fit)
├─ regime/          # Python + PyTorch (HMM)
├─ scout/           # TypeScript (edge finder)
├─ risk/            # TypeScript (portfolio caps)
├─ sizing/          # TypeScript (Bayesian‑Kelly)
├─ execution/       # Go (low‑latency Deribit exec)
└─ rl_tuner/        # Python + PyTorch (bandit tuner)
infra/              # Terraform & Helmfile
tests/e2e/          # Docker‑Compose integration harness

````

Each folder is **self‑contained:** own `Dockerfile`, own unit tests, minimal
language‑specific tool‑chain.

---

## 2 • Dev Environment Tips

| Language  | Package Manager / Tool            | Hot commands                                                                                     |
|-----------|-----------------------------------|--------------------------------------------------------------------------------------------------|
| **Python**| `poetry` (per agent)              | `poetry install && poetry shell` to drop into venv                                               |
| **TS/JS** | `pnpm` workspaces                 | `pnpm i --filter scout` to pull deps for one agent; `pnpm dlx turbo run dev --filter scout` loop |
| **Go**    | Go 1.23+ (`go work`)             | `go work use ./services/execution && go test ./...`                                              |
| **Proto** | `buf` + `make`                    | `make proto` at repo root regenerates Go / Py / TS stubs                                         |
| **Docker**| Buildx (installed in CI)          | `docker buildx bake scout --load --set *.platform=linux/amd64`                                   |

*Use `grep -R "TODO(dev)"` to jump straight to unresolved work in any agent.*

---

## 3 • Local Integration Loop (seconds, not minutes)

```bash
# one‑liner spin‑up (Kafka, PG, Redis, Prom, Grafana, *all* agents)
docker compose -f docker-compose.dev.yml up -d

# live logs for one agent
docker compose logs -f scout

# hot‑reload TypeScript agents
pnpm dlx turbo run dev --filter scout
````

The compose file binds:

* **Redpanda**   : `localhost:9092`
* **Prometheus** : `localhost:9090`
* **Grafana**   : `localhost:3000` (`admin / admin`)
* **Postgres**  : `postgres://local:local@localhost:5432/edge`

Tear‑down: `docker compose down -v`.

---

## 4 • Testing Instructions

| Layer                    | Command                          | Notes                             |
| ------------------------ | -------------------------------- | --------------------------------- |
| **All pre‑commit hooks** | `pre-commit run --all-files`     | Auto‑fixed files are re‑staged    |
| **Python units**         | `poetry run pytest -q`           | Uses in‑repo `pytest.ini`         |
| **TypeScript units**     | `pnpm vitest run --filter scout` | Fast JIT tests                    |
| **Go units**             | `go test ./... -race`            | Race detector always on           |
| **End‑to‑end harness**   | `make e2e` (from repo root)      | Spins docker‑compose, runs checks |

CI **will fail** any PR that doesn’t pass **all of the above** for the agent it
touches.

*Focus on one test:* `vitest run -t "Kelly posterior update"` or
`pytest tests/test_surface.py::test_no_arb`.

---

## 5 • Pull‑Request Hygiene

* **Title format**

  ```
  [<agent|infra|docs>] <concise imperative summary>
  ```

  Examples:

  * `[scout] fix NaN in vega calc when IV→0`
  * `[infra] bump GKE node‑pool to e2‑standard‑4`
  * `[docs] add HMM math appendix`

* **Description template**

  ```
  Closes: #<issue_id> [, #<issue_id> …]
  Risk level: <low|medium|high>
  Deployment notes:
    - Terraform plan required? <yes/no>
    - Backfill / DB migration? <yes/no>
  ```

* Link the PR to the **Task ID** in
  `docs/PROJECT_TASKS.md` so the progress auto‑rolls up.

* No direct pushes to `main`. All changes flow through PR +
  two‑reviewer rule (one domain expert, one drive‑by).

---

## 6 • Agent README Stubs (copy into each `/services/<agent>/README.md`)

```markdown
# <Agent Name>

**Path:** `services/<agent>`  
**Language:** <python | typescript | go>  

| Purpose          | Value                                             |
|------------------|---------------------------------------------------|
| Input            | <Kafka topic / HTTP / gRPC>                       |
| Output           | <Kafka topic / REST / DB table>                   |
| Local dev loop   | `make dev` or `pnpm dev`                          |
| Unit test cmd    | `pytest -q` / `vitest run` / `go test ./...`      |
| Build image      | `docker buildx bake .`                            |
| Helm chart       | `<services/<agent>/chart/>`                       |
```

*(Keep these READMEs short; implementation details belong in code comments.)*

---

## 7 • Common Pitfalls & Fixes

| Symptom                                    | Fix                                                                  |
| ------------------------------------------ | -------------------------------------------------------------------- |
| **“Provided git ref main does not exist”** | `git checkout -B main && git push -u origin main`                    |
| **pre‑commit missing in Codex logs**       | Run `pip install pre-commit && pre-commit install` inside container  |
| **Docker Buildx “no platforms specified”** | Keep stub `Dockerfile` at repo root until agent‑specific images land |
| **Kafka EOF when consuming**               | In Redpanda ≥ v24 use `--offsets-storage=kafka` in rpk consume       |

---

## 8 • Escalation / Help

* **Slack:** `#crypto-options-algo-dev` (ping `@maintainers`)
* **PagerDuty:** `OptionsEdge / DevInfra` rotation
* **Docs:** open a PR against `/docs/` – even one‑line clarifications are gold.

Happy hacking & may your *edge_realised* always be ≥ 0.85 × *edge_theoretical* 🚀

````
