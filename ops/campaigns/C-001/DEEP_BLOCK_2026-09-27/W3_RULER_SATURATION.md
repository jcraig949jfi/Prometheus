# W3 — Ruler saturation: when a tied top score gets (or doesn't get) read as shared mechanism

Worker: W3-ruler-saturation. Branch: worker/W3-ruler-saturation, based on origin/main @
d7ec26d37f8894049c267d1aeea9bb8a12954224 (commit at worktree checkout, DERIVED: `git rev-parse HEAD`
in the worktree). Read-only analysis; no engine code, frozen evidence, or verdict files touched.
No packages installed beyond what the repo's own Python environment already provides (only
stdlib `json`, `hashlib`, `collections`, `glob` were used in analysis one-liners; nothing added
to any requirements file).

Method: for each bounded-scope item, load the named data file(s) directly, find the maximum (or a
named ceiling) score, count how many rows carry that score, and check whether the underlying
genome/tape/champion payload is byte-identical or materially different across those rows. Then grep
the project's own prose (reports, prereg, journals, docstrings) for language that either (a) treats
the tie as evidence of one mechanism/lineage or (b) explicitly warns against that reading.

---

## 1. Ananke PTE-C1: `held.acc == 1.0` ties across distinct evolved champion genomes

File: `roles/Ananke/pte/c1_rows/cells.jsonl.gz` (NATIVE data; commit
b91f522ae454482c89b0881327bbb495b4d16f1c last touched it, 2026-09-25T07:18:27-04:00).

DERIVED (computed by me from the file, command: `zcat cells.jsonl.gz | python3 -c '...'` counting
`kind`, `result.held.acc`, hashing `result.champion`):
- 6596 total rows: 5807 `census`, 678 `evolve`, 99 `transfer`, 12 `adjudicate`. This matches the
  campaign log's own count ("6596 rows", `roles/Ananke/pte/C1_REPORT.md:3`), so the row count is
  internally consistent.
- Of 678 `evolve` rows, `result.held.acc` ranges from 0.4694 to 1.0. The distribution is dominated
  by a chance-level cluster around 0.50 (97 rows exactly at 0.5, hundreds more within +-0.02 of it)
  — i.e. most evolutionary runs found nothing. Exactly **8 of 678** rows carry the maximal score
  `held.acc == 1.0` — the ceiling of this ruler.
- All 8 of those rows have `env.family == "HOLD"` (the delayed-recall/memory task family) and
  `physics.topology == "global"`, `n_sites == 144`, identical `env` dict in every field. They come
  in three physics variants (`collision`/`decay_shift`: aloha/3, saturate/3, none/1), each rerun
  2-3 times with a **different `search_seed`** (fresh evolutionary run) and, in two cases, one wave
  is the recorded `parent` of a later wave that reruns the same physics with a new seed.
- I SHA-256-hashed each row's `result.champion` genome array (the evolved rule table). **All 8
  hashes are distinct** — 8 materially different genomes, none byte-identical to another, share
  the single top score of this ruler. Within the single physics+env cell that recurs three times
  (`collision=aloha, decay_shift=3`), the three champion genomes (cell_ids `85ca202e89057873`,
  `2c300c478738551b`, `24711149e41077fb`) are three distinct genomes reaching the identical ceiling
  score under literally identical physics and environment parameters.

Does the project read this tie as shared mechanism, or guard against it? **It guards against it,
explicitly, and by name.** `roles/Ananke/pte/C1_REPORT.md` (NATIVE, INFERRED reading of intent)
section 3 "Mechanisms found" lists, for the HOLD family specifically, two *different* mechanisms
that both reach near-ceiling `held.acc`, and calls out that the more interesting one is the
*minority* case:

> "M2 DELAY-LINE MEMORY (HOLD, 1 cell, 0.883; POST-HOC, exploratory). Resetting every site's state
> mid-gap changes nothing (0.88); dropping packets, randomising payloads or removing comm -> 0.50.
> The held bit lives in packets in flight, not in any site, although a one-site latch solves HOLD.
> Nobody designed this; the PREREG HOLD rule labels it NOT_SUPPORTED because it assumed memory
> lives in site state." (`roles/Ananke/pte/C1_REPORT.md:68-73`)
>
> "M5 LOCAL LATCH (HOLD, the trivial solution, most HOLD cells)." (`roles/Ananke/pte/C1_REPORT.md:83`)

