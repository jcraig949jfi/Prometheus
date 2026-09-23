"""TIER 3C end-to-end: gate -> generator qualification -> positive controls ->
shams -> meta-development (OBSERVE/VALIDATE split) -> transplant.

AMENDMENT 11 (13fd1d9b9). Each stage writes its own frozen artifact and no
stage may look at a later one's output.
"""
import hashlib
import json
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v4 as G        # noqa: E402
import conformance as C     # noqa: E402
import engine as E          # noqa: E402
import meta_tribunal as M   # noqa: E402
import semantics as S       # noqa: E402
import tier3c as T          # noqa: E402

M.use_provider(T)

N = 16
ESCROW = 250_000
MAX_HITS = 5


# ---------------------------------------------------------------- libraries
class Lib:
    """A proposal library whose entries may carry SCHEMAS. Entries are data;
    the complete base grammar remains the fallback, so every arm has identical
    ultimate expressive power."""

    def __init__(self, entries):
        self.entries = entries
        self._expanded = [T.expand_entry(e) for e in entries]

    def canonical(self):
        return json.dumps(self.entries, sort_keys=True, separators=(",", ":")).encode()

    def sha256(self):
        return hashlib.sha256(self.canonical()).hexdigest()

    def size(self):
        return sum(len(e.get("inits", [])) * len(b) * len(e.get("finals", []))
                   for e, b in zip(self.entries, self._expanded))

    def desugars(self):
        bad = []
        for e, bodies in zip(self.entries, self._expanded):
            bad += [b for b in bodies if b not in G.BODY_SPACE]
            bad += [i for i in e.get("inits", []) if i not in G.INIT_SPACE]
            bad += [f for f in e.get("finals", []) if f not in G.FINAL_SPACE]
        return (not bad), bad[:5]

    def candidates(self, rng=None):
        for e, bodies in zip(self.entries, self._expanded):
            inits, bl, finals = list(e["inits"]), list(bodies), list(e["finals"])
            if rng:
                for lst in (inits, bl, finals):
                    rng.shuffle(lst)
            for i in inits:
                for b in bl:
                    for f in finals:
                        yield ("fold", i, b, f), e["name"]
        for prog, _tag in G.scratch_candidates(rng):
            yield prog, "g4_fallback"


def pristine():
    return Lib([{"name": "organ_fold", "inits": list(G.H1_SPACE),
                 "bodies": list(G.H2_SPACE), "finals": list(G.FINAL_SPACE)}])


def search_collect(lib, examples, escrow, cap, rng, max_hits=MAX_HITS):
    parsed = [(T.nums_of(t), t["gold"]) for t in examples]
    hits = []
    for prog, coord in lib.candidates(rng):
        if escrow.remaining() <= 0 or escrow.spent >= cap:
            break
        escrow.charge(1)
        ok = True
        for nums, gold in parsed:
            got = G.run_program(prog, nums, True)
            if got is None or str(got) != gold:
                ok = False
                break
        if ok:
            hits.append((prog, coord, escrow.spent))
            if len(hits) >= max_hits:
                break
    return hits


# ---------------------------------------------------------------- stages
def stage_qualify():
    quals, pcs = {}, {}
    for fam in T.META_DEV + T.TRANSFER:
        quals[fam] = T.qualify_generator(fam)
        q = quals[fam]
        print("[gen-qual] %-32s size=%s QUALIFIED=%s" %
              (fam, q["qualified_dev_size"], q["QUALIFIED"]), flush=True)
    for fam in T.TRANSFER:
        prog = T.witness(fam)
        art = M.artifact_for(fam, prog)
        trib = M.MetaTribunal.after_freeze(art, fam)
        sc = trib.score(art)
        pcs[fam] = {"tribunal": sc, "PASSES": trib.qualified(sc)}
        print("[positive] %-32s %s" % (fam, pcs[fam]["PASSES"]), flush=True)
    usable = [f for f in T.TRANSFER if pcs[f]["PASSES"] and quals[f]["QUALIFIED"]]
    unseen_ok = [f for f in usable if f in T.UNSEEN_BODY]
    return quals, pcs, usable, unseen_ok


