# Techne Substrate Fire Log — 2026-05-21

Continuation of the Theseus-driven substrate-generation loop (Theseus's
own fire counter; last fire was Theseus #33 on 2026-05-19). This file
is the Techne-role journal for the resumed series after the
2026-05-20 OS lockup that interrupted the prior session.

The Theseus daemon auto-journals each batch to
`theseus/journals/BATCH_LOG.md` and `theseus/journals/batches.jsonl`.
This log adds Techne-role commentary per fire: pre-fire diagnostics,
algorithm work shipped between batches, self-review, commits.

Per `feedback_role_pivots.md`: I am Techne for the duration of this
loop, not Substrate-Tester (which runs its own journal in
`charon/diagnostics/substrate_tester_fire_log.md`).

---

## Fire #34 — 2026-05-21 ~09:24Z

First fire after the 13-day silence and the 2026-05-20 cascade
failure. Pre-fire diagnosis (covered in commit `47a1fce3`) identified
two interacting bugs:

1. **Bandit picked from stubs.** `daemon.py:374` passed
   `list(REGISTRY.keys())` (all 44) to `bandit.select`. The
   YieldProportionalBandit's UCB exploration bonus inflated never-fired
   stubs over time, so post-Fire-#33 batches eventually selected
   all-stub sets, producing the trail of 0-record batches at
   2026-05-20T07:13.

2. **`b3` 28M-record OOM.** `Generator.emitted: List[str]` accumulated
   record_ids forever (write-only). `CorpusWriter._seen: Set[str]`
   stored full 64-char sha256 hex. At 28M records: ~5-6GB of dedup
   state per generator — the proximate cause of the OS lockup per
   5 MemoryError() events in the b3 batch journal.

### Pre-fire fixes shipped (commit 47a1fce3)

- `daemon.py`: bandit.select(available=list_active()) constrains
  candidate set to ACTIVE-status generators upfront. runnable filter
  inside run_batch kept as defense-in-depth.
- `daemon.py`: PER_BATCH_RECORD_CAP=5_000_000 enforced in tick loop;
  `tracker.record_emission` moved inside writer.write success branch
  so reported counts == on-disk counts (was previously tracking dups
  separately from writer state).
- `generators/base.py`: `emitted` switched from List[str] to
  `deque(maxlen=2000)` — bounded ring; the writes are append-only
  and never read, so this is pure overhead-removal.
- `emit/corpus_writer.py`: `_seen: Set[str]` switched to `Set[int]`
  storing 64-bit prefix of sha256 hex via `int(rid[:16], 16)`.
  Collision probability ~7e-7 at 5M records; ~10x memory reduction.
- 9 new tests in `test_bandit_active_only.py` and
  `test_per_batch_record_cap.py` pinning all four fixes.
- Smoke validated: 3-batch bandit run picked 5/5 actives each round,
  cap test stopped at exact 200 records, no MemoryError.

### Batch result

- batch_id: `batch-20260521T092439Z-ee3b08`
- Started: 2026-05-21T09:24:39Z
- Ended:   2026-05-21T10:02:07Z
- Duration: 0.62h (37 min) — terminated by cap, not by wall budget
- Requested: a1,b5,c1,d1,e1 (default set; `--batches 1` doesn't
  trigger bandit selection)
- Records: 5,000,000 exactly (cap held strictly to spec)
- Kills: 3,455,385
- Confirmations: 1,544,615
- Inconclusive: 0
- Errors: 0
- Discoveries emitted to handoff: 60

Per-generator yield:

| gid | records   | throughput/h | info_density | diversity | yield_score | kills   | conf    |
|-----|-----------|--------------|--------------|-----------|-------------|---------|---------|
| a1  | 2,292,237 | 233.9M       | 0.531        | 0.727     | 0.0039      | 1.58M   | 712K    |
| c1  | 2,704,870 | 255.8M       | 0.531        | 0.705     | 0.0038      | 1.87M   | 831K    |
| b5  | 1,052     | 63K          | 0.599        | 0.822     | 0.0050      | 15      | 1,037   |
| d1  | 1,841     | 19K          | 0.553        | 0.882     | 0.0049      | 857     | 984     |
| e1  | 0         | 0            | 0            | 0         | 0           | 0       | 0       |

Observations:
- a1+c1 dominated at 99.95% of output. b5 and d1 are starved when run
  with a1/c1 in the same batch (round-robin gives them equal slots
  but they hit None far more often due to parent-record dependencies
  and slow-path computations).
- e1 emitted 0 — the deep_research_batch corpus is fully mined; e1
  is exhausted as a source. Bandit will downweight it; new actives
  (e2/e4/e5) will fill the literature-mining slot.
- info_density tightly clustered 0.53-0.60 — calibration deferred
  until Ergon's Learner gives ground-truth training_value per record.

Cap behavior: hit exactly 5,000,000 — that's a clean stop, not a
"close enough" stop. Memory peaked at ~3.6GB and stayed there; OOM
fully eliminated.

### Algorithm work shipped between fires (this fire only)

Concurrent with the 37-minute batch, 7 new generators implemented +
tested + registered:

- **E2** `e2_arxiv_abstract_mining.py` (commit 92c95918)
  - Offline cache pattern; `theseus.scripts.fetch_arxiv_abstracts`
    pulls math.{NT,AG,CO,GT,RT,QA,NA} + math-ph abstracts
  - 9 unit tests, no network in test path
- **E4** `e4_lmfdb_knowledge_mining.py` (commit 92c95918)
  - `theseus.scripts.fetch_lmfdb_knowls` pulls kwl_knowls from
    devmirror.lmfdb.xyz Postgres mirror
  - TeX-stripping helper handles $...$ and \[...\] math blocks
  - 8 unit tests
- **E5** `e5_mathworld_wikipedia_scrape.py` (commit 92c95918)
  - `theseus.scripts.fetch_wiki_conjectures` hits Wikipedia REST
    API on a curated 42-page seed list (RH, BSD, Poincare, etc.)
  - 7 unit tests
- **F1** `f1_monte_carlo_random_pairs.py` (commit 92c95918)
  - Pure substrate-native; null baseline for F-family. INCONCLUSIVE
    on missing values is the whole point of the null framing.
  - 6 unit tests
- **G1** `g1_galois_twist.py` (commit 35660f2f)
  - Exact-Fraction j-invariant grouping → twist-class equivalence
    classes. Caught a j-formula bug during testing (off-by-1728;
    canonical formula is c4^3/Δ, not 1728·c4^3/Δ).
  - 9 unit tests
- **G2** `g2_functional_equation.py` (commit dbcae6ae)
  - Initial draft used a flawed L1-vanish-vs-rank-parity heuristic
    (60% hold rate) — testing surfaced that LMFDB's `L1` is the
    leading non-zero Taylor coefficient, NOT L(1). Rewrote to emit
    UNVERIFIED FE claims; sigma verifies downstream.
  - 9 unit tests
- **G3** `g3_modular_transform.py` (commit 55f9266f)
  - Exact-integer Hasse bound `|a_p|² ≤ 4p` (the SL_2(Z) Hecke
    eigenvalue consequence). Strict 100% hold rate test on 500
    catalog samples — Hasse 1933 holds as expected.
  - 11 unit tests

Inventory updated to 36 of 40 active (commit 4115aa9f). Remaining 4:
i1-i4 (Tier-2 local-LLM, user-deferred this session).

### Self-review (per protocol)

(a) **Did I solve THIS fire's task or scope-creep?** Solved: ran one
batch (5M records, clean cap, 0 errors), updated journal, committed,
implemented the next 7 algorithms in the remaining-11 list. Did NOT
scope-creep into i1-i4 (correctly held at user's "Skip I-tier for
now" directive) or into Ergon/Learner work.

(b) **Did I change any contract?** The substrate primitives'
contracts are unchanged. `Generator.emitted` interface preserved (it
was List-with-append; now Deque-with-append; same write-only
semantics). `CorpusWriter._seen` is internal — not a public field.
The bandit's `select(available, history, n)` signature unchanged.

(c) **Conventional-approach drift check?** Reviewed:
- 7 new generators follow the offline-cache pattern that E1 already
  established — not pulling in "the standard literature mining lib";
  reusing existing infra
- G2's first draft was a conventional "let's use a clever heuristic"
  approach that failed when reality of catalog data structure
  intervened. Rewrote to substrate-honest UNVERIFIED emission. This
  was anti-conventional discipline working in real time.
- G3's strict 100% test is anti-conventional in a tactical sense —
  most projects soften "100%" to "at least 95%" to avoid flakiness.
  But Hasse's theorem IS 100%, so anything less would mask substrate
  signal. The strict test is the calibration discipline working.
- No paper/publication framing anywhere; no LLM-narrative inflation
  on the new generators' claim shapes.

### Diff this fire

8 commits total. Owned files only:

| File | Change |
|------|--------|
| `theseus/daemon.py` | bandit→list_active(); record cap; tracker move |
| `theseus/config.py` | PER_BATCH_RECORD_CAP=5M; 7 status flips to active |
| `theseus/generators/base.py` | emitted → bounded deque |
| `theseus/emit/corpus_writer.py` | _seen → Set[int] of hash prefixes |
| `theseus/registry.py` | 7 import lifts; 7 entry promotions |
| `theseus/generators/stubs/all_stubs.py` | 7 stub class deletions |
| `theseus/inventory.md` | active-set summary updated to Fire #34 |
| `theseus/generators/e2_arxiv_abstract_mining.py` | NEW |
| `theseus/generators/e4_lmfdb_knowledge_mining.py` | NEW |
| `theseus/generators/e5_mathworld_wikipedia_scrape.py` | NEW |
| `theseus/generators/f1_monte_carlo_random_pairs.py` | NEW |
| `theseus/generators/g1_galois_twist.py` | NEW |
| `theseus/generators/g2_functional_equation.py` | NEW |
| `theseus/generators/g3_modular_transform.py` | NEW |
| `theseus/scripts/__init__.py` | NEW |
| `theseus/scripts/fetch_arxiv_abstracts.py` | NEW |
| `theseus/scripts/fetch_lmfdb_knowls.py` | NEW |
| `theseus/scripts/fetch_wiki_conjectures.py` | NEW |
| `theseus/tests/test_*.py` | 6 NEW (one per generator + cap test) |
| `theseus/tests/test_bandit_active_only.py` | NEW |

### Tests

Pre-fire baseline: 190 passing (theseus/tests/ scope).
Post-fire: 269 passing (theseus/tests/ scope; +79 new tests).
Regressions: 0.

### Commits (chronological)

| Hash | Description |
|------|-------------|
| `47a1fce3` | bandit + OOM + record cap fixes + 9 regression tests |
| `92c95918` | E2/E4/E5/F1 — 4 of 11 algorithms |
| `35660f2f` | G1 Galois twist + j-formula correctness |
| `dbcae6ae` | G2 FE claim emitter (after L1-heuristic kill) |
| `55f9266f` | G3 SL_2(Z) Hasse bound (strict 100% test) |
| `4115aa9f` | inventory.md → 36 of 40 active |

### Cap-pacing note for future fires

The 5M-record cap meant Fire #34's batch ended at 37 min instead of
the requested 90 min wall budget. Mathematically: the new generators
(e2/e4/e5/f1/g1/g2/g3) won't appear in batch output until the bandit
selects them — and `--batches 1` doesn't trigger bandit between-batch
selection (the bandit-select call gate is `i + 1 < args.batches`).
For Fire #35+ either:
- run with `--batches 2 --bandit` so bandit picks the second batch's
  set from the freshly-actives list, OR
- explicitly pass `--generators e2,e4,e5,f1,g1` etc to give the new
  algorithms a guaranteed slot, OR
- let the bandit settle: it learns yield curves over multiple fires
  and will eventually rotate the new actives in

### Schedule wakeup

`delaySeconds=120` (2 min) with same /loop prompt verbatim. Next
fire (#35) starts immediately; cap-pacing means each fire is ~30-40
min of wall budget at current generator throughput, plus the ~30-60
min Claude takes between fires to ship the next algorithm.

---

*Fire #34 closed. 36 of 40 generators ACTIVE. 4 remain (i1-i4 deferred).
Cap held cleanly; no OOM; bandit selection from actives only verified.*
