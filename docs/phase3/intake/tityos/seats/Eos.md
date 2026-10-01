# Eos -- Tityos Phase 3 forensic dossier

Crawler: Tityos worker g4_novelty (read-only), 2026-10-01. Labels as in the brief. No holdout or
nestor_secrets path was opened.

## 0. Summary

- Eos ("The Dawn Scanner", agents/eos/, March 2026) was the intelligence pipeline's horizon scanner:
  five scanners (arXiv, OpenAlex, Semantic Scholar, GitHub, Tavily), a keyword relevance scorer, an LLM
  "Deep Analysis" hop (Nemotron 120B via NVIDIA NIM, Groq llama-3.1-8b fallback), digests, dedup index.
  Upstream Pronoia, downstream Aletheia/Hermes. [IMPLEMENTATION FACT] (agents/eos/README.md;
  agents/eos/src/eos_daemon.py)
- It produced 8 digests 2026-03-22..04-01 and 163 indexed items; one May run whose artifact was never
  collected; dormant 116 days. [REPORTED RESULT -- UNVERIFIED] (roles/Eos/ARCHAEOLOGY_2026-09-11.md)
- Re-seated 2026-09-11 as an "acquisition instrument": every external item must be typed ANCHOR /
  ACQUIRE / RESOURCE / REFUSED, admitted only if it names a referent in the repository that would change.
  [DESIGN INTENT] (roles/Eos/RESPONSIBILITIES.md)
- Its own preregistered first season killed the old scorer with controls: a content-free string of the
  scorer's own keywords scored 100/100 and a relevant item 8/100. All 28 distinct items the old pipeline
  had surfaced as ATTENTION were refused. [REPORTED RESULT -- UNVERIFIED] (roles/Eos/intake/
  FIRST_SEASON_2026-09-11.md)
- The replacement gate was then broken by Nemesis (same model family): 200/200 constructed wrong-referent
  claims crossed, 30/30 forged RESOURCE observations settled, 45 of 51 "refusals" never examined. Eos fired
  its own preregistered consequence: KEEP_DARK, no collection. Seat DORMANT since 2026-09-11.
  [LATER CORRECTION] (roles/Eos/intake/SEASON_II_2026-09-11.md, 54a1f97cc)