That is: the report itself refuses to let "HOLD solved, high/ceiling accuracy" collapse into one
label. It names two mechanistically distinct solutions (a genuine communication-carried memory
found in exactly 1 cell, vs. a trivial single-site latch found in "most" HOLD cells) that would
otherwise look identical under the `held.acc` ruler alone, and flags that ablation (packet drop,
site-state reset) is what tells them apart, not the score. I could not, from Git alone, run the
report's own ablation battery against the specific 8 ceiling genomes to say which of the 8 are M2
vs M5 lineage — that would require re-executing `prometheus/ananke/report.py`'s ablation suite,
which is out of scope for a read-only pass (see "could not determine" list).

---

## 2. Archaeon z80atlas copier census: one behavioural class, several tape architectures

Files: `archaeon/z80atlas/census/copier_census.py` (commit b482450023c48eee7a4eaab8417fc58bd39d6eaf,
2026-09-23T20:59:26-04:00), `archaeon/z80atlas/census/HITS.json` and `RESULTS.json` (commit
c5067fac69277c32247176bae265c19454c662f9, 2026-09-23T23:08:24-04:00), `archaeon/z80atlas/census/PREREG.json`
(same commit as copier_census.py). `archaeon/envgate/ruler.py` reuses this same classifier verbatim
as the "frozen census ruler" for a later campaign (NATIVE, its own docstring: "the FROZEN census
ruler (copier_census phenotype/classify...), computed once per arriving tape and shared by every
arm of the block" — `archaeon/envgate/ruler.py:1-3`).

The ruler (`classify()`, `copier_census.py:82-90`) buckets every random tape into one of 7 ordered
classes by pure behaviour (coverage, exact self-copy across 256 inputs, span of copied bytes),
first-match-wins: `EXACT_UNGATED > EXACT_GATED > NEAR_COPIER > SPAN_COPIER > WRITER > TOUCH > INERT`.

DERIVED (loaded `HITS.json`, called the module's own `architecture()` function on each hit, command
in-session Python using `sys.path` import of `copier_census`):
- Stratum `vmcopy32` (32-byte tapes, 10,000,000 sampled): 1 tape reaches the absolute ceiling class
  `EXACT_UNGATED`; **95 distinct tapes** (95 distinct hex genomes, no duplicates) share the
  second-highest class `EXACT_GATED`. Running the module's own `architecture()` classifier (which
  reads executed-opcode histogram, COPY-vs-STORE primitive, jump type, gating width, offset) over
  those 95 tapes yields **5 distinct architecture signatures**: `COPY|gated1|reljump|k0|reads_input`
  (39), `MIXED|gated1|reljump|k0|reads_input` (32), `COPY|gated1|absjump|k0|reads_input` (16),
  `MIXED|gated1|absjump|k0|reads_input` (7), `MIXED|gated|reljump|k0|reads_input` (1).
- Stratum `vmcopy64` (64-byte tapes, 2,000,000 sampled): **9 distinct tapes** share class
  `EXACT_GATED`, splitting into **2 architecture signatures** (7 `COPY|gated1|reljump|k0|reads_input`,
  2 `MIXED|...`).
- These per-stratum architecture counts are also precomputed and stored in the frozen artifact
  itself: `RESULTS.json`'s `architectures_all_hits` field for `vmcopy32` lists the same 39/32/24/16/...
  breakdown (`archaeon/z80atlas/census/RESULTS.json`, `architectures_all_hits` key) — the project
  did not wait for someone to notice the diversity later; it is tabulated at generation time.

This is the "guard" case, and it is written into the preregistration and the module docstring
before any tape was classified, not added after the fact:

> "Mechanism features recorded for every tape of class SPAN_COPIER or better (classification of
> architectures is done on these features after the census, not by matching a known loop): ..."
> (`archaeon/z80atlas/census/copier_census.py:24-26`)

