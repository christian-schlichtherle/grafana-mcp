"""Cluster management tools for Grafana MCP server."""

from typing import Dict

from .base import cluster_only_tool
from ..config import config


def list_clusters() -> Dict[str, str]:
    """List all configured Grafana clusters with their URLs.
    
    Returns:
        Dictionary mapping cluster names to their base URLs.
    """
    return config.clusters


def get_cluster() -> str:
    """Get the current active Grafana cluster.
    
    Returns:
        The name of the currently active cluster.
    """
    return config.current_cluster


@cluster_only_tool
def set_cluster(cluster: str) -> str:
    """Set the active Grafana cluster.
    
    Args:
        cluster: The name of the cluster to set as active.
        
    Returns:
        Confirmation message with the new active cluster.
        
    Raises:
        ValueError: If the cluster name is not configured.
    """
    config.set_current_cluster(cluster)
    return f"Active cluster set to: {cluster}"
