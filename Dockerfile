# Use a specialized uv image for speed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy the source code
COPY . .

# Install the project
RUN uv sync --frozen --no-dev

# Expose gRPC port
EXPOSE 50051

# Run the server
CMD ["uv", "run", "python", "-m", "strategies.service.server"]
