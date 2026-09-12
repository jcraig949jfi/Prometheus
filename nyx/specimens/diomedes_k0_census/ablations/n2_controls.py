"""Nyx 2026-09-12: N2 negative chop -- the specimen's own switch (self-test) and the PREREG s4(ii)
independent-behaviour runs for the two TEMPTED candidates, on inputs that are not Diomedes's.
The module is imported by path; nothing outside roles/Diomedes/coordinate_census.py is read by Nyx
(its self-test reads its sibling cycle005_operator_tables.json -- that is the specimen's dependency,
named in the fishing log, not opened by Nyx)."""
from __future__ import annotations
import datetime as _dt, importlib.util, io, json, math, random, subprocess, sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SRC = ROOT / "roles/Diomedes/coordinate_census.py"
spec = importlib.util.spec_from_file_location("coordinate_census", SRC)
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)  # type: ignore

REC = {"date": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "specimen": str(SRC.relative_to(ROOT)), "blocks": []}
def block(name, predicted, fn):
    try:
        obs, err = fn(), None
    except Exception as e:  # noqa: BLE001
        obs, err = None, f"{type(e).__name__}: {e}"[:300]
    REC["blocks"].append({"name": name, "predicted": predicted, "observed": obs, "error": err})

# ---- the specimen's own switch: its self-test, as shipped (subprocess, same interpreter)
def _selftest():
    r = subprocess.run([sys.executable, str(SRC)], capture_output=True, text=True, cwd=ROOT, timeout=300)
    return {"returncode": r.returncode, "first_line": (r.stdout.splitlines() or [""])[0], "stderr_tail": r.stderr[-300:]}
block("S-1_selftest_as_shipped", "exit 0; first line 'SELF-TEST PASSED'", _selftest)

# ---- c02 conditional_headroom on NON-Diomedes inputs (s4 ii): planted conditional structure vs none
rng = random.Random(20260912)
def _states_planted(n=200, k=4, strength=1.0):
    # label depends on (state parity, action): a state-conditional structure a marginal predictor cannot see
    out = []
    for i in range(n):
        acts = [f"a{j}" for j in range(k)]
        par = i % 2
        labs = [1 if ((j % 2) == par) == (rng.random() < strength) else 0 for j in range(k)]
        if 0 < sum(labs) < k:
            out.append({"actions": acts, "labels": labs})
    return out
def _states_marginal(n=200, k=4):
    # label depends on the action only: a marginal predictor sees everything; headroom should be ~0
    out = []
    for _ in range(n):
        acts = [f"a{j}" for j in range(k)]
        labs = [1 if j < k // 2 else 0 for j in range(k)]
        out.append({"actions": acts, "labels": labs})
    return out
block("C02-pos_planted_conditional_structure", "headroom well above 0.05; qualifies True (structure invisible to the marginal predictor)",
      lambda: {k: v for k, v in cc.conditional_headroom(_states_planted()).items() if k in ("state_independent_ceiling", "oracle", "conditional_headroom", "qualifies", "action_entropy_bits", "n_states")})
block("C02-neg_action_only_labels", "headroom 0.0; qualifies False",
      lambda: {k: v for k, v in cc.conditional_headroom(_states_marginal()).items() if k in ("state_independent_ceiling", "oracle", "conditional_headroom", "qualifies")})
block("C02-ctx_parity_declared_as_context_absorbs_it", "with parity given as context the planted structure is absorbed: headroom ~0",
      lambda: {k: v for k, v in cc.conditional_headroom(_states_planted(strength=1.0), context=lambda s: s["labels"][0]).items() if k in ("state_independent_ceiling", "oracle", "conditional_headroom", "qualifies")})
# duplicate control for c02: recompute the SAME quantity from textbook pieces (rank-AUC of a marginal-rate baseline vs a perfect ranker)
def _dup_c02():
    st = _states_planted()
    rate = {}
    for s in st:
        for a, l in zip(s["actions"], s["labels"]):
            t, n = rate.get(a, (0, 0)); rate[a] = (t + l, n + 1)
    r = {a: t / n for a, (t, n) in rate.items()}
    def mw_auc(pairs):  # Mann-Whitney U / (n_pos n_neg), tie-aware -- textbook
        pos = [s for s, l in pairs if l]; neg = [s for s, l in pairs if not l]
        u = sum((1.0 if p > q else 0.5 if p == q else 0.0) for p in pos for q in neg)
        return u / (len(pos) * len(neg))
    base = sum(mw_auc([(r[a], l) for a, l in zip(s["actions"], s["labels"])]) for s in st) / len(st)
    orc = 1.0  # a perfect ranker on states with both classes
    return {"textbook_baseline_auc": round(base, 4), "textbook_headroom": round(orc - base, 4),
            "module_headroom": cc.conditional_headroom(st)["conditional_headroom"]}
block("C02-dup_textbook_recomputation", "module value == Mann-Whitney marginal-baseline AUC gap to 1e-4 (the construction is a composition of textbook pieces)", _dup_c02)

# ---- c07 identifiability_ceiling on NON-Diomedes inputs
def _ic():
    pairs = [("sig_A", "cause1")] * 30 + [("sig_A", "cause2")] * 10 + [("sig_B", "cause3")] * 60
    got = cc.identifiability_ceiling(pairs)
    # textbook: Bayes-optimal accuracy with uniform guess among causes sharing a signature = sum P(sig)/|causes(sig)|
    tb = (40 / 100) / 2 + (60 / 100) / 1
    return {"module": got["exact_oracle_ceiling"], "textbook_bayes_uniform": round(tb, 4), "ambiguous_fraction": got["ambiguous_item_fraction"]}
block("C07-dup_textbook_recomputation", "module == sum P(s)/|A(s)| computed by hand (0.8)", _ic)
block("C07-neg_all_distinct", "ceiling 1.0 when every signature has one cause", lambda: cc.identifiability_ceiling([("s%d" % i, "c%d" % i) for i in range(10)])["exact_oracle_ceiling"])

# ---- c04/c05/c06: the policies and the textbook bootstrap, exercised once each
block("C04_gate_reachable_is_a_range_check", "reachable iff lo <= gate <= hi", lambda: [cc.gate_reachable(0.5, 0.0, 0.4)["reachable"], cc.gate_reachable(0.3, 0.0, 0.4)["reachable"]])
block("C05_gate_exceeds_error_is_2x_rule", "passes iff |point-gate| >= 2*err", lambda: [cc.gate_exceeds_error(0.5, 0.6, 0.06)["passes"], cc.gate_exceeds_error(0.5, 0.6, 0.04)["passes"]])
block("C06_cluster_bootstrap_vs_textbook_shape", "CI contains the point; half-width shrinks with more clusters (textbook behaviour)",
      lambda: {n: cc.cluster_bootstrap({f"c{i}": [rng.gauss(0.5, 0.1) for _ in range(5)] for i in range(n)}, n_boot=400)["half_width"] for n in (4, 16, 64)})

out = HERE / f"RECEIPT_N2_{_dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d')}.json"
out.write_text(json.dumps(REC, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
print(json.dumps(REC, indent=1, ensure_ascii=False, default=str))
