import logging
import time
from datetime import datetime
from typing import Any, Dict, List

class BasePipeline:
    """Base class for orchestrating multi-phase pipelines."""
    
    def __init__(self, name: str, telemetry_path: str):
        self.name = name
        self.telemetry_path = telemetry_path
        self.logger = logging.getLogger(name)

    def _load_telemetry(self) -> List[Dict]:
        import json
        from pathlib import Path
        path = Path(self.telemetry_path)
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_telemetry(self, entries: List[Dict]) -> None:
        import json
        from pathlib import Path
        Path(self.telemetry_path).write_text(
            json.dumps(entries, indent=2, ensure_ascii=False), 
            encoding="utf-8"
        )

    def _log_event(self, event_type: str, detail: Dict[str, Any]) -> None:
        entries = self._load_telemetry()
        entries.append({
            "ts": datetime.now().isoformat(),
            "pipeline": self.name,
            "event": event_type,
            **detail,
        })
        self._save_telemetry(entries)
        self.logger.info("Telemetry: %s", event_type)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Generic execution loop. To be overridden by child classes."""
        raise NotImplementedError("Subclasses must implement execute()")

    def finalize(self, start_time: float, results: Dict) -> Dict:
        elapsed = (time.time() - start_time)
        self.logger.info("Pipeline %s completado en %.1fs", self.name, elapsed)
        self._log_event("pipeline_complete", {"elapsed_s": round(elapsed, 1), "results": results})
        return results
