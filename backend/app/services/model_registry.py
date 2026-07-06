import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_PATH = "models/registry.json"
MODELS_DIR = "models"


class ModelRegistry:
    def __init__(self):
        self.registry_path = Path(REGISTRY_PATH)
        self.models_dir = Path(MODELS_DIR)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict]:
        if not self.registry_path.exists():
            return []
        with open(self.registry_path) as f:
            return json.load(f)

    def _save(self, registry: list[dict]):
        with open(self.registry_path, "w") as f:
            json.dump(registry, f, indent=2, default=str)

    def register(self, metrics: dict, source_path: str) -> str:
        registry = self._load()
        version_id = f"v{len(registry) + 1}"
        timestamp = datetime.now(timezone.utc).isoformat()
        filename = f"{version_id}_{timestamp[:10]}.pkl"
        filepath = str(self.models_dir / filename)

        shutil.copy2(source_path, filepath)

        entry = {
            "id": version_id,
            "created_at": timestamp,
            "filename": filename,
            "path": filepath,
            "metrics": {k: v for k, v in metrics.items() if isinstance(v, (int, float, str, bool))},
        }
        registry.append(entry)
        self._save(registry)
        return filepath

    def list_models(self) -> list[dict]:
        return self._load()

    def get_model(self, version_id: str) -> dict | None:
        for m in self._load():
            if m["id"] == version_id:
                return m
        return None

    def set_active(self, version_id: str) -> bool:
        registry = self._load()
        for m in registry:
            if m["id"] == version_id:
                latest = self.models_dir / "latest_model.pkl"
                src = self.models_dir / m["filename"]
                if src.exists():
                    shutil.copy2(str(src), str(latest))
                    return True
        return False

    def summary(self) -> dict:
        registry = self._load()
        if not registry:
            return {"active": None, "total": 0, "latest": None}
        active_path = self.models_dir / "latest_model.pkl"
        active_id = None
        if active_path.exists():
            try:
                active_stat = active_path.stat()
                for m in reversed(registry):
                    mp = self.models_dir / m["filename"]
                    if mp.exists() and abs(mp.stat().st_mtime - active_stat.st_mtime) < 1:
                        active_id = m["id"]
                        break
            except Exception:
                pass
        return {
            "active": active_id or (registry[-1]["id"] if registry else None),
            "total": len(registry),
            "latest": registry[-1] if registry else None,
        }


registry = ModelRegistry()
