"""E-003 interventional tests (ANCESTRY_PREREG v4 s4 as replaced by v5 R1/R2/R5 and Amendments B1, R4, C1, C4, C7.2).
Single-interaction counterfactuals only (v4 s1.1): each birth's recorded pre-state is re-run with one change.

--mode arms (ALL births; frozen VM only, value + write log):
  groups W (writer bytes 0..L-1), P (occupant bytes L..2L-1, absent if the window was EMPTY) and INPUT (supplied input
  bytes); K = 8 draws each. Draw rng = random.Random(int(sha256("%d|%s|%d|arms")[:16], 16)) over (birth, group, draw).
  Per written locus with data label (E, X, j) and performer entities Pf:
  - dep_changes / dep_draws: over groups OUTSIDE {X} | Pf, draws where the write AND the birth occur; changed = final
    byte differs (R1 condition 3; identified needs 0 changes);
  - q8c_changes / q8c_draws: the same groups, draws where the write occurs (R2);
  - q_input: the INPUT group alone, write-occurring draws;
  - nonmove (for CONST/COMPUTED loci): each ENTITY in turn, write-occurring draws.
  Per birth, whether (C4.1): per group, PERFORMER INCLUDED, draws in which the birth is suppressed, and per-locus write
  suppression.
--mode flip (SAMPLE): the prefix-preserving flip test (C7.2, gating) plus the strict v4 s4.1 + B1 + R4 rule (reported)
  on every written ENTITY-MOVE locus, all 8 bits.
  - Prefix rule: a bit is APPLICABLE iff the counterfactual path (fetch (pc, opclass), store and load addresses) equals
    the baseline UP TO the baseline's last store to that locus, AND the counterfactual makes no later store to it.
    Applicable -> CONFIRMED if the child byte equals the flipped source value, else FAILED.
  - Strict rule: the whole path is unchanged.
--mode completeness (a seeded 20% of the SAMPLE; R5, C1):
  - randomise each single base-labelled byte (W, P, supplied INPUT), K = 4;
  - per locus, a byte NOT named in any of its sets (data bases, ctrl, addr, exec at store) that changes the locus value
    with the prefix path preserved and the birth preserved is a LEAK (gating: <= 5% per class);
  - per-byte precision over NAMED bytes is reported (C1: not gating).
    python s4_tests.py --mode arms --export <births.jsonl.gz> --out <arms.jsonl.gz> --workers 8
    python s4_tests.py --mode flip --export ... --sample <sample.json> --out <flip.jsonl.gz>
    python s4_tests.py --mode completeness --export ... --sample <sample.json> --out <compl.jsonl.gz>
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
HARNESS = "C:/Users/James/e003_harness_16fc6c2a"
L = 64; K_ARMS = 8; K_COMPL = 4
_G = {}


def _init():
    sys.path.insert(0, HARNESS)
    from prometheus.z80atlas import vm
    import bee_tracer as BT
    _G.update(vm=vm, BT=BT)


def rng_for(*parts) -> random.Random:
    return random.Random(int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:16], 16))


def ent_of(code: str):
    """encoded base label -> (kind, locus): 'W5' -> ('W',5), 'P3' -> ('P',3), 'I0' -> ('I',0)"""
    return code[0], int(code[1:])


def group_addrs(r, vm):
    ps = r["pre_state"]; G = {"W": list(range(L))}
    if not ps.get("window_empty"):
        G["P"] = list(range(L, 2 * L))
    if ps["inputs"]:
        G["INPUT"] = [vm.IN_BASE + k for k in range(len(ps["inputs"][:16]))]
    return G


def run_frozen(mem: bytearray, ps):
    vm = _G["vm"]; m = bytearray(mem)
    tr = vm.execute(m, L, 0, ps["budget"], list(m[vm.IN_BASE:vm.IN_BASE + len(ps["inputs"][:16])]), allow_copyall=ps["allow_copyall"])
    written = {a - L for a in tr.writes if L <= a < 2 * L}
    return m, written


def birth_of(after, written, occ_bytes, empty) -> bool:
    if len(written) < L:
        return False
    return empty or bytes(after[L:2 * L]) != bytes(occ_bytes)


def _arms(line: str) -> str:
    r = json.loads(line); vm = _G["vm"]; ps = r["pre_state"]
    pre = bytearray.fromhex(ps["mem"]); empty = bool(ps.get("window_empty"))
    base_after, base_written = run_frozen(pre, ps)
    G = group_addrs(r, vm)
    loci = r["loci"]
    out_loci = [{"dep_changes": 0, "dep_draws": 0, "q8c_changes": 0, "q8c_draws": 0, "qin_changes": 0, "qin_draws": 0,
                 "nonmove_changes": 0, "nonmove_draws": 0, "write_suppressed": 0, "write_draws": 0} for _ in range(L)]
    whether = {}
    for g, addrs in G.items():
        sup = 0
        for d in range(K_ARMS):
            rg = rng_for(r["birth_index"], g, d, "arms")
            m = bytearray(pre)
            for a_ in addrs:
                m[a_] = rg.randrange(256)
            after, written = run_frozen(m, ps)
            born = birth_of(after, written, m[L:2 * L], empty)
            sup += not born
            for i, x in enumerate(loci):
                if not x["written"]:
                    continue
                o = out_loci[i]
                wr = i in written
                o["write_draws"] += 1; o["write_suppressed"] += not wr
                d_ = x["data"]
                if isinstance(d_, str) and d_[0] in "WP":
                    X = d_[0]; perf = {p[0] for p in x["performer"]}
                    if g not in ({X} | perf):
                        if wr:
                            ch = after[L + i] != base_after[L + i]
                            o["q8c_draws"] += 1; o["q8c_changes"] += ch
                            if born:
                                o["dep_draws"] += 1; o["dep_changes"] += ch
                elif g in ("W", "P") and wr:
                    o["nonmove_draws"] += 1; o["nonmove_changes"] += after[L + i] != base_after[L + i]
                if g == "INPUT" and wr:
                    o["qin_draws"] += 1; o["qin_changes"] += after[L + i] != base_after[L + i]
        whether[g] = {"suppressed": sup, "draws": K_ARMS}
    return json.dumps({"birth_index": r["birth_index"], "whether": whether, "loci": out_loci}, sort_keys=True)


def _trace_ev(mem, ps, empty):
    BT = _G["BT"]; vm = _G["vm"]
    labels = BT.initial_labels(L, len(ps["inputs"][:16]), vm.IN_BASE)
    if empty:
        for a_ in range(L, 2 * L):
            labels[a_] = ("CONST", "empty")
    ev = []
    after, recs, info = BT.trace(vm, bytearray(mem), L, ps["budget"], list(ps["inputs"][:16]), allow_copyall=ps["allow_copyall"],
                                 labels=labels, check=False, ev=ev)
    return after, recs, ev


def _last_store_idx(ev, addr):
    k = None
    for n, e in enumerate(ev):
        if e[0] == "S" and e[1] == addr:
            k = n
    return k


def _prefix_ok(ev_b, ev_c, addr):
    k = _last_store_idx(ev_b, addr)
    if k is None:
        return False
    if ev_c[:k + 1] != ev_b[:k + 1]:
        return False
    return not any(e[0] == "S" and e[1] == addr for e in ev_c[k + 1:])


def _flip(line: str) -> str:
    r = json.loads(line); ps = r["pre_state"]; pre = bytearray.fromhex(ps["mem"]); empty = bool(ps.get("window_empty"))
    base_after, _, ev_b = _trace_ev(pre, ps, empty)
    res = {}
    for i, x in enumerate(r["loci"]):
        d_ = x["data"]
        if not (x["written"] and isinstance(d_, str) and d_[0] in "WP"):
            continue
        X, j = ent_of(d_); src = j if X == "W" else L + j
        pref = {"app": 0, "fail": 0}; strict = {"app": 0, "fail": 0}
        for b in range(8):
            m = bytearray(pre); m[src] ^= (1 << b)
            after, _, ev_c = _trace_ev(m, ps, empty)
            predicted = pre[src] ^ (1 << b)
            ok_val = after[L + i] == predicted
            if _prefix_ok(ev_b, ev_c, L + i):
                pref["app"] += 1; pref["fail"] += not ok_val
            if ev_c == ev_b:
                strict["app"] += 1; strict["fail"] += not ok_val
        verdict = lambda t: "FAILED" if t["fail"] else ("CONFIRMED" if t["app"] else "INAPPLICABLE")
        res[i] = {"prefix": verdict(pref), "strict": verdict(strict), "prefix_bits": pref, "strict_bits": strict}
    return json.dumps({"birth_index": r["birth_index"], "flip": res}, sort_keys=True)


def _named(x):
    s = set()
    d_ = x["data"]

    def flat(v):
        if isinstance(v, str):
            if v[0] in "WPI": s.add(v)
        elif isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, list):
                    for w in vv: flat(w)
                else:
                    flat(vv)
    flat(d_)
    for k in ("ctrl", "addr", "exec"):
        for v in x[k]:
            if v[0] in "WPI": s.add(v)
    return s


def _compl(line: str) -> str:
    r = json.loads(line); vm = _G["vm"]; ps = r["pre_state"]; pre = bytearray.fromhex(ps["mem"]); empty = bool(ps.get("window_empty"))
    base_after, _, ev_b = _trace_ev(pre, ps, empty)
    _, base_written = run_frozen(pre, ps)
    G = group_addrs(r, vm)
    byte_code = {}
    for g, addrs in G.items():
        for a_ in addrs:
            byte_code[a_] = ("W%d" % a_) if g == "W" else (("P%d" % (a_ - L)) if g == "P" else ("I%d" % (a_ - vm.IN_BASE)))
    loci = r["loci"]; named = {i: _named(x) for i, x in enumerate(loci) if x["written"]}
    leak = {i: {} for i in named}; prec = {i: {} for i in named}
    for a_, code in byte_code.items():
        for d in range(K_COMPL):
            rg = rng_for(r["birth_index"], a_, d, "compl")
            m = bytearray(pre); m[a_] = rg.randrange(256)
            if m[a_] == pre[a_]:
                m[a_] ^= 0x01
            after, _, ev_c = _trace_ev(m, ps, empty)
            f_after, written = run_frozen(m, ps)
            born = birth_of(f_after, written, m[L:2 * L], empty)
            for i in named:
                changed = after[L + i] != base_after[L + i]
                if code in named[i]:
                    ever = changed or (i not in written) or (not born)
                    prec[i][code] = prec[i].get(code, False) or ever
                else:
                    lk = changed and born and _prefix_ok(ev_b, ev_c, L + i)
                    leak[i][code] = leak[i].get(code, False) or lk
    out = {i: {"unnamed": len(leak[i]), "leaks": sum(leak[i].values()), "named": len(prec[i]), "named_effective": sum(prec[i].values())}
           for i in named}
    return json.dumps({"birth_index": r["birth_index"], "completeness": out}, sort_keys=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("arms", "flip", "completeness"), required=True)
    ap.add_argument("--export", required=True); ap.add_argument("--out", required=True); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--sample", default=None); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    lines = gzip.open(a.export, "rt", encoding="utf-8").read().splitlines()
    if a.mode in ("flip", "completeness"):
        S = json.loads(pathlib.Path(a.sample).read_text(encoding="utf-8"))
        keep = set(S["sample"] if a.mode == "flip" else S["completeness_subset"])
        lines = [l for l in lines if json.loads(l)["birth_index"] in keep]
    if a.limit:
        lines = lines[: a.limit]
    fn = {"arms": _arms, "flip": _flip, "completeness": _compl}[a.mode]
    with mp.Pool(a.workers, initializer=_init) as pool, gzip.open(a.out, "wt", encoding="utf-8", newline="\n") as fh:
        for res in pool.imap(fn, lines, chunksize=8):
            fh.write(res + "\n")
    print(json.dumps({"mode": a.mode, "births": len(lines), "out": a.out, "sha256": hashlib.sha256(pathlib.Path(a.out).read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
