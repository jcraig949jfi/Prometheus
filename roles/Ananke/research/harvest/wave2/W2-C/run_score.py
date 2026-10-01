"""Mutation-score driver (CPU only, 1 thread). Resumable: results are appended to out/results.jsonl.

    python run_score.py spec        # write out/mr_spec.json (expectations, hashed) -- BEFORE any run
    python run_score.py baseline    # baselines for every (stage, fixture)
    python run_score.py mutants [op ...]
    python run_score.py table       # out/score_table.md + out/score_summary.json
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pte_mut import env as _env  # noqa: E402,F401
from pte_mut import fixtures as F, operators as O, score as SC, stages as ST  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
STAGES_BY_FIXTURE = {
    "relay64": ("held", "controls", "plant", "lens_swap"),
    "hold64": ("held", "controls", "plant", "lens_swap"),
    "echo": ("held", "controls", "lens_swap"),
    "relay_dirgraph": ("held", "plant"),
    "xor_hp": ("held",),
    "flip_hp": ("held",),
    "c1_relay": ("held", "controls", "plant", "lens_swap"),
    "c1_maj": ("held",),
    "c1_hold": ("held", "plant"),
    "sel_random": ("held",),
}
FIXTURE_FN = {"relay64": F.relay64, "hold64": F.hold64, "echo": F.echo, "relay_dirgraph": F.random_dir,
              "xor_hp": F.xor_hp, "flip_hp": F.flip_hp, "c1_relay": F.c1_relay, "c1_maj": F.c1_maj,
              "c1_hold": F.c1_hold, "sel_random": F.sel_random}
_FX = {}


def fx(name):
    if name not in _FX:
        _FX[name] = FIXTURE_FN[name]()
    return _FX[name]


# Compute cut (decided from BASELINE COSTS only, before any mutant ran; brief cap 0.5 CPU core-hours):
# c1_relay controls (107 s) and lens_swap (77 s) dropped; c1_hold and flip_hp dropped from mutants;
# relay_dirgraph kept only where direction is the question; sel_random only for reuse_selection_seeds.
MUTANT_SKIP = {("controls", "c1_relay"), ("lens_swap", "c1_relay"), ("held", "c1_hold"), ("plant", "c1_hold"),
               ("plant", "c1_relay"), ("held", "flip_hp"), ("controls", "hold64")}
DIRGRAPH_OPS = {"reverse_edges", "randomize_source"}


def applicable(op, stage, fname):
    if (stage, fname) in MUTANT_SKIP:
        return False
    if fname == "relay_dirgraph" and op.name not in DIRGRAPH_OPS:
        return False
    if fname == "sel_random":
        return op.name == "reuse_selection_seeds" and stage == "held"
    if op.name == "reuse_selection_seeds" and stage != "held":
        return False
    return stage in op.stages and stage in STAGES_BY_FIXTURE[fname]


def load(path):
    out = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[r["key"]] = r
    return out


def append(path, rec):
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def so_from(rec):
    d = dict(rec["out"])
    return ST.StageOut(**{k: d.get(k) for k in ("stage", "fixture", "verdict", "numeric", "alarms",
                                                   "fingerprints", "error")})


def cmd_spec():
    fixtures = {n: fx(n) for n in STAGES_BY_FIXTURE}
    sp = SC.spec_table(O.catalogue(), STAGES_BY_FIXTURE, fixtures)
    sp["fixtures"] = {n: f.describe() for n, f in fixtures.items()}
    sp["written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    p = OUT / "mr_spec.json"
    if p.exists():
        old = json.loads(p.read_text())
        assert old["sha256"] == sp["sha256"], "spec changed after it was written; refusing to overwrite"
        print("spec unchanged", sp["sha256"])
        return
    p.write_text(json.dumps(sp, indent=1, default=str))
    print("wrote", p, sp["sha256"], len(sp["table"]), "cells")


def run_one(path, key, stage, fname, op):
    t0, c0 = time.time(), time.process_time()
    if stage == "oracle":
        reg_out = ST.StageOut("oracle", "conformance", {}, {}, [], [])
        ctx = op.active() if op else None
        if ctx:
            with ctx:
                reg_out = ST.oracle(None, op)
        else:
            reg_out = ST.oracle(None, None)
        so = reg_out
    else:
        so = ST.run_stage(stage, fx(fname), op)
    rec = {"key": key, "stage": stage, "fixture": fname, "op": op.name if op else None,
           "cpu_s": round(time.process_time() - c0, 2), "wall_s": round(time.time() - t0, 2),
           "out": so.to_dict()}
    if so.raw is not None and stage in ("held", "controls", "plant"):
        rec["raw"] = json.loads(json.dumps(so.raw, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    append(path, rec)
    print(f"{key:55s} cpu {rec['cpu_s']:6.1f}s  verdict {json.dumps(so.verdict)[:110]}  alarms {so.alarms[:4]}",
          flush=True)
    return rec


def cmd_baseline():
    path = OUT / "baseline.jsonl"
    have = load(path)
    for fname, sts in STAGES_BY_FIXTURE.items():
        for st in sts:
            key = f"BASE|{st}|{fname}"
            if key not in have:
                run_one(path, key, st, fname, None)
    if "BASE|oracle|conformance" not in have:
        run_one(path, "BASE|oracle|conformance", "oracle", None, None)


def cmd_mutants(names):
    path = OUT / "results.jsonl"
    have = load(path)
    cat = O.catalogue()
    for name in (names or list(cat)):
        op = cat[name]
        for fname in STAGES_BY_FIXTURE:
            for st in ("held", "controls", "plant", "lens_swap"):
                if applicable(op, st, fname):
                    key = f"{name}|{st}|{fname}"
                    if key not in have:
                        run_one(path, key, st, fname, op)
        if op.layer == "engine" and "oracle" in op.stages:
            key = f"{name}|oracle|conformance"
            if key not in have:
                run_one(path, key, "oracle", None, op)


def report_for(recs_by_fixture):
    """Report stage: report.build over the rows of every fixture's held/controls/plant outputs."""
    outs = []
    for rec in recs_by_fixture:
        so = so_from(rec)
        so.raw = rec.get("raw")
        outs.append(so)
    return ST.report_stage(outs, "all")


