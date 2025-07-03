# Stage 1: Builder with uv and dependencies
FROM python:3.12-slim AS builder

# Copy uv binary from official image (pin version for reproducibility)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Set up workdir
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first for better caching
COPY pyproject.toml uv.lock ./
# COPY pyproject.toml  ./

# Install dependencies (but not the project itself)
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv sync --locked --no-install-project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project

# Now copy the rest of the source
ADD . .

# Install the project (editable mode for dev)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Compile bytecode for faster startup (optional)
ENV UV_COMPILE_BYTECODE=1
RUN uv sync --compile-bytecode

# Set venv path in PATH for dev shells
ENV PATH="/app/.venv/bin:$PATH"

# Final image (can be the same as builder for dev, or distroless for prod)
FROM builder AS dev

# Entrypoint for dev shells
CMD ["bash"]
