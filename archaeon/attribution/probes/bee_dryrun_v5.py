"""Prereg v5 DRY RUN on the drawn BEE run (Archaeon's process commitment; REVIEW_6_ADJUDICATION.md).

This is NOT the production result: that is the owner's native replay (commission #811 / #817). The purpose is to show, before any
owner spends compute, whether v5 is satisfiable AND informative on the real drawn run. It uses:
- Bellerophon's traced_replay on the frozen harness (git 16fc6c2a), extracted to a scratch dir with the sha256 prefixes checked,
  capturing each birth's pre-execution state (the pattern of Review 6's r6_replay.py);
- Archaeon's tracer archaeon/attribution/bee_ref_tracer.py (value-checked against the frozen VM on every call).

Steps:
  1. replay; compare the 20-column rows with the preserved births file (bit-for-bit);
  2. every birth: labels + v5 R1 interventional identification (K = 8 per source group outside {donor, performer}); Q1, Q2,
     Q3, Q7, Q-homology, Q8c (R2), Q8c-whether; the transmission class (R5);
  3. a stratified sample of <= 200 births: the R4 flip test; the per-byte precision/completeness arms on 20% of them; Q4
     (320 isolated trials) for the children;
  4. the verdict v5 would return, with every input number.
    python -m archaeon.attribution.probes.bee_dryrun_v5 --rid r022153 --config CFG.json --births BIRTHS.jsonl.gz --out OUT.json
"""
import gzip
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict

from archaeon.attribution import bee_ref_tracer as T

L = 64; BUDGET = 256; K = 8
PINS = (("world", "5b985241"), ("vm", "2536b1ac"), ("grammar", "3767d73d"), ("tasks", "e2c37f76"))


def frozen_harness(scratch):
    os.makedirs(os.path.join(scratch, "prometheus", "z80atlas"), exist_ok=True)
    open(os.path.join(scratch, "prometheus", "__init__.py"), "a").close()
    open(os.path.join(scratch, "prometheus", "z80atlas", "__init__.py"), "a").close()
    for f, h in PINS:
        src = subprocess.run(["git", "show", "16fc6c2a:prometheus/z80atlas/%s.py" % f], capture_output=True, check=True).stdout
        assert hashlib.sha256(src).hexdigest().startswith(h), f
        open(os.path.join(scratch, "prometheus", "z80atlas", "%s.py" % f), "wb").write(src)
    return scratch


def replay(cfg_path, births_path, scratch):
    sys.path.insert(0, os.path.abspath("roles/Bellerophon/forensics_2026-09-23/tools"))
    import traced_replay as TR
    TR.HARNESS = scratch
    vm, W = TR._install()
    assert os.path.abspath(os.path.dirname(vm.__file__)) == os.path.abspath(os.path.join(scratch, "prometheus", "z80atlas")), vm.__file__
    from prometheus.z80atlas import grammar as G
    TW = TR._traced_world_class(W); PRE = []

    class CW(TW):
        def _execute(self, o, partner_tape, inputs):
            self._pre = (bytes(o.tape), None if partner_tape is None else bytes(partner_tape), list(inputs), self.tick, o.id)
            return super()._execute(o, partner_tape, inputs)

        def _register_offspring(self, j, child, parent, mechanism, fidelity, tr, replaced):
            wt, pt, inp, tick, oid = self._pre
            PRE.append({"tick": tick, "writer": oid, "w": wt, "o": pt, "inputs": inp, "child": bytes(child)})
            return super()._register_offspring(j, child, parent, mechanism, fidelity, tr, replaced)

    cj = json.load(open(cfg_path)); c = cj["config"]
    cfg = G.to_config({a: c[a] for a in G.AXES}, c["ticks"], c["cells"], c["budget"], tuple(c["init_tapes"] or ()))
    w = CW(cfg, cj["seed"]); w.run()
    got = [json.loads(json.dumps(b)) for b in w.births]
    want = [json.loads(l) for l in gzip.open(births_path, "rt")]
    for p, b in zip(PRE, got): p["row"] = b
    return PRE, got == want, len(got), len(want)


def memimg(p):
    v = T.vm16(); m = bytearray(256); m[:L] = p["w"]
    if p["o"] is not None: m[L:2 * L] = p["o"]
    for k, x in enumerate(p["inputs"][:16]): m[v.IN_BASE + k] = x
    return m


def run_child(m, inputs):
    mm = bytearray(m); T.vm16().execute(mm, L, 0, BUDGET, list(inputs), allow_copyall=True); return mm


