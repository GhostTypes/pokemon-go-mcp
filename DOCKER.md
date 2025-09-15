# Docker Setup Guide for Pokemon Go MCP Server

This guide covers everything you need to run the Pokemon Go MCP Server using Docker, including integration with n8n.

## Overview

The Pokemon Go MCP Server runs as a Docker container with HTTP Streamable Transport, making it accessible to n8n and other MCP clients over HTTP. This is the modern, recommended approach for MCP server deployment.

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t pogo-mcp-server .
```

### 2. Run the Container

```bash
docker run -d -p 8000:8000 --name pogo-mcp-container pogo-mcp-server
```

### 3. Verify the Server

```bash
# Check if container is running
docker ps

# Check server logs
docker logs pogo-mcp-container

# Test HTTP Streamable Transport endpoint
curl -v http://localhost:8000/mcp
```

## Dockerfile Configuration

The `Dockerfile` is configured for optimal MCP server deployment:

```dockerfile
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
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `http` | Transport type (`stdio`, `sse`, or `http`) |
| `MCP_HOST` | `0.0.0.0` | Host for HTTP server |
| `MCP_PORT` | `8000` | Port for HTTP server |

## Docker Commands

### Basic Operations

```bash
# Build image
docker build -t pogo-mcp-server .

# Run container
docker run -d -p 8000:8000 --name pogo-mcp-container pogo-mcp-server

# View logs
docker logs pogo-mcp-container

# Follow logs in real-time
docker logs -f pogo-mcp-container

# Stop container
docker stop pogo-mcp-container

# Start stopped container
docker start pogo-mcp-container

# Remove container
docker rm pogo-mcp-container

# Remove image
docker rmi pogo-mcp-server
```

### Health Check

```bash
# Check container health status
docker inspect --format='{{.State.Health.Status}}' pogo-mcp-container

# Manual health check
docker exec pogo-mcp-container wget --no-verbose --tries=1 --spider http://localhost:8000/mcp
```

## Integration with n8n

### Option 1: Separate Containers (Recommended)

Run n8n and the MCP server in separate containers:

```bash
# Run Pokemon Go MCP Server
docker run -d -p 8000:8000 --name pogo-mcp-container pogo-mcp-server

# Run n8n
docker run -d -p 5678:5678 --name n8n-container \
  -e N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**n8n Configuration (using n8n-nodes-mcp):**
- **Connection Type**: HTTP Streamable
- **HTTP Streamable URL**: `http://host.docker.internal:8000/mcp` (Windows/Mac)
- **HTTP Streamable URL**: `http://172.17.0.1:8000/mcp` (Linux)

### Option 2: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  pokemon-mcp:
    build: .
    container_name: pogo-mcp-server
    ports:
      - "8000:8000"
    environment:
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8000/mcp"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  n8n:
    image: n8nio/n8n
    container_name: n8n-instance
    ports:
      - "5678:5678"
    environment:
      - N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true
    volumes:
      - ~/.n8n:/home/node/.n8n
    depends_on:
      pokemon-mcp:
        condition: service_healthy
    restart: unless-stopped
```

**Commands:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

**n8n Configuration with Docker Compose (using n8n-nodes-mcp):**
- **Connection Type**: HTTP Streamable
- **HTTP Streamable URL**: `http://pokemon-mcp:8000/mcp`

### Option 3: Docker Network

Create a custom network for container communication:

```bash
# Create network
docker network create mcp-network

# Run MCP server on network
docker run -d --network mcp-network --name pogo-mcp-container pogo-mcp-server

# Run n8n on same network
docker run -d --network mcp-network -p 5678:5678 --name n8n-container \
  -e N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**n8n Configuration with Docker Network (using n8n-nodes-mcp):**
- **Connection Type**: HTTP Streamable
- **HTTP Streamable URL**: `http://pogo-mcp-container:8000/mcp`

## n8n Integration with HTTP Streamable Transport

### Prerequisites

1. Install the `n8n-nodes-mcp` community package in n8n
2. Ensure your n8n instance has `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true`

### Setting up MCP Client Node

1. **Add MCP Client Node** to your workflow
2. **Create new credentials** of type "MCP Client (HTTP Streamable) API"
3. **Configure the credentials:**
   - **HTTP Streamable URL**: Your Pokemon Go MCP server endpoint
   - **Additional Headers**: (optional) Leave empty unless authentication required

### Example Configurations

