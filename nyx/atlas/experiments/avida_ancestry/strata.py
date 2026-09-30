"""The frozen domain of the Avida ancestry packet: every .spop the body ships, with flags read from CONFIG ONLY.

This module never opens a .spop. The file list, sizes and sha256 come from Techne's tracked
techne/fossils/specimens/avida/UPSTREAM_HASHES.txt; the flags come from each test's config directory (avida.cfg, the
event files, test_list overrides) in the vault body. Three further properties are decided from a file's CONTENT at
adjudication time by rules fixed here and in the packet: in_scope (the #format line), asex (no row names two parents),
hostonly (no horz/vert row).

    TECHNE_FOSSIL_VAULT=<older-bodies vault> python -m nyx.atlas.experiments.avida_ancestry.strata
        -> nyx/atlas/experiments/avida_ancestry/STRATA.json

Flags (all config-derived):
    role        expected | config        'config' files are INPUTS of unknown provenance: never adjudicated
    kind        population | flame       SaveFlameData output is not a genotype save
    hist0       the test's SavePopulation line carries save_historic=0
    loaded      a LoadPopulation event fires at or before this file's save (the run did not start from an inject)
    deme        NUM_DEMES > 1 or DEMES_USE_GERMLINE != 0 (cDeme holds passive references on genotypes)
    class_off   DISABLE_GENOTYPE_CLASSIFICATION 1 (new genotypes are founded with no parents)
    sexual_config  an instruction set or start organism names a *sex* instruction (the birth chamber then holds
                active references on genotypes)
    series      the run this file is one save of, where the body ships successive saves; sever_at for the two
                whole-genome-duplication runs (the u 99 event, stamped 100)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
HASHES = REPO / "techne" / "fossils" / "specimens" / "avida" / "UPSTREAM_HASHES.txt"
OUT = HERE / "STRATA.json"
_T = re.compile(r"-(-?\d+)\.spop$")
SERIES = {"whole_genome_duplication": 100, "whole_genome_duplication_nopc_prepend": 100}


def _event_time(tok: str):
    """'begin' -> -1, 'N' or 'N:step[:end]' -> N. The driver fires an event for update N AFTER update N is processed."""
    head = tok.split(":")[0]
    if head == "begin":
        return -1
    try:
        return int(head)
    except ValueError:
        return None


def _fires_at(trigger: str, T: int) -> bool:
    """Does an event with this timing token fire at update T? 'begin' | 'N' | 'N:step' | 'N:step:end|M'."""
    p = trigger.split(":")
    start = _event_time(p[0])
    if start is None:
        return False
    if len(p) == 1:
        return T == start
    try:
        step = int(p[1])
    except ValueError:
        return False
    if T < start or step <= 0 or (T - start) % step:
        return False
    return len(p) < 3 or p[2] == "end" or (p[2].lstrip("-").isdigit() and T <= int(p[2]))


def _events(cfgdir: Path):
    ev = []
    for p in sorted(cfgdir.glob("*.cfg")):
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines()):
            s = line.split("#")[0].strip()
            if not s:
                continue
            t = s.split()
            if t[0] in ("i", "immediate") and len(t) >= 2:
                trigger, action, args = "begin", t[1], " ".join(t[2:])
            elif t[0] in ("u", "update") and len(t) >= 3:
                trigger, action, args = t[1], t[2], " ".join(t[3:])
            elif t[0] in ("g", "generation", "b", "births", "o", "org_id") and len(t) >= 3:
                trigger, action, args = "?", t[2], " ".join(t[3:])   # not update-timed: `when` stays None
            else:
                continue
            ev.append({"file": p.name, "line": n + 1, "trigger": trigger, "when": _event_time(trigger), "action": action, "args": args})
    return ev


def _config(cfgdir: Path, test_list: Path) -> dict:
    cfg = {}
    av = cfgdir / "avida.cfg"
    if av.exists():
        for line in av.read_text(encoding="utf-8", errors="replace").splitlines():
            t = line.split("#")[0].split()
            if len(t) >= 2:
                cfg[t[0]] = t[1]
    if test_list.exists():
        for line in test_list.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip().startswith("args"):
                for m in re.finditer(r"-set\s+(\S+)\s+(\S+)", line):
                    cfg[m.group(1)] = m.group(2)
    return cfg


_SEX_INST = re.compile(r"^[a-z0-9-]*sex[a-z0-9-]*$")


def _sexual(cfgdir: Path) -> list:
    """Instruction names containing 'sex' (divide-sex, repro-sex, ...) in an instruction set or a start organism.
    Sexual births wait in the birth chamber, which holds ACTIVE references on the parents' genotypes
    (cBirthChamber.cc:135-162): a genotype with no organism left can stay alive there and is then written by nobody."""
    hits = set()
    for p in sorted(list(cfgdir.glob("*.cfg")) + list(cfgdir.glob("*.org"))):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            t = line.split("#")[0].split()
            if not t:
                continue
            name = (t[1] if t[0] == "INST" and len(t) > 1 else t[0]).split(":")[0]
            if _SEX_INST.match(name):
                hits.add(f"{p.name}: {name}")
    return sorted(hits)


def build(body: Path) -> dict:
    tests = body / "upstream" / "tree" / "avida-core" / "tests"
    rows = []
    for line in HASHES.read_text(encoding="utf-8").splitlines():
        parts = line.split(None, 2)
        if len(parts) != 3 or not parts[2].strip().endswith(".spop"):
            continue
        sha, size, rel = parts[0], int(parts[1]), parts[2].strip().replace("\\", "/")
        seg = rel.split("/")
        test, role = seg[seg.index("tests") + 1], seg[seg.index("tests") + 2]
        cfgdir = tests / test / "config"
        ev = _events(cfgdir)
        cfg = _config(cfgdir, tests / test / "test_list")
        m = _T.search(rel)
        T = int(m.group(1)) if m else None
        loads = [e for e in ev if e["action"] == "LoadPopulation"]
        saves = [e for e in ev if e["action"] == "SavePopulation"]
        loaded = None
        if role == "expected" and T is not None:
            loaded = False
            for e in loads:
                if e["when"] is None or e["when"] < T:      # a load whose time cannot be read counts as a load
                    loaded = True
                elif e["when"] == T:
                    # a load and a save in the same update: the load counts unless, in the same event file, every
                    # save line that fires at T stands before it (events of one update run in file order)
                    same = [s for s in saves if s["file"] == e["file"] and _fires_at(s["trigger"], T)]
                    loaded = loaded or not same or any(e["line"] < s["line"] for s in same)
        rows.append({
            "path": rel, "sha256": sha, "bytes": size, "test": test, "role": role,
            "kind": "flame" if "flame_data" in rel else "population", "T": T,
            "hist0": any("save_historic=0" in s["args"] for s in saves),
            "loaded": loaded,
            "deme": int(cfg.get("NUM_DEMES", "1")) > 1 or cfg.get("DEMES_USE_GERMLINE", "0") != "0",
            "class_off": cfg.get("DISABLE_GENOTYPE_CLASSIFICATION", "0") == "1",
            "sexual_config": bool(_sexual(cfgdir)),
            "series": test if test in SERIES else None, "sever_at": SERIES.get(test),
            "config_evidence": {"save_lines": [f"{s['file']}:{s['line']} {s['when']} {s['args']}".strip() for s in saves],
                                "load_lines": [f"{e['file']}:{e['line']} {e['when']} {e['args']}".strip() for e in loads],
                                "NUM_DEMES": cfg.get("NUM_DEMES"), "DEMES_USE_GERMLINE": cfg.get("DEMES_USE_GERMLINE"),
                                "DISABLE_GENOTYPE_CLASSIFICATION": cfg.get("DISABLE_GENOTYPE_CLASSIFICATION"),
                                "sexual_instructions": _sexual(cfgdir)},
        })
    rows.sort(key=lambda r: r["path"])
    return {"schema": "nyx.avida_ancestry_strata/1",
            "source": "techne/fossils/specimens/avida/UPSTREAM_HASHES.txt (list, bytes, sha256) + the body's test configs (flags); no .spop opened",
            "n_files": len(rows), "files": rows}


def stratum(row: dict, content: dict) -> dict:
    """The packet's strata. `content` is spop.measure() of the file plus 'in_scope' -- decided from the bytes at
    adjudication, by rules fixed before any byte was read."""
    base = (row["role"] == "expected" and row["kind"] == "population" and content["in_scope"]
            and content["n_unparsed"] == 0)
    s_a = (base and not row["hist0"] and not row["class_off"] and not row["sexual_config"]
           and not content["multi_parent"] and not content["parasite"])
    return {"S_A": bool(s_a),
            "S_B": bool(s_a and row["loaded"] is False and not row["deme"]),
            "S_H0": bool(base and row["hist0"])}


def main() -> int:
    from techne.fossils import vault
    body = vault.body_dir("avida")
    if not (body / "upstream" / "tree" / "avida-core" / "tests").is_dir():
        print("avida body not found under", body, "-- set TECHNE_FOSSIL_VAULT to the vault that holds it")
        return 2
    s = build(body)
    OUT.write_text(json.dumps(s, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    fs = s["files"]
    print(f"{s['n_files']} .spop files; expected {sum(f['role'] == 'expected' for f in fs)}, config {sum(f['role'] == 'config' for f in fs)}; "
          f"flame {sum(f['kind'] == 'flame' for f in fs)}; hist0 {sum(f['hist0'] for f in fs)}; loaded {sum(f['loaded'] is True for f in fs)}; "
          f"deme {sum(f['deme'] for f in fs)}; class_off {sum(f['class_off'] for f in fs)}; in a series {sum(f['series'] is not None for f in fs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
