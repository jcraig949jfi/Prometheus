"""Calibration and the A-D generation harness (rules frozen in pan/tests/negspace_prereg.json BEFORE any score).

python -m pan negspace calibrate   known-answer (26 pairs) + symbolic held-out (DSL pairs, analytic labels) for every
                                   evaluator; gates decide whether the behavioral evaluator may judge generation
python -m pan negspace smoke       the smallest functional run of every arm (tiny budgets; plumbing, NOT results)
"""
import datetime as dt
import json
import random
import re
import time

from . import calibration as cal
from . import domain, dsl
from . import evaluators as ev

CATS = ("EQUIVALENT", "DISTINCT", "CHEAT", "UNRESOLVED")


def _prereg():
    from .. import PKG
    return json.loads((PKG / "tests" / "negspace_prereg.json").read_text(encoding="utf-8"))


def calibrate(write=True, out=print, evaluators=None):
    from .. import REPO
    pr = _prereg()
    names = evaluators or list(ev.EVALUATORS)
    t0 = time.time()
    construction = dict(
        guard_rejects_os_import=domain.static_guard("import os\nclass Mechanism:\n    pass\n") is not None,
        guard_rejects_open=domain.static_guard("class Mechanism:\n    def step(self, x):\n        return open('f')\n") is not None,
        guard_passes_all_calibration_sources=all(domain.static_guard(s) is None for s in cal.M.values()),
    )
    contract = {k: domain.satisfies_contract(ev._run(s)) for k, s in cal.M.items()}
    construction["contract_set_matches"] = all((k in cal.CONTRACT_OK) == v for k, v in contract.items())
    construction["contract_mismatches"] = sorted(k for k, v in contract.items() if (k in cal.CONTRACT_OK) != v)
    known = {}
    for name in names:
        rows = []
        for pid, cat, a, b in cal.PAIRS:
            v = ev.EVALUATORS[name](cal.M[a], cal.M[b])
            rows.append(dict(pair=pid, category=cat, verdict=v["verdict"], correct=cal.correct(cat, v["verdict"]),
                             **({"witness": v["witness"]} if "witness" in v else {}),
                             **({"unexecuted": v["unexecuted"]} if "unexecuted" in v else {})))
        per = {c: round(sum(r["correct"] for r in rows if r["category"] == c) /
                        sum(1 for r in rows if r["category"] == c), 3) for c in CATS}
        known[name] = dict(per_category=per, macro=round(sum(per.values()) / len(CATS), 3), rows=rows)
    sp = pr["calibration"]["symbolic_heldout"]
    pairs = dsl.sample_pairs(sp["n_pairs"], sp["seed"])
    sym = {}
    for name in names:
        conf = {lab: {"EQUIVALENT": 0, "DISTINCT": 0, "UNKNOWN": 0} for lab in ("EQUIVALENT", "DISTINCT", "UNRESOLVED")}
        for p, q, lab in pairs:
            conf[lab][ev.EVALUATORS[name](dsl.source(p), dsl.source(q))["verdict"]] += 1
        n = {lab: sum(v.values()) for lab, v in conf.items()}
        rate = dict(EQUIVALENT=conf["EQUIVALENT"]["EQUIVALENT"] / max(1, n["EQUIVALENT"]),
                    DISTINCT=conf["DISTINCT"]["DISTINCT"] / max(1, n["DISTINCT"]),
                    UNRESOLVED=conf["UNRESOLVED"]["UNKNOWN"] / max(1, n["UNRESOLVED"]))
        nondistinct = n["EQUIVALENT"] + n["UNRESOLVED"]
        sym[name] = dict(confusion=conf, n=n, rates={k: round(v, 3) for k, v in rate.items()},
                         macro=round(sum(rate.values()) / 3, 3),
                         false_distinct_rate=round((conf["EQUIVALENT"]["DISTINCT"] + conf["UNRESOLVED"]["DISTINCT"]) /
                                                   max(1, nondistinct), 3),
                         false_equivalent_on_unresolved=round(conf["UNRESOLVED"]["EQUIVALENT"] / max(1, n["UNRESOLVED"]), 3))
    g = pr["calibration"]["promotion_gate"]
    base = [k for k in names if k != "behavioral"]
    best_known = max(known[k]["macro"] for k in base) if base else 0
    best_sym = max(sym[k]["macro"] for k in base) if base else 0
    gate = {}
    if "behavioral" in known:
        b, s = known["behavioral"], sym["behavioral"]
        gate = {
            "known_EQUIVALENT": b["per_category"]["EQUIVALENT"] >= g["known"]["EQUIVALENT"],
            "known_DISTINCT": b["per_category"]["DISTINCT"] >= g["known"]["DISTINCT"],
            "known_CHEAT": b["per_category"]["CHEAT"] >= g["known"]["CHEAT"],
            "known_UNRESOLVED": b["per_category"]["UNRESOLVED"] >= g["known"]["UNRESOLVED"],
            "known_beats_best_baseline": b["macro"] >= best_known + g["margin_over_best_baseline"],
            "sym_false_distinct": s["false_distinct_rate"] <= g["symbolic"]["max_false_distinct_rate"],
            "sym_DISTINCT_recall": s["rates"]["DISTINCT"] >= g["symbolic"]["min_distinct_recall"],
            "sym_UNRESOLVED_unknown": s["rates"]["UNRESOLVED"] >= g["symbolic"]["min_unresolved_unknown"],
            "sym_EQUIVALENT": s["rates"]["EQUIVALENT"] >= g["symbolic"]["min_equivalent_equivalent"],
            "sym_beats_best_baseline": s["macro"] >= best_sym + g["margin_over_best_baseline"],
            "construction_ok": all(v for k, v in construction.items() if k != "contract_mismatches"),
        }
    verdict = "PROMOTED" if gate and all(gate.values()) else "NOT PROMOTED"
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    doc = dict(control="PAN-43 distinctness calibration", at=at, prereg_sha256=_prereg_sha(), verdict=verdict,
               gate=gate, best_baseline_macro=dict(known=best_known, symbolic=best_sym), construction=construction,
               known_answer={k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in known.items()},
               known_answer_rows=known.get("behavioral", {}).get("rows"),
               symbolic_heldout=sym, n_symbolic_pairs=len(pairs), seconds=round(time.time() - t0, 1))
    if write:
        p = REPO / "roles" / "Pan" / "reports" / "controls" / "NEGSPACE_CALIBRATION_{}.json".format(at)
        p.write_text(json.dumps(doc, indent=1, default=str) + "\n", encoding="utf-8")
        out("wrote " + str(p))
    out("{:<18} {:>6} {:>6} {:>6} {:>6}  {:>6} | sym: {:>5} {:>5} {:>5} {:>6} fD".format(
        "evaluator", "EQUIV", "DIST", "CHEAT", "UNRES", "macro", "EQUIV", "DIST", "UNRES", "macro"))
    for k in names:
        pc, sr = known[k]["per_category"], sym[k]["rates"]
        out("{:<18} {:>6} {:>6} {:>6} {:>6}  {:>6} | sym: {:>5} {:>5} {:>5} {:>6} {}".format(
            k, pc["EQUIVALENT"], pc["DISTINCT"], pc["CHEAT"], pc["UNRESOLVED"], known[k]["macro"],
            sr["EQUIVALENT"], sr["DISTINCT"], sr["UNRESOLVED"], sym[k]["macro"], sym[k]["false_distinct_rate"]))
    out("gate: " + json.dumps(gate))
    out(verdict)
    return doc


