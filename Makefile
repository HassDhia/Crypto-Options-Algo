# Testing targets
.PHONY: test-unit test-integration clean

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

# Clean test artifacts
clean:
	@echo "Cleaning test artifacts..."
	@docker compose -f docker-compose.test.yml down -v
	@rm -rf coverage .pytest_cache __pycache__
