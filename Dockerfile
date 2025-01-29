# Dockerfile
FROM python:3.12-slim

WORKDIR /opt/dagster/app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

# Install uv
RUN pip install uv==0.5.25

# Copy the rest of the application
COPY hts_dagster_sample/ hts_dagster_sample/

# Install project dependencies using uv
RUN uv pip install -e "." --system
