"""Trajectory records for e01-e04 and the anomalies they exposed (immutable; append-only; idempotent).
Sources: each experiment's PREREGISTRATION.md, WORLD.json, RESULT.json, PACKAGE.md, DEFECTS.jsonl,
extracted 2026-09-18 with file:line citations (see the loop reconcile notes in BOUNDARY_REPORT)."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

POOL, STATE = HERE / "TRAJECTORIES.jsonl", HERE / "STATE.jsonl"
R = []


def rec(**k):
    R.append(k)


rec(trajectory_id="T-E01", kind="experiment", origin="cw01-e01", age="2026-09-17 17:24",
    originating_question_verbatim="Under economics where useful computation cannot always be completed within one step, do populations evolve to pay a holding cost to retain unfinished computation rather than recompute it - and does their advantage causally depend on that retained state?",
    derived_operationalization="64-cell priced Region surviving between steps (write 1.0, read 0.5, hold 0.1/cell/step); 120-step episodes, 40% of items exceed the step budget, 35% recur after a geometric gap; 5-gene policy (p_write, cells_frac, p_retrieve, p_reenter, persist_steps); I1 ERASE vs cost-matched sham over 32 matched streams",
    translation_loss="a 5-gene policy vector, not a rich program; A4 retrieval-by-content removed from the minimal form; A5 transfer channel specified, never exercised; one price vector, one recurrence rate",
    world_substrate="world_e01.py necessity-economics-v1 (mem + Redis backends)", representation="5 real genes",
    search_process="64 x 40, truncation selection, elite max(2, n//4) HARDCODED (world_e01.py:301), sigma 0.12", pressure="info/cost with holding priced",
    ruler="paired Delta(erase) - Delta(sham) over 32 matched streams; replication over 5 attempt seeds", compute_budget="7.6 s; 128 rows",
    result="COMPLETE: ancestor-relative +9.70% mean/+7.74% worst; dependence -10.21% mean/-8.80% weakest; 8.68 re-entries per episode; 5/5 replicates",
    failure_surface="control_no_retention cannot evolve (every gene inert with A1 disabled) so 'beats control' is a fixed baseline; absolute effect small (0.0487 vs 0.0453); one recurrence point",
    anomalies=["free lunch: the world rewarded retention at EVERY swept price; conditionality lives in configuration (recurrence), not price (WORLD.json:181,205)", "erasing the region IMPROVED score before the sham was cost-matched (D014)", "zero-recurrence control evolved AWAY from retention (p_write 0.266, persist 9.97)"],
    unrun_interventions=["I2 SCRAMBLE (having state vs finding it)", "I3 SEVER (A4 retrieval-by-content re-enters only here)", "I4 destroy-selected", "I5 swap", "recurrence sweep", "price-vector sweep across worlds", "transfer to other price vectors / frozen streams"],
    fossils=["rows/cw01-e01-a01.jsonl 128 rows (per-generation, 3 arms, interventions)", "evolved gene MEANS only; no genomes serialised; determinism from attempt_id is the fossil"],
    assumptions_at_time=["holding must cost something", "one price vector and one recurrence rate suffice for the minimal form", "the ablation must hard-refuse"],
    later_changes_relevant=["e07 built a representation-blind state-deletion family with a bit-identical sham and rho0/AURC rulers but could not evolve state use; e01 is the world where state use DID evolve", "e08 burden accounting"],
    last_perturbation="replication 2026-09-17", marginal_information_history=["a01 + 5 replicates: material"], stasis_state="ACTIVE")

rec(trajectory_id="T-E02", kind="experiment", origin="cw01-e02", age="2026-09-17 17:57",
    originating_question_verbatim="Do successive ancestor-relative gains compose into a ratchet - that is, is a later gain conditional on an earlier gain having landed - or do gains merely accumulate independently?",
    derived_operationalization="payload size/dispersion/structure; T1 normalise (cost 2.0, dispersion x0.20), T2 factor cheaper on normalised payloads, T3 reduce, T4 bind reusing e01's Region; 9-gene policy incl. 2 neutral genes; gain detector calibrated on a no-selection null; verdict by gene fixation order",
    translation_loss="the ordering is an ENHANCEMENT not a PRECONDITION (T2 alone +38.11%); detection floor 12.3% lift; 9-gene vector; the 'cannot finish in one step' pressure did not carry over (0.0% of items exceed the budget)",
    world_substrate="world_e02.py transformation-economics-v1", representation="9 real genes",
    search_process="64 x 80, elite_fraction 0.25, sigma 0.12, selection switchable (world_e02.py:216 selection=)", pressure="info/cost; nothing rewards ordering",
    ruler="detect_gains (12.3% lift, 1.3 SD, persistence 5) vs no-selection null p99; final verdict gene fixation generation (75% travel)", compute_budget="29.2 s; 6 rows (D026)",
    result="NULL: +174.1% ancestor-relative, ordered transformations 26 -> 135 per episode; p_factor fixes BEFORE p_norm 6/6 across three selection strengths; gains detected 1/0/0/0",
    failure_surface="convergence in <10 generations (+203% in gens 0-9) leaves no time-separated discoveries; T2 profitable without T1 so the foundation is acquired afterwards as an optimisation",
    anomalies=["foundation alone is a LOSS: NORM_ONLY -20.54%, UNORD +38.11%, ORD +69.41% (a fitness valley to the foundation)", "neutral genes drift up to -0.399 under elite copying (hitchhiking)", "the gain detector fired on pure noise before recalibration (D022)"],
    unrun_interventions=["K1 revert-A never executed (D024)", "K2 transplant-B, K3 ancestor restoration, K4 price shift, K5 harder workload, K6 frozen transfer", "control arms control_no_T1/no_T2/no_T4 declared, never evolved", "ratchet condition 3 (order dependence) never computed", "a world where T2 is IMPOSSIBLE without T1 (the stated design consequence)"],
    fossils=["rows/cw01-e02-a01.jsonl 6 rows; per-generation trajectories only inside RESULT.json; gene means per replicate; selection-strength sweep RESULT.json:174-228"],
    assumptions_at_time=["80 generations at elite 0.25 / sigma 0.12 leave room for sequential discovery (falsified, D028)", "a gain is detectable from the lineage-mean curve alone (falsified)"],
    later_changes_relevant=["e07's damage family could act as the pressure that makes the foundation required", "lineage.fixation_order + neutral_drift_floor exist"],
    last_perturbation="selection-strength probe 2026-09-17", marginal_information_history=["a01: NULL, material", "selection sweep: 6/6 same order, not material"], stasis_state="ACTIVE")

rec(trajectory_id="T-E03", kind="experiment", origin="cw01-e03", age="2026-09-17 18:13",
    originating_question_verbatim="Under per-activation cost, does evolution discover input-conditional selective activation - genuine coalitions - or merely static sparsity?",
    derived_operationalization="K=16 affordances at 0.5 each; M=4 latent classes needing 3-subsets; 4-dim observable features around attempt-stable class centres (overlap 0.35); deterministic linear activation policy bias + w.x > 0 (82 params); MI(latent class; activation pattern) vs shuffled null; I1 scramble vs identity sham",
    translation_loss="affordances satisfy set membership only (coverage), they transform nothing; 'coalition' = MI between class and bitmask, not interaction among affordances; linear policy",
    world_substrate="world_e03.py activation-economics-v1 (no substrate-backed state)", representation="bias[16] + w[16,4] + 2 neutral",
    search_process="64 x 60 x 3 arms, elite 0.25, sigma 0.10; arms are up-front genome transformations", pressure="info/cost with activation priced; nothing rewards sparsity",
    ruler="sparsity; MI excess over shuffled null (200 shuffles, p99); I1 collapse vs sham; lineage.decide", compute_budget="74.3 s; 726 rows",
    result="COMPLETE: treatment 1.47-1.60 vs non-conditional 0.96-1.33 vs activate-all 0.66; sparsity 0.243; MI 1.583 bits excess +1.194 4/4; I1 collapse -37.6..-61.0% 4/4; +159.6% ancestor-relative",
    failure_surface="scope: no composition or interaction among affordances observable; routing precision plateaus at 0.575-0.633 (coverage 0.69-0.80) with no explanation",
    anomalies=["BAD_ROUTER control: precision 0.915 but coverage 0.199 - more precise and worse", "non-conditional evolved arm: MI 0.0000 with exactly ONE activation pattern (maximally sparse, blind)", "class-0 centroid moved 1.955 between episodes before D029 made latent facts attempt-stable"],
    unrun_interventions=["I2 FORCE-ALL with its 'as the organism would have chosen' sham", "I3 KNOCKOUT-USED vs KNOCKOUT-RANDOM", "I4 TRANSPLANT to a world with different hidden structure at identical costs (knowledge vs habit)", "sweeps of activation_cost, K, M, needs_per_class, feature_overlap"],
    fossils=["rows/cw01-e03-a01.jsonl 726 rows (per-generation: sparsity, precision, coverage, |w|)", "no genomes; structure/centres regenerable from attempt_id"],
    assumptions_at_time=["latent facts must outlive the episode", "the static/blind solution must remain reachable", "MI read only as excess over a shuffled null"],
    later_changes_relevant=["e08 representational burden accounting could be laid over the activation policy", "e09 chain organism exists as a composition probe"],
    last_perturbation="EXECUTE 2026-09-17", marginal_information_history=["a01 4/4: material"], stasis_state="ACTIVE")

rec(trajectory_id="T-E04", kind="experiment", origin="cw01-e04", age="2026-09-17 20:15",
    originating_question_verbatim="Under a bounded, forgetful, delaying channel, does evolution discover differential handling conditional on item properties - triage - or merely a uniform policy that happens to score well?",
    derived_operationalization="items in pairs separated by a geometric gap (mean 8); combining yields log2(1+worth); channel capacity 4 FIFO, TTL 15, delay 1, p_drop 0.05, put 0.4 / get 0.3; recompute 3.0; two linear policies (place, recompute) over 4 features + 2 neutral; worth latent via an attempt-stable map; J1 permutes which features predict worth vs identity sham",
    translation_loss="ruler substituted: I(worth; place) instead of I(item properties; handling); two 5-parameter linear policies; effect sizes an order of magnitude below e03's",
    world_substrate="world_e04.py channel-economics-v1", representation="b_place, w_place[4], b_rec, w_rec[4] + 2 neutral",
    search_process="64 x 60 x 3 arms, elite 0.25, sigma 0.10; drop outcomes pre-drawn per item", pressure="contention ratio ~1.6 (capacity 4 vs demand 6.28)",
    ruler="I(worth; handling) vs shuffled null; J1 vs cost-matched identity sham; sham-vs-sham noise floor over 10 seed blocks (added after the fact)", compute_budget="54.7 s; 726 rows",
    result="INCONCLUSIVE (downgraded from COMPLETE): triage MI significant 4/4 (0.280 bits); beats non-conditional 4/4; beats always-recompute 4/4; +49.1%; J1 clears its own noise floor only 3/4 (r02 -3.27% inside [-6.69, +7.17])",
    failure_surface="the causal-dependence effect is too small for the sham-vs-sham null on one seed; the EXISTENCE of worth-conditional carrying is solid, the CAUSAL DEPENDENCE on hidden value structure fails to replicate",
    anomalies=["capacity never bound at 12: blind placement beat triage (D032); the learnability verdict flipped sign with capacity (+9.3% at 3, +3.4% at 4, -14.4% at 6)", "generality INVERTED: ttl_half -14.83%, drop_shock -8.51%, ttl_double +5.24% - the policy is tuned to having ENOUGH time", "Q8 controls within 0.5% by different routes (selectivity 1.000 vs 0.512)"],
    unrun_interventions=["J3 discipline swap FIFO->LIFO with sham", "J2/J4 cost-matched shams for the generality shocks (only shocked-vs-base was run)", "triage competence (worth-effort correlation) declared primary, never computed", "TTL/delay/capacity/p_drop sweeps during evolution", "powered re-run of J1 with the sham-vs-sham null"],
    fossils=["rows/cw01-e04-a01.jsonl 726 rows", "noise-floor bands RESULT.json:240-270", "capacity sweep WORLD.json:166-188"],
    assumptions_at_time=["capacity derived from measured demand by a pre-declared rule", "4 replicates suffice for an effect an order of magnitude smaller than e03's (falsified)"],
    later_changes_relevant=["the campaign's eligibility-rate rule (e08 D066) now says how to power the J1 re-run", "e07's schedule-generalisation framing (G2 unseen schedule) applies to the TTL inversion"],
    last_perturbation="noise-floor reanalysis 2026-09-17", marginal_information_history=["a01: COMPLETE->INCONCLUSIVE on the floor: material"], stasis_state="ACTIVE")

# ---- anomalies from e01-e04 ---------------------------------------------------------------
rec(trajectory_id="T-X08", kind="anomaly", origin="cw01-e04", age="2026-09-17",
    originating_question_verbatim="(anomaly) Why does the evolved triage policy IMPROVE when the channel forgets slower and degrade when it forgets faster - is it tuned to one damage schedule?",
    derived_operationalization="post-hoc shocks on the evolved treatment population: ttl_half -14.83%, drop_shock -8.51%, ttl_double +5.24%",
    translation_loss="no sham shocks were run (J2/J4)", world_substrate="world_e04.py", representation="e04 policies", search_process="e04 GA under ttl 15",
    pressure="channel economics", ruler="score shift under shock (no null)", compute_budget="seconds",
    result="inverted generality, unexplained", failure_surface="evolution under ONE schedule; never evolved under a distribution of TTLs",
    anomalies=["improves under LESS pressure than trained: fitting to one damage schedule (cf. e07's generalisation design)"],
    unrun_interventions=["evolve under a TTL distribution vs fixed TTL; test across TTLs with cost-matched shams"],
    fossils=["e04 rows"], assumptions_at_time=[], later_changes_relevant=["e07 preregistered exactly this schedule-generalisation contrast"],
    last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE", anti_gravity="hard to name; recorded as a generality footnote")

rec(trajectory_id="T-X09", kind="anomaly", origin="cw01-e02", age="2026-09-17",
    originating_question_verbatim="(anomaly) The foundation alone is a fitness LOSS (-20.5%) and the later gain is profitable without it (+38.1%): the ratchet world is a valley, not a staircase. What economics would make the later gain impossible without the foundation?",
    derived_operationalization="Q8 probe values NORM_ONLY/UNORD/ORD; e02's own stated design consequence: T2 must be IMPOSSIBLE (not just expensive) without T1 - a change to the economics needing a new preregistration",
    translation_loss="never built", world_substrate="world_e02.py", representation="9 genes", search_process="e02 GA", pressure="cost/info", ruler="gene fixation order + K1 knockout (never run)",
    compute_budget="seconds", result="untested", failure_surface="economics; and K1 was never executed",
    anomalies=[], unrun_interventions=["T2 refused unless the payload is normalised; K1 executed; weaker selection (D028) to spread discovery"],
    fossils=[], assumptions_at_time=[], later_changes_relevant=[], last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE")

rec(trajectory_id="T-X10", kind="anomaly", origin="cw01-e01", age="2026-09-17",
    originating_question_verbatim="(anomaly) Retention paid at EVERY swept holding price (a free lunch) with a crossover only at h~0.85; conditionality lives in the recurrence configuration, not the price. Does evolution track the price crossover, and where on the recurrence axis does retention stop paying?",
    derived_operationalization="price sweep in WORLD.json:194-204 was a probe, never an evolutionary run; recurrence swept nowhere",
    translation_loss="none yet", world_substrate="world_e01.py", representation="5 genes", search_process="e01 GA", pressure="holding price h", ruler="p_write / persist_steps and dependence vs h and recurrence",
    compute_budget="seconds per point", result="untested", failure_surface="declared expansion, never allocated",
    anomalies=["the zero-recurrence control evolved away from retention: the recurrence axis is where conditionality lives"],
    unrun_interventions=["2-D sweep: recurrence in {0, 0.15, 0.35, 0.6} x hold price in {0.1, 0.5, 0.85, 1.2}; map where retention evolves"],
    fossils=[], assumptions_at_time=[], later_changes_relevant=[], last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE")

rec(trajectory_id="T-X11", kind="anomaly", origin="cw01-e03", age="2026-09-17",
    originating_question_verbatim="(anomaly) Evolved coalitions plateau at routing precision 0.58-0.63 with coverage 0.69-0.80: is the plateau a world ceiling (feature overlap 0.35) or a search limit?",
    derived_operationalization="observed in e03 per-generation rows; never varied", translation_loss="none yet",
    world_substrate="world_e03.py", representation="linear activation policy", search_process="e03 GA", pressure="activation cost", ruler="precision/coverage vs feature_overlap and generations",
    compute_budget="seconds", result="unexplained plateau", failure_surface="no sweep", anomalies=["BAD_ROUTER: precise and worse"],
    unrun_interventions=["feature_overlap sweep {0.1, 0.2, 0.35, 0.5} x generations {60, 240}; hand-built Bayes-optimal router as the ceiling"],
    fossils=["e03 rows"], assumptions_at_time=[], later_changes_relevant=[], last_perturbation="none", marginal_information_history=[], stasis_state="ACTIVE",
    anti_gravity="a residual nobody named")


def main():
    existing = set()
    if POOL.exists():
        for line in POOL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing.add(json.loads(line)["trajectory_id"])
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    with POOL.open("a", encoding="utf-8") as fh, STATE.open("a", encoding="utf-8") as sh:
        for r in R:
            if r["trajectory_id"] in existing:
                continue
            r = dict(r)
            r["recorded"] = ts
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
            sh.write(json.dumps({"trajectory_id": r["trajectory_id"], "ts": ts, "state": r["stasis_state"],
                                 "reason": r.get("stasis_reason", "initial record"),
                                 "marginal_information_history": r.get("marginal_information_history", [])},
                                ensure_ascii=True) + "\n")
            added.append(r["trajectory_id"])
    RS.require_ascii_safe(POOL)
    RS.require_ascii_safe(STATE)
    print("appended", added)


if __name__ == "__main__":
    main()