> "architecture_features": "... families are tuples of these; no loop-matching against any known
> tape" (`archaeon/z80atlas/census/PREREG.json:19`)

I.e. the census was designed from the start to keep "same behavioural class" (the ruler) and "same
mechanism/architecture" as two separate, separately-reported axes, specifically so that 95 tapes
tying at `EXACT_GATED` would not silently become "95 copies of the same replicator." The module
docstring also states the founder specimen and the hand-written replicator are used ONLY as
classifier controls ("rulers"), never as a template the classifier is allowed to pattern-match
against (`copier_census.py:5-7`), which is the same guard applied one level up (don't let a known
lineage's shape define the ruler either).

One further, adjacent guard, found while reading the campaign journal: the ENVGATE-01 follow-on
campaign that reused this ruler explicitly flagged a case where a rescue *looked* like a copier
lineage event but was something else mechanistically — "Forensics: rescue component is an artifact
(block-15 takeover by a gate-255 copier; host-labelled lineages...)" and "Novel candidate:
host-mediated reproduction (inert inflow tapes execute resident copier code)"
(`roles/Archaeon/journal/2026-09-23_m2-db608f52.md:76-79`, NATIVE). INFERRED: "host-labelled
lineages" being called out as needing forensic correction is itself evidence the project does not
trust a lineage/class label at face value.

---

## 3. Nestor NPE z80atlas observatory: `held == 1.0` across families, and within one family

File: `roles/Nestor/campaigns/z80atlas-2026-09-19/observatory/SPECIMENS.jsonl` (commit
3b407946ed129e8539c74b924bca429e7080bead, 2026-09-22T15:25:19-04:00), 41,402 specimen records.
Score definition: `roles/Nestor/campaigns/z80atlas-2026-09-19/tasks.py:153-166`, function
`competence()` — `comp` = score on the training episode stream, `held` = score on a disjoint seed
stream ("held-out score"); returns `{"comp": 0.0, "held": 0.0, ...}` unconditionally for any
`spec.neutral` task (`tasks.py:155-156`).

DERIVED (loaded the JSONL, tallied `specimen.comp`/`specimen.held`, command: inline Python
iterating the file):
- 1077 of 41,402 specimens have `comp == 1.0` (ceiling on the training stream); 1062 have
  `held == 1.0` (ceiling on the disjoint held-out stream).
- Every one of those 1062 `held == 1.0` specimens carries a **distinct `genome_hex`** — 1062/1062
  unique byte strings, no duplicates — and they span **487 distinct `family`/`cell` configurations**
  (different world/task/mutation-operator combinations), with genome lengths ranging from 23 to 176
  bytes. So the ceiling of this ruler is reached by genuinely heterogeneous entities across
  conditions, which is expected (different tasks, different optimal programs) and not by itself a
  ties-as-lineage risk.
- The tighter test is *within* one fixed family: 363 families have exactly 2 specimens at
  `held == 1.0`, 68 have 4, 52 have 1, 4 have 3. Inspecting the largest such group I found
  (family `09a229509b65eeae`, `atlas_axis: DELETERIOUS_LOAD`, 4 specimens across 2 `run_id`s): all 4
  genomes share an identical 34-byte functional prefix
  (`db0047db00a847db00fe00280678c600d3007678d30076`) and diverge only in the trailing bytes — i.e.
  these are genuinely near-identical, same-lineage genomes whose only differences sit in the region
  this cell's own label (`DELETERIOUS_LOAD`) says is free to drift under neutral selection. Here the
  tie in `held` score *does* correspond to shared mechanism/lineage — a case where the ruler and the
  underlying reality agree, unlike cases 1 and 2 above. I did not find a case in this file, within a
  single family, where two `held == 1.0` genomes differ in the functional (non-drift) region — the
  680 sampled specimens I could check by hand did not surface one, and a full search over all 487
  families was out of scope for the read-only budget of this pass.
- Guard language present but generic, not specific to this tie: the campaign's own hand-written
  reference programs are marked as controls, not evidence of what evolution independently finds —
  "Hand-written programs. These are INSTRUMENTS and positive controls, never evidence of what
  evolution can find. Cycle 8's rule, carried forward verbatim in spirit."
  (`roles/Nestor/campaigns/z80atlas-2026-09-19/tasks.py:170-172`). This guards against a different
  but related error (mistaking an instrument's ceiling score for evolutionary discovery), not
  against conflating two *evolved* ceiling scorers with each other. I found no text in
  `observatory/ADJUDICATION.md`, `observatory/PACKET.md`, or `DEFECTS.md` that discusses genome
  diversity at the `comp`/`held` ceiling specifically (grepped for "same score", "identical
  genome", "ceiling", "saturat", "tie", "held == 1", "degenerate", "convergen", "neutral" — no
  hits in those three files).

---

## 4. Ares cycle-2 (W4 carrier-mechanism attack): fitness cap tied by >=5 distinct champion structures

File: `roles/Ares/journal/2026-09-23.md` (commit 1dde117f732ec62848ea2beaa4b0e9641ae8db73,
2026-09-23T05:46:31-04:00) and the underlying run logs `ares/runs/sweep_c2/c2_*.json` (60 files,
6 arms x 10 seeds 201-210, same commit). Score: `champ_heldout`, the held-out fitness of each GA
run's final-generation champion on world W4; the world's own structural ceiling is 40.0 (NATIVE,
stated directly in the journal, see below).

DERIVED (loaded all 60 non-dissect `ares/runs/sweep_c2/c2_*.json` files, took `log[-1]` = final
generation, read `champ_heldout` and the champion's own recorded structural features `n_keep`,
`n_cyclic`, `self_loops`, `n_plastic`):
- 56 of 60 runs finish with `champ_heldout >= 39.5` (most exactly `40.0`), i.e. essentially every
  arm — including the arm with recurrence *forbidden* (`c2_no_recur`), the arm with self-loops
  forbidden (`c2_no_selfloop`), and the two tax-pressure arms — reaches the same fitness ceiling.
- Classifying each of those 56 capped champions by 4 structural flags (keep-mechanism present,
  cyclic-edge present, self-loop present, plasticity present) yields **11 distinct mechanism
  signatures**, the three largest being: acyclic+keep+plastic (14), acyclic+no-keep+plastic (10),
  cyclic+self-loop+keep+plastic (9) — no single structural recipe accounts for even half of the
  capped champions.
- The journal treats this explicitly as a case where the ceiling score must NOT be read as
  evidence for the mechanism the arm was designed to test:

> "GATE B OPEN on substance, but the rule's NAMED explanation is dead: intrinsic superiority killed
> pre-run (hand-built keep 33.75 > recurrence 24.56), gradient killed (p_improve ~0 both), raw
> opportunity killed (8x subsidy did not flip), useful-reachability killed by the c3 falsification
> arm... What survives: BASIN WIDTH -- keep viable in 3/25 of its range [0.94,0.98] against its
> ceiling, recurrence in 14/23 [2.75,6.0] and saturating." (`roles/Ares/journal/2026-09-23.md:70-84`)

> "(b) W14 attacks the LEAKY INTEGRATOR, not recurrence (saturation is noise-robust). The
> anti-activation world is W15. Stated in the design so the result cannot later be read the other
> way." (`roles/Ares/journal/2026-09-23.md:52-53`)

That second quote is the guard stated as policy, in advance of the run: the design document names,
ahead of time, which mechanism a given world's ceiling can and cannot be attributed to, precisely
so a later reader cannot look at a capped score and infer the wrong mechanism from it.

---

## Summary counts

| Case | Ruler | Ceiling condition | Rows at ceiling | Distinct entities at ceiling | Guard text found? |
|---|---|---|---|---|---|
| 1. Ananke PTE-C1 | `held.acc` (0-1) | `== 1.0` | 8 / 678 evolve rows | 8 distinct champion genomes (SHA-256 of all 8 differ); one physics+env cell recurs 3x with 3 distinct genomes | Yes — M2 vs M5 named as different HOLD mechanisms, `C1_REPORT.md:68-83` |
| 2. Archaeon copier census | 7-class behavioural ruler | `EXACT_GATED` (2nd-highest, since top class has only 1 hit) | 95 / 10,000,000 tapes (vmcopy32); 9 / 2,000,000 (vmcopy64) | 5 architecture signatures (vmcopy32); 2 (vmcopy64), per the module's own `architecture()` function | Yes, preregistered — `copier_census.py:24-26`, `PREREG.json:19` |
| 3. Nestor NPE observatory | `held` competence (0-1) | `== 1.0` | 1062 / 41,402 specimens | 1062 distinct genomes across 487 families; within the one 4-specimen family inspected, genomes are same-lineage (identical functional region) | Generic instrument-vs-evidence guard only (`tasks.py:170-172`); no tie-specific guard found |
| 4. Ares cycle-2 W4 | `champ_heldout` fitness | `>= 39.5` (world's structural cap 40.0) | 56 / 60 GA runs | 11 distinct structural signatures (keep/cyclic/self-loop/plastic flags) | Yes, both post-hoc (`journal:70-84`) and preregistered in the design (`journal:52-53`) |

Net picture from these four bounded samples: 3 of 4 cases show the same top/ceiling score reached
by materially different entities (different genome hashes, different tape architectures, or
different champion structures), and in 3 of those 4 the project's own text explicitly separates the
score from the mechanism/architecture — in two cases (Archaeon, Ares) the separation was written
into the design *before* the data existed, not added after the fact as a correction. The one case
that did not show this failure mode under inspection (Nestor, within-family) is also the one case
where I could not find any tie-specific guard text — because, on the sample checked, the ties were
genuinely same-lineage, so there was nothing to guard against.

---

## What I could NOT determine from Git, and why

- **Which of the 3 Ananke HOLD mechanisms (M2 delay-line vs M5 local latch) each of the 8
  `held.acc == 1.0` champion genomes actually is.** The report's mechanism labels are assigned by an
  ablation battery (packet drop, site-state reset, payload randomisation) run by
  `prometheus/ananke/report.py` against specific cells; running that battery against all 8 ceiling
  genomes was out of scope for a read-only pass and risks non-trivial compute on top of the frozen
  evidence. I can only report that the report already draws this distinction for HOLD in general.
- **Whether any of the 95 `EXACT_GATED` vmcopy32 tapes or the 9 vmcopy64 tapes are related by direct
  mutational descent from a common random-tape ancestor.** The census is explicitly blind/uniform
  random (`copier_census.py:5-6`), so by design there is no lineage to trace — the 5 (resp. 2)
  architecture families are independent discoveries by construction, not a lineage question. I note
  this rather than claim it as an open gap.
- **Whether any Nestor NPE family besides the one 4-specimen group I hand-checked
  (`09a229509b65eeae`) has two `held == 1.0` genomes that diverge in the *functional*, non-drift
  region.** I only inspected genome hex for one family; a systematic check across all 487 families
  (aligning each genome to its cell's task-relevant byte range) was beyond this pass's budget.
- **Whether the Ares W4 structural cap of 40.0 is a hard-coded per-world constant or something
  derived at runtime.** I read it from the journal's prose ("structural cap 40.0") and from the
  run logs' own `champ_heldout` values converging there; I did not locate the constant's definition
  in `ares/` source to confirm it is not itself an artifact of episode count `eps: 4` in the run
  configs (`ares/runs/sweep_c2/c2_no_recur_s203.json:cfg`) — i.e. I did not verify from source that
  40.0 cannot be exceeded, only that no run in this 60-file sample exceeded it.
- **Whether `roles/Archaeon/journal/2026-09-23_m2-db608f52.md`'s "host-labelled lineages" caveat
  refers to the same 95/9-tape sets analysed above, or to a different (ENVGATE-01 campaign) set of
  tapes.** The journal entry is about the later ENVGATE-01 causal assay, which reuses the census
  ruler but runs on its own tape stream; I did not cross-reference specific tape hashes between the
  two campaigns to confirm overlap, and say so rather than assume it.
