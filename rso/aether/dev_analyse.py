"""C-018-T041 development end-to-end check of the v1.1.0 analyser (confirm.analyse) on DEVELOPMENT units only (adapter.DEV_K;
never a confirmatory seed). The real freeze check, Aether's real warm-snapshot recomputation and real native replay run; only
the design (a dev design in the frozen shape: shards of dev seeds) and RUNS point at a scratch directory.

    python -B -m rso.aether.dev_analyse <scratch> [--forged] [--shards RX.dev0,V1.dev0]   -> prints JSON
                                                                     (committed in qual/DEV_ANALYSE_v1_1_0.json)

--shards: analyse a subset of the dev shards as a design of its own (s10.6 adds a ~17 s Aether tree replay per unit, so the
20-unit set no longer fits one 600 s foreground call on harry1; the subsets are each COMPLETE designs).

--forged: the same set with dev RX k=9's unit replaced by a copy of k=8 relabelled 9 (meta seed rewritten, rows re-digested:
Pallas's B5 shape); the replay sample is stubbed to the stored units there (the copy is not a shard's first row) so the run
shows what the duplicate refusal and the per-unit snapshot binding catch on their own.
"""
import json
import os
import shutil
import sys

from rso.aether import adapter as A, confirm as C
from rso.completeness import manifest as M

HERE = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(HERE, "qual", "records")
PLAN = [("RX.dev0", "RX", list(range(0, 8))), ("RX.dev1", "RX", list(range(8, 16))), ("V1.dev0", "V1", list(range(0, 4)))]


def build(out, forged=False, plan=PLAN):
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    specs = []
    for sid, law, ks in plan:
        os.makedirs(os.path.join(out, sid))
        rows = []
        for k in ks:
            assert k in A.DEV_K
            src = k - 1 if forged and law == "RX" and k == 9 else k
            meta, arrays = A.load_unit(os.path.join(REC, "native_%s_%d" % (law, src)))
            meta = A.save_unit(os.path.join(out, sid, "native_%s_%d" % (law, k)), dict(meta, seed=k), arrays)
            rows.append({"law": law, "seed": k, "arrays_sha256": meta["arrays_sha256"], "meta_sha256": M.digest(meta)})
        with open(os.path.join(out, sid + ".shard.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(C.make_shard(sid, rows), f, sort_keys=True, indent=1)
        specs.append({"id": sid, "seeds": ks, "arm_counts": {law: len(ks)}, "rows": len(ks), "rows_sha256": "PENDING",
                      "meta_sha256": "PENDING"})
    design = M.build("C-018-T041 DEV end-to-end (dev seeds, frozen shape)", arms=list(C.ARMS), shards=specs,
                     sources=C.current_sources(), row_key_fields=["law"], seed_field="seed", early_stop=None)
    p = os.path.join(out, "design.manifest.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(design, indent=1, sort_keys=True) + "\n")
    return p, design["manifest_sha256"]


def main(scratch, forged, shards=None):
    plan = [p for p in PLAN if shards is None or p[0] in shards]
    out = os.path.join(scratch, ("dev_e2e_forged" if forged else "dev_e2e") + ("_" + "_".join(shards) if shards else ""))
    dp, pin = build(out, forged, plan)
    got = []
    kw = {"replay": lambda law, k: A.load_unit(os.path.join(out, "%s.dev%d" % (law, (k // 8) if law == "RX" else 0),
                                                            "native_%s_%d" % (law, k)))} if forged else {}
    rc = C.analyse(runs=out, design_path=dp, pin=pin, emit=got.append, **kw)
    res = dict(got[0], rc=rc, forged=forged, replay_stubbed=forged, shards=[p[0] for p in plan])
    for L in res.get("laws", {}).values():
        L["rows"] = [{k: r[k] for k in ("seed", "cls", "removed_B", "removed_N", "r_int", "ftick_B", "ftick_N", "n_targets",
                                        "problems")} for r in L["rows"]]
    print(json.dumps(res, indent=1, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sh = sys.argv[sys.argv.index("--shards") + 1].split(",") if "--shards" in sys.argv else None
    sys.exit(main(sys.argv[1], "--forged" in sys.argv, sh))
