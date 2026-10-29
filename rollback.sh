#!/usr/bin/env bash
# Usage: ./rollback.sh [version]   (default: previous version)
set -euo pipefail
cd "$(dirname "$0")"
TARGET="${1:-$(cat .previous_version 2>/dev/null || echo "")}"
if [ -z "$TARGET" ] || [ "$TARGET" = "none" ]; then echo "No version to roll back to"; exit 1; fi
echo "Rolling back to $TARGET (existing image, no rebuild)"
APP_VERSION="$TARGET" docker compose up -d --no-build
for i in $(seq 1 20); do
  if curl -fs localhost:8000/ready > /dev/null; then break; fi
  sleep 3
done
echo "$TARGET" > .current_version
echo "Now running:"
curl -s localhost:8000/health; echo
