"""E-003 BEE s4.3 agreement: FRESH set generator, Archaeon-side exporter and three-way raw comparator. Committed BEFORE the seed
exists and before any output exists (declaration: ops/.../gate_close/BEE_AGREEMENT_DECLARATION.md).

Pre-states (gen): 500 isolated BEE interactions on the frozen VM (VM_COPY, L = 64, budget 256, COPYALL allowed, entry 0).
- 300 "fuzz": writer and occupant tapes uniform, one uniform input byte at IN_BASE.
- 200 "rep": a replicator (half vm16.replicator, half replicator_copyall) padded with uniform bytes, 0-3 random point
  mutations, uniform occupant and input.
- occupied = False with p = 1/5 (the EMPTY window; ruled reading 2). Seeded by the commit SHA of the seed record.
- Record: {"k", "kind", "mem": 256-byte hex, "inputs": [x], "occupied": bool}.

Exchange serialization (per locus i of the 64-byte target window; every tracer exports the same):
- {"i", "written", "label", "addr", "ctrl", "exec", "performer"}.
- ctrl and exec are AT STORE. addr, ctrl, exec and performer are omitted for unwritten loci.
- label:
  * ["E", "W"|"P", j] (W = writer, P = occupant/partner);
  * ["INPUT", k];
  * ["CONST", kind]; kind is null where a tracer has none (the reference);
  * ["C", sorted bases] (COMPUTED);
  * ["F", sorted bases] (COMPUTED_FROM, flattened to its base set);
  * ["M", ...] (MUTATION, if any).
- A base string is "E|W|j" or "INPUT|k". CONST is never a base or a dependence-set member (C2 CHOICE 3).
- performer: the ENTITY label of the store opcode byte (["E", side, j]); null if it is not ENTITY. The class key needs only
  entity-ness, and Archaeon's tracer carries no non-ENTITY performer label. Fixed before the seed, after a smoke test on a
  throwaway seed.

Comparison (cmp), RAW per class, class = the performer relative to the executing organism (W = self, P = other,
non-ENTITY = written_perf_none; unwritten):
- Gate: >= 0.995 on label, addr, ctrl and exec, for BOTH owner-vs-Archaeon (fully raw) and owner-vs-reference (raw except the
  CONST kind, which the reference does not name).
- Also reported: written, performer, and reference-vs-Archaeon.
    python -m archaeon.attribution.probes.bee_fresh gen SEED OUT.jsonl
    python -m archaeon.attribution.probes.bee_fresh ref PRE.jsonl OUT_ARCHAEON.jsonl OUT_REFERENCE.jsonl
    python -m archaeon.attribution.probes.bee_fresh cmp OWNER.jsonl ARCHAEON.jsonl REFERENCE.jsonl OUTDIR [SEALED.json]
"""
import gzip
import hashlib
import json
import os
import random
import sys
from collections import Counter

L = 64


def gen(seed, outp, n_fuzz=300, n_rep=200):
    from archaeon.attribution import bee_ref_tracer as T
    V = T.vm16(); rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    with open(outp, "w", newline="\n") as fh:
        for k in range(n_fuzz + n_rep):
            m = bytearray(256)
            if k < n_fuzz:
                m[:2 * L] = bytes(rng.randrange(256) for _ in range(2 * L)); kind = "fuzz"
            else:
                base = V.replicator_copyall(L) if k % 2 else V.replicator(L)
                t = bytearray(base + bytes(rng.randrange(256) for _ in range(L - len(base))))
                for _ in range(rng.randrange(4)): t[rng.randrange(L)] = rng.randrange(256)
                m[:L] = t; m[L:2 * L] = bytes(rng.randrange(256) for _ in range(L)); kind = "rep"
            x = rng.randrange(256); m[V.IN_BASE] = x
            occ = rng.random() >= 0.2
            fh.write(json.dumps({"k": k, "kind": kind, "mem": bytes(m).hex(), "inputs": [x], "occupied": occ}, sort_keys=True) + "\n")
    print(hashlib.sha256(open(outp, "rb").read()).hexdigest(), outp)


