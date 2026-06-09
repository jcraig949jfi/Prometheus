"""R12 demo runner: emit a formal conjecture + first falsification test, grade
both deterministically (EXPERIMENTAL).

Design spec: harmonia/memory/architecture/
reasoning_ladder_frontier_synthesis_2026-05-29.md  §4(R12), §5.

This is the GLUE: build a randomized finite-universe trial, render the revealed
labelled data + the feature schema + the output contract into a prompt, get the
model to emit (a) a Python boolean `conjecture(obj)` and (b) a proposed next
falsification test (a single object's feature values), then grade conjecture
quality and test quality SEPARATELY with the deterministic graders.

Usage:
    python harmonia/experiments/run_r12.py                 # offline mock, 3 trials
    python harmonia/experiments/run_r12.py --live           # real Opus calls
    python harmonia/experiments/run_r12.py --live -n 5 --universe tuples

NO free-text judging anywhere. The model emits machine-checkable artifacts; the
grader is pure information theory + held-out prediction. Security: the API key is
obtained via keys.get_key inside the Anthropic client and never read or logged.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from r12_universe import (  # noqa: E402
    Trial,
    Universe,
    build_bits_universe,
    build_tuples_universe,
    enumerate_hypothesis_class,
    make_trial,
    pred_to_python,
    pred_to_str,
)
from r12_grader import (  # noqa: E402
    consistent_version_space,
    grade_emission,
)


# --------------------------------------------------------------------------- #
# Prompt rendering
# --------------------------------------------------------------------------- #
def render_prompt(trial: Trial) -> str:
    uni = trial.universe
    feats = list(uni.features)
    # describe the universe + feature domains
    dom_lines = "\n".join(
        f"    - {f}: integer in {{{', '.join(map(str, uni.feat_domain[f]))}}}"
        for f in feats
    )
    # revealed labelled data
    rows = []
    for i in trial.revealed_idx:
        o = uni.objects[i]
        fv = ", ".join(f"{f}={o[f]}" for f in feats)
        rows.append(f"    {{{fv}}}  ->  {'PASS' if trial.labels[i] else 'FAIL'}")
    revealed_block = "\n".join(rows)

    return f"""You are reverse-engineering a HIDDEN rule over a finite set of objects.

Each object is a dict of integer features:
{dom_lines}

A hidden boolean rule labels every object PASS or FAIL. You are shown a labelled
SUBSET below; the rest are held out.

REVEALED DATA ({len(trial.revealed_idx)} objects):
{revealed_block}

