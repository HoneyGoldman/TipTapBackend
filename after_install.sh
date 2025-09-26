#!/usr/bin/env bash
set -euo pipefail

DEPLOY_TAG="${DEPLOY_TAG:-stage}"  # export DEPLOY_TAG=prod|stage|dev before running

echo "[after_install] Using DEPLOY_TAG=${DEPLOY_TAG}"

case "$DEPLOY_TAG" in
  prod)
    cp settings-prod.json settings.json
    ;;
  stage)
    cp settings-stage.json settings.json
    ;;
  *)
    echo "Unknown DEPLOY_TAG '${DEPLOY_TAG}', defaulting to stage"
    cp settings-stage.json settings.json
    ;;
esac

echo "[after_install] Building and starting containers..."
docker compose down || true
docker compose build --no-cache
docker compose up -d

echo "[after_install] Done."
