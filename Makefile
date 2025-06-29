# Testing targets
.PHONY: test-unit test-integration clean dev-up

# Run unit tests for all components
test-unit:
	@echo "Running TypeScript unit tests..."
	@npm run test --workspaces
	@echo "Running Go unit tests..."
	@cd execution-agent && go test ./...
	@echo "Running Python unit tests..."
	@cd services/ingestor && pytest

# Run integration tests
test-integration:
	@echo "Starting integration test environment..."
	@docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
	@echo "Running integration tests..."
	@pytest integration-tests --maxfail=1 -q

# Start development environment
dev-up:
	@echo "Starting development environment..."
	@docker compose -f docker-compose.dev.yml up --build -d

# Provision Edge VPS
provision-edge:
	@echo "Provisioning Edge VPS..."
	@cd infra/edge-vps && make init && make apply

# Deploy Data Plane
deploy-data-plane:
	@echo "Creating namespaces and secrets..."
	@./infra/create_ns_and_secrets.sh
	@echo "Deploying data plane services..."
	@cd infra && helmfile apply

# Clean test artifacts
clean:
	@echo "Cleaning test artifacts..."
	@docker compose -f docker-compose.test.yml down -v
	@rm -rf coverage .pytest_cache __pycache__
