"""E-BEL-REPL-01 PILOT (declared feasibility only; no event scored, no verdict): the state-freedom profile of BEE's own
spontaneous-origin corpus (grounding round 2026-09-23: first self-replicator tape of every spontaneous run, with that run's
config), restricted to SHARED-layout single-execution reproduction (ENDOGENOUS_COPY / ENDOGENOUS_PARTIAL / OVERWRITE /
CONSTRUCTIVE). It answers ONE question: does BEE's origin corpus contain ZERO_DEPENDENT founders at all?
    python pilot_founders.py <grounding workdir> <out.json>
"""
import collections, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import state_free as SF  # noqa: E402
from prometheus.z80atlas.world import Config  # noqa: E402

SINGLE = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE")


def main(wd, out):
    wd = pathlib.Path(wd)
    rows = [json.loads(l) for l in open(wd / "results.jsonl", encoding="utf-8")]
    seen = {}; per = []
    for r in rows:
        if not r.get("spontaneous"):
            continue
        cfg_d = json.loads((wd / "runs" / r["id"] / "config.json").read_text(encoding="utf-8"))["config"]
        if cfg_d["reproduction"] not in SINGLE or cfg_d["layout"] != "SHARED":
            continue
        cfg = Config(**{k: (tuple(v) if k == "init_tapes" else v) for k, v in cfg_d.items()})
        tape = bytes.fromhex(r["first_self_replication"]["tape"])
        key = (tape, cfg.representation, cfg.reproduction, cfg.physics, cfg.budget, cfg.ldir, cfg.undefined_op)
        if key not in seen:
            seen[key] = SF.profile(tape, cfg)
        per.append({"id": r["id"], "lane": r["lane"], "cell": r["cell"], "seed": r["seed"], "reproduction": cfg.reproduction,
                    "representation": cfg.representation, "tape": tape.hex(), "profile": seen[key]})
    cls = collections.Counter(p["profile"]["class"] for p in per)
    by_seed = {}
    for p in sorted(per, key=lambda p: p["id"]):
        by_seed.setdefault(p["seed"], p)
    cls_seed = collections.Counter(p["profile"]["class"] for p in by_seed.values())
    res = {"about": "E-BEL-REPL-01 pilot (feasibility only)", "R1": list(SF.R1), "R2": list(SF.R2), "origins": len(per),
           "distinct_tapes_x_physics": len(seen), "class_counts_all_origins": dict(cls), "class_counts_one_per_seed": dict(cls_seed),
           "by_cell": {c: dict(collections.Counter(p["profile"]["class"] for p in per if p["lane"] + ":" + p["cell"] == c))
                       for c in sorted({p["lane"] + ":" + p["cell"] for p in per})},
           "rows": per}
    pathlib.Path(out).write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "by_cell")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
