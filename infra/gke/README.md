# GKE Dev Cluster – Terraform module

* **Region:** europe-west1  
* **Node pool:** 3 x e2-standard-4  
* **Workload Identity:** enabled (GitHub Actions → GCP)

## One-time bootstrap

```bash
cd infra/gke
export PROJECT_ID=crypto‑options‑algo‑dev
export REGION=europe-west1
make bootstrap   # create versioned GCS bucket for state
make init
make apply       # 7-8 min to finish
```

The output block shows the service-account email to wire into the GitHub
OIDC workflow (`.github/workflows/ci.yml` → `workload_identity_provider:`).

Destroy with `make destroy`.
