#!/bin/bash
# Wait for database to be ready

set -e

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
MAX_RETRIES=${MAX_RETRIES:-30}
RETRY_INTERVAL=${RETRY_INTERVAL:-2}

echo "Waiting for database at $DB_HOST:$DB_PORT..."

for i in $(seq 1 $MAX_RETRIES); do
    if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
        echo "Database is ready!"
        exit 0
    fi
    echo "Attempt $i/$MAX_RETRIES: Database not ready, waiting ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
done

echo "Error: Database did not become ready in time"
exit 1
