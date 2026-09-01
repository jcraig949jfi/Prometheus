# ATLAS OF GAME WORLDS — build record

**Built:** 2026-08-31 → 2026-09-01, nine looped iterations (ticks 1–15).
**Code:** `ludus/atlas_of_worlds/`. **Operator instruction:** *"Can we build a crawler?
Find all the games… classify them… go broad first, then deep."*
**Status of every claim below:** `heuristic` unless a world's dossier says otherwise.
Nothing here is an audited claim about a named commercial game.

---

## 1. Why this exists

`ludus/atlas/CIRCUIT_MATURITY.md` records the bench's central blocker: **no circuit
has been promoted past `ABLATION_SUPPORTED`.** r0003 is the only circuit with genuine
prospective cross-world evidence, and it is blocked at `PARTNER_ROBUST` because it
reads 0.0000 and 1.0000 in one FOUNDRY world depending only on its SELECT partner.
Three SELECT circuits have *zero* untouched test worlds.

The diagnosis: tag the six real bench worlds on their structural properties and five
of six come out as *(iid-or-deck draw, total-ruin loss, solitaire, linear accumulation,
exact)*. **That is not six worlds. It is about two cells.** Charter v2 §41 says choose
the next world by expected information gain — but that choice was being made from a
handwritten list of five candidates, which is a hunch, not a selection procedure.

This atlas is the sampling frame that makes §41 computable.

**It does not itself supply worlds to the bench.** A catalogued world is a paper
record; a bench world is a `World` subclass that `verify.py` passes. The ladder keeps
those apart on purpose.

---

## 2. The two-layer doctrine

| layer | content | trusted? |
| --- | --- | --- |
| **FOUND** | genre tags, categories, source descriptions | **No.** It is the negative control. The bench claims retention is predicted by decision structure and *not* by genre; that is only demonstrable if genre is a column you can regress against. |
| **DECLARED** | exogenous process, loss shape, live axes, horizon, scoring shape, information, interaction, turn structure, tractability | Yes — this orders work. Every field exists because some circuit's scope statement depends on it. |

`loss_shape` is the clearest case: r0003's scope says *"death forfeits the ENTIRE
pot."* `TOTAL_RUIN` vs `PARTIAL_DECAY` is therefore not a descriptive nicety, it is
the precondition the circuit's whole claim rests on.

### Method ladder

```
heuristic  ->  source  ->  reviewed  ->  audited
```

`heuristic` is machine classification from source text. `reviewed` means a
knowledgeable human asserted it. `audited` means someone checked a rulebook — only
the operator, working `ludus/bench/RULES_AUDIT.md`, can produce it. This mirrors the
bench's own epistemic states for the same reason.

Enrichment, deepening and reclassification all re-check `method` **at write time**, so
an in-flight tick cannot overwrite a reviewed value.

---

## 3. Sources

- **Wikidata** (CC0, keyless) — breadth. ~9,500 non-video game entities plus 183,579
  video games, with inception dates into the third millennium BCE, country of origin,
  player counts and derivation edges. 121 rotating probes slice by class × epoch ×
  continent × decade so variety is *enforced*, not hoped for.
- **Wikipedia** (CC BY-SA) — article text for classification, plus `Category:` and
  `List of…` / `History of…` enumeration for the long tail.
- **Curated seeds** (`seeds.py`) — 130 worlds each annotated with the grid cell it was
  chosen to fill. This is §41 applied at catalog level.

**BoardGameGeek was not used.** Its XML API returned `401 Unauthorized` on every
endpoint (`xmlapi`, `xmlapi2`, `api.geekdo.com`, any user agent) on 2026-08-31; it now
requires registered credentials. An adapter can be dropped in beside `wikidata.py` if
credentials arrive — nothing downstream depends on the source.

**Multi-language fallback was measured and rejected.** Of 180 worlds with no English
article, de.wikipedia covers 32 and every other language is in single digits. Recovering
~35% of the ceiling would also require a second, non-English rule set for the classifier.

---

## 4. Current state (tick 15)

| metric | value |
| --- | --- |
| worlds catalogued | 1,188 |
| deepened (dossier + trace + diagram) | 662 |
| research-item coverage | 93% of worlds with a source article |
| conditions extracted | 914 |
| artifacts | 2,648 |
| declared-grid coverage | **8/8 fields complete** |
| open contradictions | 7 |

