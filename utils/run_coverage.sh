#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Running tests and collecting coverage..."

# Create reports directory if missing
rm -rf htmlcov .coverage .coverage.[0-9]* coverage-reports/* || true
mkdir -p coverage-reports

# Check if running under uv (venv already active)
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    echo "✅ Virtual environment already active: $VIRTUAL_ENV"
elif [[ -d "/app/.venv" ]]; then
    echo "🐧 Activating uv virtual environment at /app/.venv"
    source /app/.venv/bin/activate
elif [[ -f ".venv/bin/activate" ]]; then
    echo "🐧 Activating local virtual environment"
    source .venv/bin/activate
elif [[ -f ".venv/Scripts/activate" ]]; then
    echo "🪟 Activating Windows virtual environment"
    source .venv/Scripts/activate
else
    echo "❌ No virtual environment found."
    echo "👉 To fix this, run: make venv"
    exit 1
fi

RUN_FULL_SUITE=true
echo "🏃 Running Pytest with coverage..."
if $RUN_FULL_SUITE; then
    coverage run pytest --junitxml=coverage-reports/junit.xml
else
    coverage run -m pytest tests/utils/test_model.py -v
fi

echo "🧾 Generating coverage reports..."
coverage xml -o coverage-reports/coverage.xml
coverage html -d coverage-reports/html

echo "📊 Checking coverage threshold..."
if [ "${CI_COMMIT_BRANCH:-}" = "production" ]; then
    echo "🔒 Enforcing minimum coverage: 70% (production branch)"
    coverage report -m --skip-covered --fail-under=70
else
    echo "ℹ️  Coverage threshold: 70% (warning only for '${CI_COMMIT_BRANCH:-local}')"
    coverage report -m --skip-covered --fail-under=70 || true
fi

# --- Local-only HTML report opening ---
if [ -z "${CI:-}" ]; then
    echo "🌐 Opening HTML coverage report (local only)..."
    HTML_REPORT="coverage-reports/html/index.html"

    if [ -f "$HTML_REPORT" ]; then
        if command -v xdg-open >/dev/null 2>&1; then
            echo "🖥️  Opening report in browser (Linux detected)..."
            xdg-open "$HTML_REPORT" >/dev/null 2>&1 &
        elif command -v open >/dev/null 2>&1; then
            echo "🍏 Opening report in browser (macOS detected)..."
            open "$HTML_REPORT" >/dev/null 2>&1 &
        elif command -v cmd.exe >/dev/null 2>&1; then
            echo "🪟 Detected Windows... opening report..."
            # Convert Git Bash path to Windows path
            WIN_PATH=$(cygpath -aw "$HTML_REPORT")
            # Don't redirect stdio for Windows GUI apps; just background it
            explorer.exe "$WIN_PATH" &
        else
            echo "⚠️  Could not detect OS or browser command. Please open '$HTML_REPORT' manually."
        fi
    else
        echo "❌ HTML report not found at $HTML_REPORT."
    fi
else
    echo "🏗️  Running in CI environment — skipping HTML report opening."
fi