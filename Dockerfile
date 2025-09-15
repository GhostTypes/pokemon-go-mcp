# Use Python 3.10 as the base image (matching project requirement)
FROM python:3.10-alpine

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install project dependencies
RUN pip install -e .

# Set environment variables for HTTP Streamable Transport
ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

# Expose port for HTTP server
EXPOSE 8000

# Health check to ensure server is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/mcp || exit 1

# Start the MCP server in HTTP Streamable Transport mode
CMD ["python", "server.py"]