def _prereg_sha():
    import hashlib
    from .. import PKG
    return hashlib.sha256((PKG / "tests" / "negspace_prereg.json").read_bytes().replace(b"\r\n", b"\n")).hexdigest()


# ---------------------------------------------------------------- generation arms

def known_classes():
    """Every known class used by the ENDPOINT (identical for all arms): supported mechanisms + all failure classes,
    given and withheld."""
    out = [(k, cal.M[v]) for k, v in cal.KNOWN_SUPPORTED.items()]
    out += [(k, cal.M[cal.FAILURE_CLASSES[k]]) for k in cal.GIVEN_FAILURES + cal.WITHHELD_FAILURES]
    return out


def exclusion_library(kind, seed):
    """What an arm's exclusion engine excludes: 'real' = supported + GIVEN failures (withheld ones are NOT in it);
    'counterfeit' = the same number of random DSL mechanisms (Hades O3R analogue: same size, wrong content)."""
    real = [(k, cal.M[v]) for k, v in cal.KNOWN_SUPPORTED.items()] + \
           [(k, cal.M[cal.FAILURE_CLASSES[k]]) for k in cal.GIVEN_FAILURES]
    if kind == "real":
        return real
    rng = random.Random(seed)
    space = list(dsl.params_space())
    return [("counterfeit-{}".format(i), dsl.source(p)) for i, p in enumerate(rng.sample(space, len(real)))]