- For novelty/prior art: Eos was the only seat built to read the outside literature continuously, but it
  ranked relevance by substring match to a retired hypothesis (RPH, CMA-ES steering vectors), sampled
  only the first N results of keyword[0], and its LLM hop analysed repos it never opened. Its re-seated
  design deliberately refuses to measure novelty or importance ("EOS MAY NOT PROVE THAT AN EXTERNAL IDEA
  IS IMPORTANT"). [IMPLEMENTATION FACT / DESIGN INTENT]

## 1. Charter and role evolution

- March 2026: README "Dawn Constitution": 75% rate-limit rule, KNOW BEFORE YOU KNOCK, frugality; five
  scanners; Nemotron analysis; ATTENTION REQUIRED flags. Pipeline wired with Aletheia, Clymene, Hermes,
  Pronoia (eb17886fa, 2026-03-23); Pronoia auto-published reports hourly (dozens of commits 03-22..04-01).
  [IMPLEMENTATION FACT]
- May 2026: instrumented into Postgres pipeline (one agora.intelligence_outputs row, 2026-05-17); a
  substrate redirect designed, built and backed out on 2026-05-18 (54ccb3e97, 82716d87d, 2de21a796), which
  also reverted a keyword-rotation fix. [HISTORICAL CLAIM per ARCHAEOLOGY]
- 2026-09-11 re-seating (8cfe19440): roles/Eos/ created; operator prompt verbatim at
  roles/Eos/prompts/2026-09-11_reseating/; "own instrument declared uncalibrated"; EOS-01 ruled ACTIVE;
  typing rule adopted. Same day: preregistration (b3245156e), first season (9b908b8f5), admission queue to
  4 seats (28ae15eb5, comms #76-79), EOS-30 attack commission (83478ad3c), Season II KEEP_DARK (54a1f97cc).
- Terminal: DORMANT (docs/fleet/FLEET_CENSUS.md row "Eos ... DORMANT ... 2026-09-11"). [IMPLEMENTATION FACT]
- Relations: Nemesis (attacker, roles/Nemesis/attacks/2026-09-11_eos_intake_gate/ and
  2026-09-11_eos_gate_repaired/), Kairos (named model-independent attacker; did not answer), Hermes
  (mailer lineage), prometheus_llm registry (RESOURCE overlap, EOS-02), Clio (corpse to Necropolis,
  EOS03). agents/eos/.env is the program's de-facto keyring (EOS-04). Host: M1/D: worktree; old daemon on
  M3/M4. [HISTORICAL CLAIM]

## 2. Code/system architecture

[IMPLEMENTATION FACT] agents/eos/ 17 tracked files.
- src/eos_daemon.py (1,084 lines): scan_apis/arxiv/github/news, RateLimiter, paper_index dedup,
  _score_relevance (lines 703-754: tier-1/tier-2 substring weights, citation/star boosts, cap 100),
  llm_analyze (lines ~611-700: prompt keyed to "RPH predicts reasoning circuits precipitate at scale",
  max_items 3), write_digest.
- src/intake.py (515 lines): the 2026-09 gate -- Item, Claim, Check, Verdict; checks
  rationale_admissible, provenance, referent_resolves (file + token exist), not_already_absorbed (referent
  file does not already cite the item URL/id), falsifier (>= 20 chars), capability_absent (git grep
  --cached of markers excluding Eos's own paths; timeout -> INDETERMINATE), destination, consumer,
  observation (RESOURCE needs a committed probe artifact with latency/bytes); classify(); season().
- src/first_season.py (harness), build_sample.py, probe.py (bounded arXiv liveness probe),
  contact_witness.py (EOS-31 duplication/interruption-quality witnesses), credential_census.py,
  shrink_registry.py, library_scanner.py (local library inventory, consumer unknown).
- data/api_registry.json (15 APIs + 4 local models), paper_index.json (163 items, frozen 2026-04-01),
  library_manifest.json (3.6 MB).
- tests/test_intake.py (25 controls first season; 34 after Season II, 3 xfail), test_credential_boundary.py.

## 3. Inputs and outputs

Old: external APIs -> reports/YYYY-MM-DD.md (gitignored), paper_index.json, api_registry.json. New:
bounded samples (roles/Eos/intake/sample_2026-09-11.json: POP-A 28 old ATTENTION items, POP-B 24 live
arXiv items, POP-C 4 bait) -> ledger_2026-09-11.json, results, REFUSALS, admission comms.

## 4. Claim class it was meant to police

Old: "this external item is relevant / deserves attention". New: "this external item would change a named
place in this repository" (ANCHOR / ACQUIRE) and "this resource has measured limits" (RESOURCE); and the
negative: what the program declined to be pulled toward (REFUSED with reason). Explicitly not novelty or
importance (Season II law). [DESIGN INTENT]

## 5. Measurement methodology

Old: substring scoring of title + summary; LLM opinion on title + 500 chars. New: deterministic repository
predicates over a claim attached to the item; the claim is written by a proposer (Eos or a seat).

## 6. Null/control generation

First season NEGATIVE / POSITIVE / CHEAT fixtures chosen by the harness (FIRST_SEASON Test 1); Test 2
two-repository-state counterfactual (referent present vs absent) -- the cleanest control in the seat;
POP-C constructed bait. [IMPLEMENTATION FACT]

## 7. Positive controls

POSITIVE fixture arXiv 2606.11521 (relevant to agents/icarus) -- old scorer 8/100, did not fire.
Gate: 6 live items admitted to PENDING with referents; owner confirmation measured 0 (no seat answered).
So detectability of a truly useful item was never demonstrated. [REPORTED RESULT -- UNVERIFIED]

## 8. Negative controls

CHEAT keyword string 100/100 under old scorer (fires -- scorer dead). Bait 4/4 refused. Nemesis's 200
wrong-referent claims all crossed (gate fails the negative control it most needed). Forged observer label
30/30 settled RESOURCE pre-repair; repaired with test_cheat_forged_observer_label_is_refused.

## 9. Neutral/intermediate controls

NOT_EXAMINED state (Season II repair 2) separates "never judged" from "refused"; INDETERMINATE for search
timeouts ("Nothing was found" vs "nothing could have been found" -- intake.py capability_absent docstring).

## 10. Qualification criteria / gates / thresholds

Old: ATTENTION threshold 20 (papers). New: all checks must pass for PENDING_ADMISSION; only REFUSED is
terminal after Season II; falsifier >= 20 chars; preregistered predictions 3a-3d; EOS-30 consequence ">= 2
of six wrong referent -> PENDING rate inflated, no restart".

## 11. Statistical methods

Counts and bounds only (useful interruptions UNKNOWN/6, bounds 0/6..5/6). No significance testing.

## 12. Independence assumptions

Nemesis runs the same model as Eos; Season II states this audit "does not satisfy the base role's
independent-failure-mode bar". Kairos (model-independent) never answered. Eos was author, gate designer
and reporter of its own first season ("author reporting on the author's own mechanism", STATUS).
Old pipeline: scorer and LLM keyed to the same premise (RPH), so the two "filters" were not independent.
[IMPLEMENTATION FACT / HISTORICAL CLAIM]

## 13. Provenance tracking

Saved: archive of 8 gitignored digests byte-for-byte (roles/Eos/archive/digests_2026-03-22_2026-04-01/);
CALIBRATION C1 exposed a success=true pipeline row pointing at an uncollected artifact; C2 found 3/8 digests
byte-identical below the date line. Self-contamination found twice: dedup search hit Eos's own records,
then its own source comment naming the item -> SELF_PATHS exclusion (intake.py). Working-tree grep in a
sparse worktree searched 44% of files while reporting "0 hits in the tracked tree" -> git grep --cached.
[LATER CORRECTION]

## 14. Known defects

Keyword scorer double-counts nested phrases ("mechanistic interpretability" + "interpretability"; EOS-08);
keyword[0]-only scanners (C5; fix reverted in May); first-N sampling; LLM hop output printed as analysis
(C4); premise retired (RPH) so all historical relevance numbers are against a dead hypothesis; auto-
generated referents into non-existent research/frontier/ made 49 refusals constants; gate cannot
distinguish right from wrong referent (structural, EOS31).

## 15. Historical audits performed

By Eos on itself: ARCHAEOLOGY_2026-09-11, CALIBRATION.md (rows C1..), FIRST_SEASON (4 preregistered
tests), EOS31 contact witness study, EOS02 registry comparison, EOS04 keyring migration/Phase 0 report.
On Eos: Nemesis 271 verdicts (two attack dirs); Kairos commissioned, no answer.

## 16. Historical findings

- Old scorer is measuring words, not relevance -- REPORTED NEGATIVE/NULL (for the instrument).
- 0/28 old ATTENTION items survive the gate -- LATER OVERTURNED in interpretation (Season II: refusals were
  not about the items).
- 6 PENDING items -- UNKNOWN (no owner response); 1 was a duplicate already cited in
  aporia/docs/frontier_campaign_69/hypotheses/206_h3_adversarial_review.md.
- No deterministic contact witness exists (EOS31) -- REPORTED NEGATIVE.
- KEEP_DARK -- standing.

## 17. Later corrections

First season "51 refusals" -> Nemesis -> 7 refusals, 45 NOT_EXAMINED; "RESOURCE settled by measurement" ->
forged label -> RESOURCE no longer terminal; "none of the refusals is about topic ... cannot name a place"
-> "THAT SENTENCE IS WRONG ... Eos never tried to find a place" (SEASON_II).

## 18. Pivots

Horizon scanner (RPH-era) -> dormant -> acquisition typing instrument -> self-declared KEEP_DARK.

## 19. Journals / TODOs / backlogs

roles/Eos/journal/2026-09-11.md, 2026-09-11_active_pass.md, 2026-09-11_season2.md; BACKLOG_H0H5.md
(EOS-01..EOS-31); STATUS.md; CALIBRATION.md.

## 20. Research reports

roles/Eos/ARCHAEOLOGY_2026-09-11.md (March-May record classified); intake/PREREGISTRATION_2026-09-11.md;
intake/FIRST_SEASON_2026-09-11.md; intake/SEASON_II_2026-09-11.md; intake/REFUSALS_2026-09-11.md;
EOS31_CONTACT_WITNESS.md; EOS02_REGISTRY_COMPARISON.md; EOS03_ARCHAEOLOGY_CLIO.md; EOS04_*.md;
archive/digests_2026-03-22_2026-04-01/.

## 21. Failure cases

FP: pavement skid-resistance paper promoted to ATTENTION REQUIRED on "mechanistic interpretability,
interpretability" (2026-03-25); 0-star repo ATTENTION at 33; LLM speculation about unopened repos printed
as analysis; success=true row for an uncollected digest; byte-identical digests read as daily intelligence.
FN: relevant item scored 8/100; scanners never reached keywords after the first; first-N results only;
dedup by URL/id cannot catch the same idea under another id; gate refused items whose referent was
auto-generated (49) regardless of content.

## 22. Mechanism archaeology

Not relevant (no mechanisms analysed).

## 23. Novelty / prior-art audit

- Novelty definition: old pipeline had none -- "relevance" score plus LLM "Does it support, challenge, or
  extend RPH?"; new design refuses novelty and importance by law and replaces them with "would change a
  named file" plus "not_already_absorbed" (the referent file does not already cite the item) and
  "capability_absent" (no tracked file contains the capability markers). These are explicit
  "unfamiliar-to-Prometheus" tests, correctly scoped to the program, never to science. [IMPLEMENTATION FACT]
- Corpora searched: arXiv cs.AI/cs.LG/cs.CL (~20/cycle), OpenAlex (~15), Semantic Scholar (~15), GitHub
  trending (~15), Tavily web (~5) -- first N of fixed queries, effectively keyword[0] only; March-April
  2026 and one May run; 163 items indexed. Season I: 24 live arXiv items from a 2-request probe.
  Tools/LLMs: substring scorer; Nemotron-3-super-120b (NIM) / llama-3.1-8b (Groq) on title + 500 chars.
  [IMPLEMENTATION FACT / REPORTED RESULT -- UNVERIFIED]
- Blind spots: domain locked to mech-interp/steering/evolutionary-ML keywords of a retired premise; no
  ALife, origin-of-life, dynamical systems, or biology sources (the domains where Hecate/Nestor/Artemis
  later needed prior art); no full-text reading; no query logging per item until the re-seat; dedup by
  identifier only; capability_absent is a lexical absence test (a capability under another name reads
  "absent").
- Effect on interpretation: the old ATTENTION stream steered no recorded decision (consumer count
  treated as ZERO, EOS-06); the re-seat showed that every surfaced item over 11 days was relevance-by-
  keyword. One live item (arXiv 2608.15546 ATLAS) was already cited elsewhere, which is the only measured
  prior-art overlap.
- Unfamiliar vs new: "capability_absent = 0 git-grep hits" is exactly "unfamiliar to Prometheus", and
  intake.py names it so ("the program must not already have the thing"); it never claims novelty to
  science. Reverse direction: not_already_absorbed only checks the referent file, so an item already
  metabolised elsewhere passes (the ATLAS duplicate). [IMPLEMENTATION FACT]

## 24. Lens inventory

- Repository-state counterfactual test (Test 2): reusable pattern for "does this instrument see the
  program at all". Cheap, model-free.
- Typed intake gate with NOT_EXAMINED / INDETERMINATE states and self-path exclusion: reusable design for
  any literature-to-program admission lane; its structural limit (no pair-side contact witness) is
  documented.
- Old scanners: toy-grade; premise-locked.

## 25. What I did not read / open questions

Not read: eos_daemon.py scanner bodies, library_scanner.py, contact_witness.py internals, Nemesis attack
files, EOS02/03/04 bodies, journals, digests archive. Open: did any of the 6 PENDING owners ever answer?
Did any later seat (Lexis? Hecate?) adopt the intake gate for prior-art admission? (No evidence found in
roles/Hecate.)