def analyse_birth(p, rng):
    """labels, R1 identification, Q8c (R2) and Q8c-whether for one birth."""
    v = T.vm16(); m = memimg(p); occupied = p["o"] is not None; inp = p["inputs"]
    _, recs, info = T.trace(m, L, BUDGET, inp, occupied=occupied)
    assert bytes(run_child(m, inp)[L:2 * L]) == p["child"], "pre-state does not reproduce the child"
    base_mem = run_child(m, inp)
    groups = {"W": list(range(L))}
    if occupied: groups["P"] = list(range(L, 2 * L))
    if inp: groups["INPUT"] = [v.IN_BASE + k for k in range(min(16, len(inp)))]
    change = {g: Counter() for g in groups}; supp = Counter(); nd = Counter()
    for g, addrs in groups.items():
        for _ in range(K):
            mm = bytearray(m)
            for a in addrs: mm[a] = rng.randrange(256)
            ii = list(mm[v.IN_BASE:v.IN_BASE + len(inp)]) if g == "INPUT" else list(inp)
            v.execute(mm, L, 0, BUDGET, ii, allow_copyall=True)
            nd[g] += 1
            for i in range(L):
                wr = recs[i]["written"]
                if mm[L + i] != base_mem[L + i]: change[g][i] += 1
    out = {"loci": {}}
    for i, r in recs.items():
        if not r["written"]: continue
        d = r["data"]; perf = {b[1] for b in r["performer"]}
        kind = d[0]; ent = d[1] if kind == "E" else None
        outside = [g for g in groups if not (g == ent or g in perf)]
        dep = max((change[g][i] / K for g in outside), default=0.0)
        ident = kind == "E" and dep == 0.0
        out["loci"][i] = {"kind": kind, "ent": ent, "src": d[2] if kind == "E" else None, "perf": sorted(perf), "ident": ident,
                          "q8c": dep if kind == "E" else None, "q8c_nonmove": max((change[g][i] / K for g in groups), default=0.0) if kind != "E" else None}
    n_written = len(out["loci"])
    ent_w = sum(1 for x in out["loci"].values() if x["kind"] == "E")
    out["n_written"] = n_written
    out["no_material"] = n_written == 0 or ent_w / n_written <= 0.10
    ids = [x for x in out["loci"].values() if x["ident"]]
    out["identifiable"] = n_written > 0 and len(ids) / n_written >= 0.90
    wmove = sum(1 for x in ids if x["ent"] == "W")
    out["transmission"] = n_written > 0 and wmove / n_written > 0.5
    donors = Counter(x["ent"] for x in ids)
    out["majority_donor"] = (donors.most_common(1)[0][0] if donors and (len(donors) == 1 or donors.most_common(2)[0][1] != donors.most_common(2)[1][1]) else ("NONE" if not donors else "TIED"))
    perfs = Counter(pp for x in out["loci"].values() for pp in x["perf"])
    out["performer"] = perfs.most_common(1)[0][0] if perfs else "none"
    out["class"] = "self" if out["performer"] == "W" else ("other" if out["performer"] != "none" else "none")
    out["q1"] = out["majority_donor"] not in ("NONE", "TIED") and out["majority_donor"] != out["performer"]
    new = sum(1 for x in out["loci"].values() if x["kind"] != "E")
    second = sorted(donors.values(), reverse=True)[1] / n_written if len(donors) > 1 else 0.0
    out["q3"] = second >= 0.10 or new / n_written >= 0.10 or out["q1"]
    out["native_label"] = p["row"][6]
    nat_major = "W" if p["row"][6] == "writer" else "P"
    out["q2_disagree"] = out["majority_donor"] not in ("NONE", "TIED") and out["majority_donor"] != nat_major
    out["homology_shift"] = sum(1 for k, x in out["loci"].items() if x["ident"] and x["src"] != k)
    out["n_ident"] = len(ids)
    out["source_diversity"] = len({(x["ent"], x["src"]) for x in ids}) / len(ids) if ids else None
    return out, recs, info, m