Oldest catalogued world: Senet, c. 2620 BCE (`DEEP_ANTIQUITY`).

### The source ceiling

**~35% of harvested worlds have no English Wikipedia article at all** — Wikidata-only
rows whose entire description is "2007 board game". They can never be classified
beyond that. This is reported as a *ceiling*, not a backlog: every enrichable world in
the atlas has been enriched.

---

## 5. The research item

Every deepened world carries a **simulated trace** generated from its declared vector:
a turn-event log, or a **clock trace** for worlds with no turn boundary (ticks,
contention, infractions accumulating toward an elimination threshold).

The trace is **not** a claim about how the published game plays. It exists because a
structural vector is easy to nod along to and hard to check. Forcing the atlas to emit
a concrete event sequence makes an incoherent classification obvious — a world tagged
`STOP` with `loss_shape=NONE` produces a trace where the stopping decision visibly does
not matter. That is a bug report about the classification.

It worked as designed. Monopoly's trace showed a game that could never end
(`loss_shape=NULL`, `horizon=NULL`) despite bankruptcy being its defining mechanic.

### Conditions — the "five fouls and you're benched" layer

Win / lose / eliminate / boundary / terminate / penalty rules pulled as whole
sentences, thresholds parsed. Real output: basketball's *7 fouls → one free throw* and
*10 fouls → two free throws*; association football's *maximum of eleven players*;
Uno's *first player to score 500 points wins*.

---

## 6. Failure metabolization (charter §31, §42)

The durable value of this build is not the row count. It is the defect record. Every
one of these was found by **looking at sampled rows before acting**, and several would
have silently corrupted the catalog.

| # | Defect | How it was caught | Scale |
| --- | --- | --- | --- |
| 1 | Enrichment selected on `catalog_state`, so a dice game whose *lead paragraph* said "dice" was promoted on one word and permanently excluded from full-text enrichment | Can't Stop, Yahtzee, Farkle stranded at ~600 chars | 3 canonical worlds silently thin |
| 2 | No positive signal existed for determinism — abstract games never *say* "perfect information", they just never mention chance | Chess and Nim returned no `exogenous_process` at all | all abstracts |
| 3 | Whole-article classification let a **Spinoffs** section decide the base game | Pandemic → `REAL_TIME` (from *Pandemic: Rapid Response*); Diplomacy → `SOLITAIRE` | systemic |
| 4 | `method` ladder unenforced on the two paths that write most; a read-then-write race clobbered reviews while leaving `method='reviewed'` — rows *claimed* human provenance while holding machine values | 3 reviews vanished minutes after being applied | integrity |
| 5 | Enrichment selected on `LENGTH(wp_extract) < 3000`; real articles are often shorter (Towie 401 chars), so they were re-fetched **forever** | Backlog never moved: 621 → 621 | 216 re-fetched, 384 starved |
| 6 | `BOUNDARY` matched a bare "at least" — *"at least not being used as if it is worth anything"* was filed as a rule of Monopoly | reading a generated dossier | **45%** of BOUNDARY rows |
| 7 | `ELIMINATE` matched "removed from the game" with no subject — *seeds* and *cards* being removed read as player elimination | sampling 4 rows before applying a repair | **57%** of ELIMINATE rows; would have written `loss_shape=ELIMINATION` across 47 worlds |
| 8 | `SOLITAIRE` matched `\bone player\b` — "one player deals" appears in every card-game rules section | coherence contradiction vs `players_max` | 44 multiplayer card games |
| 9 | `HIDDEN_INFO` / `SIMULTANEOUS_CHOICE` classed as **randomness sources**. Neither is a chance device; both already had their own fields | contradiction against the determinism rule | 132 worlds "containing chance", 77 with no other source |
| 10 | Reclassification could **never retract** — a value could be added or overwritten but not erased, so dead vocabulary persisted indefinitely | Gomoku/Fanorona kept removed values | all list fields |
| 11 | `luck_factor` returned **0.35** when no randomness was found — a confident-looking number for worlds where nothing had been observed, violating the module's own "leave NULL rather than default" contract | Gomoku, a deterministic abstract, carried 0.35 | 413 worlds |
| 12 | `turn_structure=CONTINUOUS` was **unreachable vocabulary** — no rule could set it, so it sat in the "empty values" column reporting a gap in knowledge that was really a defect in the list | reachability audit | made the grid lie |

