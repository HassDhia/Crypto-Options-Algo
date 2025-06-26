#!/usr/bin/env bash
set -euo pipefail

for ns in kafka db cache monitoring; do
  kubectl create ns "${ns}" --dry-run=client -o yaml | kubectl apply -f -
done

# placeholder weak creds – rotate before prod
kubectl -n db create secret generic postgres-admin \
  --from-literal=postgres-password='postgres123' --dry-run=client -o yaml | kubectl apply -f -

kubectl -n monitoring create secret generic grafana-admin \
  --from-literal=admin-user=admin --from-literal=admin-password='admin' \
  --dry-run=client -o yaml | kubectl apply -f -
