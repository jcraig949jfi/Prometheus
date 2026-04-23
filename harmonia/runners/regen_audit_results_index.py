"""Regenerate harmonia/memory/audit_results_index.md from cartography/docs/.

Closes axis-1 sprawl observation #3 (audit results scattered, no index) per
auditor concept_map.md axis-1 first-pass 2026-04-23.

Best-effort metadata extraction; rows where parsing fails are still listed
with file-path + mtime so humans can fill in. Re-run after new audits land.
"""
import json
import os
import re
import sys
import io
import time
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DOCS = Path("cartography/docs")
OUT = Path("harmonia/memory/audit_results_index.md")

# File-name patterns considered audit-like
PATTERNS = [
    re.compile(r"^audit_.*_results\.(json|md)$"),
    re.compile(r"^reaudit_.*_results.*\.(json|md)$"),
    re.compile(r"^wsw_.*_results\.json$"),
    re.compile(r"^.*_investigation_results\.json$"),
    re.compile(r"^pattern_\d+_audit\.md$"),
    re.compile(r"^report.*audit.*results\.json$"),
    re.compile(r"^data_audit.*\.md$"),
]


def is_audit_file(name):
    return any(p.match(name) for p in PATTERNS)


def extract_fid(name):
    """Extract F-ID from filename if present (e.g., F011, F041a)."""
    m = re.search(r"(?:^|[_./-])(F\d{2,4}[a-z]?)(?=[_./-]|$)", name)
    return m.group(1) if m else ""


def extract_pid(name):
    m = re.search(r"(?:^|[_./-])(P\d{2,4})(?=[_./-]|$)", name)
    return m.group(1) if m else ""


def _s(v, n):
    """Safe str-truncate helper; handles non-str / nested values."""
    if v is None:
        return ""
    if not isinstance(v, str):
        v = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
    return v[:n]


def extract_metadata_json(path):
    """Best-effort metadata from JSON audit files."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    out = {}
    out["verdict"] = _s(data.get("verdict") or data.get("status"), 80)
    out["instance"] = _s(data.get("instance") or data.get("posted_by"), 40)
    out["task_id"] = _s(data.get("task_id"), 80)
    out["mutation"] = data.get("tensor_mutation_recommended", None)
    out["headline"] = _s(data.get("headline") or data.get("note"), 200)
    return out


def extract_metadata_md(path):
    """Best-effort metadata from MD audit files (parse frontmatter + grep)."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return {}
    out = {}
    # Frontmatter parse (between --- ---)
    fm = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if fm:
        body = fm.group(1)
        for line in body.split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k in ("auditor", "instance", "resolver"):
                    out["instance"] = v
                if k == "verdict":
                    out["verdict"] = v[:80]
                if k in ("teeth_test_verdict", "status"):
                    out.setdefault("verdict", v[:80])
    # Heuristic: find first ## Verdict / **Verdict:** block
    m = re.search(r"\*\*Verdict.*?:\*\*\s*([^\n]{1,160})", text)
    if m and not out.get("verdict"):
        out["verdict"] = m.group(1).strip()[:80]
    # Headline: first non-blank non-frontmatter line under ##
    headlines = re.findall(r"^##\s+(.+)$", text, re.MULTILINE)
    if headlines:
        out["headline"] = headlines[0][:200]
    return out


