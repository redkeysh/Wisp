#!/bin/bash
# Migration script

set -e

ENV=${ENV:-local}
ENV_FILE=".env.${ENV}"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file $ENV_FILE not found"
    exit 1
fi

echo "Running migrations for environment: $ENV"

# Load environment variables
export $(cat "$ENV_FILE" | grep -v '^#' | xargs)

# Run alembic
alembic upgrade head

echo "Migrations completed successfully"
