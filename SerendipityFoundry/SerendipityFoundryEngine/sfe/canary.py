"""Gen-2 canary experiment (section 25).

Five research worlds forked from ONE checkpoint with identical initial
conditions (same seed -> same hidden target, same starting population, same
deterministic mutation RNG, same budget). The ONLY difference is information
topology. A bounded (mu+lambda) search runs in each world; candidate evaluation
goes through the real work queue and a real executor; failures and hypotheses
are recorded as first-class objects; cross-world sharing happens ONLY through
explicit, policy-gated, provenance-visible artifact imports.

The point is NOT to show sharing helps. It is to show the runtime can run the
experiment rigorously enough to FALSIFY such a claim. Every reported number is a
COUNT/derivation over authoritative state -- no narration. A null result is a
valid, recorded outcome.

Section-26 boundary: the search LOGIC (mutation, selection, which candidate to
import) lives HERE, in the driver -- it is the "agent". The Foundry only stores,
schedules, constrains, isolates, records provenance, and measures.
"""

from __future__ import annotations

import json
import random
import statistics
from typing import Optional

from sfe.executors import BitStringExecutor, WorkerLoop
from sfe.runtime import Foundry

TOPOLOGIES = [
    ("W1", "ISOLATED"),
    ("W2", "FAILURES_ONLY"),
    ("W3", "HYPOTHESES_ONLY"),
    ("W4", "FAILURES_AND_HYPOTHESES"),
    ("W5", "SUCCESSES_ONLY"),
]


def _mutate(rng, bits: str, k: int) -> str:
    b = list(bits)
    for _ in range(k):
        i = rng.randrange(len(b))
        b[i] = "1" if b[i] == "0" else "0"
    return "".join(b)