def main():
    files = []
    for entry in sorted(DOCS.iterdir()):
        if entry.is_file() and is_audit_file(entry.name):
            files.append(entry)
    print(f"[index] found {len(files)} audit-like files")

    rows = []
    for path in files:
        meta = extract_metadata_json(path) if path.suffix == ".json" else extract_metadata_md(path)
        mtime = time.strftime("%Y-%m-%d", time.gmtime(path.stat().st_mtime))
        size_kb = path.stat().st_size // 1024
        fid = extract_fid(path.name)
        pid = extract_pid(path.name)
        rows.append({
            "filename": path.name,
            "f_id": fid,
            "p_id": pid,
            "mtime": mtime,
            "size_kb": size_kb,
            "instance": meta.get("instance", "")[:40],
            "verdict": meta.get("verdict", "")[:60],
            "headline": meta.get("headline", "")[:120],
            "mutation": meta.get("mutation"),
        })

    # Sort by mtime descending (newest first)
    rows.sort(key=lambda r: r["mtime"], reverse=True)

    # Render MD
    md = []
    md.append("---")
    md.append("name: Audit results index (cartography/docs/)")
    md.append(
        "purpose: Single navigable cross-F-ID chronological index of substrate audit artifacts. "
        "Closes axis-1 sprawl observation #3 (auditor concept_map.md 2026-04-23) — audit "
        "results live across cartography/docs/ with no central navigation."
    )
    md.append("source_of_truth: cartography/docs/ files themselves (audit_*_results, reaudit_*, wsw_*, *_investigation_*, pattern_*_audit, report*audit*, data_audit*)")
    md.append("regeneration: `python harmonia/runners/regen_audit_results_index.py`")
    md.append("complementary_to: per-F-ID inline annotations in build_landscape_tensor.py (sessionB axis-5 consolidation #2, 2026-04-23 1776911782623-0). This index handles cross-F-ID chronological queries; sessionB's inline annotations handle per-F-ID forward navigation. Both useful.")
    md.append(f"generated_at: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    md.append("generated_by: Harmonia_M2_auditor 2026-04-23 (axis-1 consolidation candidate #1)")
    md.append("---")
    md.append("")
    md.append("# Audit results index")
    md.append("")
    md.append(f"**Auto-generated** view of {len(rows)} audit-like artifacts in `cartography/docs/`. Newest first.")
    md.append("")
    md.append("Best-effort metadata extraction — empty cells mean the file's verdict / instance was not in a parsable location. Cells in the table are NOT the source of truth; the linked file is. Discipline: never edit this MD directly; re-run the regenerator after audits land.")
    md.append("")
    md.append("## Index")
    md.append("")
    md.append("| Date | F-ID | P-ID | Instance | Verdict | File | Size kB |")
    md.append("|---|---|---|---|---|---|---|")
    for r in rows:
        verdict_short = r["verdict"].replace("|", "/").replace("\n", " ")[:60]
        instance_short = r["instance"].replace("|", "/")[:40]
        md.append(
            f"| {r['mtime']} | {r['f_id'] or '—'} | {r['p_id'] or '—'} | "
            f"{instance_short or '—'} | {verdict_short or '—'} | "
            f"[{r['filename']}](../../cartography/docs/{r['filename']}) | {r['size_kb']} |"
        )
    md.append("")
    md.append("## Cross-references")
    md.append("")
    md.append("- `harmonia/memory/concept_map.md` axis 1 — sprawl observation #3 (this index closes it) and consolidation candidate #1 (this file delivers it).")
    md.append("- `harmonia/memory/lineage_registry_view.md` — companion axis-1 view (Pattern-30 lineage classifications by F-ID).")
    md.append("- `harmonia/memory/build_landscape_tensor.py` — F-ID definitions; sessionB axis-5 consolidation #2 propagated 2026-04-22 audit outcomes inline (F041a, F044, F045).")
    md.append("- `harmonia/memory/decisions_for_james.md` — narrative entries for major retraction / promotion / methodology decisions (this index covers the audit *artifacts*; decisions_for_james covers the *narrative reasoning*).")
    md.append("")
    md.append("## Discipline")
    md.append("")
    md.append("1. New audits should land at `cartography/docs/audit_<F-ID>_<short_descriptor>_results.{json,md}` per existing convention.")
    md.append("2. After landing, re-run `harmonia/runners/regen_audit_results_index.py`.")
    md.append("3. Never edit this MD as canonical; treat it as a view (Pattern-17 discipline).")
    md.append("4. If parsing extracts the wrong verdict / instance, fix the source file's metadata block (frontmatter on MD files; top-level keys on JSON files), THEN re-regenerate.")
    md.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"[index] wrote {OUT} with {len(rows)} rows")


if __name__ == "__main__":
    main()
