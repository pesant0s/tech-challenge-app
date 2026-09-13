#!/bin/sh
# Migra o banco e sobe o servidor; o agente New Relic só entra com licença configurada.
set -e

alembic upgrade head

set -- uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${UVICORN_WORKERS:-2}" --no-access-log
if [ -n "$NEW_RELIC_LICENSE_KEY" ]; then
  set -- newrelic-admin run-program "$@"
fi
exec "$@"
