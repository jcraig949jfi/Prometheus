"""TIER 3B steps 6-7: meta-development, then transplant against the sham
distribution.

AMENDMENT 10. The donor sees only its own qualified development batteries and
its own successful programs, classified by SEMANTIC class. The tribunal is
constructed only after each worker artifact is frozen and hashed.

FALSE-POSITIVE PROTOCOL (declared here, AMENDMENT 10 s7): a recipient cannot
be told which of its development-exact programs is wrong, so it does not stop
at the first one. It records up to MAX_HITS development-exact programs in the
order encountered. Only AFTER freezing are they adjudicated, in that order:
the first tribunal-qualified one supplies M1, and the ones before it are the
false positives reached before the first qualified solution. No tribunal
information reaches the search.
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
import engine as E          # noqa: E402
import improver as I        # noqa: E402
import meta_tribunal as M   # noqa: E402
import semantics as S       # noqa: E402
import tier3b as T          # noqa: E402
import basis_v4 as G        # noqa: E402

M.use_provider(T)

QUAL = json.loads((HERE / "TIER3B_QUALIFICATION_2026-09-22.json").read_text())
FAMILIES = QUAL["usable_meta_tribunal_families"]
N = 16
ESCROW = 250_000
MAX_HITS = 5
META_WORKER_ESCROW = 250_000
META_ESCROW = 30_000_000


def search_collect(library, examples, escrow, cap, rng, max_hits=MAX_HITS):
    """Collect development-exact programs in encounter order. The searcher
    cannot distinguish them; adjudication happens post-freeze."""
    parsed = [(T.nums_of(t), t["gold"]) for t in examples]
    hits = []
    for prog, coord in library.candidates(rng):
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


# ---------------------------------------------------------------- meta-development
def meta_develop():
    base = I.pristine_library()
    meta = E.Escrow(META_ESCROW)
    observed_srcs, observed_progs = [], []
    for fam in T.META_DEV:
        q = QUAL["discrimination"][fam]
        for rep in range(2):
            esc = E.Escrow(META_WORKER_ESCROW)
            rng = random.Random(E.search_entropy("T3B-meta-%s-%d" % (fam, rep)))
            dev = T.dev_instances(fam, q, E.dev_entropy("T3B-meta-%s-%d" % (fam, rep), 0))
            hits = search_collect(base, dev, esc, META_WORKER_ESCROW, rng, max_hits=1)
            meta.charge(min(esc.spent, meta.remaining()))
            if hits:
                prog = hits[0][0]
                observed_progs.append(prog)
                observed_srcs.append(prog[2])

    # SEMANTIC classes, not source strings
    idx = S.SemanticIndex().add_all(observed_srcs)
    reps = sorted({idx.representative(S.signature(s)) for s in observed_srcs})
    inits = sorted({p[1] for p in observed_progs}) or ["0"]

    cand = {
        "unchanged": base,
        "specialise_from_successes": I.Library(
            [{"name": "specialised", "inits": inits, "bodies": reps,
              "finals": list(G.FINAL_SPACE)}] + base.entries),
    }
    scored = []
    for name, lib in cand.items():
        ok, bad = lib.desugars_into_g4()
        if not ok:
            scored.append({"operator": name, "rejected": bad[:4]})
            continue
        costs = []
        for fam in T.META_DEV:
            q = QUAL["discrimination"][fam]
            for rep in range(2):
                esc = E.Escrow(META_WORKER_ESCROW)
                rng = random.Random(E.search_entropy("T3B-eval-%s-%d" % (fam, rep)))
                dev = T.dev_instances(fam, q, E.dev_entropy("T3B-meta-%s-%d" % (fam, rep), 0))
                hits = search_collect(lib, dev, esc, META_WORKER_ESCROW, rng, max_hits=1)
                meta.charge(min(esc.spent, meta.remaining()))
                costs.append(esc.spent if hits else META_WORKER_ESCROW)
        scored.append({"operator": name, "fitness": round(statistics.mean(costs), 1),
                       "sha256": lib.sha256(), "size": lib.size()})
    ranked = sorted([s for s in scored if "fitness" in s], key=lambda s: s["fitness"])
    chosen = cand[ranked[0]["operator"]]
    return chosen, base, observed_srcs, reps, scored, meta.spent


# ---------------------------------------------------------------- transplant
def run_recipient(family, arm_name, library, i):
    q = QUAL["discrimination"][family]
    rng = random.Random(E.search_entropy("T3B-%s-%s-%03d" % (family, arm_name, i)))
    esc = E.Escrow(ESCROW)
    dev = T.dev_instances(family, q, E.dev_entropy("T3B-rx-%s-%03d" % (family, i), 0))
    hits = search_collect(library, dev, esc, ESCROW, rng)
    row = {"recipient": i, "arm": arm_name, "family": family, "escrow_spent": esc.spent,
           "dev_size": q["development_size"], "hits": len(hits)}
    fp_before, first_q = 0, None
    fp_charges = 0
    for prog, coord, charges in hits:                 # adjudicated only now
        art = M.artifact_for(family, prog)
        trib = M.MetaTribunal.after_freeze(art, family)
        sc = trib.score(art)
        if trib.qualified(sc):
            first_q = {"charges": charges, "coordinate": coord,
                       "artifact_sha256": art.sha256, "tribunal": sc,
                       "body": prog[2]}
            break
        fp_before += 1
        fp_charges = charges
    row.update({"qualified": first_q is not None,
                "charges_to_solution": first_q["charges"] if first_q else None,
                "coordinate": first_q["coordinate"] if first_q else None,
                "solution_body": first_q["body"] if first_q else None,
                "false_positives_before_first_qualified": fp_before,
                "false_positive_charges": fp_charges,
                "tribunal": first_q["tribunal"] if first_q else None})
    return row


def summarise(rows):
    q = [r for r in rows if r["qualified"]]
    ch = [r["charges_to_solution"] for r in q]
    censored = [r["charges_to_solution"] if r["qualified"] else ESCROW for r in rows]
    return {
        "PRIMARY_censored_mean_effort": round(statistics.mean(censored), 1),
        "M2_qualified": "%d/%d" % (len(q), len(rows)),
        "fp_per_recipient": round(statistics.mean(
            [r["false_positives_before_first_qualified"] for r in rows]), 3),
        "fp_charges_mean": round(statistics.mean([r["false_positive_charges"] for r in rows]), 1),
        "winners_median_TELEMETRY": statistics.median(ch) if ch else None,
    }


def main():
    t0 = time.perf_counter()
    evolved, pristine, observed_srcs, reps, scored, meta_cost = meta_develop()
    artifact = {
        "evolved_sha256": evolved.sha256(), "evolved_entries": evolved.entries,
        "pristine_sha256": pristine.sha256(),
        "observed_sources": observed_srcs,
        "observed_semantic_representatives": reps,
        "meta_scoring": scored, "meta_charges": meta_cost,
    }
    (HERE / "TIER3B_ARTIFACT_2026-09-22.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("[meta] evolved %s size %d | reps %s | meta charges %d"
          % (evolved.sha256()[:12], evolved.size(), reps, meta_cost), flush=True)

    arms = [("EVOLVED", evolved), ("PRISTINE", pristine)]
    for s in QUAL["sham_libraries"]:
        arms.append(("SHAM_%d" % s[0]["name"].split("_")[1], I.Library(s)))

    out = {"written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "families": FAMILIES, "recipients_per_arm": N, "escrow": ESCROW,
           "evolved_sha256": evolved.sha256(), "meta_charges": meta_cost,
           "per_family": {}, "detail": {}}
    for fam in FAMILIES:
        out["per_family"][fam] = {}
        out["detail"][fam] = {}
        for arm_name, lib in arms:
            rows = [run_recipient(fam, arm_name, lib, i) for i in range(N)]
            out["detail"][fam][arm_name] = rows
            out["per_family"][fam][arm_name] = summarise(rows)
        line = {k: v["PRIMARY_censored_mean_effort"] for k, v in out["per_family"][fam].items()}
        print("[%s] %s" % (fam, json.dumps(line)), flush=True)
    out["total_seconds"] = round(time.perf_counter() - t0, 1)
    (HERE / "TIER3B_RESULTS_2026-09-22.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("done in %.0fs" % out["total_seconds"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
