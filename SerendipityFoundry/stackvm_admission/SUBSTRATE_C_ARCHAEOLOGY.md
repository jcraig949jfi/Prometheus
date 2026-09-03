# Substrate C Archaeology — Discovery Only

**Provenance separation.** Everything in this document is DISCOVERY EVIDENCE
from `F:\Prometheus\archive` (~207 MB, 2,290 files, ten sub-projects). **None
of it was used to design, tune, justify, or parameterize the stackvm-v1
canonical null.** The null was built from interpreter/opcode/operator source
only, before this survey's findings were read into the design (see
`STACKVM_NULL_PROVENANCE.json`, which cites only `vm.py` and `adapter.py`).
Read-only throughout: no file modified, no service touched, no HTTP issued, no
database opened.

---

## ⚠ TIME-SENSITIVE, NOT ARCHAEOLOGY

`F:\Prometheus\archive\bitfrost-core\bitfrost-core\src\api\.env` exists (not
opened), and
`...\bitfrost-core\reports\frontier_model_inventory.md` **prints API key
prefixes for seven providers in plaintext** (`sk-or-v1-…`, `gsk_8dn…`,
`ghp_JDm…`, `csk-mwv…`, `AIzaSy…`, `xai-O63…`). **Treat as exposed; rotate.**
This is the only finding in the survey that is time-sensitive, and it is
unrelated to the scientific mission.

---

## Headline

Substrate C is not ten unrelated projects. It is **one research program,
restarted eight times in twenty-one days** (2026-03-09 → 2026-03-30). And:

> **All five phenomenon classes recur independently — four of them multiple
> times, in codebases with no shared code.**

More consequentially: **in at least four of the ten projects, a P1–P4 defect
is the direct cause of the project's headline result, and three of those
results still stand as claims in the program's evidence documents.**

## Independent recurrence of the five classes

**P1 DEGENERATE SELECTION — four unrelated codebases. Strongest class.**
- `noesis_v1`: the top 50 records by quality have **exactly one distinct
  value**; 66 *distinct* chains sit at the global maximum 0.6588, caused by a
  scalarization collision between two different score vectors. One of eight
  scoring dimensions (`execution`) has **one distinct value across all 6,641
  records** — zero information, traceable to a pre-filtered operation library
  where 389/474 entries have `test_success_rate` exactly 1.0. And worse than
  flat: of 1,129 chains scored more than once, **1,013 (90%) got a different
  quality on re-evaluation**; maximum within-chain spread (0.1588) equals the
  entire dynamic range of the fitness function. Signal-to-noise ≈ 1.
- `prometheus-v1`: speciation with `min_species_size = 2` over 13 strategies
  with 13 distinct topologies ⇒ every species size 1 ⇒ tournament selection is
  a no-op and every parent pair is a self-pair. Deterministic from shipped
  code; never executed.
- `bitfrost-core` (Gleipnir): the arbiter is unimplemented and unconditionally
  returns `fidelity_score=0.85`. Every genome-substrate pair scores
  identically. The published *"Mean Stability Gradient 0.68 vs 0.23"* is a
  mean over a two-valued fallback ladder.
- `fennel`: no ranking exists at all — `random.choice` over archive cells,
  ignoring fitness. Drift by construction.
- **Clean negative:** SETI's 109 elites show zero fitness ties.

**P2 INSTRUMENT-SHAPED FAILURE — the most damaging class.**
- `seti-v1`: the *complete* error log is 5 identical lines,
  `Probe failed for elite (1, 4): 'blocks.24.hook_resid_pre'`. Root cause is
  in a **different project**: `mech/overnight_layerband.py` hardcodes
  `LAYER_BANDS = [(10,14),(15,19),(20,24)]` for a 28-layer model; SETI ran on
  a 24-layer model (valid indices 0–23). The exception is swallowed. **Five
  cycles completed and the entire "Telescope" half produced zero output.**
- `aethon`: 82.2% of anomaly captures sit within 0.10 of their own detection
  threshold — and that threshold is a **heritable gene**, so evolution can
  manufacture anomalies by lowering the instrument. 88% of characterizations
  are `input-specific`, produced by testing `> 0.5` against a metric whose
  median is 0.795, on a budget where 140/167 anomalies saw exactly one
  transfer prompt. Written up as *"No false positives."*
- `prometheus-v1`: 167 of 167 `EXECUTE FAILED` lines are the identical HTTP
  429; only 86 of ~253 pairs completed.

**P3 BIMODAL WITH STERILE GAP — two textbook instances.**
- `noesis_v1`: `compression` splits 3,199 chains at 0.0 / **38 in the valley**
  / 1,898 at ≥0.5 — and of 20 chains promoted to building blocks, **zero came
  from the valley**. Valley members never reproduce.
- `aethon`: 168 records at exactly 0.0, **the interval (0.0, 0.2657) is
  completely empty**, 126 records above. Of the zero-mode records, **0 of 168
  ever entered the characterization battery** versus 93.7% of the other mode.