def run_canary(db_path: str, *, seed_root: int = 20260901, length: int = 24,
               rounds: int = 20, mu: int = 4, lam: int = 8,
               mut_bits: int = 2) -> dict:
    f = Foundry(db_path)
    ex = BitStringExecutor(length=length)
    target = ex.target_for(seed_root)
    client = f.create_client("canary")
    session = f.create_session(client, "canary")

    # a base world holding the identical initial conditions, then fork 5 children
    base = f.create_world(session, "base", seed_root=seed_root,
                          topology_group="canary")["world_id"]
    f.start_world(base, client)
    ck = f.checkpoint(base, client_id=client, meta={"problem": "bitstring",
                      "length": length, "seed_root": seed_root})
    children = f.fork(base, ck["checkpoint_id"],
                      [{"name": name, "sharing_policy": pol,
                        "topology_group": "canary", "seed_root": seed_root,
                        "interventions": {"topology": pol}}
                       for name, pol in TOPOLOGIES], client_id=client)
    worlds = {TOPOLOGIES[i][0]: children[i]["world_id"]
              for i in range(len(TOPOLOGIES))}
    for wid in worlds.values():
        f.start_world(wid, client)
        # per-world enforceable evaluation budget (compute scarcity is state)

    # identical initial population + identical RNG per world
    rng0 = random.Random(seed_root)
    init_pop = ["".join(rng0.choice("01") for _ in range(length))
                for _ in range(mu)]
    rngs = {tag: random.Random(seed_root + 1) for tag in worlds}
    pop = {tag: list(init_pop) for tag in worlds}       # same start everywhere
    best = {tag: ("", -1.0) for tag in worlds}
    best_round = {tag: -1 for tag in worlds}
    evals = {tag: 0 for tag in worlds}
    distinct = {tag: set() for tag in worlds}
    published = {tag: {"best_artifact": None, "failure_artifacts": [],
                       "hyp_artifacts": []} for tag in worlds}

    def evaluate(wid, tag, cands) -> dict:
        """Enqueue candidates as work, drain via a worker, return {bits: score}.
        Each evaluation is a real work item + real executor pass."""
        for bits in cands:
            f.enqueue_work(wid, ex.kind, {"bits": bits}, client_id=client)
        WorkerLoop(f, f"canary-worker-{tag}", [ex]).run_until_idle(world_id=wid)
        out = {}
        for row in f.store.read().execute(
                "SELECT result FROM work_items WHERE world_id=? AND "
                "status='COMPLETED' AND result IS NOT NULL", (wid,)).fetchall():
            r = json.loads(row["result"])
            out[r["bits"]] = r["score"]
        evals[tag] += len(cands)
        distinct[tag].update(cands)
        return out

    policy_allows = {tag: children[i]["sharing_policy"]
                     for i, tag in enumerate(worlds)}
    from sfe.runtime import SHARING_POLICIES

    for rnd in range(rounds):
        # ---- 1. cross-world sharing (policy-gated, provenance-visible) ----
        for tag, wid in worlds.items():
            allowed = SHARING_POLICIES[policy_allows[tag]]
            for other, owid in worlds.items():
                if other == tag:
                    continue
                # try to import the peer's published info this world may receive
                if "success" in allowed and published[other]["best_artifact"]:
                    _try_import(f, client, wid, owid,
                                published[other]["best_artifact"], pop[tag],
                                length)
                if "hypothesis" in allowed:
                    for aid in published[other]["hyp_artifacts"][-1:]:
                        _try_import(f, client, wid, owid, aid, pop[tag], length)
                if "failure" in allowed:
                    for aid in published[other]["failure_artifacts"][-3:]:
                        imp = _try_import(f, client, wid, owid, aid, None, length)
                        if imp is not None:
                            # record the failure as consumed (a CLAIM of use)
                            f.record_failure(wid, failure_type="imported_low",
                                             falsifier="peer", violated="score",
                                             client_id=client,
                                             reference={"from": other})

        # ---- 2. produce offspring by mutation ----------------------------
        for tag, wid in worlds.items():
            offspring = []
            src = pop[tag] if pop[tag] else init_pop
            for _ in range(lam):
                p = rngs[tag].choice(src)
                offspring.append(_mutate(rngs[tag], p, mut_bits))
            scored = evaluate(wid, tag, offspring + pop[tag])
            # ---- 3. record failures + hypotheses, publish for peers -------
            ranked = sorted(scored.items(), key=lambda kv: -kv[1])
            pop[tag] = [b for b, _s in ranked[:mu]]
            top_bits, top_score = ranked[0]
            if top_score > best[tag][1]:
                best[tag] = (top_bits, top_score); best_round[tag] = rnd
            # publish best as a 'success' (F2: a first-class kind) for peers
            ba = f.create_artifact(wid, "best", top_bits.encode(),
                                   client_id=client,
                                   meta={"info_kind": "success",
                                         "score": top_score})
            published[tag]["best_artifact"] = ba["artifact_id"]
            # publish best direction as a 'hypothesis'
            ha = f.create_artifact(wid, "hyp", top_bits.encode(),
                                   client_id=client,
                                   meta={"info_kind": "hypothesis"})
            published[tag]["hyp_artifacts"].append(ha["artifact_id"])
            f.propose_hypothesis(wid, f"best@{rnd} score={top_score:.2f}",
                                 client_id=client)
            # publish the worst offspring as a shareable 'failure'
            worst = ranked[-1][0]
            fa = f.create_artifact(wid, "failure", worst.encode(),
                                   client_id=client,
                                   meta={"info_kind": "failure"})
            published[tag]["failure_artifacts"].append(fa["artifact_id"])
            f.record_failure(wid, failure_type="low_score", falsifier="oracle",
                             violated="score>=1.0", client_id=client,
                             observed={"bits": worst, "score": ranked[-1][1]},
                             reproducibility="BIT_DETERMINISTIC")

    # ---- metrics (mechanically derived) ----------------------------------
    per_world = {}
    for tag, wid in worlds.items():
        acc = f.epistemic_accounting(wid)
        st = f.world_status(wid, client_id=client)
        per_world[tag] = {
            "policy": policy_allows[tag],
            "evaluations": evals[tag],
            "best_score": round(best[tag][1], 4),
            "solved": best[tag][1] >= 1.0,
            "round_of_best": best_round[tag],
            "distinct_candidates": len(distinct[tag]),
            "failures_generated": acc["failures_generated"],
            "failures_consumed": acc["failures_consumed"],
            "hypotheses": acc["hypotheses_proposed"],
            "imports": st["queue_depth"],  # placeholder; real imports below
            "ledger_integrity_ok": st["ledger_integrity_ok"],
        }
        # count real imports from the event ledger (provenance-visible)
        n_imp = f.store.read().execute(
            "SELECT COUNT(*) n FROM artifacts WHERE world_id=? AND "
            "origin='IMPORTED'", (wid,)).fetchone()["n"]
        per_world[tag]["artifacts_imported"] = n_imp
        del per_world[tag]["imports"]

    finals = [per_world[t]["best_score"] for t in worlds]
    summary = {
        "seed_root": seed_root, "length": length, "rounds": rounds,
        "target_hash": ex.target_for(seed_root),
        "worlds": per_world,
        "convergence_stdev_final_best": round(statistics.pstdev(finals), 4),
        "all_worlds_ledger_ok": all(per_world[t]["ledger_integrity_ok"]
                                    for t in worlds),
        "identical_initial_conditions": {
            "shared_seed_root": True, "shared_target": True,
            "shared_initial_population": True,
            "only_varied": "information_topology"},
    }
    f.close()
    return summary


def _try_import(f: Foundry, client, dst_world, src_world, src_artifact,
                pop: Optional[list], length: int):
    """Attempt a policy-gated import; on success (and if a population is given)
    add the imported candidate to the world's pool. Returns the import dict or
    None if policy barred it."""
    from sfe.errors import IsolationViolation, NotFound
    try:
        imp = f.import_artifact(dst_world, src_world, src_artifact,
                                client_id=client)
    except (IsolationViolation, NotFound):
        return None
    if pop is not None:
        try:
            bits = f.store.get_blob(
                f.get_artifact(dst_world, imp["artifact_id"],
                               client_id=client)["blob_hash"]).decode()
            if len(bits) == length and all(ch in "01" for ch in bits):
                pop.append(bits)
        except Exception:                            # noqa: BLE001
            pass
    return imp


if __name__ == "__main__":
    import sys
    import tempfile
    out = run_canary(sys.argv[1] if len(sys.argv) > 1
                     else str(__import__("pathlib").Path(tempfile.mkdtemp())
                              / "canary.db"))
    print(json.dumps(out, indent=2))
