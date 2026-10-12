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
v1.1.0 (C-018-T041, Pallas B6 / B5 / B1 / P1): `analyse` runs the freeze check FIRST and refuses on any mismatch; refuses a
duplicated arrays_sha256 across rows; binds EVERY unit to its seed (warm snapshot + origin recomputed) and states how many
units were snapshot-bound and fully replayed; compares the replayed tree / B / N / origin as well as the arrays; and a
refused analysis prints its problems and nothing verdict-bearing.
s10.6 (Argus[harry1-d48cbcfd], before the re-freeze): Aether's attributed tree is replayed for EVERY unit (B1).
"""
import glob
import json
import os
import sys

import numpy as np

from rso.aether import adapter as A
from rso.completeness import manifest as M, verify as V
from rso.registry.registry import ROOT, file_sha

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT = "C-018 Aether native ancestry-vs-content v1.1.0 (C-018-T030; repair round C-018-T041)"
ARMS = ("RX", "V1")                     # RX primary; V1 the shallow-tree comparison
N_CONFIRM = {"RX": 48, "V1": 16}        # sized from measured throughput (PREREGISTRATION s5)
SHARD = {"RX": 12, "V1": 8}             # seeds per shard
K0 = 0x2000                             # confirmatory seed index k = K0 + i; development k in adapter.DEV_K
BURNED = range(0x1000, 0x1100)          # INCIDENT 2026-10-12 (PREREGISTRATION s5): 0x1000..0x1003 executed by mistake, deleted
                                        # unread; the whole block is burned and never used as confirmatory
RELEASE_PATH = os.path.join(HERE, "RELEASE.json")   # written by the coordinator ONLY after the Q3 challenge (directive s9)
DESIGN_PATH = os.path.join(HERE, "manifests", "confirm_design.manifest.json")
RUNS = os.path.join(HERE, "runs", "CONFIRM")
SOURCES = ["rso/aether/adapter.py", "rso/aether/evaluate.py", "rso/aether/confirm.py", "rso/aether/demand/fixtures.py",
           "rso/completeness/manifest.py", "rso/completeness/verify.py",
           "Aether/V2B/PROP01/prop01_run.py", "Aether/V2B/PROP01/prop01_tree.py", "Aether/V2B/REACH01/R1/r1_test4.py",
           "Aether/V2B/REACH01/R1/r1_reduce.py", "Aether/test/reference/gpu_aeth01.py", "Aether/observatory/aeth01_run.py",
           "Aether/observatory/aeth01_observatory.py"]
REPLAY = ("first seed of every shard: full native replay (arrays_sha256 and meta tree / B / N / origin); every unit: warm "
          "snapshot + origin recomputed, and Aether's tree replayed (s10.6)")      # PREREGISTRATION s6, s10 (B1, B5)
REPLAY_META = ("tree", "B", "N", "origin", "B_tick")


def pinned_design_sha256():
    """The DESIGN manifest sha256 frozen in FROZEN.json (kept out of this file: this file is one of the manifest's sources)."""
    from rso.aether import freeze
    return freeze.load()["design_manifest_sha256"] if os.path.exists(freeze.PATH) else None


def release_problem(ref):
    """A flag is not a release: the coordinator commits RELEASE.json {released_by, release_ref, design_manifest_sha256} after
    the challenge, and the run needs `--cleared-by <release_ref>` to match it and the frozen design."""
    if not os.path.exists(RELEASE_PATH):
        return "no RELEASE.json (the coordinator writes it after the Q3 challenge)"
    with open(RELEASE_PATH, encoding="utf-8") as f:
        rel = json.load(f)
    if not rel.get("released_by") or rel.get("release_ref") != ref:
        return "RELEASE.json does not name release_ref %r" % ref
    if rel.get("design_manifest_sha256") != pinned_design_sha256():
        return "RELEASE.json releases a different design manifest"
    return None


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


def load_presented(runs=None):
    out = []
    for p in sorted(glob.glob(os.path.join(runs or RUNS, "*.shard.json"))):
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def snapshot_problem(law, k, meta, arrays, snapshot=None):
    """v1.1.0 (B5): bind a unit to its seed by recomputing Aether's warm snapshot and origin for (law, k) (~1/10 of a
    unit): the stored t0 CONTROL state, the origin and Aether's warm digest must all be the seed's. None if bound."""
    s, _, O = (snapshot or A.warm_snapshot)(law, k, meta["n"], meta["warm"])
    if not (np.array_equal(np.stack(s), arrays["snap"]) and O == meta["origin"]
            and A.P.digest(s) == meta["aether"]["warm_digest"]):
        return "warm snapshot / origin is not seed %s's" % k
    return None


def tree_problem(law, k, meta, tree_replay=None):
    """v1.1.0 s10.6 (B1, invariant-respecting form): re-run Aether's run_unit for (law, k) (~1/4 of a unit); its attributed
    tree, origin and warm digest must equal the unit's meta. B and N are then the rules' outputs on a replayed tree
    (tree_check recomputes both). None if equal."""
    u = (tree_replay or A.aether_unit)(law, k, meta["n"], meta["warm"], meta["H"])
    if not (u["tree"] == meta["tree"] and u["origin"] == meta["origin"]
            and u["warm_digest"] == meta["aether"]["warm_digest"]):
        return "replayed Aether tree / origin is not the unit's"
    return None


def _emit(out):
    print(json.dumps(out, indent=1, default=str))


def analyse(runs=None, design_path=None, pin=None, replay=None, snapshot=None, freeze_check=None, emit=_emit,
            tree_replay=None):
    """PREREGISTRATION s6 / s10. The keyword arguments exist for the guard tests (a two-shard fixture, stubbed replay);
    the CLI passes none, so the frozen paths, the FROZEN.json pin, Aether's replay and the freeze check are used."""
    from rso.aether import evaluate as E, freeze
    runs, design_path = runs or RUNS, design_path or DESIGN_PATH
    replay = replay or A.native_unit
    bad = (freeze_check or freeze.mismatches)()       # B6: the analyser runs the freeze check itself, first
    if bad:
        emit({"experiment": EXPERIMENT, "disposition": "REFUSED_FREEZE_MISMATCH", "problems": bad})
        return 4
    with open(design_path, encoding="utf-8") as f:
        design = json.load(f)
    presented = load_presented(runs)
    res = verify_presented(design, presented, current_sources(list(design["sources"])),
                           pinned_design_sha256() if pin is None else pin)
    out = {"experiment": EXPERIMENT, "completeness": res.to_dict()}
    if not res.licenses_verdict:
        emit(out)
        return 3 if res.status == V.INCOMPLETE else 4
    with open(os.path.join(HERE, "qual", "QUALIFICATION.json"), encoding="utf-8") as f:
        qualified = json.load(f)["qualified"]
    laws, problems, n_snap, n_tree, n_replay = {}, [], 0, 0, 0
    shas = [row["arrays_sha256"] for sh in presented for row in sh["rows"]]
    if len(set(shas)) != len(shas):                    # B5: a copied unit is refused, whatever its seed label says
        problems.append("%d rows share an arrays_sha256 with another row" % (len(shas) - len(set(shas))))
    for sh in presented:
        law = sh["rows"][0]["law"]
        for i, row in enumerate(sh["rows"]):
            meta, arrays = A.load_unit(os.path.join(runs, sh["id"], "native_%s_%s" % (law, row["seed"])))
            if meta["arrays_sha256"] != row["arrays_sha256"] or M.digest(meta) != row["meta_sha256"]:
                problems.append("%s seed %s: unit files differ from the shard row" % (sh["id"], row["seed"]))
            if meta.get("seed") != row["seed"] or meta.get("law") != law:
                problems.append("%s seed %s: unit meta names %s seed %s" % (sh["id"], row["seed"], meta.get("law"), meta.get("seed")))
            r = E.evaluate_unit(meta, arrays)
            problems += ["%s seed %s: %s" % (sh["id"], row["seed"], p) for p in r["problems"]]
            why = snapshot_problem(law, row["seed"], meta, arrays, snapshot)          # B5: EVERY unit
            if why:
                problems.append("%s seed %s: %s" % (sh["id"], row["seed"], why))
            else:
                n_snap += 1
            why = tree_problem(law, row["seed"], meta, tree_replay)                  # B1 (s10.6): EVERY unit's tree
            if why:
                problems.append("%s seed %s: %s" % (sh["id"], row["seed"], why))
            else:
                n_tree += 1
            if i == 0:                                    # preregistered replay sample
                m2, a2 = replay(law, row["seed"])
                if A.arrays_sha256(a2) != meta["arrays_sha256"]:
                    problems.append("%s seed %s: native replay differs" % (sh["id"], row["seed"]))
                elif any(m2.get(f) != meta.get(f) for f in REPLAY_META):             # B1: the replayed TREE too
                    problems.append("%s seed %s: replayed %s differs" % (sh["id"], row["seed"],
                                                                         [f for f in REPLAY_META if m2.get(f) != meta.get(f)]))
                else:
                    n_replay += 1
            laws.setdefault(law, []).append((r, (row["seed"], arrays["H"], arrays["D"])))
    out["problems"] = problems
    out["evidence"] = {"freeze_check": "OK", "rows": len(shas), "distinct_arrays_sha256": len(set(shas)),
                       "snapshot_bound": n_snap, "tree_replayed": n_tree,
                       "full_replay_verified": n_replay, "replay_sample": REPLAY}
    if problems:                                       # P1: a refusal prints the problems and nothing verdict-bearing
        out["disposition"] = "REFUSED_RECORD_INCONSISTENT"
        emit(out)
        return 4
    out["laws"] = {}
    for law, items in laws.items():
        rows, feats = [x[0] for x in items], [x[1] for x in items]
        L = E.law_summary(rows, E.decode(feats), E.decode(feats, null=True))
        d = E.disposition({"completeness": res.status, "records_ok": True, "qualified": qualified, "law": L})
        out["laws"][law] = dict(L, disposition=d, label=E.label(d, L), rows=rows)
    emit(out)
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
        ref = argv[argv.index("--cleared-by") + 1] if "--cleared-by" in argv[:-1] else None
        if ref is None or len(argv) < 2:
            print("REFUSED: a confirmatory run needs --cleared-by <coordinator release> (no confirmatory run in C-018-T030 / T041)")
            return 2
        why = release_problem(ref)
        if why:
            print("REFUSED: %s" % why)
            return 2
        from rso.aether import freeze
        bad = freeze.mismatches()
        if bad or pinned_design_sha256() is None:
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
