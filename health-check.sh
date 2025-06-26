#!/bin/bash

# Function to wait for a service to be ready
wait_for_service() {
  local service=$1
  local port=$2
  echo "Waiting for $service to be ready..."
  while ! nc -z localhost $port; do
    sleep 1
  done
  echo "$service is ready"
}

# Wait for core services
wait_for_service "Redis" 6379
wait_for_service "Postgres" 5432
wait_for_service "Redpanda" 9092

# Tail agent logs
echo "Tailing agent logs..."
docker compose -f docker-compose.dev.yml logs -f scout-agent execution-agent risk-agent sizing-agent
