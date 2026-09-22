"""Cross-reference the Frankenstein monsters against the workshop (harvest charter VIII).

LAYER: NECROPOLIS VALIDATION.  Reads ORGANS.jsonl, the monster files, TOOLS.jsonl and
the working tree; writes FRANKENSTEIN_XREF.json.  Nothing is executed except
`compile()` of organ source files and `importlib.util.find_spec` on their top-level
imports (no organ module is imported, no monster is run -- charter VIII: "do NOT
run them").

    python engine/necropolis/workshop/build_frankenstein_xref.py
"""
from __future__ import annotations

import ast
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NECRO = HERE.parent
REPO = HERE.parents[2]
MONSTERS = ["FRANK-002", "FRANK-003", "FRANK-004"]

# Per-monster hard dependencies named by the monster text itself (lightning_experiment /
# organ_execution_plan / cleric_gate).  Each is a (label, probe) pair; probes are read-only.
STDLIB_LIKE = set(sys.stdlib_module_names) | {"charon", "engine", "agents", "techne", "harmonia", "prometheus_math",
                                              "archaeon", "proteus", "vivarium", "comms", "roles", "sigma_kernel", "keys",
                                              "apollo", "herakles", "ergon", "attacks", "scripts", "pivot"}


def organs_for(agent: str) -> list[dict]:
    rows = [json.loads(l) for l in (NECRO / "ORGANS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if r["source_agent"] == agent]


def resolve_location(loc: str) -> dict:
    """Existence of an organ location on the reachable tree (file, dir, file::symbol, glob)."""
    loc = (loc or "").strip()
    out = {"location": loc, "kind": None, "exists": None}
    if not loc:
        out["kind"] = "NONE"
        return out
    base = loc.split("::")[0].strip()
    sym = loc.split("::")[1].strip() if "::" in loc else None
    cands = [REPO / base, NECRO / base]
    for c in cands:
        if "*" in base:
            hits = list(c.parent.glob(c.name)) if c.parent.exists() else []
            if hits:
                out.update(kind="GLOB", exists=True, n_matches=len(hits), resolved=str(hits[0].relative_to(REPO).as_posix()))
                return out
        elif c.is_file():
            out.update(kind="FILE", exists=True, resolved=c.relative_to(REPO).as_posix())
            if sym:
                src = c.read_text(encoding="utf-8", errors="replace")
                names = [n.strip() for n in re.split(r"\band\b|,", sym) if n.strip()]
                out["symbols"] = {n: bool(re.search(r"\bdef\s+" + re.escape(n.split()[0]) + r"\b", src)) for n in names[:3]}
            return out
        elif c.is_dir():
            out.update(kind="DIR", exists=True, resolved=c.relative_to(REPO).as_posix(),
                       n_py=len(list(c.rglob("*.py"))))
            return out
    out.update(kind="FILE" if base.endswith((".py", ".json", ".jsonl", ".md")) else "PATH", exists=False)
    return out


def import_health(path: Path) -> dict:
    """compile() + top-level import resolvability.  Never imports the module."""
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        return {"compiles": False, "error": str(e)[:200]}
    tops = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                tops.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            tops.add(node.module.split(".")[0])
    missing, local = [], []
    for t in sorted(tops):
        if t in STDLIB_LIKE:
            continue
        try:
            found = importlib.util.find_spec(t) is not None
        except (ValueError, ModuleNotFoundError):
            found = False
        if found:
            continue
        # sibling module reached through sys.path surgery in the organ (agents/<x>/src style)
        ancestors = [path.parent, *path.parents]
        local_hit = any((a / (t + ".py")).is_file() or (a / t).is_dir() for a in ancestors if REPO in a.parents or a == REPO)             or (REPO / "agents" / t).is_dir() or bool(list((REPO / "agents").glob("*/src/" + t + ".py")))
        if local_hit:
            local.append(t)
        else:
            missing.append(t)
    return {"compiles": True, "third_party_imports": sorted(t for t in tops if t not in STDLIB_LIKE),
            "local_sys_path_imports": local, "missing_here": missing}


def tools_for(monster_id: str) -> list[dict]:
    p = HERE / "TOOLS.jsonl"
    if not p.exists():
        return []
    out = []
    for l in p.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        if monster_id in (r.get("frankenstein_refs") or []):
            out.append({"tool_id": r["tool_id"], "name": r["name"], "status": r["necropolis_status"],
                        "path": r.get("current_path"), "dependency_status": r.get("dependency_status")})
    return out


def ledger_field_census(path: Path, fields: list[str]) -> dict:
    n, present, bad = 0, {f: 0 for f in fields}, 0
    for l in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not l.strip():
            continue
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            bad += 1
            continue
        n += 1
        for f in fields:
            if f in r:
                present[f] += 1
    return {"path": path.relative_to(REPO).as_posix(), "rows": n, "unparseable": bad, "rows_with_field": present}


def named_scripts(text: str) -> list[str]:
    return sorted(set(re.findall(r"[A-Za-z0-9_./-]+\.py", text)))


def main() -> int:
    xref = {"_README": "Measured cross-reference of FRANK-002/003/004 against the workshop registry and the reachable tree "
                       "(harvest charter VIII).  Nothing here ran a monster.  'missing_here' means the package is absent "
                       "for THIS interpreter (" + sys.version.split()[0] + "); other hosts differ.",
            "generated_by": "engine/necropolis/workshop/build_frankenstein_xref.py", "monsters": {}}
    for mid in MONSTERS:
        m = json.loads((NECRO / "monsters" / f"{mid}.monster.json").read_text(encoding="utf-8"))
        agent = m["graves_raided"][0]
        organs = []
        for o in organs_for(agent):
            loc = resolve_location(o.get("location", ""))
            row = {"organ_id": o["organ_id"], "organ_type": o["organ_type"], "in_monster": any(x["organ_id"] == o["organ_id"] for x in m["organs"]),
                   "executed_by_necromancer": o.get("executed_by_necromancer"), **loc}
            if loc.get("exists") and loc.get("kind") == "FILE" and loc["resolved"].endswith(".py"):
                row["import_health"] = import_health(REPO / loc["resolved"])
            organs.append(row)
        plan_text = m["organ_execution_plan"] + " " + json.dumps(m["lightning_experiment"])
        scripts = []
        for s in named_scripts(plan_text):
            cands = [REPO / s, NECRO / s, NECRO / "dossiers" / s]
            hit = next((c for c in cands if c.is_file()), None)
            if hit is None:  # bare basename: search the tree once
                found = list(REPO.rglob(Path(s).name)) if "/" not in s else []
                found = [f for f in found if "__pycache__" not in f.parts and ".git" not in f.parts]
                hit = found[0] if len(found) == 1 else None
                if len(found) > 1:
                    scripts.append({"named": s, "exists": True, "ambiguous": [f.relative_to(REPO).as_posix() for f in found[:5]]})
                    continue
            scripts.append({"named": s, "exists": hit is not None, "resolved": hit.relative_to(REPO).as_posix() if hit else None})
        entry = {"title": m["title"], "grave": agent, "cleric_gate_status": m["cleric_gate"]["status"],
                 "consumer_reachable_now": m["consumer"].get("reachable_now"),
                 "depends_on_frontier": m["modern_capability_enabling"].get("depends_on_frontier"),
                 "organs": organs, "plan_named_scripts": scripts, "workshop_tools": tools_for(mid),
                 "organ_summary": {"total": len(organs), "in_monster": sum(o["in_monster"] for o in organs),
                                   "located": sum(1 for o in organs if o["exists"]),
                                   "unlocated_or_missing": [o["organ_id"] for o in organs if not o["exists"]]},
                 "blocking_dependencies": []}
        if mid == "FRANK-002":
            led = REPO / "agents/hephaestus/ledger.jsonl"
            census = ledger_field_census(led, ["judge_version", "api_state", "model", "frame"]) if led.exists() else {"missing": True}
            entry["judge_attestation_census"] = census
            entry["blocking_dependencies"] = [
                {"dep": "frozen Hephaestus judge attested by judge_version + api_state on every ledger row",
                 "measured": census, "status": "UNATTESTABLE_FROM_LEDGER" if census.get("rows_with_field", {}).get("judge_version", 0) == 0 else "CHECK",
                 "consequence": "cleric_gate note (i): if no frozen judge can be attested the monster is not runnable; stage 0 stops before spend"},
                {"dep": "python package openai (hephaestus forge judge client)", "status": "MISSING" if importlib.util.find_spec("openai") is None else "PRESENT",
                 "workshop_tool": "NT-082 heph_knockout_ablation NEEDS_DEPENDENCY"},
                {"dep": "LLM spend for 1000 hypotheses + 1000 forge judgements (stage 1)", "status": "HITL_SPEND_AUTHORISATION_REQUIRED",
                 "consequence": "outside CORONER RUN scope (CORONER_RUN.md M-clauses cover reads and replays; generation is X4/X5)"},
                {"dep": "consumer (frozen-judge forge ledger) reachable_now", "status": str(m["consumer"].get("reachable_now"))},
            ]
        elif mid == "FRANK-003":
            entry["blocking_dependencies"] = [
                {"dep": "historical kill_ledger.jsonl / kill_ledger_enriched.jsonl bytes", "status": "ABSENT (gitignored state/, both trees) -- plan already says it does not read them",
                 "consequence": "stage 0 must REGENERATE the verdict-only ledger; the on-record 699-row numbers are not replayable from bytes"},
                {"dep": "third-party packages for the harnesses", "status": "see organs[*].import_health.missing_here"},
                {"dep": "test suites 146 / 608+1 / 59 must reproduce (plan (a))", "status": "NOT_RE_RUN_BY_KEEPER (author-run pytest counts only; workshop AUTHOR_TESTS.json)"},
            ]
        elif mid == "FRANK-004":
            entry["blocking_dependencies"] = [
                {"dep": "scipy (ks_2samp parity)", "status": "MISSING" if importlib.util.find_spec("scipy") is None else "PRESENT"},
                {"dep": "MAHLER_TABLE (prometheus_math/databases/_mahler_data.py)", "status": "PRESENT" if (REPO / "prometheus_math/databases/_mahler_data.py").exists() else "MISSING"},
                {"dep": "split-half positive control passable", "status": "DEAD_BEFORE_RUN",
                 "measured": "run_controls.py::adapters_resampling_null.PERTURBATION.split_half_control_fails_at_alpha_rate_for_iid_continuous (hit rate 0.0133, 0/30 resolvable)",
                 "consequence": "kill criterion (2) fires on synthetic data; see coroner_plans/CR-001 pre_run_findings PRF-1; design must be refiled before HITL"},
            ]
        xref["monsters"][mid] = entry
    out = HERE / "FRANKENSTEIN_XREF.json"
    out.write_text(json.dumps(xref, indent=1), encoding="utf-8", newline="\n")
    for mid, e in xref["monsters"].items():
        print(mid, e["grave"], "organs", e["organ_summary"], "| scripts", sum(s["exists"] for s in e["plan_named_scripts"]), "/", len(e["plan_named_scripts"]),
              "| tools", [t["tool_id"] + ":" + t["status"] for t in e["workshop_tools"]])
        for b in e["blocking_dependencies"]:
            print("   ", b["dep"][:70], "->", b["status"] if isinstance(b["status"], str) else b["status"])
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
