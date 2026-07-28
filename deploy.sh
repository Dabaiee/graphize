#!/usr/bin/env bash
# fastGraph — one-command deploy.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example."
  echo ">> Edit .env and set ANTHROPIC_API_KEY, then re-run ./deploy.sh"
  exit 1
fi

# shellcheck disable=SC1091
set -a; source .env; set +a
if [ -z "${ANTHROPIC_API_KEY:-}" ] || [[ "${ANTHROPIC_API_KEY}" == sk-ant-...* ]]; then
  echo "ERROR: set a real ANTHROPIC_API_KEY in .env first." >&2
  exit 1
fi

echo "Building and starting fastGraph (Neo4j + backend + frontend)..."
docker compose up --build -d

echo
echo "fastGraph is coming up:"
echo "  UI:            http://localhost:5280"
echo "  API docs:      http://localhost:8180/docs"
echo "  Neo4j browser: http://localhost:7580  (neo4j / ${NEO4J_PASSWORD:-fastgraph})"
echo
echo "Watch logs:  docker compose logs -f backend"
echo "Stop:        docker compose down"
