# Use official slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock README.md /app/

# Upgrade pip and install project dependencies
RUN pip install --upgrade pip \
    && pip install . --no-cache-dir

# Copy the rest of the application code
COPY . /app

# Default command to run the MCP server
CMD ["python", "-m", "app.anytype_mcp_server"]
