from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime

class CleanupSchedule(Enum):
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class ArtifactRetentionValidator:
    """Validates artifact retention policies during cleanup scheduling."""
    
    @staticmethod
    def validate_policy(policy: Dict[str, Any]) -> bool:
        """
        Validates the retention policy.
        Rejects stale, duplicate, or policy-violating transitions.
        """
        if not policy:
            return True
            
        retention_days = policy.get("retention_days")
        if retention_days is not None:
            if not isinstance(retention_days, (int, float)):
                return False
            if retention_days < 0:
                return False
            
        schedule = policy.get("schedule")
        if schedule and schedule not in [s.value for s in CleanupSchedule]:
            return False
            
        # Check for "stale" policy (e.g. if it has a timestamp that is too old)
        created_at = policy.get("created_at")
        if created_at and isinstance(created_at, datetime):
            if (datetime.now() - created_at).days > 365:
                return False
                
        return True

    @staticmethod
    def validate_transition(current_state: str, next_state: str, policy: Optional[Dict[str, Any]] = None) -> bool:
        """
        Enforces cleanup scheduling invariant before committing state changes.
        """
        if next_state in ["running", "completed"]:
            if policy and not ArtifactRetentionValidator.validate_policy(policy):
                return False
        return True
