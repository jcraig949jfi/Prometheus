# Atlas model -- schema, identity, lineage, merge, adapters

Currency: 2026-09-19 (migrations 001-004; harvesters commits/2,
archaeon_campaigns/1, frontier/3, npe/3, vivarium/2, pew/1, local_files/2;
comb/2). Charter: prompts/2026-09-19_charter/ and _charter_addendum/.

## 1. The three layers are separate tables

    WHAT RAN        attempt, segment        (+ fact layer='RAN')
    WHAT WAS SEEN   fact layer='OBSERVED'   (every fact -> fact_evidence -> source)
    WHAT WAS SAID   conclusion              (verbatim or by pointer; status
                                              STANDING | SUPERSEDED_INTERPRETATION |
                                              RETRACTED | CONTRADICTORY | UNRESOLVED)
    WHAT ATLAS SAYS experiment.atlas_class/_confidence/_method, and any fact,
                    edge or signal authored ATLAS_DERIVED with its method+version

An experiment row carries reported_disposition (verbatim) BESIDE
atlas_class; neither overwrites the other. A superseded reading stays as
a conclusion with its status changed; the execution rows are untouched.

## 2. Entity-relationship sketch

    host --< engine_instance >-- engine
     |            |                 |
     |            v                 v
     |   attempt >-- experiment >-- campaign            idea (scientific-lineage node)
     |      |            |                                 ^
     +------+            |                                 |
            v            v                                 |
         segment      fact >-- fact_evidence --< source --< source_link >-- (any entity)
                      conclusion ------------------^
    edge (typed, any entity -> any entity; src = later/derived, dst = earlier/cause)
    defect (edges AFFECTED_BY from experiments/campaigns)
    git_commit, entity_commit, seat_instance     harvest_run (provenance of every row)
    identity_collision, field_conflict           signal (the recomb layer)
    vocab (controlled terms; new engines add words, not columns)

Tier 1 (the manifest) = engine, host, engine_instance, campaign,
experiment (with world/organism/pressure/search/ruler families, seeds,
budget, reported disposition, atlas class, validity, result summary) and
attempt. View atlas.v_manifest joins the counts beside them.
Tier 2 = segment, fact, conclusion, edge, defect, idea, source,
source_link. Every tier-2 fact points at evidence.

## 3. Identity and de-duplication rules

- Keys are text built from NATIVE ids by atlas/harvest/common.py only:
  campaign  '<program>/<native>'           archaeon.campaign/cmp5
  experiment '<campaign_key>:<native>'     archaeon.campaign/cmp5:C5-03
  attempt   '<experiment_key>#<native>'    ...:C5-03#a02
  segment   '<attempt_key>@<native>'       ...#a02@chunk_000
  idea      '<program>/<native>'           nestor.cw01/T-X12
  defect    '<program>/<native>'           nestor.cw01/CW01-D086
- Filenames are never identity (a test asserts it). Paths identify
  SOURCES (pointers), not entities.
- Membership comes from the driver's structure, not from a field that can
  be wrong: Archaeon campaign = directory (RECEIPT.campaign says 'cmp2' for
  cmp3/cmp4/cmp5; recorded as a CONTRADICTORY fact + identity_collision).
- Same native id under two keys is RECORDED (identity_collision), never
  merged. A field two harvests disagree on is RECORDED (field_conflict).
- A prose field is parsed for ids and NEVER minted into a key
  (CW01 superseded_by names SFE experiments in prose; a test asserts no
  key contains prose).
- Append-only registries (LINEAGES.jsonl, PERTURBATIONS.jsonl with amend
  records) are folded in order; the source pointer carries the line range.
- Engines that mint no instance id get a synthetic, labelled key
  (npe@M1:<code sha12>, basis says ATLAS_DERIVED).

## 4. Lineage rules (atlas.edge)

One typed edge table for EXECUTION, SCIENTIFIC, ORGANISM and PROVENANCE
lineage. Relations: RERUN_OF, RESUMED_FROM, CONTINUATION_OF, DESCENDANT_OF,
DEFORMATION_OF, REPLICATION_OF, TRANSPLANT_OF, SUPERSEDES, AMENDS, TESTS,
ORIGINATES_FROM, CO_PARENT, AFFECTED_BY, EXPLAINS, CONTRADICTS,
EXECUTION_OF, SAME_MEASUREMENT_AS, CALIBRATION_CANDIDATE_FOR. Reasons:
BUG_FIX ... UNKNOWN (vocab). Every edge has basis DECLARED (a field says
so), INFERRED (a named rule; confidence stated) or ATLAS_DERIVED.

