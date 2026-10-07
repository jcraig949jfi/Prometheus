"""Witness launch configs from the frozen preregistration (C-010-T013; PREREGISTRATION.md s2-s4, s7, s10).

Deterministic: given the two subject directories written by `run_witness subject` (genome.json +
subject_record.json), it generates the s3 seed lists with every registered exclusion (ares EVAL_SEEDS,
balanced_seeds_for, every GA episode seed of BOTH subject runs) and writes three launch configs:

  CONTROLS  POS / NULL / SHUF (on S4) for P-CAL, RECUR reported   -- one launch
  S4        S (P-RET), S-NOPL (P-CHAN, same seeds and order), S (P-OBS), S (P-ERASE), S-LEAK (P-ERASE), S (P-PRES)
  S15       the same six nodes for S15

No organism is run except world-side regime draws for seed balancing (oracle only); no count, accuracy or outcome
is computed. Usage:
  python -m rso.witness.make_configs --s4 DIR --s15 DIR --out DIR
"""
import argparse
import json
import os

from rso.witness import ares_client as AC
from rso.witness import run_witness as RW

N_WITNESS = 2048          # RULER.md s2: balanced, 1024 with r = 0 and 1024 with r = 1
SUBJECT_NODES = (("S", "P-RET", "witness"), ("S-NOPL", "P-CHAN", "witness"), ("S", "P-OBS", "witness"),
                 ("S", "P-ERASE", "erase"), ("S-LEAK", "P-ERASE", "erase"), ("S", "P-PRES", "pres"))
CONTROL_NODES = (("POS", "P-CAL"), ("NULL", "P-CAL"), ("SHUF", "P-CAL"), ("RECUR", "REPORT"))


def _canon(obj):
    return (json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=True) + "\n").encode("ascii")


def exclusions(subject_dirs, world_name=AC.WORLD):
    records = [os.path.join(d, "subject_record.json") for d in subject_dirs]
    return RW._excluded_seeds(world_name, records)


def seed_lists(excluded):
    ex = set(excluded)
    witness = AC._scan(AC.WITNESS_SEED_FLOOR, 2 ** 31 - 1, [i % 2 for i in range(N_WITNESS)], ex)
    erase = AC.erase_probe_set(exclude=ex)
    pres = AC.pres_seed_set(exclude=ex)
    return {"witness": witness, "erase": [s for t in erase for s in t], "pres": [s for p in pres for s in p]}


def build(s4_dir, s15_dir, out_dir):
    ex = exclusions([s4_dir, s15_dir])
    seeds = seed_lists(ex)
    os.makedirs(out_dir, exist_ok=True)
    rel = lambda d: os.path.relpath(os.path.join(d, "genome.json"), out_dir).replace(os.sep, "/")
    records = [os.path.relpath(os.path.join(d, "subject_record.json"), out_dir).replace(os.sep, "/") for d in (s4_dir, s15_dir)]
    files = {}

    def config(label, entries):
        cfg = {"schema": RW.CONFIG_SCHEMA, "label": label, "world": AC.WORLD, "exclude_seed_records": records,
               "entries": entries}
        name = "config_%s.json" % label
        RW._write(os.path.join(out_dir, name), _canon(cfg))
        files[label] = name

    config("CONTROLS", [{"subject": rel(s4_dir), "arm": a, "predicate": p, "seeds": seeds["witness"]} for a, p in CONTROL_NODES])
    for label, d in (("S4", s4_dir), ("S15", s15_dir)):
        config(label, [{"subject": rel(d), "arm": a, "predicate": p, "seeds": seeds[k]} for a, p, k in SUBJECT_NODES])
    summary = {"schema": "rso.witness.seed_lists.v0", "n_witness": len(seeds["witness"]),
               "witness_r1": sum(AC.regime_of(s) for s in seeds["witness"]), "erase_triples": len(seeds["erase"]) // 3,
               "pres_pairs": len(seeds["pres"]) // 2, "excluded_count": len(ex), "configs": files, "seeds": seeds}
    RW._write(os.path.join(out_dir, "SEED_LISTS.json"), _canon(summary))
    RW._write(os.path.join(out_dir, "WITNESS_SEEDS.json"), _canon(seeds["witness"]))   # evaluate.py --seeds (a plain list)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m rso.witness.make_configs")
    ap.add_argument("--s4", required=True)
    ap.add_argument("--s15", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    s = build(a.s4, a.s15, a.out)
    print(json.dumps({k: v for k, v in s.items() if k != "seeds"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
