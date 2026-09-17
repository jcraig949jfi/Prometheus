"""The cross-domain QD ledger (round 2): one row per evaluated mechanism cell.

File: primordial/ledger/qd/cells.jsonl (append-only; written through
RowWriter so rows commit on write). Row schema:

  cell        {representation, world, pressure, substrate, channel}   descriptor
  mechanism   short machine name of what was evaluated
  fitness     {held64_median, iqr, n_runs, ...}   higher is better
  footprint   {genome_bytes, params?}             smaller is better (contract clause A)
  oracle      which oracles ran and their outcome ("clean" or the failure)
  baseline    true for round 1 seed rows
  source      exp_id and commit of the receipt/rows that produced the numbers
  cohort      B / C / D / E / round1
  status      record / dev / aborted / timeout / cheat / control

Contract clause A (Minimum Viable Abstraction), round 2 binding
(roles/Nestor/sidequests/graphworld/SWARM_R2.md s2): on the same world and
pressure, with oracles clean and >= 8 run seeds, a candidate PASSES if
  parity:  median >= best_baseline_median - 0.5 * that baseline's IQR
  and      genome_bytes < that baseline's genome_bytes,
or if median > best_baseline_median + 0.5 * IQR at genome_bytes <= its bytes.
`check` applies that rule against the current Pareto front.

    python -m primordial.ops.qd_ledger seed-round1        # once; computes bytes from code
    python -m primordial.ops.qd_ledger top [--world w4] [--pressure P] [--n 10]
    python -m primordial.ops.qd_ledger pareto --world w4 [--pressure P]
    python -m primordial.ops.qd_ledger check --world w4 --pressure P --median M --iqr Q --bytes B --runs N
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CELLS = ROOT / "primordial" / "ledger" / "qd" / "cells.jsonl"
E_LEDGER = ROOT / "primordial" / "ledger" / "E.jsonl"


def load(path=CELLS) -> list[dict]:
    p = pathlib.Path(path)
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def _receipts() -> dict:
    out = {}
    for line in E_LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            for k in ("science", "engineering"):
                if isinstance(d.get(k), str):
                    d[k] = json.loads(d[k])
            out[d["exp_id"]] = d
    return out


def seed_rows() -> list[dict]:
    """Round 1 MAP-Elites baseline cells, numbers read from the committed E receipts,
    genome bytes computed from the genome code (never quoted)."""
    from primordial.qd import e4_run as E4
    from primordial.qd import e7_run as E7

    rc = _receipts()
    rows = []
    worlds = ("1", "3", "4")

    def glen(gs, fam):
        return E7.G7(int(gs), fam).glen

    def row(world, rep, pressure, substrate, mech, fitness, nbytes, src, oracle):
        return {"cell": {"representation": rep, "world": f"w{world}", "pressure": pressure,
                         "substrate": substrate, "channel": "none"},
                "mechanism": mech, "fitness": fitness, "footprint": {"genome_bytes": int(nbytes)},
                "oracle": oracle, "baseline": True, "cohort": "round1", "status": "record",
                "source": {"exp_id": src, "git": rc[src].get("git"), "rows": rc[src].get("rows")}}

    e9 = rc["E9-family-ranking-fused-8-seeds"]["science"]
    for w in worlds:
        for fam in ("linear", "tt_feat", "tt_digits"):
            rows.append(row(w, fam, "train8_held64", "numba_fused", f"closed_loop_{fam}_codebook",
                            {"held64_median": e9["median"][w][fam], "iqr": e9["iqr"][w][fam],
                             "n_runs": len(e9["held64_by_run_seed"][w][fam])},
                            glen(w, fam), "E9-family-ranking-fused-8-seeds",
                            "wforge trace hash + brain ref logits clean (E9)"))
    e7b = rc["E7b-c4-families-repeat-seeds"]["science"]
    for w in worlds:
        runs = sorted(e7b["held64_runs_sorted"][w]["lut_top"])
        rows.append(row(w, "lut_top", "train8_held64", "numpy", "closed_loop_lut_top_codebook",
                        {"held64_median": runs[len(runs) // 2], "iqr": None, "n_runs": len(runs)},
                        glen(w, "lut_top"), "E7b-c4-families-repeat-seeds", "clean (E7b)"))
    e10 = rc["E10-linear-closed-vs-open-128-seeds"]["science"]["primary"]
    for w in worlds:
        p = e10[w]
        rows.append(row(w, "linear", "train128_held64", "numba_fused", "closed_loop_linear_codebook",
                        {"held64_median": p["closed_median"], "iqr": None, "n_runs": len(p["closed_linear"])},
                        glen(w, "linear"), "E10-linear-closed-vs-open-128-seeds", "clean (E10)"))
        rows.append(row(w, "open_loop_actions", "train128_held64", "numba", "open_loop_action_tensor",
                        {"held64_median": p["open_median"], "iqr": None, "n_runs": len(p["open"])},
                        E4.Spec(int(w)).glen, "E10-linear-closed-vs-open-128-seeds", "clean (E10)"))
    e8 = rc["E8-fused-closed-loop-seed-scaling"]["science"]["closed_held64_median"]
    for w in worlds:
        rows.append(row(w, "tt_digits", "train128_held64", "numba_fused", "closed_loop_tt_digits_codebook",
                        {"held64_median": e8[w]["128"], "iqr": None, "n_runs": 2},
                        glen(w, "tt_digits"), "E8-fused-closed-loop-seed-scaling", "clean (E8)"))
    return rows


def _match(r, world=None, pressure=None):
    return (world is None or r["cell"]["world"] == world) and (pressure is None or r["cell"]["pressure"] == pressure)


def top(rows, world=None, pressure=None, n=10):
    xs = [r for r in rows if _match(r, world, pressure) and r["status"] == "record"
          and r["fitness"].get("held64_median") is not None]
    return sorted(xs, key=lambda r: -r["fitness"]["held64_median"])[:n]


def pareto(rows, world, pressure=None):
    """Non-dominated on (held64_median high, genome_bytes low)."""
    xs = top(rows, world, pressure, n=10**9)
    front = []
    for r in sorted(xs, key=lambda r: (r["footprint"]["genome_bytes"], -r["fitness"]["held64_median"])):
        if not front or r["fitness"]["held64_median"] > front[-1]["fitness"]["held64_median"]:
            front.append(r)
    return front


def floor_of(rows, world, pressure):
    """M1: the highest trivial-policy floor row (floor=<kind>, status control) for (world, pressure), or None."""
    fs = [r for r in rows if r.get("floor") and r["status"] == "control" and _match(r, world, pressure)
          and r["fitness"].get("held64_median") is not None]
    return max(fs, key=lambda r: r["fitness"]["held64_median"]) if fs else None


def check(rows, world, pressure, median, iqr, nbytes, runs, oracle_clean=True, held=None, doc=None,
          readout=None, runs_total=None, rng_family_count=None, runs_per_family=None, n_per_family=None) -> dict:
    """The round 2/3 verdict (raw + floor) with the round 4 judge attached as `clause_a_r4` (H ask
    1789435262391-0: one judge, read by F12). doc: a worlds_r4 document; None reads the committed file.
    readout: the candidate's readout name (primordial.metric.readout); None = LEGACY top-16.
    runs_total / rng_family_count / runs_per_family / n_per_family: the candidate's sample (G-R5-2 CANDIDATE_N)."""
    out = _check_r2(rows, world, pressure, median, iqr, nbytes, runs, oracle_clean, held)
    out["clause_a_r4"] = clause_a_r4_block(check_r4(world, pressure, median, nbytes, runs, oracle_clean=oracle_clean,
                                                    held=held, doc=doc, readout=readout, runs_total=runs_total,
                                                    rng_family_count=rng_family_count,
                                                    runs_per_family=runs_per_family, n_per_family=n_per_family))
    return out


