FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy the complete project
COPY . .

# Make project importable
ENV PYTHONPATH=/app

# Default command (can be overridden)
CMD ["uv", "run", "gateway/main.py"]