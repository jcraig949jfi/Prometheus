MNEMOSYNE -- INDEX TODAY'S CORPORA, BRANCH
(operator 2026-09-10, via Archaeon; see 00_COMMON.md for authority)

State: migration 011 (typed_refs, ref_availability_events,
publication_outbox) landed; today the live queue carries cs-c3-2 (150
rows, ~90 complete) and cs-h1h0-1-p1 (24 complete), every row with a
PEW encounter, an engine observation, and a result projection.

DELIVER
1. Index both candidate sets as typed refs (experiment, observation, PEW
   encounter, artifact where present) with the four evidence axes, from
   authoritative references only (no raw bytes copied). Commit the
   receipt with counts per candidate set and any row that could not be
   resolved, and the exact command.
2. Demonstrate the rebuild-from-references path on cs-h1h0-1-p1 (24
   rows) and commit its output beside the index receipt.
3. The path correction you owed from your X5 report: land it.
4. BRANCH: origin/mnemosyne/evidence-wiki-v0 is fully merged into
   origin/main. Delete it and confirm.

REPORT: SHA on main and path per item.

------------------------------------------------------------------------

PROTEUS -- CASE ORDERING FOR BETA, B1 CONTROLS, BRANCH
(operator 2026-09-10, via Archaeon; see 00_COMMON.md for authority)

State: H1/H0 phase 1 ran 24 source tasks on cegis_boolean_v1: 3 SOLVED,
21 BUDGET_VM_OPS, 35 witnesses. Under `proteus_declared` case ordering
the 35 witnesses collapse to 4 distinct inputs {100,101,110,111}, all
with input 0 = 1, so every retrieval pack is the same set (Harmonia:
relevance is inert at 3 bits with K=4). Receipt:
archaeon/docs/h0h5/H1H0_PHASE2_PUBLISH_RECEIPT_2026-09-10.json.

DELIVER
1. Explain, from the evaluator, why the ordered first witness lands on
   cases 4-7 for the seeded enumeration (which candidates are tried first
   and which case they fail on), as a short committed note with the
   fixture that shows it.
2. For BETA (not for the running alpha): add ONE declared alternative
   case_ordering value to the Boolean library (e.g. a seeded permutation
   derived from the sealed candidate_seed, or Gray order), with the
   compile/evaluate parity fixture and the first-witness ordering test,
   so the witness pool can cover more than four inputs. Vivarium exposes
   it as a value; the alpha keeps `proteus_declared`.
3. B1 positive controls and the compile/evaluate parity fixtures: confirm
   they are on main and passing against the kind as registered
   (vivarium/viv/cegis_boolean.py), with the SHA.
4. BRANCH: none of yours are listed as stale; confirm, and delete any
   merged branch of yours not in the list.

REPORT: SHA on main and path per item.
