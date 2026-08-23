"""Emission probe — the measurement a scarce lane can actually settle.

RESTORED 2026-08-23. Power analysis (iteration 7) showed a paired 10-point accuracy
difference needs ~28 universes, and 2 universes give a +/-29 point confidence
interval on a mean. Accuracy is therefore unaffordable on a rate-limited lane and
any small accuracy run would be theatre.

Emission is not. The Build 1 finding was that the model emitted a well-formed
`claims` field and left it EMPTY in every turn; forcing changed that to 29/29
(Fisher p = 3.8e-09). Emission needs no evaluation calls, and every turn is scored
independently, so a lane dying partway leaves each completed turn valid.

OUTSTANDING MEASUREMENT THIS EXISTS TO TAKE: the claim truth-rate is 4/37 = 10.8%
against a 3.7% random baseline, one-sided p = 0.047 — and ONE claim reclassified
flips it (3/37 -> p = 0.156). About 61 claims settles it at p < 0.01, roughly 48
forced turns. That is one working lane window.

Claim CONTENT is persisted, not just counts: iteration 9 needed the claim texts for
a relevance analysis and only the raw transcripts made it possible.

  python emission.py --seeds 12 --turns 4 --conditions C1N
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import prompts
from arms import LLMArm, parse_claims
from config import ArmConfig
from lanes import LANES, probe as lane_probe
from reasoner import FrozenModel, ModelConfig, extract_json
from substrate import normalize
from universe import EvalSet, Session, Universe, UniverseSpec

HERE = Path(__file__).resolve().parent


def one_cell(seed: int, condition: str, args, out: Path, sink: List, lock) -> None:
    uni = Universe(UniverseSpec(seed=seed))
    ev = EvalSet(uni)
    cfg = ArmConfig(budget_per_round=args.budget, turns=args.turns)
    model = FrozenModel(
        ModelConfig(model=args.model, endpoint=args.endpoint,
                    key_env=args.key_env, max_tokens=args.max_tokens,
                    timeout=args.timeout, retries=2),
        transcript_path=out / f"transcript_seed{seed}_{condition}.jsonl")
    arm = LLMArm("P2", uni, ev, model, cfg, seed, condition=condition)
    session = Session(uni, args.budget)

    for _ in range(args.warmup):
        tag, word = next(arm.stream)
        ok, _ = session.try_run(tag, word, source="policy")
        if ok:
            arm.absorb(session.log[-1])

    for turn in range(1, args.turns + 1):
        ctx = "\n\n".join(x for x in (arm.persistent_block(),
                                      arm.round_block(session)) if x)
        cands = arm.candidates() if condition == "C3" else ()
        user = prompts.explore_user("P2", uni, session.remaining, turn,
                                    args.turns, cfg.runs_per_turn_p2, ctx,
                                    condition, cands)
        t0 = time.time()
        txt = model.call(arm.system, user, tag=f"P2|{condition}|s{seed}|t{turn}")
        if not txt:
            rec = {"seed": seed, "condition": condition, "turn": turn,
                   "ok": False, "why": "call failed"}
        else:
            obj = extract_json(txt) or {}
            raw = obj.get("claims")
            raw = raw if isinstance(raw, list) else []
            parsed = parse_claims(obj, uni, arm.store, 99)
            rules_now = list(arm.store.rules.values())
            claims = []
            for lhs, rhs, _ in parsed:
                trivial = (normalize(lhs, rules_now)[0]
                           == normalize(rhs, rules_now)[0])
                # ground truth is used ONLY for scoring, never shown to the model
                true = uni.true_word_element(lhs) == uni.true_word_element(rhs)
                claims.append({"lhs": " ".join(lhs), "rhs": " ".join(rhs),
                               "trivial": trivial, "true": true})
            rec = {"seed": seed, "condition": condition, "turn": turn,
                   "ok": True, "json_parsed": bool(obj),
                   "claims_emitted": len(raw),
                   "claims_wellformed": len(parsed),
                   "claims_trivial": sum(c["trivial"] for c in claims),
                   "claims_novel": sum(not c["trivial"] for c in claims),
                   "claims_true": sum(c["true"] for c in claims),
                   "claims": claims,            # CONTENT, not just counts
                   "runs_emitted": len(obj.get("runs") or []),
                   "latency_s": round(time.time() - t0, 1)}
        with lock:
            sink.append(rec)
            with (out / "emission.jsonl").open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
            flag = "" if rec.get("ok") else "  CALL FAILED"
            print(f"  s{seed} {condition:<4} t{turn}  "
                  f"emitted={rec.get('claims_emitted','-'):>2} "
                  f"novel={rec.get('claims_novel','-'):>2} "
                  f"true={rec.get('claims_true','-'):>2}{flag}", flush=True)
        for _ in range(args.probes_between):
            tag, word = next(arm.stream)
            ok, _ = session.try_run(tag, word, source="policy")
            if ok:
                arm.absorb(session.log[-1])


def summarise(sink: List[Dict]) -> None:
    from collections import defaultdict
    import math
    by = defaultdict(list)
    for r in sink:
        if r.get("ok"):
            by[r["condition"]].append(r)
    print(f"\n  {'cond':<5}{'turns':>7}{'w/claim':>9}{'claims':>8}{'novel':>7}{'true':>6}")
    tot_n = tot_t = 0
    for c in sorted(by):
        v = by[c]
        tw = sum(1 for r in v if r["claims_emitted"] > 0)
        nv = sum(r["claims_novel"] for r in v)
        tr = sum(r["claims_true"] for r in v)
        if c != "C0":
            tot_n += nv
            tot_t += tr
        print(f"  {c:<5}{len(v):>7}{f'{tw}/{len(v)}':>9}"
              f"{sum(r['claims_emitted'] for r in v):>8}{nv:>7}{tr:>6}")
    if tot_n:
        p0 = 0.037
        pv = sum(math.comb(tot_n, i) * p0**i * (1 - p0)**(tot_n - i)
                 for i in range(tot_t, tot_n + 1))
        print(f"\n  forced-condition truth rate {tot_t}/{tot_n} = {tot_t/tot_n:.3f} "
              f"vs baseline {p0}")
        print(f"  one-sided binomial p = {pv:.4f}"
              f"   (prior run: 4/37 = 0.108, p = 0.047, FRAGILE)")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=12)
    p.add_argument("--turns", type=int, default=4)
    p.add_argument("--conditions", default="C1N")
    p.add_argument("--budget", type=int, default=200)
    p.add_argument("--warmup", type=int, default=24)
    p.add_argument("--probes-between", type=int, default=12)
    p.add_argument("--lane", default="openrouter")
    p.add_argument("--model", default="meta-llama/llama-3.3-70b-instruct")
    p.add_argument("--max-tokens", type=int, default=700)
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--min-tps", type=float, default=1.2)
    p.add_argument("--out", default="runs/emission_next")
    args = p.parse_args()
    spec = LANES[args.lane]
    args.endpoint, args.key_env = spec["url"], spec["key"]
    args.model = args.model or spec["model"]

    r = lane_probe(args.lane, spec, timeout=args.timeout, min_tps=args.min_tps)
    if not r["up"]:
        raise SystemExit(f"preflight failed: {r['why']}")
    print(f"preflight ok: {args.lane} {r['tok_per_s']} tok/s {r['elapsed']}s")

    out = HERE / args.out
    out.mkdir(parents=True, exist_ok=True)
    conds = [c.strip() for c in args.conditions.split(",") if c.strip()]
    cells = [(s, c) for s in range(1, args.seeds + 1) for c in conds]
    (out / "manifest.json").write_text(json.dumps({
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "args": vars(args), "preflight": r,
        "calls_planned": len(cells) * args.turns}, indent=2), encoding="utf-8")
    print(f"{len(cells)} cells x {args.turns} turns = {len(cells)*args.turns} calls")

    sink: List[Dict] = []
    lock = threading.Lock()
    it, it_lock = iter(cells), threading.Lock()

    def worker():
        while True:
            with it_lock:
                try:
                    seed, cond = next(it)
                except StopIteration:
                    return
            try:
                one_cell(seed, cond, args, out, sink, lock)
            except Exception as exc:                      # noqa: BLE001
                print(f"  cell s{seed} {cond} died: {type(exc).__name__} {exc}")

    ts = [threading.Thread(target=worker) for _ in range(args.threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    summarise(sink)
    print(f"\n{len(sink)} turns -> {out/'emission.jsonl'}")


if __name__ == "__main__":
    main()
