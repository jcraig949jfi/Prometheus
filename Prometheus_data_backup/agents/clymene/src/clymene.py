"""
Clymene — The Knowledge Hoarder

Downloads and archives open-source tools, repos, and model weights
before they get paywalled. Maintains a local vault with SQLite registry.

Usage:
    python clymene.py repos                        # Clone/update all repos
    python clymene.py repos --category tensor      # Only tensor repos
    python clymene.py models                       # List tracked models
    python clymene.py models --download <hf_id>    # Download specific model
    python clymene.py status                       # Show vault status
    python clymene.py --once                       # Full hoard cycle
"""

import argparse
import json
import logging
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

CLYMENE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = CLYMENE_ROOT.parent.parent
CONFIG_PATH = CLYMENE_ROOT / "configs" / "manifest.yaml"
DATA_DIR = CLYMENE_ROOT / "data"
DB_PATH = DATA_DIR / "vault_registry.db"
LOG_PATH = DATA_DIR / "clymene.log"

# Rate limit: seconds between git clones
CLONE_DELAY = 3

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging — stdout + file, matching Eos pattern
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CLYMENE] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
    ],
)
log = logging.getLogger("clymene")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_manifest() -> dict:
    """Load the YAML manifest. Falls back to empty dict if unavailable."""
    try:
        import yaml
    except ImportError:
        log.error("PyYAML not installed. Run: pip install pyyaml")
        sys.exit(1)

    if not CONFIG_PATH.exists():
        log.error(f"Manifest not found: {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_vault_root(manifest: dict) -> Path:
    """
    Determine the vault root directory. Priority:
    1. CLYMENE_VAULT_ROOT environment variable
    2. vault_root from manifest.yaml
    3. Default: <project_root>/vault
    """
    env_root = os.environ.get("CLYMENE_VAULT_ROOT")
    if env_root:
        return Path(env_root).resolve()

    manifest_root = manifest.get("vault_root", "vault")
    vault = Path(manifest_root)
    if not vault.is_absolute():
        vault = PROJECT_ROOT / vault
    return vault.resolve()


# ---------------------------------------------------------------------------
# SQLite Registry
# ---------------------------------------------------------------------------

def init_db(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database with schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS repos (
            name        TEXT PRIMARY KEY,
            url         TEXT NOT NULL,
            local_path  TEXT,
            category    TEXT,
            tags        TEXT,  -- JSON array
            last_cloned TEXT,
            last_updated TEXT,
            commit_hash TEXT,
            size_bytes  INTEGER DEFAULT 0,
            status      TEXT DEFAULT 'pending'
        );

        CREATE TABLE IF NOT EXISTS models (
            hf_id       TEXT PRIMARY KEY,
            arch_family TEXT,
            param_count TEXT,
            vram_gb     REAL,
            local_path  TEXT,
            tags        TEXT,  -- JSON array
            downloaded_at TEXT,
            size_bytes  INTEGER DEFAULT 0,
            status      TEXT DEFAULT 'pending',
            notes       TEXT
        );

        CREATE TABLE IF NOT EXISTS datasets (
            name        TEXT PRIMARY KEY,
            source_url  TEXT,
            local_path  TEXT,
            size_bytes  INTEGER DEFAULT 0,
            downloaded_at TEXT,
            status      TEXT DEFAULT 'pending'
        );
    """)
    conn.commit()
    return conn


def get_dir_size(path: Path) -> int:
    """Calculate total size of a directory in bytes."""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Human-readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024**2:.1f} MB"
    else:
        return f"{size_bytes / 1024**3:.2f} GB"


# ---------------------------------------------------------------------------
# Git operations
# ---------------------------------------------------------------------------

def run_git(args: List[str], cwd: Optional[Path] = None,
            timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a git command, return CompletedProcess."""
    cmd = ["git"] + args
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
    )


def get_commit_hash(repo_path: Path) -> Optional[str]:
    """Get HEAD commit hash for a repo."""
    result = run_git(["rev-parse", "HEAD"], cwd=repo_path)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def clone_repo(url: str, dest: Path) -> bool:
    """Shallow clone a repo. Returns True on success."""
    log.info(f"Cloning {url} -> {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = run_git(["clone", "--depth", "1", url, str(dest)])
    if result.returncode != 0:
        log.error(f"Clone failed: {result.stderr.strip()}")
        return False
    return True


def update_repo(repo_path: Path) -> bool:
    """Pull latest for an existing repo. Returns True on success."""
    log.info(f"Updating {repo_path.name}")
    result = run_git(["pull", "--ff-only"], cwd=repo_path)
    if result.returncode != 0:
        # Shallow repos sometimes can't pull — try fetch + reset
        log.warning(f"Pull failed for {repo_path.name}, trying fetch...")
        fetch = run_git(["fetch", "--depth", "1", "origin"], cwd=repo_path)
        if fetch.returncode == 0:
            reset = run_git(["reset", "--hard", "origin/HEAD"], cwd=repo_path)
            if reset.returncode == 0:
                return True
        log.error(f"Update failed for {repo_path.name}: {result.stderr.strip()}")
        return False
    return True


# ---------------------------------------------------------------------------
# Repo commands
# ---------------------------------------------------------------------------

def cmd_repos(manifest: dict, conn: sqlite3.Connection, vault: Path,
              category: Optional[str] = None) -> dict:
    """Clone or update repos from the manifest. Returns change summary."""
    repos_dir = vault / "repos"
    repos_dir.mkdir(parents=True, exist_ok=True)

    changes = {"cloned": [], "updated": [], "failed": []}

    repos = manifest.get("repos", [])
    if category:
        repos = [r for r in repos if r.get("category", "").lower() == category.lower()]

    if not repos:
        log.info("No repos matching filter.")
        return changes

    log.info(f"Processing {len(repos)} repos...")
    now = datetime.now(timezone.utc).isoformat()

    for i, repo in enumerate(repos):
        name = repo["name"]
        url = repo["url"]
        dest = repos_dir / name

        try:
            if dest.exists() and (dest / ".git").exists():
                # Update existing
                success = update_repo(dest)
                status = "updated" if success else "update_failed"
            else:
                # Fresh clone
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=True)
                success = clone_repo(url, dest)
                status = "cloned" if success else "clone_failed"

            commit = get_commit_hash(dest) if success else None
            size = get_dir_size(dest) if success else 0

            conn.execute("""
                INSERT INTO repos (name, url, local_path, category, tags,
                                   last_cloned, last_updated, commit_hash,
                                   size_bytes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    url=excluded.url,
                    local_path=excluded.local_path,
                    category=excluded.category,
                    tags=excluded.tags,
                    last_updated=excluded.last_updated,
                    commit_hash=COALESCE(excluded.commit_hash, commit_hash),
                    size_bytes=CASE WHEN excluded.size_bytes > 0
                                    THEN excluded.size_bytes
                                    ELSE size_bytes END,
                    status=excluded.status
            """, (
                name, url, str(dest), repo.get("category", ""),
                json.dumps(repo.get("tags", [])),
                now if status == "cloned" else None,
                now, commit, size, status
            ))
            conn.commit()

            log.info(f"  [{status.upper()}] {name} ({format_size(size)})"
                     f" @ {commit[:8] if commit else '???'}")

            entry = {"name": name, "category": repo.get("category", ""),
                     "size": format_size(size),
                     "commit": commit[:8] if commit else "???"}
            if status == "cloned":
                changes["cloned"].append(entry)
            elif status == "updated":
                changes["updated"].append(entry)
            else:
                entry["error"] = status
                changes["failed"].append(entry)

        except subprocess.TimeoutExpired:
            log.error(f"  [TIMEOUT] {name} — clone took too long, skipping")
            conn.execute("""
                INSERT INTO repos (name, url, status)
                VALUES (?, ?, 'timeout')
                ON CONFLICT(name) DO UPDATE SET status='timeout'
            """, (name, url))
            conn.commit()
            changes["failed"].append({"name": name, "error": "timeout"})

        except Exception as e:
            log.error(f"  [ERROR] {name}: {e}")
            conn.execute("""
                INSERT INTO repos (name, url, status)
                VALUES (?, ?, 'error')
                ON CONFLICT(name) DO UPDATE SET status='error'
            """, (name, url))
            conn.commit()
            changes["failed"].append({"name": name, "error": str(e)})

        # Rate limit between clones (not after the last one)
        if i < len(repos) - 1:
            time.sleep(CLONE_DELAY)

    return changes


# ---------------------------------------------------------------------------
# Model commands
# ---------------------------------------------------------------------------

def download_model_hf_hub(hf_id: str, dest: Path) -> bool:
    """Download model using huggingface_hub library."""
    try:
        from huggingface_hub import snapshot_download
        log.info(f"Downloading {hf_id} via huggingface_hub -> {dest}")
        dest.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            repo_id=hf_id,
            local_dir=str(dest),
            local_dir_use_symlinks=False,
        )
        return True
    except ImportError:
        log.warning("huggingface_hub not installed, falling back to git clone")
        return download_model_git(hf_id, dest)
    except Exception as e:
        log.error(f"huggingface_hub download failed: {e}")
        return download_model_git(hf_id, dest)


