"""Configuration management for Grafana MCP server."""

from os import getenv
from typing import Dict, List


class GrafanaConfig:
    """Configuration for Grafana MCP server."""

    def __init__(self):
        self._clusters: Dict[str, str] = {}
        self._tokens: Dict[str, str] = {}
        self._labels: List[str] = []
        self._folder: str = ""

        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        # Parse cluster URLs
        clusters_env = getenv("GRAFANA_CLUSTERS", "localhost=http://localhost:3000")
        self._clusters = self._parse_key_value_pairs(clusters_env)

        # Parse cluster tokens (optional - for authenticated clusters only)
        tokens_env = getenv("GRAFANA_TOKENS", "")
        self._tokens = self._parse_key_value_pairs(tokens_env)

        # Note: We no longer require all clusters to have tokens
        # This supports local development with unauthenticated Grafana instances

        # Stateless server - no default or current cluster concept

        # Parse labels
        labels_env = getenv("GRAFANA_LABELS", "MCP")
        self._labels = [label.strip() for label in labels_env.split() if label.strip()]

        if not self._labels:
            raise ValueError("GRAFANA_LABELS must not be empty")

        # Set folder restriction
        self._folder = getenv("GRAFANA_FOLDER", "/")
        if not self._folder:
            raise ValueError("GRAFANA_FOLDER must not be empty")

    def _parse_key_value_pairs(self, env_value: str) -> Dict[str, str]:
        """Parse space-separated key=value pairs."""
        result = {}
        if not env_value.strip():
            return result

        for pair in env_value.split():
            if "=" not in pair:
                raise ValueError(f"Invalid key=value pair: {pair}")
            key, value = pair.split("=", 1)
            result[key.strip()] = value.strip()

        return result

    @property
    def clusters(self) -> Dict[str, str]:
        """Get all configured clusters."""
        return self._clusters.copy()


    @property
    def labels(self) -> List[str]:
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

    def has_token(self, cluster: str) -> bool:
        """Check if cluster has authentication configured."""
        return cluster in self._tokens and bool(self._tokens[cluster])


    def validate_cluster(self, cluster: str) -> None:
        """Validate that a cluster exists."""
        if cluster not in self._clusters:
            available = ", ".join(self._clusters.keys())
            raise ValueError(f"Unknown cluster '{cluster}'. Available clusters: {available}")


# Global configuration instance
config = GrafanaConfig()
