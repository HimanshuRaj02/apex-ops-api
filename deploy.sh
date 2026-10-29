#!/usr/bin/env bash
# Usage: ./deploy.sh <version>   e.g. ./deploy.sh 1.1.0
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
VERSION="${1:?usage: ./deploy.sh <version>}"
CURRENT="$(cat .current_version 2>/dev/null || echo none)"
echo "Deploying $VERSION (current: $CURRENT)"
APP_VERSION="$VERSION" docker compose up -d --build
ok=""
for i in $(seq 1 20); do
  if curl -fs localhost:8000/ready > /dev/null; then ok=1; break; fi
  sleep 3
done
if [ -z "$ok" ]; then
  echo "RELEASE $VERSION FAILED readiness check"
  if [ "$CURRENT" != "none" ]; then
    echo "Auto-rolling back to $CURRENT"
    ./rollback.sh "$CURRENT"
  fi
  exit 1
fi
if [ "$CURRENT" != "$VERSION" ]; then echo "$CURRENT" > .previous_version; fi
echo "$VERSION" > .current_version
echo "Deployed $VERSION OK:"
curl -s localhost:8000/health; echo
