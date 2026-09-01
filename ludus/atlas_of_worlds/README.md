# Atlas of Game Worlds

A crawler and classifier that builds a broad, structurally-tagged catalog of games
— board, card, dice, video, RPG, puzzle, party, traditional, and sport — and
deepens the most informative of them into full dossiers with object models, state
transition diagrams and simulated turn/clock traces.

It exists to serve `ludus/bench`. The bench cannot promote a circuit past
`ABLATION_SUPPORTED` because its six real worlds occupy roughly two cells of the
structural grid (see `ludus/atlas/CIRCUIT_MATURITY.md`). This catalog is the
sampling frame that makes charter v2 §41 — *choose the next world by expected
information gain* — computable rather than a hunch.

## The two layers

| layer | what it is | trusted? |
| --- | --- | --- |
| **FOUND** | genre tags, categories, descriptions as the source states them | **No.** It is the negative control. The bench's claim is that retention is predicted by decision structure and *not* by genre; that is only demonstrable if genre is a column you can regress against. |
| **DECLARED** | exogenous process, loss shape, live axes, horizon, scoring shape, information, interaction, turn structure, tractability | Yes — this orders the work. Every field exists because some circuit's scope statement depends on it. |

Every declared value carries a **method**: `heuristic` (machine-inferred from
source text) → `source` → `reviewed` → `audited`. Heuristic values place a world
on the grid and rank it for deepening; they are **not evidence about a named
game**. The store's merge policy never lets a weaker method overwrite a stronger
one. This mirrors `ludus/bench/RULES_AUDIT.md` for the same reason.

## Catalog ladder

```
CATALOGUED -> SPECIFIED -> DEEPENED -> IMPLEMENTED -> AUDITED
```

- **CATALOGUED** — name, source, found tags
- **SPECIFIED** — declared vector filled heuristically from the lead extract
- **DEEPENED** — full article read; conditions extracted; dossier, object model,
  state diagram and turn/clock trace written to `worlds/<slug>.md`
- **IMPLEMENTED** — a `World` subclass exists in `ludus/bench` and `verify.py` passes
- **AUDITED** — rules checked against a real rulebook by the operator

The first three rungs are automatic. The last two are deliberately not.

## Three throughput tiers

A tick does the same work at three very different volumes, because the costs
differ by two orders of magnitude:

| tier | volume/tick | cost | produces |
| --- | --- | --- | --- |
| harvest | 100–200 | batched (20 titles/request) | name, found tags, lead extract |
| **enrich** | 120+ | 1 request each, **6 in parallel** | full text → declared vector |
| **deepen** | 120+ | 1 request each, **6 in parallel** | dossier, state diagram, trace, conditions |

MediaWiki caps `exchars` at 1200 and forces `exlimit=1` for whole-article
extracts, so the request *count* for enrich and deepen is irreducible — one per
world. The wall-clock is not: `wikipedia.full_text_many()` runs a 6-worker pool
and measured ~25x on enrichment (0.041 s/world) and ~20x on deepening
(0.072 s/world).

**Enrichment tracks attempts, not text length.** The selector is
`enriched_ts IS NULL`. It used to be `LENGTH(wp_extract) < 3000`, which
permanently re-selected worlds whose articles are genuinely short (Towie is 401
characters) — 216 worlds were re-fetched every tick while 384 never-fetched ones
waited behind them.

## The source ceiling

Enrichment reads English Wikipedia. Roughly **35% of harvested worlds have no
English article at all** — Wikidata-only rows whose entire description is
"2007 board game". They can never be classified beyond that, so `report.py`
reports them as a *ceiling*, not a backlog, and they are excluded from the
enrichment queue rather than retried forever.

Multi-language fallback was measured and rejected: of 180 such worlds,
de.wikipedia covers 32 and every other language is in single digits. Recovering
~35% of the ceiling would also require a second, non-English rule set for the
classifier, which is a large maintenance surface for a modest gain.

## Hand review

```bash
python crawl.py review --slug pandemic_board_game \
    --set turn_structure=ACTION_POINT --note "Four actions per player turn."
```

