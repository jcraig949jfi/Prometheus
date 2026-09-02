# V2 Leakage Audit — interim record (charter s30)

## Event 1: haiku-control directory-exclusion violations (detected mid-campaign)
Deterministic op-log audit of all Arm A proposals found 7 haiku/sonnet
control cells whose logs mention evidence_wiki paths. Classification by
ACTUAL reads (logged by the agents themselves):

SEVERE — own-task wiki-derived content read; cell INVALID as control:
- V2-T06_A_haiku: read v2/packs/V2-T06_pack.json (its own task's pack,
  including the D-8 contradiction) + another arm's proposal.
- V2-T10_A_haiku: read v2/packs/V2-T10_pack.json + V2-T10_C_sonnet.md +
  V2-T07_A_haiku.md; cited wiki claim ids in a control proposal.

MODERATE — wiki-layer content from OTHER tasks read; cell INVALID:
- V2-T01_A_haiku: read v1b/proposals/T1_wiki.md + T3_wiki.md (wiki-arm
  proposals containing claim ids) + TASK_CORPUS_V2.md.
- V2-T04_A_haiku: read two peer control proposals + v2/packs/V2-T08_pack.json.
- V2-T05_A_haiku: read v2/packs/V2-T06_pack.json + TASK_CORPUS_V2.md +
  the V2 charter (charter is outside evidence_wiki; packs are not).

MINOR — peer Arm-A proposals only (format mimicry, no wiki-derived
content); cells RETAINED with disclosure:
- V2-T03_A_haiku (read PILOT-1_A_sonnet.md), V2-T07_A_haiku (read
  V2-T02_A_sonnet.md).

Sonnet controls: 0 violations (all evidence_wiki hits are logged
aborts/exclusions). Pilot controls: 0.

## Disposition (frozen-rules-compatible)
Invalid cells quarantined as *.CONTAMINATED (preserved, never scored as
controls). Replacement runs use the BYTE-IDENTICAL frozen prompt (decision
criterion = arm compliance, observable pre-scoring; no outcome inspection
preceded the decision). If a replacement violates again, the cell is
excluded and reported under G12 as haiku-control non-compliance; the prompt
is never strengthened mid-campaign.

## Standing vector (anticipated by s30)
Mid-campaign artifacts under evidence_wiki/v2/ (packs, proposals) reveal
wiki-layer content to any designer that disobeys the exclusion. The
condition boundary held for sonnet, failed for haiku. This is BOTH a
leakage event AND a G12 model-robustness observation: weaker models may not
respect access-boundary instructions, which bears directly on any future
READ_BEFORE_REINVENTING deployment where condition isolation matters.

## Also logged
- The /api/v1/schema endpoint does not expose the mechanism dictionary;
  one Arm C retrieval agent guessed mechanism terms (0 hits on 3 guesses).
  Frozen mid-campaign; noted as a wiki-side handicap, not fixed.

## Event 1 addendum (final sweep after reruns)
- T10_A_haiku REPLACEMENT read V2-T10_pack.json again (second violation of
  the identical prompt). Cell EXCLUDED from all analyses per the frozen
  one-replacement rule; both attempts preserved (.CONTAMINATED/.CONTAMINATED2).
- T08_A_haiku (landed after the first sweep) read V2-T01_pack.json + two
  peer proposals -> quarantined; one identical replacement launched.
- Reruns T01/T04/T05/T06 A_haiku: CLEAN (grep false-positives on the word
  'PACKET' in ordinary repo docs verified innocent by path).
- Haiku-control compliance final: 5/8 original cells violated; 1/6
  replacement violated. Sonnet: 0/12. This asymmetry is a primary G12 input.

## Event 2: harness auto-memory as a shared retrieval channel (MAJOR instrument note)
Control proposals for T08/T09 cite memory doctrine files
(feedback_se_on_the_wrong_unit, feedback_greedy_lora_surface_not_reasoning,
feedback_ergon_learner_north_star) with body-level detail. These files exist
NOWHERE under F:\Prometheus (verified by repo-wide grep) — they are the
operator's project auto-memory, which the agent harness recalls into EVERY
session run in this project, subagents included.

Consequences, stated precisely:
- TOOL PARITY HELD: both arms received the same injection; the A-vs-B
  contrast is not differentially contaminated.
- The "hidden gold" premise was weakened for tasks whose gold is condensed
  in the memory doctrine: T02 (allowlist-over-denylist), T04
  (behavioral-not-semantic routing), T08 (LoRA surface decomposition),
  T09 (SE on the wrong unit), T10 (permutation-null doctrine). For those
  tasks measured control recall is INFLATED by an out-of-band memory channel
  and the wiki's measured retrieval delta is a LOWER BOUND.
- Tasks with little/no memory-index overlap (T01, T05, T06, T07) are the
  cleanest cells for the retrieval-advantage reading.
- Deeper irony, recorded as evidence: the campaign designed to test an
  explicit memory system was partially confounded by an IMPLICIT memory
  system already operating. The program does not lack memory transmission;
  it lacks provenance-preserving, queryable, shared memory — the operator's
  auto-memory reaches only sessions on this machine/project and carries no
  provenance chain.