def equivalent_to(src, refs):
    """Names of refs the behavioral evaluator calls EQUIVALENT to src (UNKNOWN never merges)."""
    return [name for name, ref in refs if ev.behavioral(src, ref)["verdict"] == "EQUIVALENT"]


API = """Write Python 3 code defining exactly one class:

class Mechanism:
    def __init__(self, world):   # world: a dict shared with the environment; you may use it or ignore it
        ...
    def step(self, x):           # called once per time step with an int 0..9; must return an int
        ...

Task (the contract): step(x) must return the input received exactly 3 steps earlier (return 0 for the first 3 steps).
Only the modules collections, itertools, math and functools may be imported. Reply with one ```python code block."""


def llm_prompt(arm, history, feedback):
    parts = [API]
    if arm == "B":
        parts.append("Known failures to avoid:\n" + "\n".join("- " + cal.FAILURE_TEXT[k] for k in cal.GIVEN_FAILURES))
    parts.append("Propose a mechanism that works DIFFERENTLY from the ones already proposed in this session"
                 + (":\n" + "\n---\n".join(history[-3:]) if history else "."))
    if feedback:
        parts.append(feedback)
    return "\n\n".join(parts)


def extract_code(text):
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", text or "", re.S)
    return (m[-1] if m else (text or "")).strip() + "\n"


def _gen(model, prompt, seed):
    """One sampled proposal (prereg: temperature 0.8, top_p 0.95, per-call seed, 700 tokens, thinking off)."""
    import requests
    from ..modelbench import OLLAMA
    body = dict(model=model, prompt=prompt, stream=False, think=False,
                options=dict(temperature=0.8, top_p=0.95, seed=seed, num_ctx=4096, num_predict=700))
    r = requests.post(OLLAMA + "/api/generate", json=body, timeout=900)
    if r.status_code == 400 and "think" in r.text:
        body.pop("think")
        r = requests.post(OLLAMA + "/api/generate", json=body, timeout=900)
    r.raise_for_status()
    from ..modelbench import strip_thinking
    return strip_thinking(r.json().get("response", ""))


