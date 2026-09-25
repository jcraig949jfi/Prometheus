"""P-J02 [T-R01, deformation D]: ACTUAL MUTATIONAL DISTANCE from the identity plateau to the conditional
transforms, measured in the VM on 6 plateau genomes (P-I01 world-A tops, seeds 1-3, ranks 0-1).
  (0) PROBES at the reached OUT (found by knockout): how many of the ask tick's words are still unread
      when the answer is emitted (3 = the organism answers BEFORE reading the ask tick), and whether any
      register holds the regime word at that moment (literal equality; cross-set lookup).
  (1) WITNESSES: hand-constructed conditional programs from templates (instruments / positive controls,
      not discoveries), inserted at every position with a small set of register choices; VERIFIED on the
      4 held-out sets; the minimal verified size is an UPPER BOUND on the distance.
  (2) INTERMEDIATES: fitness of every prefix of the minimal witness in insertion order, and of the witness
      with each single instruction removed (which instructions are individually necessary).
  (3) EXHAUSTIVE STRUCTURED ONE-EDIT CENSUS: insertion and replacement of (op, a = out, b = out, c = j) for
      op in XOR/ADD/SUB/OR/AND/MUL/MOV/IN at every position and every j; fitness on A' (xor 1) and A (xor 15).
  (4) SAMPLED GRAMMAR NEIGHBOURHOOD: 2000 one-operator and 2000 two-operator mutants under grammar v0.4
      per genome; shares hit / beneficial / neutral / deleterious on both worlds.
  (5) the grammar's EXACT probability of producing a census hit per birth and the expected hits over a
      P-J01 run (11520 births); routes named per world.
Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ctxworlds as CW         # noqa: E402
import ctxevo as CE            # noqa: E402
sys.path.insert(0, str(HERE.parent / "P-I02"))
from run_PI02 import eval_reg  # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-J02", "T-R01"
IW = 4
OPS = {"XOR": 12, "ADD": 7, "SUB": 8, "OR": 11, "AND": 10, "MUL": 9, "MOV": 4, "IN": 21}
XOR, ADD, SUB, MUL, LDC, IN, INQ, NOP, OUT = 12, 7, 8, 9, 3, 21, 22, 0, 23
MARGIN = 0.0625          # 2 of 32 asks on the 2-set screen
MARGIN4 = 0.05           # confirmation on 4 sets
CONFIRM_CAP = 300
N_SAMPLE = 2000
BIRTHS_PJ01 = 96 * 120


def instrs(m):
    g = m["genome"]
    return [g[i:i + IW] for i in range(0, len(g), IW)]


def with_genome(m, ins):
    c = json.loads(json.dumps(m))
    c["genome"] = [w for x in ins for w in x]
    return c


def insert(m, pos, new):
    ins = instrs(m)
    return with_genome(m, ins[:pos] + [list(x) for x in new] + ins[pos:])


def replace(m, pos, new):
    ins = instrs(m)
    ins[pos] = list(new)
    return with_genome(m, ins)


def fit(m, sets):
    return CE.held_reward(m, sets)


def answers(m, eps):
    return [t["answer"] for t in eval_reg(m, eps)["trace"]]


def reached_out(m, eps):
    """The OUT whose knockout (opcode -> NOP) changes the most answers; returns (index, out_register, share changed)."""
    nr = m["n_regs"]
    base = answers(m, eps)
    best = None
    for i, x in enumerate(instrs(m)):
        if x[0] % 25 == OUT:
            k = json.loads(json.dumps(m))
            k["genome"][i * IW] = NOP
            ch = float(np.mean([u != v for u, v in zip(base, answers(k, eps))]))
            if best is None or ch > best[0]:
                best = (ch, i, x[1] % nr)
    return (best[1], best[2], best[0]) if best else (None, None, 0.0)


def probe_out(m, pos, a, sets):
    """Replace the reached OUT's source by a probe: INQ (unread words) or another register j; the first
    output word of the ask tick is then the probed value at the moment the answer would have been emitted."""
    nr = m["n_regs"]
    # unread words at the OUT
    free = [j for j in range(nr) if j != a][0]
    c = insert(m, pos, [[INQ, free, 0, 0]])
    c["genome"][(pos + 1) * IW + 1] = free
    unread = [t["answer"] for t in eval_reg(c, sets[0])["trace"]]
    out = {"unread_at_out_mean": float(np.mean([u if u is not None else -1 for u in unread])), "unread_at_out_values": dict(Counter(unread))}
    # registers at the OUT
    lit, xval = [], []
    for j in range(nr):
        c = json.loads(json.dumps(m))
        c["genome"][pos * IW + 1] = j
        tr0 = eval_reg(c, sets[0])["trace"]
        tr1 = eval_reg(c, sets[1])["trace"]
        if all(t["answer"] == t["regime"] for t in tr0 + tr1):
            lit.append(j)
        table = {}
        for t in tr0:
            table.setdefault(t["answer"], []).append(t["regime"])
        pred = {k: Counter(v).most_common(1)[0][0] for k, v in table.items()}
        acc = float(np.mean([pred.get(t["answer"], -1) == t["regime"] for t in tr1]))
        if acc >= 0.95:
            xval.append({"reg": j, "xval_acc": acc, "n_values_set0": len(table)})
    out["literal_regime_registers_at_out"] = lit
    out["xval_regime_registers_at_out"] = xval
    return out


def templates(kind, a, nr):
    """Witness templates (instruction lists) with named registers to be bound; each yields (name, seq)."""
    regs = [j for j in range(nr) if j != a]
    if kind == "xor1":
        for j in range(nr):
            yield "xor_reg%d" % j, [[XOR, a, a, j]]
        for k in (1, 2, 3):
            for t in regs[:6]:
                yield "in%d_t%d_xor" % (k, t), [[IN, t, 0, 0]] * k + [[XOR, a, a, t]]
    else:
        for j in regs[:6]:
            for t in regs[:6]:
                if t != j:
                    yield "ldc_mul_reg%d_t%d" % (j, t), [[LDC, t, 15, 0], [MUL, t, t, j], [XOR, a, a, t]]
        for k in (1, 2, 3):
            for u, t in ((0, 1), (0, 2), (1, 2), (2, 4), (4, 5)):
                if a in (u, t):
                    continue
                yield "in%d_u%d_t%d_ldc_mul_xor" % (k, u, t), [[IN, u, 0, 0]] * k + [[LDC, t, 15, 0], [MUL, t, t, u], [XOR, a, a, t]]
    # PUT-neutral general template: reads kind k, tag g, word x; k' = k - 1 (0 at PUT, 1 at ASK);
    # PUT: out ^= x (stores v); ASK: out ^= C * x  (C = 1 or 15)
    C = 1 if kind == "xor1" else 15
    for (k, g, x, o, t, u) in (((0, 1, 2, 4, 5, 6)), ((1, 2, 4, 5, 6, 7)), ((7, 8, 9, 10, 11, 12))):
        if a in (k, g, x, o, t, u):
            continue
        seq = [[IN, k, 0, 0], [IN, g, 0, 0], [IN, x, 0, 0], [LDC, o, 1, 0], [SUB, k, k, o], [MUL, t, x, k], [SUB, u, o, k], [MUL, x, x, u], [XOR, a, a, x]]
        if C != 1:
            seq += [[LDC, o, C, 0], [MUL, t, t, o]]
        seq += [[XOR, a, a, t]]
        yield "put_neutral_k%d" % k, seq


def witness_search(m, sets, thr, kind, a, positions):
    found = []
    for name, seq in templates(kind, a, m["n_regs"]):
        for p in positions:
            c = insert(m, p, seq)
            f = fit(c, sets[:2])
            if f >= thr:
                f4 = fit(c, sets)
                if f4 >= thr:
                    found.append({"name": name, "pos": p, "seq": seq, "n_instr": len(seq), "held": round(f4, 4)})
    found.sort(key=lambda w: (w["n_instr"], -w["held"]))
    return found


def intermediates(m, w, sets, f0, thr):
    """Prefix path (insertion order) and single-instruction necessity of the minimal witness."""
    seq, p = w["seq"], w["pos"]
    prefix = [round(fit(insert(m, p, seq[:k]), sets[:2]), 4) for k in range(1, len(seq) + 1)]
    inter = prefix[:-1]
    route = ("ONE_STEP" if not inter else "BENEFICIAL_PATH" if all(s > f0 + MARGIN for s in inter) else "DELETERIOUS_VALLEY" if any(s < f0 - MARGIN for s in inter) else "NEUTRAL_BRIDGE")
    first_gain = next((k + 1 for k, s in enumerate(prefix) if s > f0 + MARGIN), None)
    drop1 = [round(fit(insert(m, p, seq[:i] + seq[i + 1:]), sets[:2]), 4) for i in range(len(seq))]
    return {"prefix_fitness": prefix, "route_prefix_path": route, "first_gain_at_prefix": first_gain, "n_instr": len(seq),
            "drop_one_fitness": drop1, "n_individually_necessary": sum(1 for d in drop1 if d < thr)}


def classify(f, f0, thr):
    if f >= thr:
        return "hit"
    if f > f0 + MARGIN:
        return "beneficial"
    if f < f0 - MARGIN:
        return "deleterious"
    return "neutral"


def structured_census(m, a, sets_by_world, f0, thr):
    nr, n = m["n_regs"], len(instrs(m))
    rows = []
    for mode in ("insert", "replace"):
        for opn, op in OPS.items():
            for p in range(n + (1 if mode == "insert" else 0)):
                for j in range(nr):
                    new = [op, a, a, j] if opn != "IN" else [op, a, j, 0]
                    c = insert(m, p, [new]) if mode == "insert" else replace(m, p, new)
                    r = {"mode": mode, "op": opn, "pos": p, "j": j}
                    for w, sets in sets_by_world.items():
                        f = fit(c, sets[:2])
                        r[w] = round(f, 4)
                        r[w + "_class"] = classify(f, f0[w], thr)
                    rows.append(r)
    return rows


def grammar_sample(m, sets_by_world, f0, thr, seed, n_ops):
    rng = A.SplitMix64(A.seed_from("nestor.pj02.grammar", A.LOOP_SEED, seed, n_ops))
    rows = []
    for i in range(N_SAMPLE):
        c, ops = m, []
        for _ in range(n_ops):
            for _try in range(8):
                try:
                    c, rec = A.GR.mutate(c, rng, mate=None, name=None)
                    ops.append(rec["operator"])
                    break
                except Exception:      # noqa: BLE001
                    continue
        r = {"ops": ops, "m": c}
        for w, sets in sets_by_world.items():
            f = fit(c, sets[:2])
            r[w] = round(f, 4)
            r[w + "_class"] = classify(f, f0[w], thr)
        rows.append(r)
    return rows


def confirm_beneficial(rows, sets_by_world, f0_4, thr, build):
    """Re-evaluate screened beneficial / hit rows on all 4 sets (cap); per world the confirmed counts."""
    out = {}
    for w, sets in sets_by_world.items():
        cand = [r for r in rows if r[w + "_class"] in ("beneficial", "hit")][:CONFIRM_CAP]
        conf = [fit(build(r), sets) for r in cand]
        out[w] = {"screened": sum(1 for r in rows if r[w + "_class"] in ("beneficial", "hit")), "checked": len(cand), "confirmed_beneficial": sum(1 for f in conf if f > f0_4[w] + MARGIN4), "confirmed_hit": sum(1 for f in conf if f >= thr),
                  "best_4set": max(conf, default=None)}
    return out


def grammar_exact_p(m, hits_ins, hits_rep):
    """Per-birth probability that grammar v0.4 produces one of the census hits exactly: insertion draws k
    in 1..4 (k = 1 needed), a uniform position among n+1, and uniform 32-bit words (op ~ 1/25, each operand
    ~ 1/nr); replacement draws a uniform position among n and one random instruction."""
    w = dict(zip(A.GR.NAMES, A.GR.WEIGHTS))
    nr, n = m["n_regs"], len(instrs(m))
    rng = A.SplitMix64(A.seed_from("nestor.pj02.k", A.LOOP_SEED))
    pk1 = float(np.mean([A.GR._k(rng) == 1 for _ in range(20000)]))
    per_instr = (1 / 25) * (1 / nr) ** 3
    p_ins = w.get("insertion", 0.0) * pk1 * hits_ins * per_instr / (n + 1)
    p_rep = w.get("replacement", 0.0) * hits_rep * per_instr / n
    return {"w_insertion": w.get("insertion"), "w_replacement": w.get("replacement"), "p_k1": pk1, "p_per_birth": p_ins + p_rep,
            "expected_hits_per_PJ01_run": (p_ins + p_rep) * BIRTHS_PJ01, "expected_hits_per_generation": (p_ins + p_rep) * 96}


def job(j):
    t0 = time.time()
    m = j["m"]
    sets = {"xor1": CE.held_sets("A", j["seed"], xor=1), "xor15": CE.held_sets("A", j["seed"], xor=15)}
    thr = CE.THRESH["A"]
    f0_4 = {w: fit(m, s) for w, s in sets.items()}
    f0 = {w: fit(m, s[:2]) for w, s in sets.items()}          # the screen baseline on the SAME 2 sets as the mutants
    pos, a, ch = reached_out(m, sets["xor1"][0])
    n = len(instrs(m))
    out = {"seed": j["seed"], "rank": j["rank"], "n_instr": n, "n_regs": m["n_regs"], "persist": m["persist"], "f0_4set": f0_4, "f0_2set": f0, "out_index": pos, "out_reg": a, "out_knockout_changed": ch}
    if pos is None:
        out["error"] = "no reached OUT"
        return out
    out["probe"] = probe_out(m, pos, a, sets["xor1"])
    positions = list(range(n + 1))
    out["witness"] = {}
    out["intermediates"] = {}
    for w, kind in (("xor1", "xor1"), ("xor15", "xor15")):
        ws = witness_search(m, sets[w], thr, kind, a, positions)
        out["witness"][w] = {"n_verified": len(ws), "minimal": ws[0] if ws else None, "min_n_instr": ws[0]["n_instr"] if ws else None, "by_size": dict(Counter(x["n_instr"] for x in ws)),
                             "by_template": dict(Counter(x["name"].split("_")[0] for x in ws)), "positions_of_minimal": sorted({x["pos"] for x in ws if ws and x["n_instr"] == ws[0]["n_instr"]})[:30]}
        if ws:
            out["intermediates"][w] = intermediates(m, ws[0], sets[w], f0[w], thr)

    def build_census(r):
        new = [OPS[r["op"]], a, a, r["j"]] if r["op"] != "IN" else [OPS[r["op"]], a, r["j"], 0]
        return insert(m, r["pos"], [new]) if r["mode"] == "insert" else replace(m, r["pos"], new)
    census = structured_census(m, a, sets, f0, thr)
    census_conf = confirm_beneficial(census, sets, f0_4, thr, build_census)
    out["census"] = {}
    for w in sets:
        cls = Counter(r[w + "_class"] for r in census)
        hits = [r for r in census if r[w + "_class"] == "hit"]
        conf = []
        for r in hits:
            new = [OPS[r["op"]], a, a, r["j"]] if r["op"] != "IN" else [OPS[r["op"]], a, r["j"], 0]
            c = insert(m, r["pos"], [new]) if r["mode"] == "insert" else replace(m, r["pos"], new)
            f = fit(c, sets[w])
            if f >= thr:
                conf.append(dict(r, held4=round(f, 4)))
        hi = sum(1 for r in conf if r["mode"] == "insert")
        hr = sum(1 for r in conf if r["mode"] == "replace")
        ben = [r for r in census if r[w + "_class"] == "beneficial"]
        out["census"][w] = {"n": len(census), "classes": dict(cls), "hits_screen": len(hits), "hits_confirmed": len(conf), "hits_insert": hi, "hits_replace": hr,
                            "beneficial_best_2set": max([r[w] for r in ben], default=None), "beneficial_ops": dict(Counter(r["op"] for r in ben)), "confirm4": census_conf[w],
                            "hit_ops": dict(Counter(r["op"] for r in conf)), "grammar_exact": grammar_exact_p(m, hi, hr), "examples": conf[:5]}
    g1 = grammar_sample(m, sets, f0, thr, j["seed"] * 10 + j["rank"], 1)
    g2 = grammar_sample(m, sets, f0, thr, j["seed"] * 10 + j["rank"], 2)
    out["grammar"] = {}
    for tag, rows in (("one_op", g1), ("two_op", g2)):
        d = {"confirm4": confirm_beneficial(rows, sets, f0_4, thr, lambda r: r["m"])}
        for w in sets:
            cls = Counter(r[w + "_class"] for r in rows)
            d[w] = {k: cls.get(k, 0) / len(rows) for k in ("hit", "beneficial", "neutral", "deleterious")}
            d[w]["best"] = max(r[w] for r in rows)
            d[w]["beneficial_ops"] = dict(Counter("+".join(r["ops"]) for r in rows if r[w + "_class"] in ("beneficial", "hit")))
        out["grammar"][tag] = d
    routes = {}
    for w in sets:
        c, g1w, g2w = out["census"][w], out["grammar"]["one_op"][w], out["grammar"]["two_op"][w]
        wit = out["witness"][w]["min_n_instr"]
        if g1w["hit"] > 0:
            routes[w] = "BENEFICIAL_PATH"
        elif c["hits_confirmed"] > 0:
            routes[w] = "BENEFICIAL_PATH_GRAMMAR_RARE(E_hits/run=%.3g)" % c["grammar_exact"]["expected_hits_per_PJ01_run"]
        elif g2w["hit"] > 0:
            routes[w] = "TWO_EDIT_REACHABLE"
        elif wit is not None:
            routes[w] = "NO_ONE_OR_TWO_EDIT_HIT; witness at %d instructions via %s" % (wit, out["intermediates"][w]["route_prefix_path"])
        else:
            routes[w] = "UNREACHABLE_WITHIN_CENSUS_AND_TEMPLATES"
    out["routes"] = routes
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out


def main():
    t0 = time.time()
    tops = json.load(open(HERE.parent / "P-I01" / "tops.json", encoding="utf-8"))
    jobs = [{"m": r["tops"][k]["m"], "seed": r["seed"], "rank": k} for r in tops if r["world"] == "A" and r["control"] is None for k in (0, 1)]
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "D", "scope": CM.SCOPE, "claim_type": "instrument-census", "genomes": [(j["seed"], j["rank"]) for j in jobs],
                         "probes": "unread words and register contents at the reached OUT (knockout-identified) on the ask tick",
                         "witnesses": {"templates": "XOR out,out,j | IN^k t; XOR out,out,t | LDC t,15; MUL t,t,j; XOR out,out,t (+IN^k) | PUT-neutral 10/12-instruction template", "positions": "every position", "verified": "4 held-out sets >= %.2f" % CE.THRESH["A"], "reading": "minimal verified size = UPPER BOUND on distance"},
                         "intermediates": "prefix fitness in insertion order; drop-one necessity",
                         "census": {"structured": "insert + replace (op in %s, a=out, b=out, c=j) at every position, 2 held set screen with the baseline on the same sets, beneficial / hits confirmed on 4" % list(OPS), "grammar": "%d one-op and %d two-op mutants (v0.4), 2 held sets, beneficial / hits confirmed on 4 (cap %d)" % (N_SAMPLE, N_SAMPLE, CONFIRM_CAP)},
                         "classes": {"hit": ">= threshold", "beneficial": "> f0 + %.2f" % MARGIN, "deleterious": "< f0 - %.2f" % MARGIN, "neutral": "otherwise"},
                         "routes": ["BENEFICIAL_PATH", "BENEFICIAL_PATH_GRAMMAR_RARE", "TWO_EDIT_REACHABLE", "NO_ONE_OR_TWO_EDIT_HIT; witness at n via {BENEFICIAL_PATH|NEUTRAL_BRIDGE|DELETERIOUS_VALLEY}", "UNREACHABLE_WITHIN_CENSUS_AND_TEMPLATES"],
                         "material_rule": "always material (instrument)", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    with A.pool(6) as ex:
        rows = list(ex.map(job, jobs))
    W = ("xor1", "xor15")
    summary = {"unread_at_out": [r["probe"]["unread_at_out_mean"] for r in rows], "literal_regime_regs_at_out": [r["probe"]["literal_regime_registers_at_out"] for r in rows],
               "xval_regime_regs_at_out": [[x["reg"] for x in r["probe"]["xval_regime_registers_at_out"]] for r in rows],
               "witness_min_instr": {w: [r["witness"][w]["min_n_instr"] for r in rows] for w in W}, "witness_templates": {w: [r["witness"][w]["by_template"] for r in rows] for w in W},
               "routes": [r["routes"] for r in rows], "census_hits": {w: [r["census"][w]["hits_confirmed"] for r in rows] for w in W},
               "census_beneficial_confirmed": {w: [r["census"][w]["confirm4"]["confirmed_beneficial"] for r in rows] for w in W}, "census_beneficial_best4": {w: [r["census"][w]["confirm4"]["best_4set"] for r in rows] for w in W},
               "grammar_one_op_confirm4": {w: [r["grammar"]["one_op"]["confirm4"][w] for r in rows] for w in W}, "grammar_two_op_confirm4": {w: [r["grammar"]["two_op"]["confirm4"][w] for r in rows] for w in W}, "census_classes": {w: [r["census"][w]["classes"] for r in rows] for w in W},
               "grammar_one_op": {w: {k: float(np.mean([r["grammar"]["one_op"][w][k] for r in rows])) for k in ("hit", "beneficial", "neutral", "deleterious", "best")} for w in W},
               "grammar_two_op": {w: {k: float(np.mean([r["grammar"]["two_op"][w][k] for r in rows])) for k in ("hit", "beneficial", "neutral", "deleterious", "best")} for w in W},
               "intermediates": {w: [r["intermediates"].get(w, {}).get("route_prefix_path") for r in rows] for w in W},
               "first_gain_at_prefix": {w: [r["intermediates"].get(w, {}).get("first_gain_at_prefix") for r in rows] for w in W}}
    out = {"perturbation_id": PID, "parent": TID, "summary": summary, "rows": rows, "material": True, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "witnesses.json").write_text(json.dumps([{"seed": r["seed"], "rank": r["rank"], "out_index": r["out_index"], "out_reg": r["out_reg"], "m": None, "xor1": r["witness"]["xor1"]["minimal"], "xor15": r["witness"]["xor15"]["minimal"]} for r in rows], ensure_ascii=True), encoding="utf-8")
    L.append_evidence(TID, PID, "mutational distance (6 plateau genomes): unread words at the answering OUT %s; literal regime registers at OUT %s; witness min instr xor1 %s xor15 %s; census hits xor1 %s xor15 %s (beneficial confirmed on 4 sets %s, best %s); grammar one-op %s; two-op %s; intermediates %s; routes %s" % (
        summary["unread_at_out"], summary["literal_regime_regs_at_out"], summary["witness_min_instr"]["xor1"], summary["witness_min_instr"]["xor15"], summary["census_hits"]["xor1"], summary["census_hits"]["xor15"], summary["census_beneficial_confirmed"], summary["census_beneficial_best4"],
        {w: {k: round(v, 4) for k, v in d.items()} for w, d in summary["grammar_one_op"].items()}, {w: {k: round(v, 4) for k, v in d.items()} for w, d in summary["grammar_two_op"].items()}, summary["intermediates"], summary["routes"]), True, detail=summary)
    L.append_evidence("T-X21", PID, "cross: distance of the plateau to XOR-1 / XOR-15 in the VM: witnesses %s / %s instructions; unread words at the answering OUT %s; routes %s" % (summary["witness_min_instr"]["xor1"], summary["witness_min_instr"]["xor15"], summary["unread_at_out"], summary["routes"]), True)
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps(summary, default=CM.js)[:2500])


if __name__ == "__main__":
    main()
