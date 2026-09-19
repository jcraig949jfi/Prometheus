"""PORT CLOSURE over a DECLARED replication domain (operator directive 6, 2026-09-19, s3): a deterministic,
machine-readable census in which 100% of the declared members are accounted for -- EXECUTABLE or EXPLICITLY
EXCLUDED with a named reason -- before the freeze. No silent class: any member the port refuses for a reason
not in the fixed vocabulary makes the census FAIL, so a new failure mode cannot slip into execution.

Domain file: JSONL, one member per line, exactly as the ruler will execute it:
    {"member_id": "...", "params": {...}, "ic": "IC-CAT:<code>" | "IC-ORB" | "IC-BLOB", "seed": <int|null>}
(For IC-CAT the pattern is the FIRST catalogue entry with that code, the ruler's own rule; for a stable
positional identity the member may instead carry "cat_index": <int> into the 2D catalogue list.)

Exclusion vocabulary (closed):
    PATTERN_LARGER_THAN_WORLD      the initial pattern does not fit the world (size given)
    UNSUPPORTED_CORE               kn/gn outside the port's 1-4 / 1-3
    NOT_2D                         a 3D/4D catalogue entry
    DEGENERATE_KERNEL              kernel sums to 0 or is non-finite for these params
    NON_FINITE_STATE               one step produced NaN/inf
Any other exception -> UNACCOUNTED (census fails).
Run: python techne/scripts/lenia_domain_closure.py --domain members.jsonl --out CLOSURE_<date>.json [--world 128]
     python techne/scripts/lenia_domain_closure.py --from-rows rows.jsonl --out ... (re-census a past run's domain)
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2])); sys.path.insert(0, str(HERE.parent))
from techne.fossils import vault
import techne107_asal_observer as port

EXCLUSIONS = ("PATTERN_LARGER_THAN_WORLD", "UNSUPPORTED_CORE", "NOT_2D", "DEGENERATE_KERNEL", "NON_FINITE_STATE")


def catalogue():
    animals = vault.body_dir("lenia-chan-2019") / "upstream" / "tree" / "Python" / "animals.json"
    cat = json.load(open(animals, encoding="utf-8"))
    lst = [e for e in cat if isinstance(e, dict) and "params" in e and "cells" in e and "x" not in str(e.get("code", ""))]
    first = {}
    for e in lst:
        first.setdefault("IC-CAT:%s" % e.get("code"), e)
    return lst, first, hashlib.sha256(animals.read_bytes()).hexdigest()


def blob(world: int, rng: np.random.Generator) -> np.ndarray:
    """A neutral blob initialiser used ONLY to instantiate a member whose ic is IC-BLOB: the ruler's own
    initialiser is authoritative for execution; here the question is whether the PARAMS instantiate."""
    yy, xx = np.mgrid[0:world, 0:world]; c = world // 2
    return np.exp(-(((xx - c) ** 2 + (yy - c) ** 2) / (2 * (world / 8) ** 2))) * rng.random((world, world))


def instantiate(m: dict, lst, first, world: int) -> tuple[str, str | None]:
    p = dict(m["params"]); ic = m.get("ic", "")
    kn, gn = int(p.get("kn", 1)), int(p.get("gn", 1))
    if kn - 1 not in port.KERNEL_CORE or gn - 1 not in port.GROWTH:
        return "EXCLUDED", "UNSUPPORTED_CORE kn=%s gn=%s" % (kn, gn)
    try:
        sim = port.Lenia2D(world, p)
    except ValueError as e:
        return "EXCLUDED", "DEGENERATE_KERNEL %s" % str(e)[:60]
    if "cat_index" in m:
        e = lst[int(m["cat_index"])]
        cells = e["cells"]
    elif ic.startswith("IC-CAT:"):
        e = first.get(ic)
        if e is None:
            return "UNACCOUNTED", "catalogue code %s not found" % ic
        cells = e["cells"]
    elif ic == "IC-ORB":
        cells = first["IC-CAT:O2u"]["cells"]
    elif ic == "IC-BLOB":
        cells = None
    else:
        return "UNACCOUNTED", "unknown ic %r" % ic
    if cells is not None:
        if any(ch in str(cells) for ch in "%#@"):
            return "EXCLUDED", "NOT_2D"
        pat = port.rle2arr_2d(cells)
        if pat.shape[0] > world or pat.shape[1] > world:
            return "EXCLUDED", "PATTERN_LARGER_THAN_WORLD %dx%d > %d" % (pat.shape[0], pat.shape[1], world)
        A = sim.place(pat)
    else:
        A = blob(world, np.random.default_rng(int(m.get("seed") or 0)))
    A = sim.step(A)
    if not np.isfinite(A).all():
        return "EXCLUDED", "NON_FINITE_STATE"
    return "EXECUTABLE", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default=None); ap.add_argument("--from-rows", default=None); ap.add_argument("--out", required=True); ap.add_argument("--world", type=int, default=128)
    a = ap.parse_args()
    if a.from_rows:
        members = []
        for l in open(a.from_rows, encoding="utf-8"):
            r = json.loads(l)
            if "params" not in r: continue
            members.append({"member_id": "%s_%s" % (r["stage"], r["idx"]), "params": r["params"], "ic": r.get("ic"), "seed": r.get("seed")})
        src = a.from_rows
    else:
        members = [json.loads(l) for l in open(a.domain, encoding="utf-8") if l.strip()]; src = a.domain
    lst, first, cat_sha = catalogue()
    t0 = time.time(); rows = []; counts = collections.Counter()
    for m in members:
        try:
            status, reason = instantiate(m, lst, first, a.world)
        except Exception as ex:                         # noqa: BLE001 -- anything not in the vocabulary is UNACCOUNTED
            status, reason = "UNACCOUNTED", "%s: %s" % (type(ex).__name__, str(ex)[:80])
        rows.append({"member_id": m["member_id"], "status": status, "reason": reason})
        counts[status if status != "EXCLUDED" else "EXCLUDED:" + reason.split()[0]] += 1
    n = len(rows); acc = sum(1 for r in rows if r["status"] == "EXECUTABLE"); exc = sum(1 for r in rows if r["status"] == "EXCLUDED"); un = n - acc - exc
    out = {"schema": "techne.lenia_port.domain_closure/1", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "domain_source": src,
           "domain_sha256_lf": hashlib.sha256(pathlib.Path(src).read_bytes().replace(b"\r\n", b"\n")).hexdigest(), "world": a.world,
           "catalogue_sha256": cat_sha, "port_sha256_lf": hashlib.sha256(open(HERE.parent / "techne107_asal_observer.py", "rb").read().replace(b"\r\n", b"\n")).hexdigest(),
           "exclusion_vocabulary": EXCLUSIONS, "n_members": n, "executable": acc, "excluded": exc, "unaccounted": un,
           "closure": (un == 0), "counts": dict(counts), "seconds": round(time.time() - t0, 1), "rows": rows}
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("members", n, "| executable", acc, "| excluded", exc, "| UNACCOUNTED", un, "| closure", out["closure"], "|", dict(counts))


if __name__ == "__main__":
    main()