def stage_shams():
    idx = S.SemanticIndex().add_all(G.H2_SPACE)
    reps = sorted(idx.representative(s) for s in idx.classes())
    schemas = sorted({T.antiunify_bodies(a, b) for a in reps[:60] for b in reps[:60]
                      if a != b and T.antiunify_bodies(a, b)})
    out = []
    for k in range(T.SHAM_COUNT):
        rng = random.Random(int(hashlib.sha256(
            ("APHRODITE/TIER3C/SHAM/v1/%d" % k).encode()).hexdigest()[:16], 16))
        entry = {"name": "sham_%d" % k, "inits": ["0", "1"],
                 "bodies": sorted(rng.sample(reps, 6)),
                 "schemas": sorted(rng.sample(schemas, 1)) if schemas else [],
                 "finals": list(G.FINAL_SPACE)}
        out.append([entry] + pristine().entries)
    return out


def stage_meta(quals):
    """The frozen exclusion rule applies here too: a family whose GENERATOR
    failed qualification cannot serve as an OBSERVE or VALIDATE family, because
    its development batteries cannot discriminate the target from wrong
    semantic classes. No replacement family is substituted."""
    """OBSERVE families supply semantic classes; VALIDATE families score the
    candidate libraries. The donor never sees a tribunal."""
    base = pristine()
    meta_charges = 0
    observed = []
    observe_fams = [f for f in T.OBSERVE if quals[f]["QUALIFIED"]]
    validate_fams = [f for f in T.VALIDATE if quals[f]["QUALIFIED"]]
    print("[meta] OBSERVE=%s VALIDATE=%s (unqualified families excluded)"
          % (observe_fams, validate_fams), flush=True)
    if not observe_fams or not validate_fams:
        raise SystemExit("STOP: no qualified OBSERVE or VALIDATE family remains")
    for fam in observe_fams:
        size = quals[fam]["qualified_dev_size"]
        for rep in range(3):
            esc = E.Escrow(ESCROW)
            rng = random.Random(E.search_entropy("T3C-obs-%s-%d" % (fam, rep)))
            dev = T.tasks(fam, size, E.dev_entropy("T3C-obs-%s-%d" % (fam, rep), 0))
            hits = search_collect(base, dev, esc, ESCROW, rng, max_hits=1)
            meta_charges += esc.spent
            if hits:
                observed.append(hits[0][0])

    idx = S.SemanticIndex().add_all([p[2] for p in observed])
    classes = sorted({idx.representative(S.signature(p[2])) for p in observed})
    inits = sorted({p[1] for p in observed}) or ["0"]

    schemas = sorted({s for a in classes for b in classes
                      if a != b for s in [T.antiunify_bodies(a, b)] if s})
    op_schemas = sorted({s for a in classes for b in classes
                         if a != b for s in [T.antiunify_operator(a, b)] if s})

    cands = {
        "unchanged": base,
        "memorise": Lib([{"name": "memorised", "inits": inits, "bodies": classes,
                          "finals": list(G.FINAL_SPACE)}] + base.entries),
        "abstract": Lib([{"name": "abstracted", "inits": inits, "bodies": classes,
                          "schemas": schemas, "op_schemas": op_schemas,
                          "finals": list(G.FINAL_SPACE)}] + base.entries),
    }
    scored = []
    for name, lib in cands.items():
        ok, bad = lib.desugars()
        if not ok:
            scored.append({"operator": name, "rejected": bad})
            continue
        costs = []
        for fam in validate_fams:                 # scored on families never observed
            size = quals[fam]["qualified_dev_size"]
            for rep in range(3):
                esc = E.Escrow(ESCROW)
                rng = random.Random(E.search_entropy("T3C-val-%s-%s-%d" % (name, fam, rep)))
                dev = T.tasks(fam, size, E.dev_entropy("T3C-val-%s-%d" % (fam, rep), 0))
                hits = search_collect(lib, dev, esc, ESCROW, rng, max_hits=1)
                meta_charges += esc.spent
                costs.append(esc.spent if hits else ESCROW)
        scored.append({"operator": name, "validate_fitness": round(statistics.mean(costs), 1),
                       "sha256": lib.sha256(), "size": lib.size()})
        print("[meta] %-12s validate fitness %.1f size %d" %
              (name, scored[-1]["validate_fitness"], lib.size()), flush=True)
    ranked = sorted([s for s in scored if "validate_fitness" in s],
                    key=lambda s: s["validate_fitness"])
    chosen_name = ranked[0]["operator"]
    return (cands[chosen_name], base, chosen_name, classes, schemas, op_schemas,
            scored, meta_charges, [list(p) for p in observed])


