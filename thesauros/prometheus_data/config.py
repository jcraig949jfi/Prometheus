"""
Centralized configuration for all Prometheus database connections.

Priority: environment variables > ~/.prometheus/db.toml > defaults.

Credentials are loaded from ~/.prometheus/credentials.toml or environment
variables. Never stored in code (except the public LMFDB mirror credentials).
"""
import os
from pathlib import Path

# ============================================================
# Defaults (public LMFDB mirror — safe to hardcode)
# ============================================================

_DEFAULTS = {
    "lmfdb": {
        "host": "devmirror.lmfdb.xyz",
        "port": 5432,
        "dbname": "lmfdb",
        "user": "lmfdb",
        "password": "lmfdb",
    },
    "sci": {
        "host": "devmirror.lmfdb.xyz",
        "port": 5432,
        "dbname": "prometheus_sci",
        "user": "harmonia",
        "password": "",
    },
    "fire": {
        "host": "devmirror.lmfdb.xyz",
        "port": 5432,
        "dbname": "prometheus_fire",
        "user": "ergon",
        "password": "",
    },
    "redis": {
        "host": "devmirror.lmfdb.xyz",
        "port": 6379,
        "db": 0,
        "password": "",
    },
    "local": {
        "duckdb_path": "",
        "share_path": "",
    },
}

# ============================================================
# Configuration loader
# ============================================================

_config_cache = None


def _find_prometheus_root():
    """Walk up from this file to find the Prometheus repo root."""
    p = Path(__file__).resolve().parent.parent
    if (p / "CLAUDE.md").exists():
        return p
    return p


def _load_toml(path):
    """Load a TOML file. Returns empty dict if file doesn't exist or toml unavailable."""
    if not path.exists():
        return {}
    try:
        import tomllib
        with open(path, "rb") as f:
            return tomllib.load(f)
    except ImportError:
        try:
            import tomli
            with open(path, "rb") as f:
                return tomli.load(f)
        except ImportError:
            # Fall back to simple key=value parsing for basic configs
            return _parse_simple_toml(path)


def _parse_simple_toml(path):
    """Minimal TOML parser for [section] / key = value format."""
    result = {}
    current_section = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                result[current_section] = {}
            elif "=" in line and current_section:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                # Type coercion
                if val.isdigit():
                    val = int(val)
                elif val.lower() in ("true", "false"):
                    val = val.lower() == "true"
                result[current_section][key] = val
    return result


def _load_config():
    """Load configuration from all sources with priority resolution."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    config = {}
    for section, defaults in _DEFAULTS.items():
        config[section] = dict(defaults)

    # Load db.toml
    config_dir = Path.home() / ".prometheus"
    db_toml = _load_toml(config_dir / "db.toml")
    for section, values in db_toml.items():
        if section in config:
            config[section].update(values)

    # Load credentials.toml (separate file, gitignored)
    cred_toml = _load_toml(config_dir / "credentials.toml")
    for section, values in cred_toml.items():
        if section in config and "password" in values:
            config[section]["password"] = values["password"]

    # Environment variable overrides
    env_map = {
        "PROMETHEUS_LMFDB_HOST": ("lmfdb", "host"),
        "PROMETHEUS_LMFDB_PORT": ("lmfdb", "port"),
        "PROMETHEUS_SCI_HOST": ("sci", "host"),
        "PROMETHEUS_SCI_PORT": ("sci", "port"),
        "PROMETHEUS_SCI_USER": ("sci", "user"),
        "PROMETHEUS_SCI_PASSWORD": ("sci", "password"),
        "PROMETHEUS_FIRE_HOST": ("fire", "host"),
        "PROMETHEUS_FIRE_PORT": ("fire", "port"),
        "PROMETHEUS_FIRE_USER": ("fire", "user"),
        "PROMETHEUS_FIRE_PASSWORD": ("fire", "password"),
        "PROMETHEUS_REDIS_HOST": ("redis", "host"),
        "PROMETHEUS_REDIS_PORT": ("redis", "port"),
        "PROMETHEUS_REDIS_PASSWORD": ("redis", "password"),
        "PROMETHEUS_DUCKDB_PATH": ("local", "duckdb_path"),
        "PROMETHEUS_SHARE_PATH": ("local", "share_path"),
    }

    for env_key, (section, field) in env_map.items():
        val = os.environ.get(env_key)
        if val is not None:
            if field == "port":
                val = int(val)
            config[section][field] = val

    # Resolve local paths
    root = _find_prometheus_root()
    if not config["local"]["duckdb_path"]:
        config["local"]["duckdb_path"] = str(root / "charon" / "data" / "charon.duckdb")
    if not config["local"]["share_path"]:
        # Platform-specific default
        if os.name == "nt":
            config["local"]["share_path"] = r"C:\prometheus_share"
        else:
            config["local"]["share_path"] = str(Path.home() / "prometheus_share")

    _config_cache = config
    return config


# ============================================================
# Public API
# ============================================================

def get_config(section=None):
    """Get configuration dict. If section specified, return just that section."""
    config = _load_config()
    if section:
        return dict(config.get(section, {}))
    return config


def get_pg_dsn(db_name):
    """Get psycopg2 connection kwargs for a database."""
    config = get_config(db_name)
    return {
        "host": config["host"],
        "port": config["port"],
        "dbname": config["dbname"],
        "user": config["user"],
        "password": config["password"],
        "connect_timeout": 15,
    }


def get_redis_config():
    """Get Redis connection kwargs."""
    config = get_config("redis")
    result = {
        "host": config["host"],
        "port": config["port"],
        "db": config.get("db", 0),
    }
    if config.get("password"):
        result["password"] = config["password"]
    return result