def _b_mine(b):
    if b[0] == "E": return "E|%s|%d" % (b[1], b[2])
    if b[0] == "INPUT": return "INPUT|%d" % b[1]
    return None                                           # CONST: never a base


def _lab_mine(l):
    k = l[0]
    if k == "E": return ["E", l[1], l[2]]
    if k == "INPUT": return ["INPUT", l[1]]
    if k == "CONST": return ["CONST", l[1] if len(l) > 1 else None]
    if k in ("COMPUTED", "COMPUTED_FROM"):
        return ["C" if k == "COMPUTED" else "F", sorted(x for x in (_b_mine(b) for b in l[1]) if x)]
    return ["M", repr(l[1:])]


def _b_ref(b):
    if b[0] == "ENTITY": return "E|%s|%d" % ({"w": "W", "o": "P"}[b[1]], b[2])
    if b[0] == "INPUT": return "INPUT|%d" % b[1]
    return None


def _lab_ref(l):
    k = l[0]
    if k == "ENTITY": return ["E", {"w": "W", "o": "P"}[l[1]], l[2]]
    if k == "INPUT": return ["INPUT", l[1]]
    if k == "CONSTANT": return ["CONST", None]
    if k == "COMPUTED": return ["C", sorted(x for x in (_b_ref(b) for b in l[1]) if x)]
    if k == "COMPUTED_FROM":
        inner = l[1]
        bs = inner[1] if inner[0] == "COMPUTED" else [inner]
        return ["F", sorted(x for x in (_b_ref(b) for b in bs) if x)]
    return ["M", repr(l[1:])]


def ref(pre, out_a, out_r):
    from archaeon.attribution import bee_ref_tracer as T
    from archaeon.attribution.probes.tracer_agreement import load_ref
    R = load_ref()
    fa = open(out_a, "w", newline="\n"); fr = open(out_r, "w", newline="\n")
    for line in open(pre):
        rec = json.loads(line); m = bytearray(bytes.fromhex(rec["mem"]))
        _, mine, _ = T.trace(bytearray(m), L, 256, rec["inputs"], occupied=rec["occupied"])
        res = R.trace_interaction(bytes(m), rec["inputs"], R.Cfg(), occupant=rec["occupied"])
        la, lr = [], []
        for i in range(L):
            r = mine[i]; x = {"i": i, "written": r["written"], "label": _lab_mine(r["data"])}
            if r["written"]:
                x.update({"addr": sorted(filter(None, map(_b_mine, r["addr"]))), "ctrl": sorted(filter(None, map(_b_mine, r["ctrl"]))),
                          "exec": sorted(filter(None, map(_b_mine, r["exec"]))),
                          "performer": _lab_mine(sorted(r["performer"])[0]) if len(r["performer"]) == 1 and sorted(r["performer"])[0][0] == "E" else None})
            la.append(x)
            loc = res.loci[i]; y = {"i": i, "written": loc.written, "label": _lab_ref(loc.label)}
            if loc.written:
                y.update({"addr": sorted(filter(None, map(_b_ref, loc.addr_deps))),
                          "ctrl": sorted(filter(None, map(_b_ref, loc.ctrl_deps_at_store or ()))),
                          "exec": sorted(filter(None, map(_b_ref, loc.exec_deps_at_store or ()))),
                          "performer": _lab_ref(loc.performer) if loc.performer and loc.performer[0] == "ENTITY" else None})
            lr.append(y)
        fa.write(json.dumps({"k": rec["k"], "loci": la}, sort_keys=True) + "\n")
        fr.write(json.dumps({"k": rec["k"], "loci": lr}, sort_keys=True) + "\n")
    fa.close(); fr.close()
    for p in (out_a, out_r): print(hashlib.sha256(open(p, "rb").read()).hexdigest(), p)


def _load(p, sealed=None):
    raw = (gzip.open if p.endswith(".gz") else open)(p, "rb").read()
    h = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
    if sealed: assert h == sealed, "%s hash %s != sealed %s" % (p, h, sealed)
    return {r["k"]: r for r in (json.loads(l) for l in raw.decode().splitlines() if l.strip())}


