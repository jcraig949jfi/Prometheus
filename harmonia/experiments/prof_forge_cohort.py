"""PROF-FORGE-COHORT — first-light ladder profiling of Hephaestus forged tools.

Phase A: importability + determinism + timing over a stratified sample of
agents/hephaestus/humanreadable/*/tool.py (P26 flagged both as asserted-not-measured).
Phase B: answer-selection battery (R0 from reasoning_phase0 + R4a/b/c from
reasoning_r4) via the MC adapter: probe -> prompt text + candidate set
[truth, surface_answer?, distractors], tool picks argmax evaluate() score.

Per-tool profile row -> harmonia/experiments/prof_forge_cohort_results.jsonl.

Pre-stated readings (also in worklog P27, committed before the run):
  A-import : IMPORT-CLEAN >=95% | IMPORT-DEGRADED 80-95% | IMPORT-BROKEN <80%
  A-det    : DET-CLEAN >=90% identical repeat | DET-MIXED 50-90% | DET-BROKEN <50%
  B        : ADAPTER-FLOOR (VACUOUS, pre-committed): median acc ~ chance (0.25)
             AND surface-pick ~ chance across tools -> battery says nothing about
             tool differences; do not interpret per-tool numbers.
             TOOLS-DISCRIMINATE: acc IQR >= 0.15 or structured surface-trap spread.
             TOOLS-FLAT: uniform above-chance.

Process-isolated (one child per tool, 90s cap) so a hanging tool cannot kill the
sweep. Windows spawn-safe: worker does its own imports.
"""
from __future__ import annotations
import json
import pathlib
import random
import sys
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutTimeout

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOLS_DIR = ROOT / "agents/hephaestus/humanreadable"
OUT = pathlib.Path(__file__).parent / "prof_forge_cohort_results.jsonl"
SEED = 20260820
SAMPLE_N = 48
PER_TOOL_TIMEOUT = 90
N_R0 = 8          # probes drawn from gen_R0 output
N_R4_EACH = 4     # per R4 family


def build_battery():
    """Deterministic battery: list of (probe_id, tier, version, prompt, candidates, truth, surface)."""
    sys.path.insert(0, str(ROOT / "harmonia/experiments"))
    import sympy as sp
    from reasoning_phase0 import gen_R0
    from reasoning_r4 import gen_R4a, gen_R4b, gen_R4c

    rng = random.Random(SEED)
    battery = []

    def mc(truth_str, surface_str, perturb):
        cands = [truth_str]
        if surface_str is not None and surface_str != truth_str:
            cands.append(surface_str)
        while len(cands) < 4:
            d = perturb(len(cands))
            if d not in cands:
                cands.append(d)
        random.Random(SEED + len(battery)).shuffle(cands)
        return cands

    for p in gen_R0(rng)[: N_R0]:
        expr = p.data["expr"]
        var = p.data.get("var")
        vname = str(var) if var is not None else "x"
        truth = sp.nsimplify(p.ground_truth)
        ts = str(truth)
        prompt = f"Solve for {vname}: {sp.sstr(expr)} = 0. Give {vname} exactly."
        cands = mc(ts, None, lambda i: str(sp.nsimplify(truth + i)))
        battery.append(("R0-%d" % len(battery), "R0", p.version, prompt, cands, ts, None))

    for gen, fam in ((gen_R4a, "R4a"), (gen_R4b, "R4b"), (gen_R4c, "R4c")):
        for p in gen(random.Random(SEED))[: N_R4_EACH]:
            truth = str(p.ground_truth)
            surface = p.data.get("surface_answer")
            prompt = p.data["prompt"]

            def perturb(i, t=truth):
                try:
                    return str(int(t) + i * 3)
                except ValueError:
                    return t + str(i)
            cands = mc(truth, surface, perturb)
            battery.append((f"{fam}-%d" % len(battery), "R4", p.version, prompt,
                            cands, truth, surface))
    return battery