def download_model_git(hf_id: str, dest: Path) -> bool:
    """Download model via git clone from HuggingFace."""
    url = f"https://huggingface.co/{hf_id}"
    log.info(f"Downloading {hf_id} via git clone -> {dest}")
    return clone_repo(url, dest)


def model_local_dir(vault: Path, hf_id: str) -> Path:
    """Convert HF ID to local directory path (/ -> --)."""
    safe_name = hf_id.replace("/", "--")
    return vault / "models" / safe_name


def cmd_models(manifest: dict, conn: sqlite3.Connection, vault: Path,
               download_id: Optional[str] = None) -> None:
    """List tracked models, optionally download one."""
    models = manifest.get("models", [])

    if download_id:
        # Download a specific model
        model = next((m for m in models if m["hf_id"] == download_id), None)
        if not model:
            # Allow download even if not in manifest
            model = {"hf_id": download_id, "arch_family": "unknown",
                     "param_count": "?", "vram_estimate_gb": 0,
                     "tags": [], "priority": "manual", "notes": "Manual download"}
            log.warning(f"{download_id} not in manifest — downloading anyway")

        dest = model_local_dir(vault, download_id)
        if dest.exists() and any(dest.iterdir()):
            log.info(f"{download_id} already downloaded at {dest}")
            return

        now = datetime.now(timezone.utc).isoformat()
        success = download_model_hf_hub(download_id, dest)
        status = "downloaded" if success else "download_failed"
        size = get_dir_size(dest) if success else 0

        conn.execute("""
            INSERT INTO models (hf_id, arch_family, param_count, vram_gb,
                                local_path, tags, downloaded_at, size_bytes,
                                status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(hf_id) DO UPDATE SET
                local_path=excluded.local_path,
                downloaded_at=excluded.downloaded_at,
                size_bytes=excluded.size_bytes,
                status=excluded.status
        """, (
            download_id, model.get("arch_family", ""),
            model.get("param_count", ""), model.get("vram_estimate_gb", 0),
            str(dest), json.dumps(model.get("tags", [])),
            now, size, status, model.get("notes", "")
        ))
        conn.commit()
        log.info(f"  [{status.upper()}] {download_id} ({format_size(size)})")
        return

    # List all tracked models
    log.info(f"Tracked models ({len(models)}):")
    log.info(f"{'HF ID':<48} {'Arch':<12} {'Params':<8} {'VRAM':<6} {'Priority':<8}")
    log.info("-" * 90)
    for m in models:
        hf_id = m["hf_id"]
        dest = model_local_dir(vault, hf_id)
        marker = " [LOCAL]" if dest.exists() else ""
        log.info(
            f"  {hf_id:<46} {m.get('arch_family', '?'):<12} "
            f"{m.get('param_count', '?'):<8} "
            f"{m.get('vram_estimate_gb', '?'):<6} "
            f"{m.get('priority', '?'):<8}{marker}"
        )