### Two standing lessons

**Predicted fixes were wrong three iterations running.** Iteration 5 predicted
multi-language fallback was "the single highest-value change" — measurement showed a
third of the value at twice the cost. Iteration 8 predicted the determinism rule was
over-firing and should defer to randomness detection — the determinism rule was
*right*, and deferring would have deleted correct answers in favour of wrong ones.
Iteration 6's prediction that enrichment "no amount of cleverness compresses" was
wrong within one turn.

**Only the rows settled it.** Every correct diagnosis came from printing sampled rows
and reading them. This is charter §35's cheating assumption turned inward: the atlas's
own flattering explanation of its state was wrong more often than not.

**Prefer NULL to a fabricated cell.** Repeatedly the right fix was to *withdraw* a
value rather than replace it — `interaction` cleared when the player count proves
SOLITAIRE wrong but nothing proves what is right; `luck_factor` NULL when no evidence
exists. The coverage grid is only worth reading if its cells mean something.

---

## 7. Coherence checking

`coherence.py` derives structure twice by unrelated routes — the **declared vector**
(weighted keyword scoring) and the **conditions table** (whole sentences with parsed
thresholds) — and compares them. Neither is authoritative, but where they disagree at
least one is wrong, and the disagreement is free to compute.

`repair` fills NULLs where the conditions table is the more specific evidence, never
touching a reviewed or audited world, logging every change with
`reviewer='coherence-check'`. **A repair does not promote a world to `reviewed`** — it
is still machine inference, merely corroborated by a second machine route.

Contradictions where *both* sides are assertions are **reported and never
auto-repaired**; silently picking one would manufacture false confidence.

---

## 8. What this does not establish

- **No claim about any named commercial game.** Every rule is `HYPOTHESIZED` under
  charter v1 §8 until audited against a rulebook.
- **No world has been admitted to the bench.** `IMPLEMENTED` requires a `World`
  subclass passing `ludus/bench/verify.py`; the atlas has produced none. GATE-W1 is
  untouched by this work.
- **No transfer measurement.** The atlas supplies candidates and ranks them. It does
  not score circuits, and nothing here moves any cell of `transfer_matrix.json`.
- **Classification is English-Wikipedia-bounded** and thin for 35% of rows.

---

## 9. What it unblocks

1. **`ludus/atlas/BACKLOG.md` is stale** and can now be regenerated from data rather
   than intuition. It still says *"all four worlds are push-your-luck"* — Coloretto and
   Lucky Numbers have since been built.
2. **For Sale remains the correct next build.** It is catalogued, it carries a
   registered r0012 prediction, and it is the bench's first simultaneous-information
   cell.
3. **`loss_shape=TOTAL_RUIN` candidates now exist in quantity** — the precondition
   r0003's promotion depends on, which the bench previously could not vary.
4. **Charter §41 is now arithmetic.** Rank unbuilt worlds by declared-vector distance
   from the worlds a given circuit was measured in, on the dimension that circuit's
   scope statement names.

---

## 10. Operation

```bash
cd ludus/atlas_of_worlds
python crawl.py tick --probes 8 --per-probe 40 --deepen 60 --wp-titles 60
python report.py                      # -> ATLAS.md
python crawl.py coherence --repair
python crawl.py seed-audit            # did each seed land in its target cell?
python crawl.py review --slug X --set FIELD=VALUE --note "..."
python crawl.py reclassify            # after any classifier change
```

Ran on a 30-minute cron (`7,37 * * * *`) across a 48-hour block, per §7's hourly-looping
authorisation. **Caveat recorded honestly:** cron fires only *enqueue* a prompt — nothing
executes while the session is idle — so the atlas advanced only while the session was
actively processing. One 19.5-hour gap occurred between ticks 9 and 10 for this reason.

Wikipedia rate-limits: 6 sustained workers across ~900 requests drew **HTTP 429**.
Concurrency is now 4, chunked with pauses. The atlas depends on continued access.

Generated per-world dossiers live in `ludus/atlas_of_worlds/worlds/*.md`.
`atlas.db` and `crawl.log` are gitignored; the database is rebuildable by re-running
the crawler, but the dossiers are committed because they are the deliverable.
