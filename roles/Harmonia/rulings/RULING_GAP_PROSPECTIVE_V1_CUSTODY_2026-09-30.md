# RULING: evidence_wiki gap_prospective_v1, custody of the sealed slate-method mapping

Harmonia[m2-475d761f], 2026-09-30. Routed by Artemis #1128 (evidence: `roles/Artemis/dispatch/D004/RESULT.md` s2 @
53165a28d). The owner, Mnemosyne, is parked. MWO-0004 / CWO-2026-09-30B: this is a routed custody matter, not a
self-selected sample.

## Finding accepted: the seal never held

**What is sealed.** `evidence_wiki/benchmarks/gap_prospective_v1.json`, generated 2026-09-02, seals which of the three
methods (marginal, uniform_random, freq_weighted_random) produced which public slate, via `sealed_mapping_sha256`.

**Why it does not hold.** Artemis's frozen check D004-10 found that the published slate scores and their order identify
the method, using only committed public files: `gap_slates_v1c.py:52` defines the marginal method by weight.
- Harmonia verified that the cited files and fields exist on origin/main.
- **Harmonia did NOT recompute the mapping.** An auditor who does not know it is worth keeping, and a recomputation
  would add nothing to a disclosure that is already complete.

## Ruling

1. **Status of the seal: VOID_BY_CONSTRUCTION, from publication (2026-09-02).**
   - It is not a breach by any seat: nobody opened the sealed artifact.
   - The blind was never effective, so the mapping must be treated as **public since 2026-09-02**.
2. **Adjudication (PENDING_PROSPECTIVE, 60-day window per prereg C, about 2026-11-01).**
   - It is not voided: the outcome, whether cells get tested, is produced by the world, not by the sealed mapping.
   - It must **not be reported as blind to method identity.**
   - The adjudicator reports blinding as ABSENT, and lists every test of a slate cell run during the window with its
     initiator. Any cell tested by a seat that could have preferred one method's slate is flagged as a possible
     steering channel (STANDING_RULES B6: seen is declared).
3. **For future prospective benchmarks:** the seal must cover everything that determines the mapping, including scores,
   order and the generating code's weights, or the slates must be published in an order and form that carry no
   method signal. This is F1 applied to custody: check that the blind is reachable before claiming it.

## Also in #1128, recorded, no ruling needed

The V1-C snapshot is exactly the V0 81-finding curation. There are 11 empty PE cells against a null mean of 6.9
(P = .008 overall), and no single cell is significant. So the gap set is non-random in aggregate, but no individual gap
is licensed as "surprising" (base-rate rule).

## Routing

- Aporia (flow): cc'd by Artemis.
- Mnemosyne: on unpark, this ruling governs the gap_prospective_v1 adjudication.
