# Campaign 6 -- the Vivarium lane (execution / data plane), read against the directive

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-18 (Vivarium m2-fce3fe0b). Directive: DIRECTIVE_verbatim.md (this directory). Campaigns 4 and 5
are COMPLETE and CLOSED (#444, #451); production: consumer ALIVE at pin 6e7ac48f0, viv at migrations 001-010,
engine 699ca0f9 / eng_906356f7 / schema 9 on the NVMe. Nothing below has been built or deployed.

Vivarium's charter in one line: the durable, receipted execution service between producers (Archaeon's
generators) and the engine/PEW -- it runs what it is given, records exactly what happened, replays what it can
prove, and adjudicates nothing. Campaign 6 stresses exactly that: "retain the ability to notice, preserve,
reproduce and investigate events that were not specified in advance" is the data plane's promise, and
SCALING_HEALTH is graded on it by name.

## 1. Where the directive lands on the data plane (mapping, not commitment)

    directive                                   Vivarium object today                        gap for C6
    ----------------------------------------    -----------------------------------------    ------------------------------------------
    complete generative provenance of every     start bundle v1 (closed keys; producer's     bundle v2: provenance_class in the closed
    world; provenance labels HUMAN_DIRECTED /   declaration sealed at claim; factors)        set {HUMAN_DIRECTED, LLM_PROPOSED,
    LLM_PROPOSED / PROCEDURAL /                                                              PROCEDURAL, EVOLUTION_GENERATED, MIXED} +
    EVOLUTION_GENERATED / MIXED                                                              generator identity {generator_id, version,
                                                                                             seed}; admission REFUSES a C6 row without it
    exact pressure history per lineage;         intervention receipts (intended vs           a `source` field on interventions and on the
    EXOGENOUS vs ENDOGENOUS                     realised); engine WORLD_EVENT (schema 9)     engine's WORLD_EVENT: EXOGENOUS (applied by
                                                                                             the harness) | ENDOGENOUS (arose in-world);
                                                                                             Daedalus's half is the event's field
    T0 fingerprint for EVERY evaluation         result_schema per kind; observation content  a declared `fingerprint` result field with a
                                                carries the result dict; digests on steps    size bound (T0 <= 4 KB), in the observation
                                                                                             content and digested on the step; Vivarium
                                                                                             never reads inside it
    T1 richer trace around unusual events       artifacts by digest (engine artifact route;  a kind-declared optional artifact slot
                                                Limits: 16 MiB total / 4 MiB each)           `trace` the executor emits on a declared
                                                                                             trigger; bounded by the same Limits
    T2 full capture after escalation:           execution_attempt / step / bundle /          `viv.cli replay-packet <experiment_id>`: one
    freeze organism, parent, ancestors,         gate_receipt / intervention_receipt are      file = bundle + step keys + result digests +
    siblings, world state, pressure history,    append-only; engine worlds are immutable     engine anchors + artifact digests + the row's
    mutation chain; generate a replay packet    ledgers                                      relations (replication_of, family, arm);
                                                                                             FREEZE = pin those digests in PEW, not copy
    replay A exact / B lineage / C world-seed   replication_of + request_key relations;      a REPLAY row kind that names the packet and
                                                keyed steps; deterministic seeds             the replay class (A-G); Vivarium compares
                                                                                             result digests step by step and records
                                                                                             SAME / DIFFERENT per step -- no verdict
    replay D rollback / E ablation /            interventions_declared in the bundle;        nothing new structurally: a replay row whose
    F transfer / G pressure perturbation        intervention receipts per repeat             bundle differs from the packet in ONE named
                                                                                             key; bundle.diff() already names it
    long runs; archive exponentially;           repeat state=persist within a row;           an `evo_segment` shape: one row = generations
    "fitness plateau is not inactivity"         checkpoints as artifacts; keyed resume        g..g+k of one population under one pressure
                                                across worker death (proved C4-REH-1)        schedule, checkpoint artifact in / out, T0
                                                                                             table out; archive policy (1,2,4,8,... + event
                                                                                             neighbourhoods) declared in the bundle
    detectors (11), disagreement as an event    none (by charter: no adjudication here)      NOT Vivarium's. They read PEW (Mnemosyne's
                                                                                             readers) and the T0 stream. Vivarium's part is
                                                                                             that every T0 reaches PEW in order (outbox)
    planted fixtures hidden from operating      blinding of arms (viv/blinding, candidate    a sealed COMMITMENT: the planter (a seat that
    seats                                       sets); rows carry no "fixture" field         does not operate the campaign) registers
                                                                                             sha256 of the fixture id set before launch;
                                                                                             rows are indistinguishable on every column;
                                                                                             reveal = the list + the hash, after
    SCALING_HEALTH                              canary, dead-man auto-recovery, outbox,      a C6 load rehearsal: N segments x M
                                                010 release path                             generations at the intended T0 rate through
                                                                                             queue -> engine -> outbox -> PEW, measured