def cmd_models_high_priority(manifest: dict, conn: sqlite3.Connection,
                             vault: Path) -> None:
    """Download all high-priority models that aren't already local."""
    models = manifest.get("models", [])
    high = [m for m in models if m.get("priority") == "high"]
    log.info(f"High-priority models: {len(high)}")

    for m in high:
        hf_id = m["hf_id"]
        dest = model_local_dir(vault, hf_id)
        if dest.exists() and any(dest.iterdir()):
            log.info(f"  [SKIP] {hf_id} — already downloaded")
            continue
        cmd_models(manifest, conn, vault, download_id=hf_id)
        time.sleep(CLONE_DELAY)


# ---------------------------------------------------------------------------
# Status command
# ---------------------------------------------------------------------------

def cmd_status(conn: sqlite3.Connection, vault: Path) -> dict:
    """Show what's in the vault. Returns summary dict for report generation."""
    log.info("=== Clymene Vault Status ===")
    log.info(f"Vault root: {vault}")
    log.info("")

    summary = {"repos": [], "models": [], "datasets": [], "total_size": 0}

    # Repos
    rows = conn.execute(
        "SELECT name, category, status, size_bytes, commit_hash, last_updated "
        "FROM repos ORDER BY category, name"
    ).fetchall()
    total_repo_size = sum(r["size_bytes"] or 0 for r in rows)
    log.info(f"Repos: {len(rows)} tracked, {format_size(total_repo_size)} total")
    if rows:
        by_status: Dict[str, int] = {}
        for r in rows:
            s = r["status"] or "unknown"
            by_status[s] = by_status.get(s, 0) + 1
        log.info(f"  Status breakdown: {dict(by_status)}")
        for r in rows:
            commit = r["commit_hash"][:8] if r["commit_hash"] else "--------"
            log.info(
                f"  [{r['status']:<14}] {r['name']:<28} "
                f"{r['category']:<14} {format_size(r['size_bytes'] or 0):<10} "
                f"{commit}"
            )
            summary["repos"].append({
                "name": r["name"], "category": r["category"],
                "status": r["status"], "size": format_size(r["size_bytes"] or 0),
                "commit": commit,
            })
    log.info("")

    # Models
    rows = conn.execute(
        "SELECT hf_id, arch_family, status, size_bytes, downloaded_at "
        "FROM models ORDER BY arch_family, hf_id"
    ).fetchall()
    total_model_size = sum(r["size_bytes"] or 0 for r in rows)
    log.info(f"Models: {len(rows)} in registry, {format_size(total_model_size)} total")
    for r in rows:
        log.info(
            f"  [{r['status']:<14}] {r['hf_id']:<48} "
            f"{r['arch_family']:<12} {format_size(r['size_bytes'] or 0)}"
        )
        summary["models"].append({
            "hf_id": r["hf_id"], "arch": r["arch_family"],
            "status": r["status"], "size": format_size(r["size_bytes"] or 0),
        })
    log.info("")

    # Datasets
    rows = conn.execute(
        "SELECT name, status, size_bytes FROM datasets ORDER BY name"
    ).fetchall()
    log.info(f"Datasets: {len(rows)} in registry")
    for r in rows:
        log.info(f"  [{r['status']:<14}] {r['name']}")
        summary["datasets"].append({"name": r["name"], "status": r["status"]})
    log.info("")

    # Disk summary
    total = total_repo_size + total_model_size
    summary["total_size"] = format_size(total)
    log.info(f"Total vault size: {format_size(total)}")

    return summary


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

