"""Configuration management for Grafana MCP server."""

from os import getenv
from typing import Any


def check_truthy(value: Any, message: str) -> Any:
    """Check if the value is truthy."""
    if not value:
        raise ValueError(message)
    return value


def parse_key_value_pairs(pairs: str) -> dict[str, str]:
    """Parse space-separated key=value pairs."""
    return {
        k: v for k, v in (e.split("=", 1) for e in pairs.split()) if k and v
    }


class GrafanaConfig:
    """Configuration for the Grafana MCP server."""

    def __init__(self):
        self._clusters = check_truthy(
            parse_key_value_pairs(getenv("GRAFANA_CLUSTERS", "localhost=http://localhost:3000")),
            "GRAFANA_CLUSTERS must not be empty")
        self._folder = check_truthy(getenv("GRAFANA_FOLDER", "/"), "GRAFANA_FOLDER must not be empty")
        self._labels = check_truthy(getenv("GRAFANA_LABELS", "MCP").split(), "GRAFANA_LABELS must not be empty")
        self._tokens = parse_key_value_pairs(getenv("GRAFANA_TOKENS", ""))

    @property
    def clusters(self) -> dict[str, str]:
        """Get all configured clusters."""
        return self._clusters.copy()

    @property
    def labels(self) -> list[str]:
        """Get protection labels."""
        return self._labels.copy()

    @property
    def folder(self) -> str:
        """Get folder restriction."""
        return self._folder

    def get_cluster_url(self, cluster: str) -> str:
        """Get URL for specified cluster."""
        if cluster not in self._clusters:
            raise ValueError(f"Unknown cluster: {cluster}")
        return self._clusters[cluster]

    def get_cluster_token(self, cluster: str) -> str:
        """Get token for specified cluster.
        
        Returns empty string for unauthenticated clusters.
        """
        return self._tokens.get(cluster, "")

    def validate_cluster(self, cluster: str) -> None:
        """Validate that a cluster exists."""
        if cluster not in self._clusters:
            available = ", ".join(self._clusters.keys())
            raise ValueError(f"Unknown cluster '{cluster}'. Available clusters: {available}")


config = GrafanaConfig()