## 2. The one design question that decides whether the queue scales (needs Archaeon + Daedalus before any code)

Campaign 4 ran on the harness path because no queue kind evaluated a variant in a WSE world (#411). The
cheap fix -- `wse_evaluate_v1`, one row per evaluation -- is right for C4-05-shaped slots (thousands of
independent evaluations with retries) and WRONG as the unit for C6's long runs: one row = one engine world =
one experiment, and a long run is millions of evaluations. The queue's unit for C6 must be the SEGMENT:

    row  = {population manifest (by digest), world generator + provenance, pressure schedule + provenance,
            generation range [g, g+k), checkpoint artifact in (digest or none), archive policy, T0 policy}
    out  = {checkpoint artifact (digest), T0 fingerprint table (artifact, one line per evaluation, bounded),
            lineage delta (births/deaths/mutations as records), the segment's engine observations (one per
            archived generation, not per evaluation), pressure history slice (with EXOGENOUS/ENDOGENOUS)}
    next = the producer enqueues [g+k, g+2k) with replication_of/parent = this row and checkpoint = out

That keeps the transaction model intact (a segment is an attempt; a worker death mid-segment replays or
recomputes it from the checkpoint; the engine carries one observation per archived generation with the
fingerprint table as an artifact), keeps the engine's per-call load at C4 levels, and puts the archive policy
where the directive wants it (dense near events, sparse elsewhere). The evolution loop inside the segment is
Archaeon's (archaeon/wse/evolve.py); Vivarium wraps it as a kind with the provenance, the receipts and the
resume. I will not start the segment kind until Archaeon agrees the unit; `wse_evaluate_v1` I build now
regardless (it is asked for and is the T3 adjudication primitive: one evaluation, one world, one receipt).

## 3. What I build, in order (each behind the freeze rules: staged on main, canaried on a test schema,
##    pin advanced in a named window; production untouched until then)

    1  wse_evaluate_v1 (#411/#445; bare manifest blob by digest; episodes_for + evaluate; golden parity)   1 day
       + the dead-man probe retry (one retry after 30 s inside the tick; C4-REH-1 lost a tick twice)
    2  bundle v2: provenance_class + generator identity in the closed key set; admission refuses a C6 row
       without them; `source` on intervention receipts                                                     1 day
    3  `viv.cli replay-packet` and the REPLAY row kind (A/B/C exact/lineage/world-seed; D-G as one-key
       bundle diffs); SAME/DIFFERENT per step in the receipt                                                2 days
    4  T0 fingerprint field + T1 trace slot in the kind contract; size bounds enforced at admission          1 day
    5  the fixture commitment (register hash before launch; reveal after) as a queue table + CLI            0.5 day
    6  the segment kind, once the unit is agreed (s2)                                                        3-5 days
    7  C6 load rehearsal through the whole plane, measured, before the first real segment                   1 day

Items 1-5 are additive: no existing row's meaning changes; each ships with positive / negative / cheat
controls in the suite and a canary row on production before it is trusted.

## 4. Rulings I need (from the campaign lead / operator), none blocking items 1-5

    R1  the execution UNIT for C6 long runs: segment (s2) or per-evaluation rows -- Archaeon, with Daedalus
        on the engine's per-call budget
    R2  who plants the fixtures: a seat that does NOT operate the campaign (Nemesis / Rhadamanthus /
        Pronoia are the candidates by charter); Vivarium holds the commitment, not the list
    R3  where the detectors run and what they read: PEW readers over the T0 stream (Mnemosyne) is my
        assumption; if a detector needs to READ the queue tables directly, that is a read grant, not a hook

## 5. What Campaign 6 must NOT expect from Vivarium

Vivarium will not compute novelty, disagreement or interestingness; will not decide escalation thresholds;
will not choose which events to freeze; will not narrate a trajectory. It will make every one of those
decisions reproducible after the fact: the row, the bundle, the steps, the receipts, the artifacts by digest,
and the replay -- SAME or DIFFERENT, per step, on the record.
