"""Read an Avida Structured Population Save (.spop) and compute the ancestry observables.

Everything here follows the WRITER in the fossil, not any file:
    Output::File::Endl / WriteColumnDesc   avida-core/source/output/File.cc:183-252
        line 1 '#filetype genotype_data', line 2 '#format <column names> ', then '# ...' comments, then one row per
        line, fields separated by ONE space, written in the order the Write calls were made.
    Genotype::LegacySave                   avida-core/source/systematics/Genotype.cc:356-392   (+ Genome::LegacySave)
        id src src_args parents num_units total_units length merit gest_time fitness gen_born update_born
        update_deactivated depth hw_type inst_set sequence
    cPopulation::SavePopulation            avida-core/source/main/cPopulation.cc:6362-6563
        living genotypes first (each followed by cells gest_offset lineage ...), then, if save_historic, every
        genotype on the arbiter's historic list (the 17 columns above and nothing else).

A DEFECT OF THE FORMAT the reader must survive: src_args is written raw, and an injected organism's source arguments
may contain spaces (PopulationActions.cc:169 passes "whole-genome duplication"). Such a row has more
whitespace-separated tokens than the #format line names and every later column is shifted. parse_row therefore
anchors on the first token at or after position 3 that looks like a parents field and is followed by three
integers, and takes everything between position 2 and it as src_args.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

FIRST17 = ("id", "src", "src_args", "parents", "num_units", "total_units", "length", "merit", "gest_time", "fitness",
           "gen_born", "update_born", "update_deactivated", "depth", "hw_type", "inst_set", "sequence")
_PARENTS = re.compile(r"^(\(none\)|-?\d+(,-?\d+)*)$")
_INT = re.compile(r"^-?\d+$")
_T = re.compile(r"-(-?\d+)\.spop$")
MAX_SHIFT = 8


def parse_row(toks: List[str]) -> Optional[dict]:
    """One data row -> dict, or None if no alignment satisfies the writer's column types."""
    if len(toks) < 17 or not _INT.match(toks[0]):
        return None
    for k in range(0, MAX_SHIFT + 1):
        if len(toks) < 17 + k:
            break
        if not _PARENTS.match(toks[3 + k]):
            continue
        if not all(_INT.match(toks[i + k]) for i in (4, 5, 6, 10, 11, 12, 13, 14)):
            continue
        par = toks[3 + k]
        rest = toks[17 + k:]
        return {
            "id": int(toks[0]), "src": toks[1], "src_args": " ".join(toks[2:3 + k]), "shift": k,
            "parents": [] if par == "(none)" else [int(x) for x in par.split(",")],
            "num_units": int(toks[4 + k]), "total_units": int(toks[5 + k]), "length": int(toks[6 + k]),
            "gen_born": int(toks[10 + k]), "update_born": int(toks[11 + k]), "update_deactivated": int(toks[12 + k]),
            "depth": int(toks[13 + k]), "hw_type": int(toks[14 + k]), "inst_set": toks[15 + k], "sequence": toks[16 + k],
            "n_cells": len(rest[0].split(",")) if rest else 0, "n_trailing": len(rest),
        }
    return None


def read_text(text: str, name: str = "") -> dict:
    filetype, fmt, rows, unparsed = "", [], [], 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#filetype"):
            filetype = s.split()[1] if len(s.split()) > 1 else ""
        elif s.startswith("#format"):
            fmt = s.split()[1:]
        elif s.startswith("#"):
            continue
        else:
            r = parse_row(s.split())
            if r is None:
                unparsed += 1
            else:
                rows.append(r)
    m = _T.search(name)
    return {"name": name, "filetype": filetype, "format": fmt, "rows": rows, "n_unparsed": unparsed,
            "in_scope": filetype == "genotype_data" and tuple(fmt[:17]) == FIRST17,
            "T": int(m.group(1)) if m else None}


def read(path) -> dict:
    p = Path(path)
    return read_text(p.read_text(encoding="utf-8", errors="replace"), p.name)


def _src_class(r: dict) -> str:
    """Genotype::Matches (Genotype.cc:406-456): DIVISION and DUPLICATION are one class; VERTICAL / HORIZONTAL are the
    other and additionally require equal source arguments (the parasite inject label)."""
    head = r["src"].split(":")[0]
    if head in ("div", "dup"):
        return "D"
    if head in ("horz", "vert"):
        return "P:" + r["src_args"]
    return ""          # 'unknown': Matches() returns false for it, so such a genotype never absorbs a second unit