def clause_a_r4_block(r4: dict) -> dict:
    """check_r4's result in F12's block: screen SURVIVED|HELD|CULLED|NOT_REACHED|UNSCREENED."""
    if r4.get("why") in ("UNSCREENED", "CULLED", "HELD", "PENDING"):
        screen = "NOT_REACHED" if r4.get("cull_reason") == "NOT_REACHED" else r4["why"]
    else:
        screen = "SURVIVED"
    return {"verdict": r4["verdict"], "why": r4.get("why"), "progress": r4.get("progress"), "readout": r4.get("readout"),
            "progress_ci": r4.get("progress_ci95"), "floor": r4.get("floor"), "baseline_median": r4.get("baseline_median"),
            "baseline_bytes": r4.get("baseline_bytes"), "variant": r4.get("variant"), "screen": screen}


def _check_r2(rows, world, pressure, median, iqr, nbytes, runs, oracle_clean=True, held=None) -> dict:
    """Clause A verdict (raw) plus the M1 floor reading: `floor` = the verdict read against the
    trivial-policy floor. No new threshold: BELOW_FLOOR if the candidate's lower bound <= floor;
    NO_HEADROOM if every baseline on the front is <= floor (parity with it means nothing); else the raw
    verdict, with normalized = (median - floor) / (baseline - floor) per front baseline.
    M3: pass `held` (the candidate's per-run-seed held64 values) and the band is the bootstrap 95% CI of
    the median (primordial.metric.ci) instead of +-0.5 IQR; the verdict names which band it used."""
    raw = _check_raw(rows, world, pressure, median, iqr, nbytes, runs, oracle_clean, held)
    f = floor_of(rows, world, pressure)
    if f is None:
        raw["floor"] = {"verdict": "NO_FLOOR"}
        return raw
    fv = f["fitness"]["held64_median"]
    base = pareto([r for r in rows if r.get("baseline")], world, pressure)
    norm = {b["mechanism"]: (round((median - fv) / (b["fitness"]["held64_median"] - fv), 4)
                             if b["fitness"]["held64_median"] > fv else None) for b in base}
    lo = raw["band"][0] if "band" in raw else median - 0.5 * (iqr or 0.0)
    if raw["verdict"] in ("INELIGIBLE", "NO_BASELINE"):
        v = raw["verdict"]
    elif lo <= fv:
        v = "BELOW_FLOOR"
    elif base and all(b["fitness"]["held64_median"] <= fv for b in base):
        v = "NO_HEADROOM"
    else:
        v = raw["verdict"]
    raw["floor"] = {"verdict": v, "floor_held64": fv, "floor_kind": f["floor"], "normalized": norm}
    return raw