REPORTS_DIR = CLYMENE_ROOT / "reports"


def write_report(summary: dict, new_clones: list = None,
                 updated: list = None, failed: list = None) -> Path:
    """Write a hoard report to reports/YYYY-MM-DD_hoard.md."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_DIR / f"{today}_hoard.md"

    lines = [
        f"# Clymene Hoard Report — {today}",
        "",
        f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
    ]

    # New clones
    if new_clones:
        lines.append(f"## New Clones ({len(new_clones)})")
        lines.append("")
        for item in new_clones:
            lines.append(f"- **{item['name']}** ({item.get('category', '?')}) — "
                         f"{item.get('size', '?')}")
        lines.append("")

    # Updated repos
    if updated:
        lines.append(f"## Updated ({len(updated)})")
        lines.append("")
        for item in updated:
            lines.append(f"- **{item['name']}** — {item.get('commit', '?')}")
        lines.append("")

    # Failures
    if failed:
        lines.append(f"## Failed ({len(failed)})")
        lines.append("")
        for item in failed:
            lines.append(f"- **{item['name']}** — {item.get('error', 'unknown error')}")
        lines.append("")

    # No changes
    if not new_clones and not updated and not failed:
        lines.append("## No Changes")
        lines.append("")
        lines.append("All repos up to date. Nothing new to clone.")
        lines.append("")

    # Vault summary
    lines.append("## Vault Summary")
    lines.append("")
    lines.append(f"- **Repos:** {len(summary.get('repos', []))}")
    lines.append(f"- **Models:** {len(summary.get('models', []))}")
    lines.append(f"- **Total size:** {summary.get('total_size', '?')}")
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Report written: {report_path}")
    return report_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="clymene",
        description="Clymene — archive open-source tools and models",
    )
    parser.add_argument(
        "command", nargs="?", default=None,
        choices=["repos", "models", "status"],
        help="Command to run",
    )
    parser.add_argument(
        "--category", type=str, default=None,
        help="Filter repos by category",
    )
    parser.add_argument(
        "--download", type=str, default=None, metavar="HF_ID",
        help="Download a specific HuggingFace model",
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Full hoard cycle: clone all repos + download high-priority models",
    )

    args = parser.parse_args()

    # Must specify command or --once
    if not args.command and not args.once:
        parser.print_help()
        sys.exit(1)

    manifest = load_manifest()
    vault = resolve_vault_root(manifest)
    conn = init_db(DB_PATH)

    log.info(f"Vault root: {vault}")
    log.info(f"Registry:   {DB_PATH}")

    try:
        if args.once:
            log.info("=== Full hoard cycle ===")
            changes = cmd_repos(manifest, conn, vault)
            cmd_models_high_priority(manifest, conn, vault)
            summary = cmd_status(conn, vault)
            report = write_report(
                summary,
                new_clones=changes["cloned"],
                updated=changes["updated"],
                failed=changes["failed"],
            )
            # Save timestamp so Pronoia can check cooldown
            ts_file = DATA_DIR / "last_run.txt"
            ts_file.write_text(
                datetime.now(timezone.utc).isoformat(), encoding="utf-8"
            )
            log.info(f"Timestamp saved: {ts_file}")

        elif args.command == "repos":
            cmd_repos(manifest, conn, vault, category=args.category)

        elif args.command == "models":
            cmd_models(manifest, conn, vault, download_id=args.download)

        elif args.command == "status":
            cmd_status(conn, vault)

    except KeyboardInterrupt:
        log.info("Interrupted by user — vault state saved.")
    finally:
        conn.close()

    log.info("Done.")


if __name__ == "__main__":
    main()