def measure(f: dict) -> dict:
    """Per-file observables. Every count comes with its ELIGIBLE count: zero violations among zero eligible rows is
    'nothing could have fired', not a pass."""
    rows = f["rows"]
    ids = {}
    dup_ids = 0
    for r in rows:
        if r["id"] in ids:
            dup_ids += 1
        ids[r["id"]] = r
    named = set(p for r in rows for p in r["parents"])
    live = [r for r in rows if r["num_units"] > 0]
    dead = [r for r in rows if r["num_units"] == 0]

    parent_refs = sum(len(r["parents"]) for r in rows)
    dangling = sum(1 for r in rows for p in r["parents"] if p not in ids)

    dead_leaves = sum(1 for r in dead if r["id"] not in named)

    depth_elig = [r for r in rows if r["parents"] and r["parents"][0] in ids]
    depth_bad = sum(1 for r in depth_elig if r["depth"] != ids[r["parents"][0]]["depth"] + 1)

    seen, live_dup, live_keyed = set(), 0, 0
    for r in live:
        if not _src_class(r):
            continue
        live_keyed += 1
        key = (_src_class(r), r["hw_type"], r["inst_set"], r["sequence"])
        if key in seen:
            live_dup += 1
        seen.add(key)

    T = f.get("T")
    born_zero = sum(1 for r in rows if r["update_born"] == 0)
    born_late = sum(1 for r in rows if T is not None and r["update_born"] > T + 1)

    live_with_parent = [r for r in live if r["parents"]]
    live_parent_live = sum(1 for r in live_with_parent if all(p in ids and ids[p]["num_units"] > 0 for p in r["parents"]))

    return {
        "n_rows": len(rows), "n_live": len(live), "n_dead": len(dead), "n_unparsed": f["n_unparsed"], "dup_ids": dup_ids,
        "n_roots": sum(1 for r in rows if not r["parents"]), "n_shifted_rows": sum(1 for r in rows if r["shift"]),
        "multi_parent": any(len(r["parents"]) > 1 for r in rows),
        "parasite": any(r["src"].split(":")[0] in ("horz", "vert") for r in rows),
        "I1_dangling_parent_refs": dangling, "I1_eligible_parent_refs": parent_refs,
        "I2_dead_leaves": dead_leaves, "I2_eligible_dead_rows": len(dead),
        "I3_depth_violations": depth_bad, "I3_eligible_rows": len(depth_elig),
        "I4_live_duplicate_keys": live_dup, "I4_eligible_live_rows": live_keyed,
        "I5_dead_rows": len(dead), "I5_eligible_rows": len(rows),
        "I6_born_at_zero": born_zero, "I6_born_after_T_plus_1": born_late, "I6_eligible_rows": len(rows) if T is not None else 0,
        # READOUT, not a prediction: what Avida's own save_historic=0 followed by LoadPopulation's parent-drop keeps.
        "R_live_rows_with_parent": len(live_with_parent), "R_live_rows_whose_parents_are_all_live": live_parent_live,
    }


_IMMUTABLE = ("src", "src_args", "parents", "gen_born", "update_born", "depth", "hw_type", "inst_set", "sequence")


def measure_series(files: List[dict], sever_at: Optional[int] = None) -> dict:
    """Observables over successive saves of ONE run (files carry T; ids are the arbiter's m_next_id++, stable in a run).

    I7 persistence   a row present at the later save t2 whose update_born <= t1 must be present at the earlier save t1
                     (a pruned genotype never returns, an id is never reused), and a row present in both must agree
                     on every field the writer never changes. Pairs whose earlier save is the 'begin' save (T = -1)
                     are NOT eligible: the stamp -1 covers both 'before the run' and 'during update 0'
                     (GenotypeArbiter.cc:49,87), so a row stamped -1 may have been founded after that save. The
                     definedness fixture caught this before the packet hash.
    I8 severance     after an event that replaces every organism with a parentless injected one at update s-1 (stamped
                     s), no save taken at T >= s contains a row stamped before s, and every root in those saves is
                     stamped s at depth 0.
    """
    fs = sorted([f for f in files if f.get("T") is not None], key=lambda f: f["T"])
    by = [(f["T"], {r["id"]: r for r in f["rows"]}) for f in fs]
    missing = changed = elig = 0
    lost_curve = []
    fencepost = 0
    for (t1, a), (t2, b) in zip(by, by[1:]):
        for i, r in b.items():
            if t1 < 0:
                fencepost += int(r["update_born"] <= t1 and i not in a)
                continue
            if r["update_born"] <= t1:
                elig += 1
                if i not in a:
                    missing += 1
                elif any(a[i][k] != r[k] for k in _IMMUTABLE):
                    changed += 1
        lost_curve.append({"t1": t1, "t2": t2, "rows_t1": len(a), "rows_t2": len(b), "lost": sum(1 for i in a if i not in b)})
    out = {"n_saves": len(by), "I7_missing_at_earlier_save": missing, "I7_changed_immutable_fields": changed,
           "I7_eligible_rows": elig, "R_rows_stamped_minus_one_founded_after_the_begin_save": fencepost,
           "R_loss_curve": lost_curve}
    if sever_at is not None:
        pre = post_rows = old = bad_roots = roots = 0
        for t, rows in by:
            if t < sever_at:
                pre = max(pre, len(rows))
                continue
            for r in rows.values():
                post_rows += 1
                if r["update_born"] < sever_at:
                    old += 1
                if not r["parents"]:
                    roots += 1
                    if r["update_born"] != sever_at or r["depth"] != 0:
                        bad_roots += 1
        out.update({"I8_rows_stamped_before_severance": old, "I8_roots_not_stamped_at_severance": bad_roots,
                    "I8_eligible_rows": post_rows, "I8_roots": roots, "I8_max_rows_in_a_save_before_severance": pre})
    return out