PROGRESS_PASS = 0.95
BASELINE_MIN_RUNS = 32          # operator 16 (SWARM_R4 s9): >= 32 run seeds pooled across
BASELINE_MIN_FAMILIES = 4       # >= 4 RNG families; else INELIGIBLE(BASELINE_N)
BASELINE_MIN_PER_FAMILY = 8     # >= 8 run seeds in EVERY family (no 29+1+1+1 concentration, D-R4-2)


def check_r4(world, pressure, median, nbytes, runs, oracle_clean=True, cheat_failed=True, held=None,
             doc=None, readout=None, runs_total=None, rng_family_count=None, runs_per_family=None,
             n_per_family=None) -> dict:
    """Clause A, round 4 binding (SWARM_R4 s4), read against primordial/ledger/qd/worlds_r4.json.

    The cell must be SURVIVED under the file's active variant (else INELIGIBLE UNSCREENED / CULLED / HELD,
    looked up, never recomputed). floor = that variant's floor; baseline = the cell's M2 baseline.
      progress = (median - floor) / (baseline median - floor)          (> 0 denominator by the screen)
      PASS iff progress >= 0.95 AND bytes < baseline bytes; BELOW_FLOOR iff progress < 0; else FAIL.
    `held` (per-run-seed values) adds the bootstrap CI of the median mapped through the same formula:
    reported, not judged.
    Operator 15 R15-1: the candidate's readout (None = readout.LEGACY) must equal the cell baseline's readout
    (absent = LEGACY), else INELIGIBLE READOUT_MISMATCH -- one reader on both sides of the fraction.
    Operator 16: the cell baseline must pool >= BASELINE_MIN_RUNS run seeds over >= BASELINE_MIN_FAMILIES distinct
    RNG families with >= BASELINE_MIN_PER_FAMILY run seeds in every family (baseline.n_runs, baseline.families,
    baseline.n_per_family -- G's worlds_r4/v2 names; absent families or n_per_family = refused), else
    INELIGIBLE BASELINE_N.
    Operator 19 O4 (SWARM_R5 s1, G-R5-2): the CANDIDATE must meet the same three-field sample rule -- runs_total >= 32,
    rng_family_count >= 4, runs_per_family >= 8 (every family when n_per_family is given) -- else INELIGIBLE
    CANDIDATE_N. `runs` is the legacy positional run count and stands for runs_total when runs_total is not given; a
    caller that gives no rng_family_count is refused. Campaign stage never changes this (operator 19 s3).
    Order: screen guard -> BASELINE_N -> CANDIDATE_N -> READOUT_MISMATCH -> oracles / cheats -> progress."""
    from primordial.metric import readout as RO
    from primordial.metric import worlds as WR
    doc = WR.load() if doc is None else doc
    base = {"rules": "r4", "world": world, "pressure": pressure}
    g = WR.guard(doc, world, pressure)
    if g is not None:
        c = WR.lookup(doc, world, pressure)
        if c is not None:
            base.update(floor=c["verdicts"][g["variant"]].get("floor"),
                        baseline_median=(c["baseline"] or {}).get("median"),
                        baseline_bytes=(c["baseline"] or {}).get("bytes"))
        return {**base, **g}
    c = WR.lookup(doc, world, pressure)
    from primordial.metric import screen as SC
    k = SC.vkey(doc["q1_floor_policy"], doc["q2_policy"])
    cb = c["baseline"] or {}
    fams, npf = cb.get("families"), cb.get("n_per_family")
    if (int(cb.get("n_runs") or 0) < BASELINE_MIN_RUNS or len(set(fams or ())) < BASELINE_MIN_FAMILIES
            or not npf or min(int(v) for v in npf.values()) < BASELINE_MIN_PER_FAMILY):
        return {**base, "verdict": "INELIGIBLE", "why": "BASELINE_N", "baseline_n_runs": cb.get("n_runs"),
                "baseline_families": fams, "baseline_n_per_family": npf, "need_runs": BASELINE_MIN_RUNS,
                "need_families": BASELINE_MIN_FAMILIES, "need_per_family": BASELINE_MIN_PER_FAMILY,
                "variant": k, "floor": c["verdicts"][k]["floor"], "baseline_median": cb.get("median"),
                "baseline_bytes": cb.get("bytes")}
    from primordial.metric import sample as SM
    cand = {"runs_total": runs if runs_total is None else runs_total, "rng_family_count": rng_family_count,
            "runs_per_family": runs_per_family, "n_per_family": n_per_family}
    if not SM.meets(cand):
        return {**base, "verdict": "INELIGIBLE", "why": "CANDIDATE_N", **SM.refusal(cand, "candidate"),
                "variant": k, "floor": c["verdicts"][k]["floor"], "baseline_median": cb.get("median"),
                "baseline_bytes": cb.get("bytes")}
    base.update(readout=readout or RO.LEGACY, baseline_readout=cb.get("readout", RO.LEGACY))
    if base["readout"] != base["baseline_readout"]:
        return {**base, "verdict": "INELIGIBLE", "why": "READOUT_MISMATCH", "variant": k,
                "floor": c["verdicts"][k]["floor"], "baseline_median": c["baseline"]["median"],
                "baseline_bytes": c["baseline"]["bytes"]}
    if not oracle_clean:
        return {**base, "verdict": "INELIGIBLE", "why": "oracles not clean"}
    if not cheat_failed:
        return {**base, "verdict": "INELIGIBLE", "why": "a cheat control did not fail"}
    fv, bm, bb = c["verdicts"][k]["floor"], c["baseline"]["median"], c["baseline"]["bytes"]
    if not bm > fv:
        raise ValueError(f"screen defect: {world} {pressure} SURVIVED with baseline median {bm} <= floor {fv}")
    prog = (median - fv) / (bm - fv)
    out = {**base, "variant": k, "floor": fv, "baseline_median": bm, "baseline_bytes": bb, "median": median,
           "bytes": nbytes, "progress": prog, "pass_at": PROGRESS_PASS}
    if held is not None:
        from primordial.metric.ci import median_ci
        lo, hi = median_ci(held)
        out["candidate_ci95"] = [lo, hi]
        out["progress_ci95"] = [(lo - fv) / (bm - fv), (hi - fv) / (bm - fv)]
    if prog < 0:
        out["verdict"] = "BELOW_FLOOR"
    elif prog >= PROGRESS_PASS and nbytes < bb:
        out["verdict"] = "PASS"
    else:
        out["verdict"] = "FAIL"
        out["why"] = "progress < 0.95" if prog < PROGRESS_PASS else "bytes not below the baseline's"
    return out


