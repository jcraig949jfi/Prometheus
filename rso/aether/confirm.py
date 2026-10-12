"""C-018-T030 confirmatory design, completeness wrapper and (guarded) runner / analyser. NO confirmatory run in this packet.

    python -m rso.aether.confirm design [--write]              the sealed DESIGN manifest (digests PENDING), from the
                                                               preregistered plan below; --write commits it to manifests/
    python -m rso.aether.confirm run <shard> --cleared-by REF  refused (exit 2) without --cleared-by or on a FROZEN mismatch
    python -m rso.aether.confirm analyse                       verify() FIRST (rso/completeness), then evaluate; exit 0 / 3 / 4

Completeness (directive Gen-4 s2A; rso/completeness/README.md): before the run there are no artifact bytes, so the frozen
object is a DESIGN manifest: every shard id, its seed partition and per-law execution count, the source hashes, digests
PENDING. At analysis the presented shards fill the digests (`fill`) and rso.completeness.verify runs on the filled manifest
with the shard writer's own rows digest (native_digest = manifest.digest) so a row edited after writing is ALTERED; missing,
duplicate, conflicting, foreign, seed-partition, count and source findings are verify()'s own. The DESIGN manifest's sha256 is
pinned in FROZEN.json, so a smaller re-sealed design is REFUSED. After the run the filled manifest is committed and pinned too
(then SUBSTITUTED becomes detectable for later re-verification). There is no early-stop rule: early_stop = null.
"""
import glob
import json
import os
import sys

from rso.aether import adapter as A
from rso.completeness import manifest as M, verify as V
from rso.registry.registry import ROOT, file_sha

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT = "C-018-T030 Aether native ancestry-vs-content v1.0.0"
ARMS = ("RX", "V1")                     # RX primary; V1 the shallow-tree comparison
N_CONFIRM = {"RX": 48, "V1": 16}        # sized from measured throughput (PREREGISTRATION s5)
SHARD = {"RX": 12, "V1": 8}             # seeds per shard
K0 = 0x1000                             # confirmatory seed index k = K0 + i; development k in adapter.DEV_K
DESIGN_PATH = os.path.join(HERE, "manifests", "confirm_design.manifest.json")
RUNS = os.path.join(HERE, "runs", "CONFIRM")
PINNED_DESIGN_SHA256 = None             # set at freeze (FROZEN.json carries it too)
SOURCES = ["rso/aether/adapter.py", "rso/aether/evaluate.py", "rso/aether/confirm.py", "rso/aether/demand/fixtures.py",
           "rso/completeness/manifest.py", "rso/completeness/verify.py",
           "Aether/V2B/PROP01/prop01_run.py", "Aether/V2B/PROP01/prop01_tree.py", "Aether/V2B/REACH01/R1/r1_test4.py",
           "Aether/V2B/REACH01/R1/r1_reduce.py", "Aether/test/reference/gpu_aeth01.py", "Aether/observatory/aeth01_run.py",
           "Aether/observatory/aeth01_observatory.py"]
REPLAY = "first seed of every shard"     # native replay sample (bit-exact arrays_sha256), PREREGISTRATION s6


def seeds(law):
    return [K0 + i for i in range(N_CONFIRM[law])]


