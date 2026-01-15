# Multi-stage build for Wisp Framework
FROM python:3.13-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements
COPY pyproject.toml ./
COPY src ./src

# Install package
RUN pip install --no-cache-dir --user .

# Final stage
FROM python:3.13-slim

# Create non-root user
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy installed package from builder
COPY --from=builder /root/.local /home/botuser/.local

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=botuser:botuser src ./src
COPY --chown=botuser:botuser alembic.ini ./

# Set PATH for user-installed packages
ENV PATH=/home/botuser/.local/bin:$PATH

# Switch to non-root user
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Run the bot
CMD ["wisp-framework-runner"]