Some cells cannot be recovered from source prose at all — the word
"simultaneous" appears nowhere in the Wikipedia articles for 7 Wonders or
Pandemic, both canonical examples of the mechanic. `review` sets fields
directly with vocabulary validation, promotes the world to `method='reviewed'`,
and records old value, new value, note, reviewer and timestamp in the `reviews`
table.

`reviewed` sits deliberately *below* `audited`: it means a knowledgeable human
asserted it, not that anyone checked a rulebook. Enrichment and deepening both
re-check `method` **at write time**, so an in-flight tick cannot silently
overwrite a review.

## Sources

- **Wikidata** (CC0, keyless) — the breadth engine. ~9,500 non-video game
  entities plus 183,579 video games, with inception dates reaching the third
  millennium BCE, country of origin, player counts and derivation edges.
- **Wikipedia** (CC BY-SA) — article text for classification, plus `Category:`
  and `List of …` / `History of …` enumeration for the long tail Wikidata misses:
  playground games, regional variants, sport rule structures.

**BoardGameGeek is not used.** Its XML API returned `401 Unauthorized` on every
endpoint (`xmlapi`, `xmlapi2`, `api.geekdo.com`) as of 2026-08-31 and now
requires registered credentials. A BGG adapter can be dropped in beside
`wikidata.py` if credentials arrive; nothing downstream depends on the source.

## Probes

Harvest is organised as **probes** — slices of the space (a class, an epoch, a
continent, a decade of video games). The crawler *rotates* probes rather than
draining one, because the atlas is graded on coverage of the declared grid, not
on headcount. A thousand more push-your-luck dice games would raise the row count
and teach nothing; `ludus/atlas/BACKLOG.md` makes the same argument about the bench.

Probes that yield nothing are marked exhausted and retried occasionally.
Wikipedia enumeration targets that yield nothing are marked dead and skipped.

Titles found via Wikipedia enumeration pass a **membership gate**: their QID must
resolve as an instance of a game class. Without it, "List of dice games" injects
*Advantage gambling* and *Amerigame* into the atlas and the coverage numbers stop
meaning anything.

## Files

| file | role |
| --- | --- |
| `wikidata.py` | SPARQL harvester, probe definitions, membership gate |
| `wikipedia.py` | article text, category/list enumeration, QID resolution |
| `taxonomy.py` | the classifier vocabulary — both layers |
| `classify.py` | heuristic classification, condition extraction, novelty scoring |
| `deepen.py` | object model, state diagram, turn/clock trace, dossier |
| `store.py` | SQLite schema and merge policy |
| `crawl.py` | the tick: harvest → classify → deepen → record |
| `report.py` | atlas-level coverage grid, matrices, lineage graph → `ATLAS.md` |
| `atlas.db` | the catalog |
| `worlds/*.md` | per-world dossiers |
| `ATLAS.md` | the current map, regenerated each tick |

## Running

```bash
python crawl.py tick --probes 8 --per-probe 40 --deepen 6 --wp-titles 60
python report.py
python crawl.py status
python crawl.py reclassify     # backfill after a classifier change
```

`reclassify` matters on a long run: without it, early rows keep whatever the
classifier believed on tick 1, and the coverage grid becomes a record of *when* a
world was harvested rather than *what it is*.

## The research item

Every deepened world gets a simulated trace, generated from its declared vector:

- **turn-based worlds** get an event log — draws, option sets, stop decisions,
  bank/bust events, with pot and bust probability tracked
- **worlds with no turn boundary** get a **clock trace** — ticks, contention,
  infractions accumulating toward an elimination threshold

The trace is not a claim about how the published game plays. It exists because a
structural vector is easy to nod along to and hard to check: forcing the atlas to
emit a concrete sequence of events makes an incoherent classification obvious. A
world tagged `STOP` with `loss_shape=NONE` produces a trace where the stopping
decision visibly does not matter — that is a bug report about the classification.

## Conditions

The `conditions` table is the "five fouls and you're benched" layer: win, lose,
eliminate, boundary, terminate and penalty rules pulled as whole sentences, with
thresholds parsed where they exist. Sentences carrying an explicit threshold rank
first, because those are the ones that are machine-checkable rather than prose.

Working examples from the current catalog: basketball's *7 fouls → one free
throw* and *10 fouls → two free throws*; association football's *maximum of
eleven players*; Uno's *first player to score 500 points wins*.