def run_arm(arm, budget, seed, model=None, out=print):
    """One arm at a fixed proposal budget. A: LLM; B: LLM + failure descriptions; C: LLM + real exclusion (rejections
    are fed back only as 'rejected'); Cx: LLM + counterfeit exclusion; D: DSL sampler + real exclusion; Dx: DSL sampler
    + counterfeit exclusion. Returns per-proposal records."""
    lib = {"C": "real", "Cx": "counterfeit", "D": "real", "Dx": "counterfeit"}.get(arm)
    library = exclusion_library(lib, seed) if lib else []
    rng = random.Random(seed)
    space = list(dsl.params_space())
    rng.shuffle(space)
    accepted, history, feedback, recs = [], [], None, []
    for i in range(budget):
        t = time.time()
        if arm in ("D", "Dx"):
            src = dsl.source(space[i % len(space)])
        else:
            text = _gen(model, llm_prompt("A" if arm in ("C", "Cx") else arm, history, feedback), seed * 1000 + i)
            src = extract_code(text)
        guard = domain.static_guard(src)
        rec = dict(i=i, guard=guard, seconds=None)
        if guard is None:
            hits = equivalent_to(src, library + [("accepted-{}".format(j), a) for j, a in enumerate(accepted)]) if lib else []
            rec["excluded_by"] = hits
            if hits:
                feedback = "Your previous proposal was rejected: it is equivalent to an excluded mechanism. Propose a different one."
            else:
                feedback = None
                accepted.append(src)
            history.append(src)
        else:
            feedback = "Your previous proposal could not be run ({}). Follow the API exactly.".format(guard)
        rec["src"] = src
        rec["seconds"] = round(time.time() - t, 2)
        recs.append(rec)
    return recs


def endpoints(recs):
    """Identical for every arm: executable, contract-satisfying, equivalent to each known class, and the PRIMARY
    endpoint -- distinct behavioral classes among contract-satisfying proposals equivalent to NO known class."""
    known = known_classes()
    reps, novel_unknown = [], 0
    res = dict(proposals=len(recs), executable=0, contract=0, eq_supported=0, eq_given=0, eq_withheld=0, novel_classes=0)
    for r in recs:
        if r.get("guard"):
            continue
        run = ev._run(r["src"])
        if "error" in run:
            continue
        res["executable"] += 1
        hit = equivalent_to(r["src"], known)
        res["eq_supported"] += any(h in cal.KNOWN_SUPPORTED for h in hit)
        res["eq_given"] += any(h in cal.GIVEN_FAILURES for h in hit)
        res["eq_withheld"] += any(h in cal.WITHHELD_FAILURES for h in hit)
        if not domain.satisfies_contract(run):
            continue
        res["contract"] += 1
        if hit:
            continue
        verdicts = [ev.behavioral(r["src"], rep)["verdict"] for rep in reps]
        if "EQUIVALENT" not in verdicts:
            reps.append(r["src"])
            novel_unknown += "UNKNOWN" in verdicts
    res["novel_classes"] = len(reps)
    res["novel_classes_with_unknown_overlap"] = novel_unknown
    return res


def smoke(write=True, out=print, llm_model="qwen2.5-coder:14b", llm_budget=3, dsl_budget=24, use_llm=True):
    """Smallest functional run: every arm end to end at tiny budgets. Plumbing evidence only -- NOT a result."""
    from .. import REPO
    rows = {}
    for arm in ("D", "Dx"):
        rows[arm] = endpoints(run_arm(arm, dsl_budget, seed=1))
        out("{} {}".format(arm, rows[arm]))
    if use_llm:
        for arm in ("A", "B", "C", "Cx"):
            rows[arm] = endpoints(run_arm(arm, llm_budget, seed=1, model=llm_model))
            out("{} {}".format(arm, rows[arm]))
        import subprocess
        subprocess.run(["ollama", "stop", llm_model], capture_output=True, timeout=60)
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    doc = dict(control="PAN-43 harness SMOKE (plumbing, not results)", at=at, prereg_sha256=_prereg_sha(),
               budgets=dict(dsl=dsl_budget, llm=llm_budget if use_llm else 0), llm_model=llm_model if use_llm else None,
               arms=rows)
    if write:
        p = REPO / "roles" / "Pan" / "reports" / "controls" / "NEGSPACE_SMOKE_{}.json".format(at)
        p.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        out("wrote " + str(p))
    return doc