def _check_raw(rows, world, pressure, median, iqr, nbytes, runs, oracle_clean=True, held=None) -> dict:
    """Clause A verdict of a candidate against the baseline Pareto front for (world, pressure)."""
    if not oracle_clean:
        return {"verdict": "INELIGIBLE", "why": "oracles not clean"}
    if runs < 8:
        return {"verdict": "INELIGIBLE", "why": f"{runs} run seeds < 8"}
    # front over BASELINE rows only: a front over all rows lets an appended candidate that
    # dominates a baseline evict it, flipping that candidate's own PASS to FAIL (lane B ask, 2026-09-14)
    base = pareto([r for r in rows if r.get("baseline")], world, pressure)
    if not base:
        return {"verdict": "NO_BASELINE", "why": f"no baseline cell for {world} {pressure}"}
    if held is not None:
        from primordial.metric.ci import median_ci
        band = list(median_ci(held))
        ext = {"band_rule": "bootstrap_ci95", "band": band}
    else:
        ext = {"band_rule": "iqr"}
    for b in base:
        bm, bi, bb = b["fitness"]["held64_median"], b["fitness"].get("iqr") or 0.0, b["footprint"]["genome_bytes"]
        parity = band[1] >= bm if held is not None else median >= bm - 0.5 * bi
        better = band[0] > bm if held is not None else median > bm + 0.5 * bi
        if parity and nbytes < bb:
            return {"verdict": "PASS", "rule": "parity at fewer bytes", "vs": b["mechanism"], "vs_median": bm,
                    "vs_bytes": bb, **ext}
        if better and nbytes <= bb:
            return {"verdict": "PASS", "rule": "better at <= bytes", "vs": b["mechanism"], "vs_median": bm,
                    "vs_bytes": bb, **ext}
    return {"verdict": "FAIL", "front": [(b["mechanism"], b["fitness"]["held64_median"],
                                          b["footprint"]["genome_bytes"]) for b in base], **ext}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed-round1")
    t = sub.add_parser("top"); t.add_argument("--world"); t.add_argument("--pressure"); t.add_argument("--n", type=int, default=10)
    p = sub.add_parser("pareto"); p.add_argument("--world", required=True); p.add_argument("--pressure")
    c = sub.add_parser("check", help="clause A; round 4 (default) reads worlds_r4.json, --rules r2 the old front")
    for k in ("world", "pressure"):
        c.add_argument(f"--{k}", required=True)
    for k in ("median", "bytes"):
        c.add_argument(f"--{k}", type=float, required=True)
    c.add_argument("--iqr", type=float, default=0.0, help="r2 only")
    c.add_argument("--runs", type=int, required=True, help="the candidate's runs_total")
    c.add_argument("--rng-family-count", type=int, help="the candidate's rng_family_count (G-R5-2 CANDIDATE_N)")
    c.add_argument("--runs-per-family", type=int, help="the candidate's runs_per_family (G-R5-2 CANDIDATE_N)")
    c.add_argument("--screen", choices=("file", "r16"), default="file",
                   help="r16: judge against eligibility.r16_doc() (complete R16 cells only, e.g. w13 train128)")
    c.add_argument("--held", help="comma-separated per-run-seed held64 values -> bootstrap CI band (M3)")
    c.add_argument("--rules", choices=("r4", "r2"), default="r4")
    c.add_argument("--oracle-unclean", action="store_true")
    c.add_argument("--cheat-did-not-fail", action="store_true")
    c.add_argument("--worlds", help="worlds_r4.json path (default primordial/ledger/qd/worlds_r4.json)")
    c.add_argument("--readout", help="candidate readout name (primordial.metric.readout; default the legacy top-16)")
    cb = sub.add_parser("check-b", help="clause B (S1, builder H): graft vs both cheats per run seed, Holm")
    cb.add_argument("--rows", nargs="+", required=True, help="transfer harness rows (E-T1b protocol)")
    cb.add_argument("--alpha", type=float, default=0.05)
    a = ap.parse_args(argv)
    if a.cmd == "check-b":
        from primordial.score import transfer_b
        print(json.dumps(transfer_b.check_b(transfer_b.load_rows(a.rows), a.alpha), indent=1, default=str))
        return 0
    if a.cmd == "seed-round1":
        if any(r.get("baseline") for r in load()):
            print("round 1 baseline already seeded")
            return 0
        from primordial.fabric.rows import RowWriter
        with RowWriter(CELLS, "QD-ledger-round1-baseline", commit_every_s=10**9) as w:
            for r in seed_rows():
                w.write(r)
        print(f"seeded {len(load())} rows into {CELLS.relative_to(ROOT).as_posix()}")
        return 0
    rows = load()
    if a.cmd == "top":
        for r in top(rows, a.world, a.pressure, a.n):
            c_ = r["cell"]
            print(f"{c_['world']} {c_['pressure']:16s} {c_['representation']:18s} median {r['fitness']['held64_median']:8.2f} "
                  f"bytes {r['footprint']['genome_bytes']:6d} runs {r['fitness'].get('n_runs')} [{r['source']['exp_id']}]")
    elif a.cmd == "pareto":
        for r in pareto(rows, a.world, a.pressure):
            print(f"{r['cell']['pressure']:16s} {r['mechanism']:32s} median {r['fitness']['held64_median']:8.2f} "
                  f"bytes {r['footprint']['genome_bytes']:6d}")
    elif a.cmd == "check":
        held = [float(x) for x in a.held.split(",")] if a.held else None
        if a.rules == "r4":
            from primordial.metric import worlds as WR
            if a.screen == "r16":
                from primordial.metric import eligibility as EL
                doc = EL.r16_doc()
            else:
                doc = WR.load(a.worlds) if a.worlds else WR.load()
            out = check_r4(a.world, a.pressure, a.median, int(a.bytes), a.runs, oracle_clean=not a.oracle_unclean,
                           cheat_failed=not a.cheat_did_not_fail, held=held, doc=doc, readout=a.readout,
                           runs_total=a.runs, rng_family_count=a.rng_family_count, runs_per_family=a.runs_per_family)
        else:
            out = check(rows, a.world, a.pressure, a.median, a.iqr, int(a.bytes), a.runs,
                        oracle_clean=not a.oracle_unclean, held=held)
        print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
