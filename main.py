"""Main entry point for Grafana MCP server."""

import asyncio
from mcp.server.fastmcp import FastMCP
from grafana_mcp.config import config  # Validate configuration at startup
from grafana_mcp.tools import clusters, dashboards, datasources, folders

# Create the MCP server
mcp = FastMCP("Grafana MCP Server")

# Register cluster management tools
mcp.tool()(clusters.list_clusters)
mcp.tool()(clusters.get_cluster)
mcp.tool()(clusters.set_cluster)

# Register dashboard tools
mcp.tool()(dashboards.create_dashboard)
mcp.tool()(dashboards.read_dashboard)
mcp.tool()(dashboards.update_dashboard)
mcp.tool()(dashboards.delete_dashboard)
mcp.tool()(dashboards.search)
mcp.tool()(dashboards.copy_dashboard)

# Register dashboard testing and validation tools
mcp.tool()(dashboards.inspect_dashboard)
mcp.tool()(dashboards.validate_dashboard)
mcp.tool()(dashboards.snapshot_dashboard)
mcp.tool()(dashboards.test_panel_render)
mcp.tool()(dashboards.compare_dashboards)

# Register folder management tools
mcp.tool()(folders.list_folders)
mcp.tool()(folders.get_folder)
mcp.tool()(folders.create_folder)
mcp.tool()(folders.update_folder)
mcp.tool()(folders.delete_folder)

# Register datasource tools
mcp.tool()(datasources.list_datasources)


if __name__ == "__main__":
    mcp.run()
