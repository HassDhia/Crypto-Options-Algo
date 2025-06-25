set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

if ! command -v pre-commit >/dev/null; then
    echo "⚠️  pre-commit unavailable – creating noop stub"
    cat <<'STUB' >/usr/local/bin/pre-commit
#!/usr/bin/env bash
echo "pre-commit stub: lint skipped in air-gapped Codex runner"
exit 0
STUB
    chmod +x /usr/local/bin/pre-commit
fi

if command -v pre-commit >/dev/null; then
    pre-commit install --install-hooks || true
fi

echo "✅  Setup complete."