def _cls(y):
    if not y["written"]: return "unwritten"
    p = y.get("performer")
    if not p or p[0] != "E": return "written_perf_none"
    return "written_self" if p[1] == "W" else "written_other"


def cmp(own, arc, refp, outdir, sealed=None):
    S = json.load(open(sealed)) if sealed else {}
    O, A, R = _load(own, S.get("owner")), _load(arc, S.get("archaeon")), _load(refp, S.get("reference"))
    assert sorted(O) == sorted(A) == sorted(R), "record sets differ"
    tot = Counter(); bad = Counter(); disc = []
    for k in sorted(O):
        for x, a, r in zip(O[k]["loci"], A[k]["loci"], R[k]["loci"]):
            c = _cls(a)
            for pair, y, kindless in (("owner~archaeon", a, False), ("owner~reference", r, True), ("reference~archaeon", a, True)):
                u = r if pair == "reference~archaeon" else x
                lu, ly = u["label"], y["label"]
                if kindless and lu[0] == "CONST" and ly[0] == "CONST": lu, ly = ["CONST"], ["CONST"]
                chk = {"label": lu == ly, "written": u["written"] == y["written"]}
                if u["written"] and y["written"]:
                    for f in ("addr", "ctrl", "exec"): chk[f] = u.get(f) == y.get(f)
                    pu, py = u.get("performer"), y.get("performer")
                    if kindless and pu and py and pu[0] == py[0] == "CONST": pu, py = ["CONST"], ["CONST"]
                    chk["performer"] = pu == py
                elif u["written"] or y["written"]:
                    for f in ("addr", "ctrl", "exec"): chk[f] = False
                for f, ok in chk.items():
                    tot[(pair, c, f)] += 1; bad[(pair, c, f)] += not ok
                if not all(chk.values()):
                    disc.append({"k": k, "i": x["i"], "pair": pair, "class": c, "fields": sorted(f for f, ok in chk.items() if not ok),
                                 "a": {f: u.get(f) for f in ("label", "performer")}, "b": {f: y.get(f) for f in ("label", "performer")}})
    lines = ["E-003 BEE s4.3 FRESH-set agreement, RAW per class (CONST kind not compared only where the reference is a party)"]
    fails = []
    for pair in ("owner~archaeon", "owner~reference", "reference~archaeon"):
        lines.append("[%s]" % pair)
        for c in sorted({c for p, c, _ in tot if p == pair}):
            row = []
            for f in sorted({f for p, cc, f in tot if p == pair and cc == c}):
                t = tot[(pair, c, f)]; ac = 1 - bad[(pair, c, f)] / t
                gate = pair != "reference~archaeon" and f in ("label", "addr", "ctrl", "exec")
                if gate and ac < 0.995: fails.append("%s/%s/%s %.4f" % (pair, c, f, ac))
                row.append("%s %d/%d%s" % (f, t - bad[(pair, c, f)], t, " FAIL" if gate and ac < 0.995 else ""))
            lines.append("  %-18s %s" % (c, "; ".join(row)))
    lines += ["discrepancy records: %d" % len(disc), "BEE s4.3 FRESH GATE: %s" % ("PASS" if not fails else "FAIL on " + ", ".join(fails))]
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "BEE_FRESH_AGREEMENT.txt"), "w", newline="\n").write("\n".join(lines) + "\n")
    with open(os.path.join(outdir, "BEE_FRESH_DISCREPANCIES.jsonl"), "w", newline="\n") as fh:
        for d in disc: fh.write(json.dumps(d, sort_keys=True) + "\n")
    print("\n".join(lines))
    return 0 if not fails else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "gen": gen(a[1], a[2])
    elif a[0] == "ref": ref(a[1], a[2], a[3])
    elif a[0] == "cmp": sys.exit(cmp(a[1], a[2], a[3], a[4], a[5] if len(a) > 5 else None))