def flip_r4(m, inp, recs, info, occupied):
    """R4: path-preserving flip (with B1 load sequence) where opcode-equivalent (undefined <-> undefined) flips keep the path."""
    V = T.vm16()
    def norm(path): return [(pc, op if op in V.DEFINED else "NOP") for pc, op in path]
    base_path = norm(info["path"]); st = {}
    for i, r in recs.items():
        d = r["data"]
        if not r["written"] or d[0] != "E": continue
        a = T.addr_of(d, L); app = fail = 0
        for bit in range(8):
            mm = bytearray(m); mm[a] ^= (1 << bit)
            m2, _, inf2 = T.trace(mm, L, BUDGET, inp, occupied=occupied)
            if norm(inf2["path"]) != base_path or inf2["stores"] != info["stores"] or inf2["loads"] != info["loads"]: continue
            app += 1
            if m2[L + i] != mm[a]: fail += 1
        st[i] = "FAILED" if fail else ("CONFIRMED" if app else "INAPPLICABLE")
    return st


def byte_arms(m, inp, recs, rng, K4=4):
    """R5 per-byte arms: precision = named base-label bytes that ever change value/write/birth; completeness = unnamed bytes that
    change the locus value with the child written."""
    V = T.vm16(); base_mem = run_child(m, inp); eff = {}
    for a in list(range(2 * L)) + [V.IN_BASE + k for k in range(min(16, len(inp)))]:
        ch = set()
        for _ in range(K4):
            mm = bytearray(m); mm[a] = rng.randrange(256)
            ii = list(mm[V.IN_BASE:V.IN_BASE + len(inp)]); mm2 = bytearray(mm); V.execute(mm2, L, 0, BUDGET, ii, allow_copyall=True)
            ch |= {i for i in range(L) if mm2[L + i] != base_mem[L + i]}
        eff[a] = ch
    def lab_addr(b):
        if b[0] == "E": return b[2] if b[1] == "W" else L + b[2]
        if b[0] == "INPUT": return V.IN_BASE + b[1]
        return None
    prec_n = prec_hit = comp_n = comp_hit = 0
    for i, r in recs.items():
        if not r["written"]: continue
        named = {lab_addr(b) for s in (T.base(r["data"]), r["ctrl"], r["addr"], r["exec"]) for b in s} - {None}
        for a, ch in eff.items():
            if a in named:
                prec_n += 1; prec_hit += i in ch
            else:
                comp_n += 1; comp_hit += i in ch
    return {"precision": prec_hit / prec_n if prec_n else None, "completeness_leak": comp_hit / comp_n if comp_n else None,
            "prec_n": prec_n, "comp_n": comp_n}


def capable(child, rng, n_occ=8, n_in=40):
    V = T.vm16(); ok = 0
    for _ in range(n_occ):
        occ = bytes(rng.randrange(256) for _ in range(L))
        for _ in range(n_in):
            m = bytearray(256); m[:L] = child; m[L:2 * L] = occ; x = rng.randrange(256); m[V.IN_BASE] = x
            V.execute(m, L, 0, BUDGET, [x], allow_copyall=True)
            ok += bytes(m[L:2 * L]) == bytes(child)
    return ok / (n_occ * n_in)


def boot(vals, clusters=None, B=1000, seed=0):
    rng = random.Random(seed)
    if not vals: return None
    n = len(vals); ms = []
    for _ in range(B):
        s = [vals[rng.randrange(n)] for _ in range(n)]; ms.append(sum(s) / n)
    ms.sort(); return [round(sum(vals) / n, 4), round(ms[int(0.025 * B)], 4), round(ms[int(0.975 * B) - 1], 4)]


