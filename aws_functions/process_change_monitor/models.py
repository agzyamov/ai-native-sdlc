"""Data models for process change events."""

import json
from dataclasses import dataclass, field
from typing import Dict, Optional

from aws_functions.shared.utils import (
    calculate_ttl_timestamp,
    format_partition_key,
    format_sort_key,
    safe_json_dumps,
)


@dataclass
class ProcessChangeEvent:
    """Represents a detected modification to an Azure DevOps process template."""

    event_timestamp: float  # Unix epoch seconds
    actor_id: str
    actor_display_name: str
    actor_ip: str
    action: str  # e.g., "Process.Field.Add"
    area: str  # Always "Process"
    category: str  # Create/Modify/Delete
    details: str  # Human-readable description
    correlation_id: str
    process_name: Optional[str] = None
    work_item_type: Optional[str] = None
    field_reference_name: Optional[str] = None
    state_name: Optional[str] = None
    alert_sent: bool = False
    alert_sent_timestamp: Optional[float] = None
    alert_failed: bool = False
    retry_count: int = 0
    raw_event_json: str = ""
    ttl_days: int = 90

    def to_dynamodb_item(self) -> Dict[str, any]:
        """
        Convert ProcessChangeEvent to DynamoDB item format.

        Returns:
            Dictionary suitable for DynamoDB PutItem operation
        """
        partition_key = format_partition_key(self.event_timestamp)
        sort_key = format_sort_key(self.correlation_id, self.event_timestamp)
        ttl = calculate_ttl_timestamp(self.event_timestamp, self.ttl_days)

        item = {
            "PartitionKey": partition_key,
            "SortKey": sort_key,
            "EventTimestamp": int(self.event_timestamp),
            "ActorId": self.actor_id,
            "ActorDisplayName": self.actor_display_name,
            "ActorIP": self.actor_ip,
            "Action": self.action,
            "Area": self.area,
            "Category": self.category,
            "Details": self.details,
            "CorrelationId": self.correlation_id,
            "AlertSent": self.alert_sent,
            "AlertFailed": self.alert_failed,
            "RetryCount": self.retry_count,
            "TTL": ttl,
            "RawEventJson": self.raw_event_json or safe_json_dumps({}),
        }

        # Add optional fields if present
        if self.process_name:
            item["ProcessName"] = self.process_name
        if self.work_item_type:
            item["WorkItemType"] = self.work_item_type
        if self.field_reference_name:
            item["FieldReferenceName"] = self.field_reference_name
        if self.state_name:
            item["StateName"] = self.state_name
        if self.alert_sent_timestamp:
            item["AlertSentTimestamp"] = int(self.alert_sent_timestamp)

        return item

    @classmethod
    def from_audit_event(cls, audit_event: Dict[str, any]) -> "ProcessChangeEvent":
        """
        Create ProcessChangeEvent from Azure DevOps audit event.

        Args:
            audit_event: Azure DevOps audit event dictionary

        Returns:
            ProcessChangeEvent instance

        Raises:
            ValueError: If required fields are missing
        """
        # Extract actor information
        actor = audit_event.get("actor", {})
        actor_id = actor.get("id", actor.get("uniqueName", ""))
        actor_display_name = actor.get("displayName", actor_id)
        actor_ip = audit_event.get("actorIPAddress", "")

        # Extract event metadata
        event_time = audit_event.get("eventTime", "")
        correlation_id = audit_event.get("correlationId", audit_event.get("id", ""))

        # Parse event timestamp (ISO 8601 format)
        from dateutil import parser as date_parser
        try:
            event_timestamp = date_parser.parse(event_time).timestamp()
        except (ValueError, TypeError):
            # Fallback to current time if parsing fails
            import time
            event_timestamp = time.time()

        # Extract action details
        action = audit_event.get("actionId", "")
        area = audit_event.get("area", "")
        category = audit_event.get("activityCategory", "")

        # Extract details
        details_dict = audit_event.get("details", {})
        process_name = details_dict.get("ProcessName")
        work_item_type = details_dict.get("WorkItemType")
        field_reference_name = details_dict.get("FieldReferenceName")
        state_name = details_dict.get("StateName")

        # Generate human-readable description
        details = cls._generate_description(audit_event)

        # Store raw event as JSON
        raw_event_json = safe_json_dumps(audit_event)

        return cls(
            event_timestamp=event_timestamp,
            actor_id=actor_id,
            actor_display_name=actor_display_name,
            actor_ip=actor_ip,
            action=action,
            area=area,
            category=category,
            details=details,
            correlation_id=correlation_id,
            process_name=process_name,
            work_item_type=work_item_type,
            field_reference_name=field_reference_name,
            state_name=state_name,
            raw_event_json=raw_event_json,
        )

    @staticmethod
    def _generate_description(audit_event: Dict[str, any]) -> str:
        """
        Generate human-readable description from audit event.

        Args:
            audit_event: Azure DevOps audit event dictionary

        Returns:
            Human-readable description string
        """
        action = audit_event.get("actionId", "")
        activity_type = audit_event.get("activityType", "")
        category = audit_event.get("activityCategory", "")
        details = audit_event.get("details", {})

        # Build description based on action type
        if "Field" in action:
            field_name = details.get("FieldName", details.get("FieldReferenceName", "field"))
            work_item_type = details.get("WorkItemType", "work item")
            process_name = details.get("ProcessName", "")

            if category == "Create":
                return f'Field "{field_name}" created on work item type "{work_item_type}" in process "{process_name}"'
            elif category == "Modify":
                return f'Field "{field_name}" modified on work item type "{work_item_type}" in process "{process_name}"'
            elif category == "Delete":
                return f'Field "{field_name}" deleted from work item type "{work_item_type}" in process "{process_name}"'

        elif "State" in action:
            state_name = details.get("StateName", "state")
            work_item_type = details.get("WorkItemType", "work item")
            process_name = details.get("ProcessName", "")

            if category == "Create":
                return f'State "{state_name}" created for work item type "{work_item_type}" in process "{process_name}"'
            elif category == "Modify":
                return f'State "{state_name}" modified for work item type "{work_item_type}" in process "{process_name}"'
            elif category == "Delete":
                return f'State "{state_name}" deleted from work item type "{work_item_type}" in process "{process_name}"'

        # Fallback to generic description
        return f"{action} in {audit_event.get('area', 'Process')} area"