Your tasks:
  (1) CONJECTURE: write a single Python boolean function that you believe equals
      the hidden rule, using ONLY: feature reads like obj['{feats[0]}'], integer
      arithmetic (+, -, *, %, //, ** with small exponents), comparisons, and
      and/or/not. NO imports, NO other function calls except abs/min/max/len/sum,
      NO loops, NO attribute access. Form:
          def conjecture(obj):
              return <expression>
      Aim for the rule that GENERALIZES, not one that merely memorizes the
      revealed rows.
  (2) FIRST TEST: propose the single most informative next object to probe (the
      one whose hidden label would best discriminate among rules still
      consistent with the revealed data). Give it as feature values.

Respond with EXACTLY one JSON object, no prose, no markdown fences:
{{
  "conjecture_src": "def conjecture(obj):\\n    return ...",
  "test_object": {{ {', '.join(f'"{f}": <int>' for f in feats)} }},
  "predicted_counterexample_region": "one short line naming where you expect your rule is most likely wrong",
  "reasoning": "one short line"
}}"""


# --------------------------------------------------------------------------- #
# Live Opus emission (standalone -- does NOT edit reasoners_llm.py)
# --------------------------------------------------------------------------- #
def make_r12_opus_emitter(model: str = "claude-opus-4-8",
                          max_tokens: int = 4000,
                          use_thinking: bool = True,
                          call_log: Optional[list] = None):
    """Return fn(trial) -> emission_dict, backed by Opus with a structured-output
    schema specific to R12 (conjecture_src + test_object). This is a SEPARATE
    emitter from reasoners_llm.make_opus_reasoner because R12 needs to emit a
    Python predicate STRING and a test object, which the ph0 per-kind schemas do
    not cover. We deliberately do not touch reasoning_phase0/reasoners_llm.

    Security: key via keys.get_key, never logged. Prompt caching on the system
    block. Structured outputs eliminate the free-text parse-failure class.
    """
    import anthropic
    from keys import get_key
    from pydantic import BaseModel, Field, create_model

    system = ("You are a careful scientist inducing a hidden rule from data. You "
              "emit a Python predicate that GENERALIZES (never one that merely "
              "memorizes the shown rows) and you name your single most "
              "informative next experiment. You ALWAYS reply with one JSON object.")
    client = anthropic.Anthropic(api_key=get_key("claude"), max_retries=8)
    sys_blocks = [{"type": "text", "text": system,
                   "cache_control": {"type": "ephemeral"}}]

    # Per-universe schema cache: the test_object is a model with REQUIRED int
    # fields (one per feature) so structured outputs force the model to emit a
    # concrete probe (an empty Dict[str,int] let earlier runs return {}).
    _schema_cache: Dict[Tuple[str, ...], Any] = {}

    def _emission_schema(feats: Tuple[str, ...]):
        if feats in _schema_cache:
            return _schema_cache[feats]
        test_fields = {f: (int, Field(description=f"integer value of feature {f}"))
                       for f in feats}
        TestObj = create_model("R12TestObject", **test_fields)
        Emission = create_model(
            "R12Emission",
            conjecture_src=(str, Field(description="def conjecture(obj): return <expr>")),
            test_object=(TestObj, Field(description="the single most informative next object to probe")),
            predicted_counterexample_region=(str, ""),
            reasoning=(str, ""),
        )
        _schema_cache[feats] = Emission
        return Emission

    def emit(trial: Trial) -> Dict[str, Any]:
        prompt = render_prompt(trial)
        schema = _emission_schema(tuple(trial.universe.features))
        kw = dict(model=model, max_tokens=max_tokens, system=sys_blocks,
                  messages=[{"role": "user", "content": prompt}],
                  output_format=schema)
        if use_thinking:
            kw["thinking"] = {"type": "adaptive"}
        last_err = None
        for _ in range(2):
            try:
                resp = client.messages.parse(**kw)
                po = resp.parsed_output
                d = po.model_dump() if po is not None else {}
                if call_log is not None:
                    u = resp.usage
                    call_log.append({
                        "provider": model,
                        "in": getattr(u, "input_tokens", 0),
                        "out": getattr(u, "output_tokens", 0),
                        "parse_error": None,
                    })
                d["_provider"] = model
                d["_error"] = None
                return d
            except Exception as e:  # noqa: BLE001
                last_err = e
        if call_log is not None:
            call_log.append({"provider": model, "parse_error":
                             f"api_error:{type(last_err).__name__}"})
        return {"conjecture_src": "", "test_object": {}, "_provider": model,
                "_error": f"api_error:{type(last_err).__name__}: {str(last_err)[:160]}"}

    return emit


# --------------------------------------------------------------------------- #
# Offline mock emitter -- 3 archetypes so the demo is meaningful without network
# --------------------------------------------------------------------------- #
def make_mock_emitter(archetype: str = "good"):
    """Deterministic offline emitter. archetype in {good, overfit, naive}.
    Clearly labelled in the trace so it is never mistaken for real LLM output.

      good     : emits the true target rule (the ceiling) + a near-optimal probe.
      overfit  : memorizes the revealed positives (collapses under baseline pen.)
      naive    : emits `return True` (const mimic) + a useless probe.
    """
    import math as _m

    def emit(trial: Trial) -> Dict[str, Any]:
        uni = trial.universe
        feats = list(uni.features)
        if archetype == "good":
            src = "def conjecture(obj):\n    return " + pred_to_python(trial.target)
            # near-optimal probe: scan the universe for the best version-space split
            V = consistent_version_space(trial)
            m = len(V)
            best_j, best_g = trial.holdout_idx[0] if trial.holdout_idx else 0, -1.0
            if m > 1:
                prior = _m.log2(m)
                for j in range(len(uni)):
                    t = sum(1 for _hi, sig in V if j in sig)
                    f = m - t
                    ep = 0.0
                    if t: ep += (t/m)*_m.log2(t)
                    if f: ep += (f/m)*_m.log2(f)
                    g = prior - ep
                    if g > best_g:
                        best_g, best_j = g, j
            test_obj = {f: uni.objects[best_j][f] for f in feats}
        elif archetype == "overfit":
            pos = [i for i in trial.revealed_idx if trial.labels[i]]
            clauses = ["(" + " and ".join(f"obj['{f}'] == {uni.objects[i][f]}"
                                          for f in feats) + ")" for i in pos]
            body = " or ".join(clauses) if clauses else "False"
            src = "def conjecture(obj):\n    return " + body
            test_obj = {f: uni.objects[trial.holdout_idx[0]][f] for f in feats} \
                if trial.holdout_idx else {}
        else:  # naive
            src = "def conjecture(obj):\n    return True"
            # a deliberately useless probe: an already-revealed object
            ri = trial.revealed_idx[0]
            test_obj = {f: uni.objects[ri][f] for f in feats}
        return {"conjecture_src": src, "test_object": test_obj,
                "predicted_counterexample_region": f"(mock:{archetype})",
                "reasoning": f"mock {archetype}", "_provider": f"MOCK:{archetype}",
                "_error": None}

    return emit


# --------------------------------------------------------------------------- #
# Run + report (failure-SHAPE oriented, not pass/fail verdicts)
# --------------------------------------------------------------------------- #
def run(emit, trials: List[Trial], label: str) -> None:
    print(f"\n================ {label} ================")
    for t in trials:
        em = emit(t)
        provider = em.get("_provider")
        err = em.get("_error")
        src = (em.get("conjecture_src") or "").strip()
        test_obj = em.get("test_object") or None
        print(f"\n--- trial seed={t.seed}  universe={t.universe.name}  "
              f"|U|={len(t.universe)}  provider={provider} ---")
        print(f"  HIDDEN target : {pred_to_str(t.target)}   |ext|={len(t.target_sig)}")
        print(f"  revealed={len(t.revealed_idx)}  holdout={len(t.holdout_idx)}  "
              f"|V|={len(consistent_version_space(t))}")
        if err:
            print(f"  EMISSION ERROR: {err}")
            continue
        print(f"  emitted conjecture: {src.splitlines()[-1].strip() if src else '(none)'}")
        if em.get("predicted_counterexample_region"):
            print(f"  self-named danger zone: {em['predicted_counterexample_region']}")
        print(f"  proposed test object: {test_obj}")

        res = grade_emission(t, src, test_obj)
        if not res.safe:
            # an UNSAFE emission is a failure SHAPE, recorded, never silently 0
            print(f"  [SANDBOX REJECT] unsafe emission: {res.unsafe_reason}")
            continue
        cq, tq = res.conjecture, res.test
        print(f"  features used: {res.feature_keys}   pred accepts {res.pred_ext_size}/{len(t.universe)}")
        print(f"  CONJECTURE-QUALITY = {cq.quality:.3f}   "
              f"(holdout_acc={cq.raw_holdout_acc:.3f}, jaccard_to_target="
              f"{cq.raw_jaccard_full:.3f}, exact_partition={cq.exact_partition})")
        print(f"     baseline penalty: most-similar={cq.most_similar_baseline} "
              f"@ jaccard={cq.max_baseline_jaccard:.3f}")
        if tq is not None:
            print(f"  TEST-QUALITY = {tq.info_gain_bits:.3f} bits expected "
                  f"(worst-case {tq.worst_case_gain_bits:.3f}; optimal "
                  f"{tq.optimal_gain_bits:.3f}; efficiency {tq.efficiency:.3f}; "
                  f"|V|={tq.version_space_size}, split {tq.splits_true}/{tq.splits_false}; "
                  f"in_universe={tq.is_in_universe})")
        else:
            print("  TEST-QUALITY = (no test object emitted)")
        # the two scores are reported SEPARATELY -- never fused into one scalar.


def build_trials(universe_name: str, n: int, n_reveal: int, max_terms: int,
                 base_seed: int) -> Tuple[List[Trial], Universe]:
    if universe_name == "tuples":
        uni = build_tuples_universe(0, 7)
    else:
        uni = build_bits_universe(5)
    H = enumerate_hypothesis_class(uni, max_terms=max_terms)
    trials = [make_trial(seed=base_seed + i, universe=uni, H=H, n_reveal=n_reveal)
              for i in range(n)]
    return trials, uni


def main() -> int:
    ap = argparse.ArgumentParser(description="R12 conjecture-under-falsification demo")
    ap.add_argument("--live", action="store_true",
                    help="use real Opus calls (else offline mock archetypes)")
    ap.add_argument("-n", type=int, default=3, help="number of trials")
    ap.add_argument("--universe", choices=["bits", "tuples"], default="tuples")
    ap.add_argument("--reveal", type=int, default=8, help="# revealed objects")
    ap.add_argument("--max-terms", type=int, default=2, help="grammar size bound k")
    ap.add_argument("--seed", type=int, default=20260529, help="base trial seed")
    ap.add_argument("--model", default="claude-opus-4-8")
    args = ap.parse_args()

    trials, uni = build_trials(args.universe, args.n, args.reveal,
                               args.max_terms, args.seed)
    H = trials[0].H
    print(f"R12 demo | universe={uni.name} |U|={len(uni)} features={uni.features}")
    print(f"         | grammar max_terms={args.max_terms} -> |H|={len(H)} "
          f"distinct extensions | reveal={args.reveal} | trials={args.n}")

    if args.live:
        log: list = []
        emit = make_r12_opus_emitter(model=args.model, call_log=log)
        run(emit, trials, f"LIVE {args.model}")
        tin = sum(c.get("in", 0) for c in log)
        tout = sum(c.get("out", 0) for c in log)
        errs = [c for c in log if c.get("parse_error")]
        # Opus pricing (per the ph0 run_r8 convention): $5/Mtok in, $25/Mtok out
        est = tin * 5 / 1e6 + tout * 25 / 1e6
        print(f"\n[cost] calls={len(log)} in={tin} out={tout} "
              f"est=${est:.3f} api_errors={len(errs)}")
    else:
        # offline: run all three archetypes on the SAME trials so the grader's
        # discrimination (good >> overfit ~ naive) is visible end-to-end.
        for arch in ("good", "overfit", "naive"):
            run(make_mock_emitter(arch), trials, f"MOCK [{arch}]")
        print("\nRead: 'good' should show high conjecture-quality + high info-gain; "
              "'overfit' and 'naive' should collapse toward 0 conjecture-quality "
              "(baseline penalty), and 'naive's probe earns ~0 info-gain.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