def shard_plan():
    out = {}
    for law in ARMS:
        ks = seeds(law)
        for i in range(0, len(ks), SHARD[law]):
            out["%s.%d" % (law, i // SHARD[law])] = (law, ks[i:i + SHARD[law]])
    return out


def current_sources(paths=SOURCES):
    return {p: file_sha(p, ROOT) for p in paths if os.path.exists(os.path.join(ROOT, p))}


def design_manifest(sources=None):
    specs = [{"id": sid, "seeds": ks, "arm_counts": {law: len(ks)}, "rows": len(ks), "rows_sha256": "PENDING",
              "meta_sha256": "PENDING"} for sid, (law, ks) in shard_plan().items()]
    return M.build(EXPERIMENT, arms=list(ARMS), shards=specs, sources=current_sources() if sources is None else sources,
                   row_key_fields=["law"], seed_field="seed", early_stop=None)


def make_shard(sid, rows):
    return {"id": sid, "rows": rows, "meta": {"shard": sid, "experiment": EXPERIMENT, "rows": len(rows),
                                             "rows_sha256": M.digest(rows)}}


def fill(design, presented):
    first = {}
    for sh in presented:
        first.setdefault(sh["id"], sh)
    specs = [dict(s, rows_sha256=M.digest(first[s["id"]]["rows"]), meta_sha256=M.digest(first[s["id"]]["meta"]))
             if s["id"] in first else s for s in design["shards"]]
    return M.seal(dict(design, shards=specs))


def verify_presented(design, presented, sources, pinned_design_sha256=None):
    if not M.is_sealed(design) or (pinned_design_sha256 is not None and design["manifest_sha256"] != pinned_design_sha256):
        return V.Result(V.REFUSED, [], [{"kind": V.MANIFEST_ALTERED, "shard": None,
                                         "detail": "design manifest is not sealed or is not the pinned one"}])
    return V.verify(fill(design, presented), presented, sources=sources, native_digest=M.digest)


def _shard_file(sid):
    return os.path.join(RUNS, sid + ".shard.json")


def run(sid):
    law, ks = shard_plan()[sid]
    d = os.path.join(RUNS, sid)
    os.makedirs(d, exist_ok=True)
    rows = []
    for k in ks:
        meta, arrays = A.native_unit(law, k)
        meta = A.save_unit(A.unit_path(d, meta), meta, arrays)
        rows.append({"law": law, "seed": k, "arrays_sha256": meta["arrays_sha256"], "meta_sha256": M.digest(meta)})
        print(sid, law, k, meta["B"], meta["N"], file=sys.stderr, flush=True)
    with open(_shard_file(sid), "w", encoding="utf-8", newline="\n") as f:
        json.dump(make_shard(sid, rows), f, sort_keys=True, indent=1)


def load_presented():
    out = []
    for p in sorted(glob.glob(os.path.join(RUNS, "*.shard.json"))):
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def analyse():
    from rso.aether import evaluate as E
    with open(DESIGN_PATH, encoding="utf-8") as f:
        design = json.load(f)
    presented = load_presented()
    res = verify_presented(design, presented, current_sources(list(design["sources"])), PINNED_DESIGN_SHA256)
    out = {"experiment": EXPERIMENT, "completeness": res.to_dict()}
    if not res.licenses_verdict:
        print(json.dumps(out, indent=1))
        return 3 if res.status == V.INCOMPLETE else 4
    with open(os.path.join(HERE, "qual", "QUALIFICATION.json"), encoding="utf-8") as f:
        qualified = json.load(f)["qualified"]
    laws, problems = {}, []
    for sh in presented:
        law = sh["rows"][0]["law"]
        for i, row in enumerate(sh["rows"]):
            meta, arrays = A.load_unit(os.path.join(RUNS, sh["id"], "native_%s_%s" % (law, row["seed"])))
            if meta["arrays_sha256"] != row["arrays_sha256"] or M.digest(meta) != row["meta_sha256"]:
                problems.append("%s seed %s: unit files differ from the shard row" % (sh["id"], row["seed"]))
            r = E.evaluate_unit(meta, arrays)
            problems += ["%s seed %s: %s" % (sh["id"], row["seed"], p) for p in r["problems"]]
            if i == 0:                                    # preregistered replay sample
                m2, a2 = A.native_unit(law, row["seed"])
                if A.arrays_sha256(a2) != meta["arrays_sha256"]:
                    problems.append("%s seed %s: native replay differs" % (sh["id"], row["seed"]))
            laws.setdefault(law, []).append((r, (row["seed"], arrays["H"], arrays["D"])))
    out["problems"], out["laws"] = problems, {}
    for law, items in laws.items():
        rows, feats = [x[0] for x in items], [x[1] for x in items]
        L = E.law_summary(rows, E.decode(feats), E.decode(feats, null=True))
        out["laws"][law] = dict(L, disposition=E.disposition({"completeness": res.status, "records_ok": not problems,
                                                               "qualified": qualified, "law": L}))
    print(json.dumps(out, indent=1, default=str))
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd == "design":
        m = design_manifest()
        if "--write" in argv:
            os.makedirs(os.path.dirname(DESIGN_PATH), exist_ok=True)
            with open(DESIGN_PATH, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(m, indent=1, sort_keys=True) + "\n")
        print(m["manifest_sha256"])
        return 0
    if cmd == "run":
        if "--cleared-by" not in argv or len(argv) < 2:
            print("REFUSED: a confirmatory run needs --cleared-by <coordinator release> (no confirmatory run in C-018-T030)")
            return 2
        from rso.aether import freeze
        bad = freeze.mismatches()
        if bad or PINNED_DESIGN_SHA256 is None or design_manifest()["manifest_sha256"] != PINNED_DESIGN_SHA256:
            print("REFUSED: FROZEN mismatch or design not pinned: %s" % (bad or "design"))
            return 2
        run(argv[1])
        return 0
    if cmd == "analyse":
        return analyse()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
