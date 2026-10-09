"""Pan -- the program's data layer: inventory, catalog, full-text and vector
indices, a Parquet/Iceberg lake and frontier intake (roles/Pan/RESPONSIBILITIES.md).

Sources stay authoritative. Pan writes only schema pan / pan_iceberg on the
canonical cluster and files under the configured lake.
"""
import json
import os
import platform
from pathlib import Path

PKG = Path(__file__).resolve().parent
REPO = PKG.parent
VERSION = "0.1.0"


def host() -> str:
    return (platform.node() or "unknown-host").upper()


def config() -> dict:
    cfg = json.loads((PKG / "config.json").read_text(encoding="utf-8"))
    h = dict(cfg["hosts"].get(host(), {}))
    if os.environ.get("PAN_LAKE"):
        h["lake"] = os.environ["PAN_LAKE"]
    if os.environ.get("PAN_CANONICAL"):
        h["canonical_checkout"] = os.environ["PAN_CANONICAL"]
    if os.environ.get("PAN_DATA_ROOTS"):
        h["data_roots"] = os.environ["PAN_DATA_ROOTS"].split(os.pathsep)
    cfg["host"] = h
    return cfg


def lake() -> Path:
    p = config()["host"].get("lake")
    if not p:
        raise RuntimeError("no lake configured for host {} (set PAN_LAKE or pan/config.json)".format(host()))
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p