def main(a):
    t0 = time.time(); g = lambda k: a[a.index(k) + 1]
    rid, cfgp, birthp, outp = g("--rid"), g("--config"), g("--births"), g("--out")
    scratch = frozen_harness(os.path.abspath(g("--scratch") if "--scratch" in a else "_dryrun_scratch"))
    PRE, equal, ng, nw = replay(cfgp, birthp, scratch)
    print("replay", ng, nw, "ALL EQUAL" if equal else "DIFFER", round(time.time() - t0, 1)); sys.stdout.flush()
    rng = random.Random(1)
    births = []; bcache = []
    for p in PRE:
        o, recs, info, m = analyse_birth(p, rng)
        births.append(o); bcache.append((p, recs, info, m))
    print("analysed", len(births), round(time.time() - t0, 1)); sys.stdout.flush()
    nm = [b for b in births if not b["no_material"]]
    tx = [b for b in births if b["transmission"]]
    res = {"rid": rid, "replay_equal": equal, "births": len(births), "no_material": len(births) - len(nm), "transmission": len(tx),
           "identifiable_share_non_no_material": round(sum(b["identifiable"] for b in nm) / len(nm), 4) if nm else None,
           "classes": dict(Counter(b["class"] for b in births)),
           "q1_rate_tx": boot([float(b["q1"]) for b in tx]), "q3_rate_tx": boot([float(b["q3"]) for b in tx]),
           "q2_disagree_tx": boot([float(b["q2_disagree"]) for b in tx]),
           "q2_disagree_target_labelled_tx": boot([float(b["q2_disagree"]) for b in tx if b["native_label"] == "target"]),
           "homology_shift_share_tx": boot([b["homology_shift"] / b["n_ident"] for b in tx if b["n_ident"]]),
           "source_diversity_tx": boot([b["source_diversity"] for b in tx if b["source_diversity"] is not None]),
           "q8c_tx": boot([sum(x["q8c"] for x in b["loci"].values() if x["q8c"] is not None) / max(1, sum(1 for x in b["loci"].values() if x["q8c"] is not None)) for b in tx]),
           "q8c_all_entity": boot([sum(x["q8c"] for x in b["loci"].values() if x["q8c"] is not None) / max(1, sum(1 for x in b["loci"].values() if x["q8c"] is not None)) for b in nm if any(x["q8c"] is not None for x in b["loci"].values())]),
           "native_label_counts": dict(Counter(b["native_label"] for b in births))}
    # stratified sample for flip / arms / Q4
    strata = defaultdict(list)
    for k, b in enumerate(births): strata[(b["class"], b["transmission"])].append(k)
    sample = []
    for key, ks in sorted(strata.items()):
        take = max(1, round(200 * len(ks) / len(births))); sample += rng.sample(ks, min(take, len(ks)))
    sample = sample[:220]
    flips = Counter(); fl_cls = defaultdict(Counter); arms_out = []; caps = []
    for n, k in enumerate(sample):
        p, recs, info, m = bcache[k]; b = births[k]
        st = flip_r4(m, p["inputs"], recs, info, p["o"] is not None)
        # only loci identified under R1 are gated by the flip
        for i, s in st.items():
            if b["loci"].get(i, {}).get("ident"): flips[s] += 1; fl_cls[b["class"]][s] += 1
        if n % 5 == 0: arms_out.append(byte_arms(m, p["inputs"], recs, rng))
        if b["transmission"]: caps.append(capable(p["child"], rng))
    res["sample"] = len(sample)
    res["flip"] = dict(flips); res["flip_by_class"] = {c: dict(v) for c, v in fl_cls.items()}
    res["byte_arms"] = {"precision_mean": round(sum(x["precision"] for x in arms_out if x["precision"] is not None) / max(1, len(arms_out)), 4),
                        "completeness_leak_mean": round(sum(x["completeness_leak"] for x in arms_out if x["completeness_leak"] is not None) / max(1, len(arms_out)), 4),
                        "n": len(arms_out)}
    res["q4_capable_share_tx_sample"] = boot([float(c >= 0.5) for c in caps]); res["q4_trials_mean"] = round(sum(caps) / len(caps), 4) if caps else None
    # the verdict v5 would return
    q8 = res["q8c_tx"]
    if res["transmission"] < 30 or (res["identifiable_share_non_no_material"] or 0) < 0.80: verdict = "INCONCLUSIVE"
    elif q8 and q8[1] > 0.50: verdict = "ALTERED(DOMINANT)"
    elif q8 and q8[1] >= 0.05: verdict = "ALTERED(WEIGHTED)"
    elif q8 and q8[2] < 0.05: verdict = "VALIDATED (pending round-trip, three-tracer agreement, fixtures)"
    else: verdict = "INCONCLUSIVE (Q8c interval straddles 5%)"
    fl = res["flip"]; cov = (fl.get("CONFIRMED", 0) + fl.get("FAILED", 0)) / max(1, sum(fl.values()))
    res["flip_coverage"] = round(cov, 4); res["flip_failed_share"] = round(fl.get("FAILED", 0) / max(1, fl.get("CONFIRMED", 0) + fl.get("FAILED", 0)), 4)
    if res["flip_failed_share"] > 0.01: verdict = "INSTRUMENT/SPEC check: flip FAILED > 1% (" + verdict + ")"
    if cov < 0.5: verdict = "INCONCLUSIVE (flip coverage floor) / " + verdict
    res["verdict_v5_would_return"] = verdict; res["wall_s"] = round(time.time() - t0, 1)
    json.dump(res, open(outp, "w"), indent=1)
    json.dump([{k: v for k, v in b.items() if k != "loci"} for b in births], gzip.open(outp + ".births.json.gz", "wt"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