def profile_tool(args):
    """Child process: import one tool, determinism check, run battery."""
    tool_dir, battery = args
    import importlib.util
    import time
    row = {"tool": pathlib.Path(tool_dir).name}
    t0 = time.time()
    try:
        spec = importlib.util.spec_from_file_location("forged_tool", str(pathlib.Path(tool_dir) / "tool.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        tool = mod.ReasoningTool()
    except BaseException as e:  # noqa: BLE001 — arbitrary generated code
        row.update(importable=False, error=f"{type(e).__name__}: {e}"[:200])
        return row
    row["importable"] = True
    row["import_s"] = round(time.time() - t0, 3)

    def pick(prompt, cands):
        res = tool.evaluate(prompt, list(cands))
        if not isinstance(res, list) or not res:
            raise ValueError(f"evaluate returned {type(res).__name__}")
        scored = []
        for i, r in enumerate(res):
            if isinstance(r, dict):
                s = r.get("score", r.get("confidence", 0.0))
                c = r.get("candidate", r.get("answer", cands[i] if i < len(cands) else None))
            else:
                s, c = float(r), cands[i] if i < len(cands) else None
            scored.append((float(s), c))
        return max(scored, key=lambda t: t[0])[1], [round(s, 6) for s, _ in scored]

    # determinism: same call twice, compare full score vectors
    try:
        pid, tier, ver, prompt, cands, truth, surface = battery[0]
        _, s1 = pick(prompt, cands)
        _, s2 = pick(prompt, cands)
        row["deterministic"] = (s1 == s2)
    except BaseException as e:  # noqa: BLE001
        row.update(deterministic=None, det_error=f"{type(e).__name__}: {e}"[:200])

    n_ok = n_correct = n_surface = n_err = 0
    per_tier = {}
    t1 = time.time()
    for pid, tier, ver, prompt, cands, truth, surface in battery:
        try:
            choice, _ = pick(prompt, cands)
            n_ok += 1
            d = per_tier.setdefault(f"{tier}/{ver}", {"n": 0, "correct": 0, "surface": 0})
            d["n"] += 1
            if choice == truth:
                n_correct += 1
                d["correct"] += 1
            elif surface is not None and choice == surface:
                n_surface += 1
                d["surface"] += 1
        except BaseException as e:  # noqa: BLE001
            n_err += 1
            row.setdefault("eval_errors", []).append(f"{pid}: {type(e).__name__}"[:80])
    row.update(n_probes=len(battery), n_scored=n_ok, n_correct=n_correct,
               n_surface_picks=n_surface, n_eval_errors=n_err,
               acc=round(n_correct / n_ok, 4) if n_ok else None,
               surface_rate=round(n_surface / n_ok, 4) if n_ok else None,
               battery_s=round(time.time() - t1, 2), per_tier=per_tier)
    return row


def build_battery_v2():
    """Adapter v2 (P28): distractors EXCHANGEABLE with truth — drawn from the same
    generator family/version's own truth pool at matched string length (the
    control-selection doctrine applied to MC design; v1's truth+3i construction
    let surface-feature scorers separate truth from distractors).

    Candidate sets: [truth, d_truthlike x2] (+ [surface, d_surfacelike] when the
    probe carries a surface answer, giving 5 candidates; else 4). d_surfacelike is
    a pool value length-matched to the SURFACE answer, so surface-capture can be
    separated from plain length preference (v1 weakness #4).
    """
    sys.path.insert(0, str(ROOT / "harmonia/experiments"))
    import sympy as sp
    from reasoning_phase0 import gen_R0
    from reasoning_r4 import gen_R4a, gen_R4b, gen_R4c

    def pool_for(gen, n_seeds=6):
        vals = {}
        for k in range(1, n_seeds + 1):
            for p in gen(random.Random(SEED + k)):
                s = p.data.get("surface_answer")
                vals.setdefault(p.version, []).append((str(p.ground_truth), str(s) if s else None))
        return vals

    def near_len(pool_strs, target, taken, k):
        cands = sorted((abs(len(v) - len(target)), v) for v in pool_strs
                       if v not in taken and v != target)
        return [v for _, v in cands[:k]]

    battery = []

    r0_pool = {}
    rng = random.Random(SEED)
    r0_probes = gen_R0(rng)[: N_R0]
    for k in range(1, 7):
        for p in gen_R0(random.Random(SEED + k)):
            r0_pool.setdefault(p.version, []).append(str(sp.nsimplify(p.ground_truth)))
    for p in r0_probes:
        expr = p.data["expr"]
        vname = str(p.data.get("var") or "x")
        ts_ = str(sp.nsimplify(p.ground_truth))
        prompt = f"Solve for {vname}: {sp.sstr(expr)} = 0. Give {vname} exactly."
        cands = [ts_] + near_len(r0_pool.get(p.version, []), ts_, {ts_}, 3)
        random.Random(SEED + 1000 + len(battery)).shuffle(cands)
        battery.append(("R0v2-%d" % len(battery), "R0", p.version, prompt, cands, ts_, None, None))

    for gen, fam in ((gen_R4a, "R4a"), (gen_R4b, "R4b"), (gen_R4c, "R4c")):
        pool = pool_for(gen)
        for p in gen(random.Random(SEED))[: N_R4_EACH]:
            truth = str(p.ground_truth)
            surface = p.data.get("surface_answer")
            surface = str(surface) if surface else None
            truths = [t for t, _ in pool.get(p.version, [])]
            surfaces = [s for _, s in pool.get(p.version, []) if s]
            taken = {truth, surface} if surface else {truth}
            cands = [truth] + near_len(truths, truth, taken, 2)
            d_surfacelike = None
            if surface:
                cands.append(surface)
                sl = near_len(surfaces or truths, surface, taken | set(cands), 1)
                if sl:
                    d_surfacelike = sl[0]
                    cands.append(d_surfacelike)
            random.Random(SEED + 1000 + len(battery)).shuffle(cands)
            battery.append((f"{fam}v2-%d" % len(battery), "R4", p.version, p.data["prompt"],
                            cands, truth, surface, d_surfacelike))
    return battery


def profile_tool_v2(args):
    """Child: like profile_tool but records surface-like distractor picks too."""
    tool_dir, battery = args
    import importlib.util
    import time
    row = {"tool": pathlib.Path(tool_dir).name}
    try:
        spec = importlib.util.spec_from_file_location("forged_tool", str(pathlib.Path(tool_dir) / "tool.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        tool = mod.ReasoningTool()
    except BaseException as e:  # noqa: BLE001
        row.update(importable=False, error=f"{type(e).__name__}: {e}"[:200])
        return row
    row["importable"] = True

    def pick(prompt, cands):
        res = tool.evaluate(prompt, list(cands))
        scored = []
        for i, r in enumerate(res):
            if isinstance(r, dict):
                s = r.get("score", r.get("confidence", 0.0))
                c = r.get("candidate", r.get("answer", cands[i] if i < len(cands) else None))
            else:
                s, c = float(r), cands[i] if i < len(cands) else None
            scored.append((float(s), c))
        return max(scored, key=lambda t: t[0])[1]

    n_ok = n_correct = n_surface = n_surfacelike = n_err = 0
    per_tier = {}
    t1 = time.time()
    for pid, tier, ver, prompt, cands, truth, surface, d_surfacelike in battery:
        try:
            choice = pick(prompt, cands)
            n_ok += 1
            d = per_tier.setdefault(f"{tier}/{ver}", {"n": 0, "correct": 0, "surface": 0, "surfacelike": 0})
            d["n"] += 1
            if choice == truth:
                n_correct += 1
                d["correct"] += 1
            elif surface is not None and choice == surface:
                n_surface += 1
                d["surface"] += 1
            elif d_surfacelike is not None and choice == d_surfacelike:
                n_surfacelike += 1
                d["surfacelike"] += 1
        except BaseException:  # noqa: BLE001
            n_err += 1
    row.update(n_probes=len(battery), n_scored=n_ok, n_correct=n_correct,
               n_surface_picks=n_surface, n_surfacelike_picks=n_surfacelike,
               n_eval_errors=n_err,
               acc=round(n_correct / n_ok, 4) if n_ok else None,
               surface_rate=round(n_surface / n_ok, 4) if n_ok else None,
               surfacelike_rate=round(n_surfacelike / n_ok, 4) if n_ok else None,
               battery_s=round(time.time() - t1, 2), per_tier=per_tier)
    return row


def main():
    v2 = "--v2" in sys.argv
    dirs = sorted(d for d in TOOLS_DIR.iterdir() if d.is_dir() and (d / "tool.py").exists())
    step = max(1, len(dirs) // SAMPLE_N)
    sample = dirs[::step][:SAMPLE_N]
    print(f"{len(dirs)} tool dirs; stratified sample {len(sample)} (every {step}th, sorted)")
    if v2:
        battery = build_battery_v2()
        out = pathlib.Path(__file__).parent / "prof_forge_cohort_results_v2.jsonl"
        worker = profile_tool_v2
        print(f"battery v2: {len(battery)} probes, exchangeable distractors + surface-like controls")
        rows = []
        with ProcessPoolExecutor(max_workers=6) as ex:
            futs = {ex.submit(worker, (str(d), battery)): d for d in sample}
            for fut, d in futs.items():
                try:
                    rows.append(fut.result(timeout=PER_TOOL_TIMEOUT))
                except FutTimeout:
                    rows.append({"tool": d.name, "importable": None, "error": "TIMEOUT>90s"})
                except BaseException as e:  # noqa: BLE001
                    rows.append({"tool": d.name, "importable": None, "error": f"POOL:{type(e).__name__}"[:120]})
        out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
        imp = [r for r in rows if r.get("importable")]
        accs = sorted(r["acc"] for r in imp if r.get("acc") is not None)
        surf = [r.get("surface_rate") or 0 for r in imp]
        slk = [r.get("surfacelike_rate") or 0 for r in imp]

        def q(v, p):
            return v[int(p * (len(v) - 1))] if v else None
        print(f"import {len(imp)}/{len(rows)}")
        if accs:
            print(f"acc median {q(accs,0.5)} IQR [{q(accs,0.25)},{q(accs,0.75)}] min {accs[0]} max {accs[-1]}")
            print(f"surface-rate mean {sum(surf)/len(surf):.3f} | surfacelike-rate mean {sum(slk)/len(slk):.3f}")
        print(f"rows -> {out}")
        return
    battery = build_battery()
    print(f"battery: {len(battery)} probes (R0 x {N_R0}, R4a/b/c x {N_R4_EACH})")

    rows = []
    with ProcessPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(profile_tool, (str(d), battery)): d for d in sample}
        for fut, d in futs.items():
            try:
                rows.append(fut.result(timeout=PER_TOOL_TIMEOUT))
            except FutTimeout:
                rows.append({"tool": d.name, "importable": None, "error": "TIMEOUT>90s"})
            except BaseException as e:  # noqa: BLE001
                rows.append({"tool": d.name, "importable": None, "error": f"POOL:{type(e).__name__}"[:120]})

    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

    imp = [r for r in rows if r.get("importable")]
    det = [r for r in imp if r.get("deterministic") is True]
    accs = sorted(r["acc"] for r in imp if r.get("acc") is not None)
    surf = sorted(r["surface_rate"] for r in imp if r.get("surface_rate") is not None)

    def q(v, p):
        return v[int(p * (len(v) - 1))] if v else None
    print(f"import: {len(imp)}/{len(rows)} | deterministic: {len(det)}/{len(imp)}")
    if accs:
        print(f"acc median {q(accs,0.5)} IQR [{q(accs,0.25)},{q(accs,0.75)}] min {accs[0]} max {accs[-1]}")
        print(f"surface-rate median {q(surf,0.5)} max {surf[-1] if surf else None}")
    print(f"rows -> {OUT}")


if __name__ == "__main__":
    main()
