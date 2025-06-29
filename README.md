# Grafana MCP

This repository provides an MCP (Model Context Protocol) server for CRUD operations on Grafana dashboards which are protected with labels.

## Quick Start

```bash
# Install and run with zero configuration (uses localhost:3000 by default)
uv sync
python main.py

# That's it! The server is ready to use with your local Grafana instance.
```

## Features

+ **Dashboard Protection**: When creating Grafana dashboards, the MCP server labels them to mark itself as the origin
+ **Selective Modification**: Only dashboards with required protection labels can be updated or deleted
+ **Unrestricted Reading**: No restrictions for reading dashboards, allowing enhancement of existing dashboards by copying them
+ **Folder Restrictions**: Configurable access control to specific folders and subfolders
+ **Multi-Cluster Support**: Manage dashboards across multiple Grafana instances
+ **Comprehensive Search**: Full support for Grafana's search API with filtering options

## Available MCP Tools

### Cluster Management
- `list_clusters()` - List all configured Grafana clusters
- `get_cluster()` - Get currently active cluster
- `set_cluster(cluster)` - Switch active cluster

### Search Operations
- `search(cluster, *, query="", tags=[], starred=False, folder_uids=[], dashboard_uids=[], dashboard_ids=[], type="", limit=1000, page=1)` - Search dashboards and folders with comprehensive filtering

### Dashboard Operations
- `create_dashboard(cluster, dashboard_json, *, folder_uid="")` - Create new dashboard with protection labels
- `read_dashboard(cluster, dashboard_uid)` - Read dashboard by UID (no restrictions)
- `update_dashboard(cluster, dashboard_uid, dashboard_json)` - Update dashboard (requires protection labels)
- `delete_dashboard(cluster, dashboard_uid)` - Delete dashboard (requires protection labels)
- `copy_dashboard(cluster, source_uid, new_title, *, folder_uid="")` - Copy dashboard with new protection labels

### Folder Management
- `list_folders(cluster, *, parent_uid="")` - List folders, optionally under a parent
- `get_folder(cluster, folder_uid)` - Get detailed folder information
- `create_folder(cluster, title, *, parent_uid="")` - Create new folder, optionally as subfolder
- `update_folder(cluster, folder_uid, title, *, parent_uid="")` - Update/rename/move folder
- `delete_folder(cluster, folder_uid, *, force_delete_rules=False)` - Delete folder

### Datasource Operations
- `list_datasources(cluster)` - List all datasources in cluster

## Configuration

### Environment Variables

Configure the MCP server using these environment variables:

```bash
# Cluster URLs (space-separated key=value pairs, defaults to "localhost=http://localhost:3000")
export GRAFANA_CLUSTERS="localhost=http://localhost:3000 dev=https://grafana.dev.example.com prod=https://grafana.prod.example.com"

# Cluster API tokens (space-separated key=value pairs, optional)
# Only required for clusters that need authentication
export GRAFANA_TOKENS="dev=glsa_yyy prod=glsa_zzz"  # Note: localhost has no token (unauthenticated)

# Default cluster (optional, defaults to first cluster in GRAFANA_CLUSTERS)
export GRAFANA_DEFAULT_CLUSTER=localhost

# Protection labels (space-separated, defaults to "MCP")
export GRAFANA_LABELS="MCP Claude"

# Folder restriction (defaults to "/" for root access)
export GRAFANA_FOLDER=/MCP
```

### Local Development Without Authentication

For local development, you can run Grafana in a Docker container without authentication:

```bash
# Run Grafana without authentication
docker run -d \
  -p 3000:3000 \
  -e "GF_AUTH_ANONYMOUS_ENABLED=true" \
  -e "GF_AUTH_ANONYMOUS_ORG_ROLE=Admin" \
  -e "GF_AUTH_BASIC_ENABLED=false" \
  --name grafana \
  grafana/grafana:latest

# Configure MCP server for unauthenticated local access
export GRAFANA_CLUSTERS="localhost=http://localhost:3000"
# No GRAFANA_TOKENS needed!

# Or use the default configuration (no environment variables needed!)
# This defaults to localhost=http://localhost:3000 without authentication

# Run the MCP server
python main.py
```