def run_recipient(fam, arm, lib, i, size):
    rng = random.Random(E.search_entropy("T3C-%s-%s-%03d" % (fam, arm, i)))
    esc = E.Escrow(ESCROW)
    dev = T.tasks(fam, size, E.dev_entropy("T3C-rx-%s-%03d" % (fam, i), 0))
    hits = search_collect(lib, dev, esc, ESCROW, rng)
    row = {"recipient": i, "arm": arm, "family": fam, "escrow_spent": esc.spent}
    fp, first = 0, None
    for prog, coord, ch in hits:
        art = M.artifact_for(fam, prog)
        trib = M.MetaTribunal.after_freeze(art, fam)
        sc = trib.score(art)
        if trib.qualified(sc):
            first = {"charges": ch, "coordinate": coord, "body": prog[2],
                     "bytes": len(art.bytes), "tribunal": sc}
            break
        fp += 1
    row.update({"qualified": first is not None,
                "charges": first["charges"] if first else None,
                "coordinate": first["coordinate"] if first else None,
                "solution_body": first["body"] if first else None,
                "artifact_bytes": first["bytes"] if first else None,
                "false_positives": fp})
    return row


def summarise(rows):
    q = [r for r in rows if r["qualified"]]
    return {
        "PRIMARY_censored_effort": round(statistics.mean(
            [r["charges"] if r["qualified"] else ESCROW for r in rows]), 1),
        "qualified": "%d/%d" % (len(q), len(rows)),
        "fp_per_recipient": round(statistics.mean([r["false_positives"] for r in rows]), 3),
        "winners_median_TELEMETRY": statistics.median([r["charges"] for r in q]) if q else None,
        "solution_classes": sorted({S.canonical_form(r["solution_body"]) for r in q}),
        "median_artifact_bytes": (statistics.median([r["artifact_bytes"] for r in q])
                                  if q else None),
    }


def main():
    t0 = time.perf_counter()
    gate = C.check(limit_cases=120)
    print("[gate] GREEN=%s (%d comparisons)" % (gate["GREEN"], gate["checked"]), flush=True)
    if not gate["GREEN"]:
        print("CONFORMANCE GATE RED -- no run begins")
        return 2

    quals, pcs, usable, unseen_ok = stage_qualify()
    if len(unseen_ok) < 2:
        print("STOP: fewer than two unseen-body families survived qualification")
        return 2
    shams = stage_shams()
    (evolved, base, chosen, classes, schemas, op_schemas,
     scored, meta_charges, observed) = stage_meta(quals)

    artifact = {"selected_operator": chosen, "evolved_sha256": evolved.sha256(),
                "evolved_entries": evolved.entries, "evolved_size": evolved.size(),
                "pristine_sha256": base.sha256(),
                "observed_semantic_classes": classes, "schemas": schemas,
                "op_schemas": op_schemas, "meta_scoring": scored,
                "meta_charges": meta_charges, "observed_programs": observed,
                "OBSERVE": T.OBSERVE, "VALIDATE": T.VALIDATE,
                "observe_used": [f for f in T.OBSERVE if quals[f]["QUALIFIED"]],
                "validate_used": [f for f in T.VALIDATE if quals[f]["QUALIFIED"]]}
    (HERE / "TIER3C_ARTIFACT_2026-09-22.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("[meta] SELECTED %s sha %s size %d" % (chosen, evolved.sha256()[:12],
                                                 evolved.size()), flush=True)

    arms = [("EVOLVED", evolved), ("PRISTINE", base)]
    arms += [("SHAM_%d" % k, Lib(s)) for k, s in enumerate(shams)]
    out = {"written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "conformance_gate": {"GREEN": gate["GREEN"], "comparisons": gate["checked"]},
           "families": usable, "unseen_body_usable": unseen_ok,
           "generator_qualification": {f: {"size": quals[f]["qualified_dev_size"],
                                           "calibration": quals[f]["calibration"]}
                                       for f in quals},
           "evolved_sha256": evolved.sha256(), "selected_operator": chosen,
           "meta_charges": meta_charges, "escrow": ESCROW,
           "per_family": {}, "detail": {}}
    for fam in usable:
        size = quals[fam]["qualified_dev_size"]
        out["per_family"][fam] = {}
        out["detail"][fam] = {}
        for arm, lib in arms:
            rows = [run_recipient(fam, arm, lib, i, size) for i in range(N)]
            out["detail"][fam][arm] = rows
            out["per_family"][fam][arm] = summarise(rows)
        line = {k: v["PRIMARY_censored_effort"] for k, v in out["per_family"][fam].items()}
        print("[%s] %s" % (fam, json.dumps(line)), flush=True)
    out["total_seconds"] = round(time.perf_counter() - t0, 1)
    (HERE / "TIER3C_RESULTS_2026-09-22.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("done in %.0fs" % out["total_seconds"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
