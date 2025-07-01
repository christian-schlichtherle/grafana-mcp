"""Security validation and enforcement for Grafana operations."""

import uuid
from typing import Any

from ..config import config


class SecurityValidator:
    """Validates and enforces security restrictions for dashboard operations."""

    @staticmethod
    def validate_dashboard_labels(dashboard: dict[str, Any]) -> bool:
        """Check if dashboard has all required protection labels."""
        dashboard_tags = dashboard.get("tags", [])
        required_labels = config.labels

        # Check if all required labels are present in dashboard tags
        for label in required_labels:
            if label not in dashboard_tags:
                return False
        return True

    @staticmethod
    def add_protection_labels(dashboard: dict[str, Any]) -> dict[str, Any]:
        """Add protection labels to dashboard."""
        dashboard_copy = dashboard.copy()

        # Get existing tags or initialize empty list
        existing_tags = dashboard_copy.get("tags", [])
        if not isinstance(existing_tags, list):
            existing_tags = []

        # Add required labels if not already present
        for label in config.labels:
            if label not in existing_tags:
                existing_tags.append(label)

        dashboard_copy["tags"] = existing_tags
        return dashboard_copy

    @staticmethod
    def validate_folder_access(folder_uid: str = "") -> bool:
        """Validate that operations are allowed in the specified folder."""
        folder_restriction = config.folder

        # If no folder restriction (root access), allow everything
        if folder_restriction == "/":
            return True

        # If no folder specified, check if root operations are allowed
        if not folder_uid:
            return folder_restriction == "/"

        # For specific folder operations, would need to resolve folder path
        # This is simplified - in a real implementation, you'd resolve the folder hierarchy
        return True

    @staticmethod
    def generate_dashboard_uid() -> str:
        """Generate a unique dashboard UID."""
        # Generate a UUID and take first 10 characters (Grafana UID format)
        return uuid.uuid4().hex[:10]

    @staticmethod
    def prepare_dashboard_for_creation(dashboard: dict[str, Any], folder_uid: str = "") -> dict[str, Any]:
        """Prepare dashboard for creation with security requirements."""
        # Validate folder access
        if not SecurityValidator.validate_folder_access(folder_uid):
            raise ValueError(f"Access denied to folder. Operations restricted to: {config.folder}")

        # Add protection labels
        dashboard_with_labels = SecurityValidator.add_protection_labels(dashboard)

        # Generate UID if not present
        if "uid" not in dashboard_with_labels or not dashboard_with_labels["uid"]:
            dashboard_with_labels["uid"] = SecurityValidator.generate_dashboard_uid()

        # Ensure version is not set for new dashboards
        dashboard_with_labels.pop("version", None)

        return dashboard_with_labels

    @staticmethod
    def validate_dashboard_for_modification(dashboard: dict[str, Any], operation: str) -> None:
        """Validate that a dashboard can be modified (updated or deleted)."""
        if not SecurityValidator.validate_dashboard_labels(dashboard):
            required_labels = ", ".join(config.labels)
            raise ValueError(
                f"Cannot {operation} dashboard: missing required labels {required_labels}. "
                f"This dashboard was not created by this MCP server or has been modified."
            )

    @staticmethod
    def prepare_dashboard_for_update(dashboard: dict[str, Any], folder_uid: str = "") -> dict[str, Any]:
        """Prepare dashboard for update with security requirements."""
        # Validate folder access
        if not SecurityValidator.validate_folder_access(folder_uid):
            raise ValueError(f"Access denied to folder. Operations restricted to: {config.folder}")

        # Ensure protection labels are maintained
        dashboard_with_labels = SecurityValidator.add_protection_labels(dashboard)

        return dashboard_with_labels

    @staticmethod
    def copy_dashboard_for_creation(
            source_dashboard: dict[str, Any],
            new_title: str,
            folder_uid: str = "",
            target_uid: str = ""
    ) -> dict[str, Any]:
        """Prepare a dashboard copy for creation."""
        # Start with the source dashboard
        new_dashboard = source_dashboard.copy()

        # Remove fields that shouldn't be copied
        fields_to_remove = ["id", "version", "url"]
        
        for field in fields_to_remove:
            new_dashboard.pop(field, None)

        # Set new title
        new_dashboard["title"] = new_title

        # Handle UID assignment
        if target_uid:
            # Explicit target UID provided
            new_dashboard["uid"] = target_uid
        else:
            # No target UID: remove existing UID and let prepare_dashboard_for_creation generate one
            new_dashboard.pop("uid", None)

        # Add protection labels and validate folder access
        return SecurityValidator.prepare_dashboard_for_creation(new_dashboard, folder_uid)
