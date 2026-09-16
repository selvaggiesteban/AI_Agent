import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from core.logger import logger

class StateStore:
    """
    Manages the persistent state of the AI Agent.
    Stored as a JSON file in the data directory.
    """
    def __init__(self, storage_path: str = "data/state.json"):
        self.storage_path = Path(storage_path)
        self._state: Dict[str, Any] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Loads state from disk or returns an empty dict if not found."""
        if not self.storage_path.exists():
            logger.info(f"State file not found at {self.storage_path}, creating new one.")
            return {}
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state from {self.storage_path}: {e}")
            return {}

    def save(self):
        """Persists the current state to disk."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=4, ensure_ascii=False)
            logger.info(f"State saved successfully to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save state to {self.storage_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a value from the state."""
        return self._state.get(key, default)

    def set(self, key: str, value: Any):
        """Sets a value in the state."""
        self._state[key] = value

    def update_metrics(self, category: str, metrics: Dict[str, Any]):
        """Updates a specific category of metrics."""
        if "metrics" not in self._state:
            self._state["metrics"] = {}

        if category not in self._state["metrics"]:
            self._state["metrics"][category] = {}

        self._state["metrics"][category].update(metrics)

    def get_metrics(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Retrieves metrics for a specific category or all metrics."""
        if category:
            return self._state.get("metrics", {}).get(category, {})
        return self._state.get("metrics", {})

# Global instance for the project
state_store = StateStore()
