# Execution lineage: which engine, which session, produced this evidence

Frozen 2026-09-05 (session-affinity provenance sprint). Companion to
`FIRST_INTEGRATION_EVIDENCE_CONTRACT.md`; this is the multi-engine half.

## 1. The problem, stated exactly

M1 and M2 are byte-parity engines. Measured today, both report

    engine_source_hash = sha256:6a4f3aeec05a3ed9a31364e21f55cd11dc511f8f1d9789b2bcc37ce98f8447cf

so the BUILD cannot say which engine produced an anchor. World ids are minted
from the same scheme on every engine, so an id from M1 is syntactically valid
on M2 and refers to nothing there. Only `engine_instance_id` distinguishes
engines — and it is minted once and stored in the engine's SQLite `meta`
table, so it travels with the substrate.

## 2. What PEW records (non-secret handles only)

On `ew.fossil_encounters`, all nullable, all additive (migration 010):

    sfe_engine_instance_id   eng_<hex>   which engine instance
    sfe_session_id           ses_<hex>   which session (engine-local id)
    sfe_session_key_fp       sfp_<16hex> FINGERPRINT of the session key
    sfe_affinity_mode        STRICT | LEGACY
    sfe_ledger_head_hash                 optional ledger head at anchor time

**The raw session key is never stored, and never accepted.** It is bearer
material. A write carrying anything shaped like `sfes_<engine>_<tail>` in any
lineage field is refused with 422
`session_key_must_not_be_sent_to_pew`. PEW deliberately does not hash it on
the caller's behalf: silently accepting a credential "safely" is how a
credential store starts. PEW holds a provenance handle, not a secret.

The engine instance id and session id are already published by
`verify_anchor` and the audit envelope, so neither is a new secret.

## 3. LEGACY vs STRICT — and why nothing is back-filled

    STRICT   minted under a session-affine engine, with engine + session bound
    LEGACY   pre-session evidence, or an engine that issues no session key
    NULL     not asserted

All 11,953 fossils that existed before this migration are LEGACY: their
session and engine columns are NULL and stay NULL. **No binding is ever
synthesized for evidence that did not have one.** A back-filled session id
would be a fabricated provenance claim — the exact failure this work exists to
prevent. A LEGACY row is not upgraded in place; if it is ever re-established,
that is a new record citing the old one.

A row that asserts `STRICT` without both engine and session is refused (422
`strict_affinity_requires_engine_and_session`), and a session id without its
engine is refused (422 `sfe_session_id_requires_engine_instance_id`) because
session ids are engine-local and mean nothing on their own.

## 4. What verification now discriminates

`checks` returned by anchor verification, extending `binds_exp_id` /
`binds_obs_id`:

    binds_engine_instance   the engine that ANSWERED equals the engine the
                            fossil CLAIMS. False -> not verified.
    claimed_engine_instance / answering_engine_instance   both recorded
    binds_session           consumed from the engine when present.
                            NOT YET ASSERTED by SFE -- see blocker B1.

`verified` is true only when valid, both id bindings hold, and neither
`binds_engine_instance` nor `binds_session` is explicitly false. A missing
`binds_session` is recorded as unknown, never as success.

## 5. PEW's own witnesses (they need no engine change)

PEW sees anchors from many engines, so it can witness contradictions that no
single engine can see.

**Fork witness** — `ew.ledger_observations`, PK `(engine_instance_id,
event_seq)`. The SFE ledger is hash-chained and `event_seq` is a ledger
position, so one engine identity must have exactly one `entry_hash` at a given
seq. A second, different hash proves two divergent ledgers claim one identity.
The write is refused with 409 `split_brain_ledger_fork`, and the divergence is
recorded in `ew.ledger_fork_events` **even though the write was refused** — a
refused write that leaves no trace would erase the only record that a fork was
ever seen.

**Splice witness** — `ew.world_session_bindings`, PK `(engine_instance_id,
world_id)`. An SFE world belongs to exactly one session, so a fossil claiming
a different session for an already-witnessed world is evidence spliced across
sessions: 409 `cross_session_splice`, recorded in `ew.session_splice_events`.