def cmd_table():
    spec = json.loads((OUT / "mr_spec.json").read_text())
    base = load(OUT / "baseline.jsonl")
    res = load(OUT / "results.jsonl")
    cat = O.catalogue()
    cells = {}
    for key, r in res.items():
        op, st, fname = key.split("|")
        b = base.get(f"BASE|{st}|{fname}")
        if b is None:
            continue
        e = spec["table"].get(key, "unknown")
        c = SC.classify(so_from(b), so_from(r), e)
        c["cpu_s"] = r["cpu_s"]
        c["error"] = r["out"].get("error")
        cells[key] = c
    # report stage per operator, from rows (no new simulation)
    brep = report_for([r for k, r in base.items() if k.split("|")[1] in ("held", "controls", "plant")
                       and k.split("|")[2] != "sel_random"])
    for name, op in cat.items():
        if "report" not in op.stages:
            continue
        recs = []
        for k, r in base.items():
            _, st, fname = k.split("|")
            if st in ("held", "controls", "plant") and fname != "sel_random":
                mk = f"{name}|{st}|{fname}"
                recs.append(res.get(mk, r))      # unmutated stage outputs where the op was not applicable
        mrep = report_for(recs)
        cells[f"{name}|report|all"] = SC.classify(brep, mrep, "change")
    (OUT / "score_cells.json").write_text(json.dumps(cells, indent=1, default=str))
    write_table(cells, cat)


def write_table(cells, cat):
    cols = [("held", f) for f in STAGES_BY_FIXTURE if "held" in STAGES_BY_FIXTURE[f]]
    cols += [("controls", f) for f in STAGES_BY_FIXTURE if "controls" in STAGES_BY_FIXTURE[f]]
    cols += [("plant", f) for f in STAGES_BY_FIXTURE if "plant" in STAGES_BY_FIXTURE[f]]
    cols += [("lens_swap", f) for f in STAGES_BY_FIXTURE if "lens_swap" in STAGES_BY_FIXTURE[f]]
    cols += [("report", "all"), ("oracle", "conformance")]
    ab = {"KILLED(A)": "K-A", "KILLED(D)": "K-D", "EQUIVALENT": "EQ", "SURVIVED": "SURV", "UNRESOLVED": "UNR",
          "FRAGILE": "FRAG"}
    lines = ["| operator | " + " | ".join(f"{s}:{f}" for s, f in cols) + " |",
             "|---|" + "---|" * len(cols)]
    tot = {}
    for name in cat:
        row = []
        for s, f in cols:
            c = cells.get(f"{name}|{s}|{f}")
            if c is None:
                row.append(".")
                continue
            row.append(ab[c["category"]])
            tot.setdefault(s, {}).setdefault(c["category"], 0)
            tot[s][c["category"]] += 1
        lines.append(f"| {name} | " + " | ".join(row) + " |")
    md = "\n".join(lines) + "\n"
    (OUT / "score_table.md").write_text(md, encoding="utf-8")
    allc = {}
    for c in cells.values():
        allc[c["category"]] = allc.get(c["category"], 0) + 1
    summ = {"per_stage": tot, "all": allc,
            "cpu_s_total_mutants": round(sum(c.get("cpu_s") or 0 for c in cells.values()), 1)}
    (OUT / "score_summary.json").write_text(json.dumps(summ, indent=1))
    print(md)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "spec":
        cmd_spec()
    elif cmd == "baseline":
        cmd_baseline()
    elif cmd == "mutants":
        cmd_mutants(sys.argv[2:])
    elif cmd == "table":
        cmd_table()
    else:
        raise SystemExit(__doc__)