**P4 NEUTRAL SELF-REPRODUCTION — and in two projects it is rewarded.**
- `noesis_v1`: mutation can select the operation it is replacing, with no
  unchanged-detection; **644 of 3,259 mutation records (19.8%) are
  re-emissions**. Promotion to building blocks is by raw appearance count, so
  **18 of 20 promoted blocks got a majority of their "appearances" from
  mutation** — and the corpus headline claim *"293× amplification"* rests on
  that promotion statistic.
- `seti-v1`: **36 of 109 archive entries (33%) are byte-identical duplicates**,
  because the MAP-Elites cell coordinate derives from properties of the
  stochastic LLM output rather than of the genome. Neutral copies are awarded
  *extra archive slots* — selected for, not merely tolerated.
- `prometheus-v1`: 106 of 107 pattern files share one `pattern_name`, from a
  harvest prompt that is never `.format()`ted. 214 of 321 exported artifacts
  are one deterministic constant.

**P5 CONVERGENT INDEPENDENT SOLUTION — recurs, and one instance is a false
positive.**
- `noesis_v1`: 393 chains found by both an ancestry-free uniform sampler and a
  lineage-descended mutation strategy — but only 47 scored identically under
  both, directly confirming the P1 non-stationarity.
- `aethon`: byte-identical 146-character outputs from independently seeded
  runs; and `null_markov` and `qwen_uniform` both archived the output
  `Planet` in the same cell — an n-gram babbler and a 7B model converging.
- `vesta`: an explicit independent-rediscovery counter — 122 of 645 taxonomy
  rows were produced by ≥2 model lineages.
- **⚠ FALSE POSITIVE, flagged:** the 106/107 identical `pattern_name` in
  `prometheus-v1` looks like spectacular convergent rediscovery. It is the P4
  prompt bug. Any P5 analysis over that directory measures a defect.

## The most decisive single file in 207 MB

`archive/aethon-v1-scripts/aethon/archive/null_markov/map_elites.json` — a
**pure n-gram babbler with no LLM at all** reaches best fitness **0.9312**,
beating `llama_uniform` (0.8779) and `qwen_uniform` (0.8380). The fitness
function does not discriminate reasoning from random text. Neither this nor
the SETI error log is mentioned in any summary document.

The program **pre-specified the test that would have caught it** and never
built it: `AETHON_Prompt_Library_and_Handoff_From_Claude.md:262-278` describes
a `--fitness-mode random` drift control; no such config exists.

## Prior art the current program should know about

`archive/bitfrost-root-docs/BitFrost_Living_Ideas_Document_v1.md` already
defines an evidence-wiki design with a **claim lifecycle
(Observed → Replicated → Confirmed, plus Disputed and Retired)**, evidence
grades, an ownership table, in-line retractions, and five validation
principles including *"Density is not evidence"* and *"Nulls and controls come
first."* It also pre-specifies a P5 test that was never run (*">50% seed
emergence, ≥3 independent lineages, chi-square p<0.05"*).

`archive/reasoning-precipitation-standalone/.../docs/phases.md` is the most
formal preregistration in the corpus: five phases each with explicit GO and
NO-GO gates, numeric thresholds, and pre-committed null-result triage. **The
project never ran** — every `outputs/` directory contains only `.gitkeep`.

## What this changes about priority

1. **Correcting the standing record is the highest-value, lowest-cost work
   available on this corpus.** Three headline claims are artifacts and none
   requires new compute to correct.
2. **A standard six-check audit** — score-dimension variance, within-genotype
   fitness spread, error-histogram vs resource ceiling, no-op mutation rate,
   valley-propagation test, cross-lineage duplicate detection — would run
   against every archive here and against future runs. **Every project failed
   at least two of the six; none of the six was in anyone's protocol.**
3. **Replication exists in exactly one place** (aethon: 9 seeds + 3 nulls).
   Every cross-project claim currently rests on a single run.
4. `noesis_v1` is a **partial** extraction — six named design docs, `prompts/`,
   `docs/`, `the_maths/`, and the v2 DuckDB are all absent — while a live
   `F:\Prometheus\noesis` tree (966 files) is authoritative. For the other
   seven projects the archive is the only copy.

## Effect on the five frozen candidates

**None promoted, none demoted on the strength of recurrence.** Independent
recurrence of P1–P5 in unrelated codebases raises the prior that these are
*generic defect classes of this kind of research program* rather than
substrate-specific phenomena — which, if anything, **lowers** the scientific
interest of the stackvm-v1 instances and **raises** the value of the
cross-cutting audit. That is a discovery-side judgement and carries no
admission weight.

## Not examined

MLflow DB (live-service constraint), ~110 MB of `.npz` embedding archives
(the novelty-metric substrate — **the most valuable unexamined asset**, since
loading them would directly test whether the novelty signal is degenerate),
four large prose documents read only by header, and the live `F:\BitFrost\`
and `F:\bitfrost-mech\seti-pipeline_v2\` trees which are outside the archive
and likely more current.