#### Local Development
```
Connection Type: HTTP Streamable
HTTP Streamable URL: http://localhost:8000/mcp
```

#### Docker Compose Setup
```
Connection Type: HTTP Streamable
HTTP Streamable URL: http://pokemon-mcp:8000/mcp
```

#### Separate Docker Containers
```
Connection Type: HTTP Streamable
HTTP Streamable URL: http://host.docker.internal:8000/mcp  (Windows/Mac)
HTTP Streamable URL: http://172.17.0.1:8000/mcp           (Linux)
```

### Using Pokemon Go Tools in n8n

Once configured, you can call any of the 20+ Pokemon Go tools:

**Example: Get Current Events**
```json
{
  "tool": "get_current_events"
}
```

**Example: Search for Specific Pokemon**
```json
{
  "tool": "search_pokemon_everywhere",
  "arguments": {
    "pokemon_name": "Pikachu"
  }
}
```

**Example: Get Shiny Raids**
```json
{
  "tool": "get_shiny_raids"
}
```

### Troubleshooting n8n Connection

1. **Check MCP server is running:**
   ```bash
   curl -v http://localhost:8000/mcp
   ```

2. **Verify n8n can reach the server:**
   - Test from n8n container: `docker exec n8n-container curl http://pokemon-mcp:8000/mcp`

3. **Check n8n logs:**
   ```bash
   docker logs n8n-container
   ```

4. **Common issues:**
   - Network connectivity between containers
   - Firewall blocking communication
   - Incorrect URL format (ensure `/mcp` endpoint)

## MCP Server Endpoints

When the container is running, the following endpoints are available:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mcp` | GET/POST | HTTP Streamable Transport endpoint for bidirectional MCP communication |

## Testing the Server

### Basic Connectivity Test

```bash
# Test HTTP Streamable Transport endpoint
curl -v http://localhost:8000/mcp

# Should return 200 OK
```

### Full MCP Test

```bash
# Send tools/list request via HTTP Streamable Transport
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

## Troubleshooting

### Common Issues

1. **Container won't start:**
   ```bash
   docker logs pogo-mcp-container
   ```

2. **Port already in use:**
   ```bash
   # Use different port
   docker run -d -p 8001:8000 --name pogo-mcp-container pogo-mcp-server
   ```

3. **n8n can't connect:**
   - Check if containers are on same network
   - Verify firewall settings
   - Use `docker inspect` to check container IPs

### Debug Commands

```bash
# Enter container shell
docker exec -it pogo-mcp-container /bin/sh

# Check container networking
docker network ls
docker network inspect bridge

# View container details
docker inspect pogo-mcp-container

# Check port bindings
docker port pogo-mcp-container
```

## Production Considerations

### Security

```bash
# Run with read-only filesystem
docker run -d -p 8000:8000 --read-only --name pogo-mcp-container pogo-mcp-server

# Run with specific user
docker run -d -p 8000:8000 --user 1000:1000 --name pogo-mcp-container pogo-mcp-server
```

### Resource Limits

```bash
# Limit memory and CPU
docker run -d -p 8000:8000 \
  --memory=512m \
  --cpus=0.5 \
  --name pogo-mcp-container \
  pogo-mcp-server
```

### Persistent Data

The MCP server caches API data. To persist cache across container restarts:

```bash
# Create volume for cache
docker volume create mcp-cache

# Run with volume
docker run -d -p 8000:8000 \
  -v mcp-cache:/app/cache \
  --name pogo-mcp-container \
  pogo-mcp-server
```

## Available Tools

Once the server is running, it provides 20+ Pokemon Go tools:

### Event Tools
- `get_current_events` - Active events
- `get_event_details` - Specific event details
- `get_community_day_info` - Community Day information

### Raid Tools
- `get_current_raids` - Current raid bosses
- `get_shiny_raids` - Shiny-eligible raid bosses
- `search_raid_boss` - Search for specific raid boss

### Research Tools
- `get_current_research` - Active research tasks
- `get_shiny_research_rewards` - Research with shiny rewards

### Cross-Platform Tools
- `get_all_shiny_pokemon` - All available shinies
- `get_server_status` - Server statistics
- `get_daily_priorities` - Today's priorities

## Support

For issues with Docker setup:
1. Check container logs: `docker logs pogo-mcp-container`
2. Verify network connectivity between containers
3. Ensure n8n has `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true`
4. Test endpoints manually with curl

For MCP-specific issues, refer to the main project documentation.