Both are witnesses, not proofs of correctness. They fire only on
contradictions PEW actually observes, and each PEW store sees only its own
machine's traffic (M1 and M2 run separate stores by ruling). A fleet-wide
witness needs a federated or central PEW; that is not built.

## 6. Restart / restore / migration matrix

    process restart .............. identity STABLE. Verified: M1's engine was
                                   restarted mid-sprint and kept
                                   eng_8a37a5d305969034d488c43e.
    machine reboot ............... identity stable (it lives in the DB).
                                   Inferred from the same mechanism, not
                                   separately exercised.
    same DB, same identity ....... coherent by construction.
    backup restored, same host ... identity and ledger both preserved; the
                                   restored engine IS the same lineage.
    backup restored, OTHER host .. identity preserved BY DESIGN. If the
                                   original is still running, two live engines
                                   now share one identity -> SPLIT BRAIN.
    cold rollback to older DB .... identity preserved, ledger REWINDS. New
                                   events reuse seqs PEW has already witnessed
                                   with different hashes, so PEW's fork
                                   witness fires. This is correct: a rollback
                                   IS a divergence from the recorded history.
    code rollback, newer DB ...... engine's concern; PEW records
                                   schema_version and source_commit per
                                   attestation, so the mismatch is visible.
    migrating an ACTIVE session .. NO MECHANISM EXISTS. Undefined behaviour;
                                   see blocker B3.
    cloned DB run concurrently ... SPLIT BRAIN, measured (section 7).

## 7. Split brain — measured, not argued

Procedure (2026-09-05, against copies, disturbing no live service): copy M1's
`engine.db` twice, advance each independently through the pristine committed
runtime.

    cloneA engine_instance_id  eng_8a37a5d305969034d488c43e
    cloneB engine_instance_id  eng_8a37a5d305969034d488c43e     IDENTICAL

    seq 32162 WORLD_CREATED        A=8dd7baeeb4dbc2b6b6  B=8ea602b4314dda8c3a
    seq 32163 WORLD_STARTED        A=260801d0c2cf1a5ab7  B=cdf13739e814bbf3da
    seq 32164 HYPOTHESIS_PROPOSED  A=f455b63d5baf0ac7f8  B=fe2fd0c4ccc655b4c3

Two live ledgers, one identity, divergent history — and each would verify its
own anchors happily. `engine_instance_id` answers "which ledger is this
descended from", NOT "which execution produced this". PEW's fork witness turns
the contradiction into a refusal, but detection is after the fact and only
covers seqs PEW has observed. Prevention belongs in the engine: see B2.

## 8. Fleet-readiness: assumptions that still imply one SFE

    S1  ew.fossil_worlds PRIMARY KEY (world_id). World ids are ENGINE-LOCAL by
        contract; two engines may mint the same id and PEW would merge them
        into one row. Should be keyed (engine_instance_id, world_id).
    S2  run_id = exp_id:work_id is engine-local too, and participates in the
        encounter primary key. Collision across engines is improbable (96-bit
        ids) but is not excluded BY CONTRACT, only by luck.
    S3  ew/closure.py holds ONE SFE verify target (url/cacert/token). An anchor
        from any other engine cannot be verified -- it fails closed
        (event_exists=false, proven by gate P), but as the fleet grows every
        remote-engine anchor becomes unverifiable. An engine registry mapping
        engine_instance_id -> endpoint/credential is required.
    S4  ops/pew_serve_m2.py still defaults --db-host to 192.168.1.202, a relic
        of the pre-independence M2 mode.
    S5  Batteries carry a two-host hostname map. Fine for harnesses with env
        overrides; not a fleet mechanism.

## 9. Reading old evidence honestly

An investigator distinguishes the eras by field, not by folklore:

    sfe_affinity_mode IS NULL or 'LEGACY'  -> pre-session evidence. Engine and
                                              session are unknown and were
                                              never recorded. Do not infer.
    sfe_affinity_mode = 'STRICT'           -> engine + session recorded at
                                              write time.
    attestation->>'sfe_anchor_verified'    -> whether an engine confirmed the
                                              anchor, and
    attestation->'sfe_anchor_checks'       -> exactly which bindings held.

`ew.ledger_fork_events` and `ew.session_splice_events` are the record of
contradictions PEW refused. They are evidence in their own right and are never
pruned to make the substrate look clean.
