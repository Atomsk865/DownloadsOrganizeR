"""Runtime config accessor to decouple routes from __main__ module.
Provides in-memory copies of organizer and dashboard configs and file paths.
"""
import json
from typing import Dict, Any

_config: Dict[str, Any] = {}
_dashboard_config: Dict[str, Any] = {}
_config_path: str = "organizer_config.json"
_dash_config_path: str = "dashboard_config.json"

def initialize(config_path: str, dash_config_path: str, default_config: Dict[str, Any], default_dash: Dict[str, Any]):
    global _config_path, _dash_config_path, _config, _dashboard_config
    _config_path = config_path
    _dash_config_path = dash_config_path
    _config = default_config.copy()
    _dashboard_config = default_dash.copy()
    try:
        with open(_config_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            _config.update(loaded)
    except Exception:
        pass
    try:
        with open(_dash_config_path, 'r', encoding='utf-8') as f:
            loaded_dash = json.load(f)
        if isinstance(loaded_dash, dict):
            for k, v in default_dash.items():
                if k not in loaded_dash:
                    loaded_dash[k] = v
            _dashboard_config = loaded_dash
    except Exception:
        pass

def get_config() -> Dict[str, Any]:
    return _config

def get_dashboard_config() -> Dict[str, Any]:
    return _dashboard_config

def reload_dashboard_config() -> Dict[str, Any]:
    """Reload dashboard config from disk into runtime cache and return it."""
    global _dashboard_config
    try:
        with open(_dash_config_path, 'r', encoding='utf-8') as f:
            loaded_dash = json.load(f)
        if isinstance(loaded_dash, dict):
            _dashboard_config = loaded_dash
    except Exception:
        pass
    return _dashboard_config

def save_config() -> None:
    with open(_config_path, 'w', encoding='utf-8') as f:
        json.dump(_config, f, indent=4)

def save_dashboard_config() -> None:
    with open(_dash_config_path, 'w', encoding='utf-8') as f:
        json.dump(_dashboard_config, f, indent=4)

def get_paths() -> Dict[str, str]:
    return {"config_path": _config_path, "dash_config_path": _dash_config_path}
