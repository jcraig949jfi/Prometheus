# Eos calibration ledger -- this seat's own wrong calls

Currency: 2026-09-11. Kept because it is unflattering (base s2). Rows
are added when a call is found wrong, never removed. Every row names the
evidence that convicted it. Rows 1-7 are reconstructed from the
March-May record on the re-seating pass; the seat has run nothing since,
so no row is newer than 2026-05-18.

Columns: id | the call | what convicted it | the standing correction

    C1 | 2026-05-17: the pipeline recorded stage 'eos' success=true,
       output 'digest 2026-05-17.md', and the program read that as a
       working scanner. | MEASURED 2026-09-11: agora.intelligence_
       outputs holds exactly one eos row, ever; the artifact it names
       is not in the repository, not on the canonical checkout's disk,
       and was written on a host (M4) whose gitignored output nobody
       collected. A success label pointing at an unreadable artifact.
       | A stage row is not a receipt. An Eos cycle records the digest
       PATH, its sha256 over LF bytes, the item counts BY TYPE and the
       eligible count, or it records a no-op reason. Nothing else
       counts as having run.

    C2 | March-April: the hourly daemon was read as producing daily
       intelligence because it exited 0 every hour and wrote a file
       every hour. | MEASURED 2026-09-11: 3 of 8 archived digests
       (03-22, -23, -24) are byte-identical below the date line; the
       log shows two cycles an hour apart both writing the same dated
       file. | Charter constraint 3: a digest whose body hashes to its
       predecessor is refused and replaced by an explicit no-op reason.
       Base rule 8.

    C3 | The "ATTENTION REQUIRED" section was presented as a priority
       signal a human should act on. | The scorer is a substring count
       with hand-set weights (eos_daemon.py:703-752) and has never had
       a negative, positive or cheat control. On 2026-04-01 it promoted
       a 0-star repository to ATTENTION REQUIRED on a score of 33,
       earned by the two substrings "mechanistic interpretability" and
       "interpretability" -- one of which contains the other, so a
       single phrase scored twice. | Charter constraint 1: no score and
       no ATTENTION section may be read until the three controls exist
       and are committed with their rows. The double-count is EOS-08.

    C4 | The LLM hop was labelled "Deep Analysis" in a document written
       for a human to act on. | The 2026-04-01 digest prints the
       model's own reasoning scratchpad -- "Likely they provide...",
       "Could be they find..." -- about a repository it never opened,
       from a title and 500 characters, at max_tokens=200. | Charter
       constraint 2: no LLM output enters a digest as analysis. The
       model may propose a query, a type assignment or a predicate to
       check. Epistemic turn 2026-08-25.

    C5 | Scanners were treated as sampling their sources. | Each scanner
       takes the first N results of a fixed query and every keyword
       list after the first entry was never reached, because the
       single-keyword scanners always used keyword[0] -- a defect
       DIAGNOSED and fixed in May (COMMIT 82716d87d, hour-of-epoch
       rotation) and then REVERTED with the substrate backout
       (2de21a796). The defect is in the code today. | Charter
       constraint 6: enumerate and stratify the query set; report the
       eligible count beside every yield. EOS-11 restores rotation
       independent of the retired substrate premise.

    C6 | "Free tier: true" rows in api_registry.json were written from
       provider documentation and read as capacity. | 15 API rows carry
       free_tier and rate_limit fields; not one carries an OBSERVED
       limit, latency or failure shape, and the registry has not been
       touched since 2026-04-01T07:21Z. Three of them (Groq, Cerebras,
       OpenRouter) were superseded by prometheus_llm in August without
       the registry noticing. | Charter constraint 5: a RESOURCE row is
       not ACTIVE until a call has been made and the observed behaviour
       recorded, with the date. Verify the property, never the label.

    C7 | The seat carried a relevance model keyed to RPH ("reasoning
       circuits precipitate at scale") and CMA-ES steering vectors, and
       kept scoring against it after the program's premise moved. | The
       scorer's tier-1 weights and the LLM prompt both name RPH and the
       residual stream (eos_daemon.py:611-658, :703-715); nothing in
       the current north star or the H0-H5 ecology carries that
       hypothesis. | Base rule 5: currency is correctness. A scorer is
       a claim about what matters and it expires. Every historical Eos
       score is annotated with the premise it was scored against and
       may not be cited without it.

## Pre-registered prediction (written before the test, so it can be lost)

Registered 2026-09-11, before any control has been built or run. The
test is EOS-07; it has not been executed.

    CLAIM: the current _score_relevance() fails a cheat control.
    PROCEDURE: construct three fixture items --
      (a) POSITIVE: a real item a human judges relevant to a current
          program lane, whose abstract does not contain the seat's
          tier-1 substrings;
      (b) NEGATIVE: a real item a human judges irrelevant;
      (c) CHEAT: an item with no content -- a keyword-stuffed abstract
          assembled from the tier-1 and tier-2 substring lists and
          nothing else.
    PREDICTION: (c) scores at or above the ATTENTION threshold and
    outranks (a); (a) scores below (b) or near it. That is: the scorer
    measures substring presence, and a document engineered to contain
    substrings beats a document that is actually relevant.
    WHAT WOULD FALSIFY IT: (a) outranking (c). If the scorer ranks a
    genuinely relevant, non-keyword-matching item above a stuffed
    null, the prediction is wrong and the scorer is better than this
    seat believes. That result is reported as prominently as the
    predicted one.
    WHAT FOLLOWS EITHER WAY: the numbers go in this file, the fixtures
    go in the repository, and the digest's ATTENTION section stays
    unreadable until they exist.

    RESULT, 2026-09-11 (roles/Eos/intake/results_2026-09-11.json):
    PREDICTION HELD, and by a wider margin than predicted.
        NEGATIVE    0/100   does not fire
        POSITIVE    8/100   DOES NOT FIRE -- below the scorer's own
                            paper threshold of 20, so the one item in
                            the sample that bears on a live lane would
                            never have been surfaced
        CHEAT     100/100   FIRES -- saturates the scale on an abstract
                            that is nothing but the scorer's own tier-1
                            and tier-2 substring lists
    The prediction said CHEAT would outrank POSITIVE. It did so 100 to 8,
    with POSITIVE below the firing threshold entirely. The scorer is
    retired, not repaired: EOS-08 (the containment double-count) is moot
    in production and the code stays only as archaeological material.

## Rows added by the first active season (2026-09-11)

    C8 | The new gate's ACQUIRE dedup search was allowed to record a
       search failure as a fact about an item. | The first run's ACQUIRE
       candidate came back REFUSED with "search failed ... INDETERMINATE,
       not absent" folded into the refusal reason; `git grep` over 39,284
       files had exceeded its 60 s budget. | INDETERMINATE is now a state
       of its own, is never a refusal, and test_indeterminate_is_not_a_
       refusal holds it. An instrument that did not answer cannot refuse
       anything.

    C9 | The dedup search asked "does the program already have this?"
       over a tree that contains Eos's own records -- so every item Eos
       wrote down became "already present" on the next pass. | First run:
       "Microcosmos" returned 2 hits, both of them this seat's probe and
       sample files. After excluding roles/Eos/intake/ and
       roles/Eos/archive/, 1 hit remained and it was
       agents/eos/src/intake.py: the COMMENT DOCUMENTING THE
       CONTAMINATION DEFECT contaminated the instrument by naming a real
       item. | The search asks what THE PROGRAM has, and Eos is not the
       program: roles/Eos/ and agents/eos/ are both excluded, held by
       test_dedup_search_excludes_everything_this_seat_writes. Two rounds
       of the same bug one level apart is the reason the rule is now
       stated as a principle rather than a path list.

    C10 | This seat preregistered an ACQUIRE destination it had not
       verified: `vivarium/worlds/microcosmos`. There is no
       vivarium/worlds/ directory. | The gate refused the claim on the
       destination check. The refusal was correct and was about the
       PROPOSER, not the item. | Claims are verified before they are
       preregistered, not after. The resubmission with a real destination
       is recorded separately (RESUBMISSION_acquire_2026-09-11.json) and
       the original refusal stands in the ledger. The encouraging part is
       that the gate caught its own author; the unflattering part is that
       it had to.

    C11 | The gate cannot tell a real referent from the RIGHT referent.
       | Preregistered Test 4, run 2026-09-11: a bait item written to
       echo the operator's north-star phrasing, paired with
       roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates -- a file
       and token chosen because they exist -- passed every check and
       reached PENDING_ADMISSION. | Predicted in writing before it ran,
       so it cannot later be presented as a limitation that was always
       understood. The hole is locked into the test suite
       (test_cheat_a_real_but_unrelated_referent_still_passes): closing
       it FAILS that test and forces the ledger, the test and the module
       docstring to be updated together. The gate's only power is
       refusal; ANCHOR and ACQUIRE stay human admissions because of this
       row.