- A new attempt of the same spec is an attempt + RERUN_OF/RESUMED_FROM
  (EXECUTION). A changed spec is a new experiment + DESCENDANT_OF /
  DEFORMATION_OF (SCIENTIFIC). A rerun never overwrites its parent: both
  rows exist, the earlier attempt's validity becomes SUPERSEDED.
- Reason comes from a declared field (frontier dims, CW01 type/axis,
  suffix .d_seed) or stays UNKNOWN. Atlas does not invent a reason.
- Dangling endpoints are kept (v_edge_dangling): a parent Atlas has not
  indexed yet is not a parent that does not exist.
- atlas.descendants(type,key) / atlas.ancestors(type,key) walk the graph.

## 5. Machine merge strategy (for the second Atlas instance on M2)

- Keys are machine-independent, so M2's harvest of the same experiment
  lands on the SAME row and enriches it.
- Upsert = never erase: scalar COALESCE(offered, existing); arrays union
  (seen_from_hosts, hosts, seeds); jsonb merge. Identity-critical fields
  (host_id, engine_instance_key, commit_sha, started_at) are WATCHED:
  a disagreeing non-null value writes field_conflict first.
- Every row carries last_harvest_id -> harvest_run(host_id, harvester,
  version): which host saw it and with which extractor.
- Sources carry visibility: GIT_REMOTE | GIT_LOCAL:<host> | FS:<host> |
  PG:<host> | EXPECTED:<host>. EXPECTED means "referenced, not seen from
  here" -- never "did not happen". present=false only when the same host
  looked again and the file was gone.
- Recomb pruning removes only derived rows (edges/facts/conclusions/links)
  that the SAME harvester wrote on the SAME host and did not re-emit.
  Another host's rows are never pruned (a cheat-control test proves it).
- An M2 instance adds its own "local_roots" rows (host "M2") to
  atlas/registry.json and runs `python -m atlas harvest local_files`
  (plus any M2-only git refs through the git adapters with --ref).

## 6. Adapters (atlas/harvest/, each read-only, idempotent, versioned)

    reference           atlas/registry.json -> host, engine
    commits             every remote + local ref since --since: seat,
                        lane, instance, ids, lineage words, local-only flag
    archaeon_campaigns  archaeon/campaignN (SFE): campaign, experiment,
                        attempt (ATTEMPTS.json / C1 shape), step segments,
                        prereg/receipt facts, conclusions, declared parents,
                        supersession notes, friction-ledger defects,
                        DECISIONS lines, engine instance, ledger:// pointers
    frontier            archaeon/frontier: lineages as ideas,
                        transformations as experiments, RUN events as
                        attempts, chunks as segments (EXPECTED:M2 pointers),
                        observations, interpretations, gates, queues
    npe                 local ref nestor/sidequest-graphworld-*: rounds
                        receipts (primordial/ledger) and CW01 (state,
                        experiments, trajectories, perturbations, stasis,
                        evidence, defects), cross-engine edges
    vivarium            viv.research_experiment_queue / execution_attempt
    pew                 ew.campaign_observations pointers + ew.experiments
    local_files         host-local roots: SQLite engine ledgers (idle,
                        read-only, immutable: counts/ranges/clients and
                        membership of indexed engine ids), logs, telemetry
                        dirs, run logs
    comb (atlas/comb.py) the recomb rules R01..R13 -> atlas.signal,
                        identity collisions

Run: from a linked worktree (the canonical checkout is refused)

    python -m atlas migrate
    python -m atlas harvest all            # or one name; --fetch, --since, --ref, --npe-ref
    python -m atlas comb
    python -m atlas report --out roles/Atlas/reports/REPORT_<date>.txt
    python -m pytest -q atlas/tests

## 7. Adding an engine

1. Add it to atlas/registry.json (engines[]; local_roots[] for its host).
2. Write atlas/harvest/<name>.py: build keys with common.*_key, sources with
   Batch.git_source / other_source, facts with a layer and kind from vocab,
   edges with basis; new words go in a new migration (vocab rows).
3. Add it to ORDER in atlas/harvest/__init__.py, run it, run comb, run tests.
Nothing in the schema is SFE- or NPE-specific; Vivarium was added this way.

## 8. Non-interference

Git: object reads only (cat-file, ls-tree, log, for-each-ref); no fetch
unless --fetch; never a command in another seat's worktree. Files: stat,
small reads, sha256 of files <= 5 MB; live service trees stat-only
(registry "no_hash"). SQLite: only idle ledgers, mode=ro&immutable=1.
Postgres: SELECT in READ ONLY transactions outside schema atlas. No
engine depends on Atlas; deleting schema atlas changes nothing they do.