#### Mixed Authentication Environments

You can mix authenticated and unauthenticated clusters:

```bash
# Local without auth, production with auth
export GRAFANA_CLUSTERS="localhost=http://localhost:3000 prod=https://grafana.prod.com"
export GRAFANA_TOKENS="prod=glsa_abc123"  # Only prod needs a token
```

### Authentication Setup (For Production Clusters)

For production or authenticated Grafana clusters, you need to create service account tokens. Service accounts are the recommended way to authenticate with Grafana's HTTP API (API keys are deprecated).

**Note**: Skip this section if you're only using local unauthenticated Grafana instances.

#### Creating Service Account Tokens via Grafana UI

1. **Create Service Account**:
   - Navigate to **Administration** → **Users and access** → **Service Accounts**
   - Click **"Add service account"**
   - Enter a **Display name** (e.g., "MCP Server")
   - Select appropriate **Role**: `Viewer`, `Editor`, or `Admin`
   - Click **"Create"**

2. **Generate Token**:
   - Select your newly created service account
   - Click **"Add service account token"**
   - Enter a **Display name** for the token
   - Set **Expiration date** (or select "No expiration")
   - Click **"Generate token"**
   - **Important**: Copy and save the token immediately - it's only shown once!

#### Creating Service Account Tokens via API

```bash
# Create service account
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "mcp-server", "role": "Editor"}' \
  http://admin:admin@localhost:3000/api/serviceaccounts

# Create token for the service account (use ID from previous response)
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "mcp-token"}' \
  http://admin:admin@localhost:3000/api/serviceaccounts/{id}/tokens
```

#### Using Tokens

Tokens should be prefixed with `glsa_` and used in the `GRAFANA_TOKENS` environment variable:

```bash
export GRAFANA_TOKENS="prod=glsa_abc123def456 dev=glsa_xyz789uvw012"
```

#### Authentication in Requests

The MCP server automatically adds the Bearer token to all requests:

```bash
Authorization: Bearer glsa_abc123def456
```

For more information, see the [official Grafana documentation on service accounts](https://grafana.com/docs/grafana/latest/administration/service-accounts/).

## Installation & Usage

1. **Install dependencies**:
   ```bash
   uv sync
   # or
   pip install -e .
   ```

2. **Set environment variables** (see Configuration section above)

3. **Run the MCP server**:
   ```bash
   python main.py
   ```

The server will validate your configuration and start the MCP server, making all tools available to MCP clients.

## Example Usage

```python
# List all configured clusters
clusters = list_clusters()
# Returns: {"localhost": "http://localhost:3000", "prod": "https://grafana.prod.com"}

# Explore folder hierarchy
root_folders = list_folders("prod")  # List root-level folders
subfolders = list_folders("prod", parent_uid="folder123")  # List subfolders

# Search for dashboards and folders
dashboards = search("prod", query="monitoring", tags=["production"])
folders_only = search("prod", type="dash-folder", query="team")
dashboards_only = search("prod", type="dash-db", starred=True)

# Create and manage folders
folder = create_folder("prod", "Team Alpha", parent_uid="parent123")
updated = update_folder("prod", "folder123", "New Name", parent_uid="new_parent")

# Copy a dashboard into a specific folder
new_dash = copy_dashboard("prod", "abc123def", "My New Dashboard", folder_uid="folder123")

# Create a dashboard with protection labels automatically added
result = create_dashboard("prod", {
    "title": "Test Dashboard",
    "panels": [...],
    "tags": ["custom"]  # MCP labels will be automatically added
}, folder_uid="folder123")
```

## Security Model

- **Label-Based Protection**: Dashboards created by this MCP server are automatically tagged with protection labels
- **Selective Operations**: Only dashboards with required labels can be updated or deleted
- **Folder Restrictions**: Operations can be restricted to specific folder hierarchies
- **Token-Based Auth**: Uses secure service account tokens instead of deprecated API keys
- **No Overwrites**: Dashboard creation prevents accidental overwrites of existing dashboards
