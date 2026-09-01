# Atlas loop log

Running log of what each 30-minute tick added and which single improvement it
made. Cron job `503c90b4`, cadence `7,37 * * * *`, started 2026-08-31, 48h budget.

---

## Iteration 1 — 2026-08-31 ~19:40 UTC (ticks 4–5)

**Harvest.** 221 → 246 worlds. Probes drawn: `region:traditional:oceania`,
`epoch:traditional:-1000_1`, `epoch:card:-1000_1`, `class:party`,
`epoch:card:2000_2015`, `region:board:europe`, `epoch:abstract:1750_1900`,
`epoch:card:2015_now`, `region:card:oceania`, `class:wargame`,
`epoch:dice:1970_2000`. Wikipedia enumeration: `Mesoamerican ballgame`
(60 links → 5 games), `History of video games` (30 links → 4 games).

**Deepened (10).** Haggle, Stone Age, Twister, The Resistance, Coup, Fictionary,
Puerto Rico, Secret Hitler, Cards Against Humanity, Hanabi.

**Improvement made: the enrichment tier.**

The coverage grid after tick 4 showed 211 of 221 worlds with no
`exogenous_process` at all. Diagnosis: the bulk harvest can only afford a lead
extract, and a lead paragraph almost never contains rules language — so the
declared grid was really a record of *what had been deepened*, not of what the
catalog holds.

Attempted fix was to batch full-article extracts. MediaWiki refuses: `exchars`
is capped at 1200 and `exlimit` is forced to 1 for whole-article extracts, so
full text costs one request per world. Confirmed against the live API rather
than assumed.

So the tick gained a middle tier between harvest and deepen:

| tier | volume | cost | what it produces |
| --- | --- | --- | --- |
| harvest | 25–100/tick | batched | name, found tags, lead extract |
| **enrich** | **60–80/tick** | **1 req each** | **full text → reclassified declared vector** |
| deepen | 4–6/tick | 1 req each | dossier, object model, state diagram, trace, conditions |

Enrich many, deepen few. 60 worlds enriched in ~40 s.

**Effect on coverage:**

| field | before | after |
| --- | --- | --- |
| `scoring_shape` | 6/7 | **7/7** |
| `turn_structure` | 3/11 | **6/11** |
| `exogenous_process` | 3/6 | **4/6** |
| `horizon` | 3/5 | **4/5** |

**Standing gaps (next iterations should target these):**
`loss_shape` still 2/5 — missing TOTAL_RUIN, NONE, OPPORTUNITY_ONLY, which is
awkward because TOTAL_RUIN is the precondition r0003's whole scope statement
rests on. `tractability` has no EXACT worlds. `information` has no PERFECT.
`turn_structure` missing SIMULTANEOUS, ACTION_POINT, VARIABLE_ORDER,
PRIORITY_QUEUE.

**Note on balance.** Enrich rate (60/tick) must keep pace with harvest rate
(25–95/tick) or the unclassified backlog grows. Raise `--enrich` if the
`unclassified` column climbs across consecutive ticks.

---

## Iteration 2 — 2026-08-31 ~20:20 UTC (ticks 6–8)

**Harvest.** 246 → 433 worlds. New probes drawn included `video:1958s`,
`class:wargame`, `epoch:card:1750_1900`. Wikipedia enumeration:
`Category:African games` (24 links → 19 games), `Category:Tile-laying games`
(dead, marked). Deepened: Diplomacy, Hex, Go, Russian Schnapsen, 304, All Fours,
Berserk.

**Improvement made: curated cell-filling seeds + two classifier bugs they exposed.**

Diagnosis first. After tick 6 the catalog held 323 worlds and **not one
push-your-luck game** — no Yahtzee, Farkle, Pig, Can't Stop or Incan Gold — so
`loss_shape=TOTAL_RUIN` was empty. That is the precondition r0003's entire scope
statement rests on. Cause: every probe slices by CLASS, EPOCH or REGION, which
are properties of surface and provenance. **No probe can reach a mechanism**, and
every remaining hole in the declared grid is mechanical. Wikipedia has no
press-your-luck category to crawl either — checked, returns zero members.

Added `seeds.py`: 130 curated worlds, each annotated with the grid cell it was
chosen to fill (charter v2 §41 active selection, applied to the catalog). Seeds
run before the probes each tick and skip the membership gate, being hand-verified.
`crawl.py seed-audit` then checks whether each seed actually *landed* in its
target cell — a seed that misses is a classifier bug made visible, and it is the
cheapest standing check the atlas has on its own classification quality.

The first audit read **14 landed / 34 missed**, which surfaced two real bugs:

1. **Enrichment skipped the worlds that needed it most.** The selector took
   `catalog_state='CATALOGUED'`, but a dice game whose lead paragraph contains
   the word "dice" gets `exogenous_process=IID` and is promoted to `SPECIFIED`
   on the strength of that one word — permanently excluding it from enrichment.
   Can't Stop, Yahtzee and Farkle were all stranded at ~600 characters. Fixed by
   selecting on `LENGTH(wp_extract) < 3000` instead of on state.

2. **No positive signal exists for determinism.** Chess and Nim had full text and
   still returned *no* `exogenous_process` at all, because every pattern needs a
   phrase like "perfect information" or "no element of luck" that abstract game
   articles simply never contain — they just never mention chance. Added a
   determinism-by-absence rule: across >3000 characters, the absence of all
   chance vocabulary is itself evidence. Gated on length so the silence means
   something. Also routed solved-game status to `tractability=EXACT`, the only
   cheap positive evidence for exact enumerability available from text.

**Effect:**

| metric | before | after |
| --- | --- | --- |
| seeds landing in target cell | 14 | **33** |
| `loss_shape` | 4/5 | **5/5** |
| `tractability` | 3/4 | **4/4** (EXACT now populated) |
| `information` | 4/5 | **5/5** |
| `horizon` | 4/5 | **5/5** |

Chess now reads `exo=NONE, info=PERFECT, tract=EXACT`; Can't Stop reads
`loss=TOTAL_RUIN`; Connect Four `NONE/PERFECT/EXACT`. Ran `reclassify` over 290
stored worlds to propagate both rules.

**One honest finding against the seed list itself.** Yahtzee still misses
TOTAL_RUIN — correctly. Yahtzee is not a total-ruin game: a bad roll takes a zero
in one category, it does not forfeit an accumulated pot. The seed annotation was
wrong, not the classifier. Farkle reads PARTIAL_DECAY and is genuinely arguable.

**Standing gaps for next iterations:** `turn_structure` missing SIMULTANEOUS,
ACTION_POINT, VARIABLE_ORDER, CONTINUOUS; `interaction` missing PARALLEL and
SEMI_COOPERATIVE; `exogenous_process` missing HIDDEN_FIXED. All have seeds queued
— 35 remain unharvested — so the next tick should land several without new code.

---

## Iteration 3 — 2026-08-31 ~20:45 UTC (tick 9)

**Harvest.** 433 → 597 worlds, 40 deepened, 142 conditions.

**Improvement made: classify against rules-bearing sections, not whole articles.**

Diagnosis came from pre-testing the queued seeds *before* harvesting them —
checking whether the classifier could even detect the cells they were meant to
fill. It could not, and the failures were not near-misses:

| world | want | got |
| --- | --- | --- |
| Pandemic | ACTION_POINT | **REAL_TIME** |
| Diplomacy | SIMULTANEOUS | **SOLITAIRE** |
| Minesweeper | HIDDEN_FIXED | **CONTINUOUS_TIME** |
| 7 Wonders | SIMULTANEOUS | **TEAM** |
| Agricola | ALLOCATE | exogenous **NONE** |

Cause, found by dumping section headers: **Pandemic's article is mostly
`Expansions` and `Spinoffs`**, one of which — *Pandemic: Rapid Response* — is a
real-time game. The base game inherited its spinoff's structure. Diplomacy's
`Other ways to play` mentions solo play, and the base game came back SOLITAIRE.
One stray mention in a 20k-character article outweighed the entire Gameplay
section, because scoring sums keyword hits over the whole text.

Added `wikipedia.rules_text()`: keeps the lead plus rule-bearing sections,
drops excluded subtrees (Expansions, Spinoffs, Reception, Tournament, Variants,
Legacy…) with hierarchy tracked so a subsection is dropped with its parent.
Pandemic 20906 → 6116 chars; Diplomacy 30670 → 6306. Wired into enrich, deepen,
and `reclassify` — stored extracts keep their `== Heading ==` markers, so the
filter applies retroactively with no re-fetching.

Then strengthened five patterns that had no chance of firing: SIMULTANEOUS,
ACTION_POINT, PARALLEL, HIDDEN_FIXED, and TEAM (which was matching any mention
of the word "teams" — that is why Chess read TEAM).

Added a **floor**: if the kept text falls under 1200 characters, widen to every
non-excluded section. Sushi Go! kept 440 of 3159 characters under the strict
filter and classified to nothing at all.

**Effect:**

| metric | before | after |
| --- | --- | --- |
| seeds in target cell | 33 | **41** |
| `interaction` | 6/8 | **7/8** (PARALLEL filled) |
| `turn_structure` | 7/11 | **8/11** (SIMULTANEOUS filled) |
| seeds unharvested | 35 | **1** |

Diplomacy now reads NEGOTIATION, Chess COMPETITIVE, Mastermind HIDDEN_FIXED,
Cartographers PARALLEL. Reclassified 370 worlds.

**A source limit, not a classifier bug.** The word "simultaneous" does not appear
*anywhere* in the Wikipedia articles for 7 Wonders or Pandemic — both canonical
examples of the mechanic. No pattern can recover what the source never says.
Cells like ACTION_POINT and VARIABLE_ORDER may not be reachable from Wikipedia
prose at all, and filling them may require either a mechanics-tagged source
(BGG, if credentials ever arrive) or hand review promoting worlds to `reviewed`.

**Balance problem, now the dominant bottleneck.** 406 of 597 worlds still hold
under 3000 characters. Harvest runs ~160/tick against an enrich default of 40,
so the unclassified backlog grows monotonically and the coverage grid decays
into a record of what was harvested first. Raised the `--enrich` default to 120
so the cron's own command line (which passes no `--enrich`) outpaces harvest.

**Open item.** Pandemic still reads REAL_TIME from its stored 12000-character
truncation; worth re-checking once it is re-enriched under the new path.

---

## Iteration 4 — 2026-09-01 ~16:15 UTC (tick 10)

**Note on cadence.** ~40 cron fires had queued while the session sat idle; they
all arrived at once. Cron fires only *enqueue* a prompt — nothing executes while
the REPL is idle — so the atlas had not advanced in the 19.5 h between tick 9 and
tick 10. Ran ONE iteration, not forty. 20.6 h of the 48 h budget elapsed.

**Harvest.** 597 → 696 worlds (catch-up tick, `--enrich 220` against the
406-world short-text backlog).

**Improvement made: the `review` command — and the ladder bug it exposed.**

The `method` ladder (`heuristic → source → reviewed → audited`) was **decorative**:
nothing in the system could set anything above `heuristic`. That mattered because
iteration 3 established some cells are unreachable from source prose — the word
"simultaneous" appears nowhere in the Wikipedia articles for 7 Wonders or
Pandemic, both canonical examples of the mechanic.

Added `crawl.py review --slug X --set FIELD=VALUE --note "..."`, with vocabulary
validation (rejects any value not in `taxonomy.VOCAB` and prints what is allowed)
and a `reviews` table recording old value, new value, note, reviewer and
timestamp for every change. `reviewed` sits deliberately *below* `audited`: it
means a knowledgeable human asserted it, not that anyone opened a rulebook.

Applied 14 field changes across 10 worlds — 7 Wonders and Sushi Go! (SIMULTANEOUS),
Pandemic (ACTION_POINT), Minesweeper (HIDDEN_FIXED), Dead of Winter
(SEMI_COOPERATIVE), Diplomacy and RoboRally (SIMULTANEOUS), Caylus
(VARIABLE_ORDER), Thebes and Patchwork (PRIORITY_QUEUE).

**The bug this surfaced.** Three reviews were silently overwritten minutes after
being applied. Cause: `enrich_batch` selects a batch, then spends minutes
fetching articles, then writes — a **read-then-write race**. A review landing in
that window was clobbered, and worse, `method` stayed `'reviewed'`, so the row
*claimed* human provenance while holding machine values. `deepen_batch` was worse
still: it had **no method filter at all**, so it could overwrite a reviewed world
on any tick.

Fixed both: added the method filter to `deepen_batch`'s SELECT, and guarded both
UPDATEs with `AND method IN ('heuristic','source')` so the check happens at write
time rather than only at select time. Verified by re-running `enrich_batch`
against reviewed rows — values held.

This was the whole merge policy being unenforced on the two paths that write the
most. `store.upsert_world` had always respected the ladder; nothing else did.

**Effect — declared grid now essentially complete:**

| field | before | after |
| --- | --- | --- |
| `exogenous_process` | 5/6 | **6/6** |
| `interaction` | 7/8 | **8/8** |
| `turn_structure` | 9/11 | **10/11** |
| `loss_shape`, `horizon`, `scoring_shape`, `information`, `tractability` | — | **complete** |

Seven of eight declared-vector fields fully covered. Only `turn_structure=CONTINUOUS`
remains, and it is arguably redundant with `REAL_TIME` — worth a taxonomy
decision next iteration rather than a hunt for a world.

**Next bottleneck is unchanged and now dominant:** ~450 worlds still carry no
`exogenous_process` because they hold under 3000 characters. Coverage of the
*vocabulary* is done; coverage of the *catalog* is not. Enrichment throughput,
not classifier quality, is the limit from here.

---

## Iteration 5 — 2026-09-01 ~16:45 UTC (tick 11)

**Harvest.** 696 → 868 worlds. `Category:Gambling games` (60 links → 37 games),
`class:sport` probe opened (+40).

**Improvement made: concurrent article fetching.**

Correcting iteration 4's closing claim, which was wrong. I wrote that enrichment
is "one HTTP request per world, which no amount of cleverness compresses." The
request *count* is indeed fixed — MediaWiki forces `exlimit=1` for whole-article
extracts — but the *wall-clock* is not. Those fetches are independent and
latency-bound, so they parallelise.

Added `wikipedia.full_text_many()`: a 6-worker thread pool over a shared
connection pool, with retry on 429/503 and the same identified User-Agent.
Measured on a 6-article sample: **2.04 s serial → 0.39 s parallel, 5.3x**.
`enrich_batch` now fetches the whole batch up front, then classifies and writes
from memory. Fetching first also shrinks the window in which a concurrent review
could be clobbered — the write-time method guard from iteration 4 closes it
entirely.

Deliberately capped at 6 workers. This is an identified, courteous client well
inside what Wikipedia tolerates, not a scraper.

*Caveat on the in-tick number:* the 63 s / 59-world figure logged during this
iteration was measured while a full tick was running concurrently and competing
for the network and the SQLite write lock. It is not a clean read. The isolated
5.3x fetch benchmark is the trustworthy one; a clean end-to-end measurement is
owed next iteration.

**Also closed: the `CONTINUOUS` question flagged last iteration.**

`turn_structure=CONTINUOUS` had sat empty for four iterations and was being
reported as a gap in the atlas's *knowledge*. It was actually a defect in the
*vocabulary*: no classifier rule could ever set it, and it drew no distinction
from `REAL_TIME` that anything could act on. Removed it. An unreachable value is
worse than one value fewer — it makes the coverage grid lie about what is known.

To stop that recurring, `report.py` now runs a **reachability check**: any
vocabulary value that no classifier rule can set is reported under "Unreachable
vocabulary (defect, not a gap)" rather than sitting quietly in the empty-values
column. The section is currently empty, which is the point.

**Declared grid — all eight fields now complete:**

| field | coverage |
| --- | --- |
| `exogenous_process` | 6/6 |
| `loss_shape` | 5/5 |
| `horizon` | 5/5 |
| `scoring_shape` | 7/7 |
| `information` | 5/5 |
| `interaction` | 8/8 |
| `turn_structure` | **10/10** |
| `tractability` | 4/4 |

**Remaining work is throughput, not design.** Every declared value is now
reachable and at least one world occupies each. The open number is the ~460
worlds still holding under 3000 characters, and that is now a wall-clock problem
with a 5x-faster tool pointed at it rather than a modelling problem.

### Iteration 5 addendum — the clean benchmark, and what it exposed

**Clean end-to-end enrichment: 97 worlds in 4.0 s = 0.041 s/world.** Roughly 25x
the serial path, measured with nothing else running, as owed above.

**But the backlog did not move: 621 → 621.** That was a bug, not noise.

`enrich_batch` selected on `LENGTH(wp_extract) < 3000`. Many real articles are
simply that short — Towie is 401 characters, Adji-boto 798, Hawalis 1633 — so
those worlds failed the test *after* being fetched and were re-selected on every
subsequent tick, forever. 216 worlds were being re-fetched indefinitely while
384 never-fetched worlds waited behind them. It is why the "backlog" appeared to
grow no matter how much enrichment ran.

Length was the wrong signal. Added an explicit `enriched_ts` column recording
that the attempt happened, with an idempotent `ALTER TABLE` migration in
`store.connect()` that backfills anything already past CATALOGUED. The selector
is now `enriched_ts IS NULL`, and the timestamp is stamped on the short-article
path too, since the attempt did occur.

**Then the real backlog drained in seconds — and hit a hard ceiling.**

Only 80 of the remaining 384 were eligible. The other 304 have **no English
Wikipedia article at all**: they are Wikidata-only rows whose entire description
is "2007 board game" or, in some cases, `None`.

| state | worlds | share |
| --- | --- | --- |
| enriched from full article | 564 | 65% |
| awaiting enrichment | 0 | 0% |
| no English article (ceiling) | 329 | 38% |

**Every enrichable world in the atlas is now enriched.** What remains is a
property of the source, not a queue, so `report.py` now reports it as a separate
"Source ceiling" section rather than letting it inflate the unclassified column.

**Next iteration's target, now clearly identified.** Those 329 are heavily
German- and French-published titles (Vikings, Sagani, Aqualin, Hepta). de.wikipedia
and fr.wikipedia very likely carry articles for a large share of them. Adding
multi-language fallback to the enrichment fetcher is the single highest-value
change available, and it raises the ceiling rather than working under it.

---

## Iteration 6 — 2026-09-01 ~17:20 UTC (tick 12)

**Harvest.** 868 → 939 worlds.

**Prediction from iteration 5 was wrong, and testing it first saved the work.**

I had named multi-language Wikipedia fallback as "the single highest-value change
available." Measured it before building it: of 180 worlds with no English article,
de.wikipedia covers **32**, and every other language is in single digits (ja 8,
sv 7, it 5, nl 5, fr 2, es 1). The union recovers roughly a third of the ceiling
— and every recovered article would then need a **second, non-English rule set**
for the classifier, since every pattern in `classify.py` is English. Large
maintenance surface, modest gain. Rejected, and recorded in the README so it is
not re-proposed.

**Improvement made instead: parallel deepening, and the research-item backfill.**

The real shortfall was in plain sight. The research item — a simulated turn trace,
or a clock trace for worlds with no turn boundary — is an explicit requirement for
*every* world, and only **60 of 939** had one. `deepen_batch` was capped at ~6 per
tick by a serial fetch plus a 0.6 s sleep per world.

Applied the same treatment enrichment got: concurrent fetch, no sleep, batched
commits. **0.072 s/world, ~20x.** Then backfilled every enriched world.

| metric | before | after |
| --- | --- | --- |
| worlds DEEPENED | 60 | **575** |
| artifacts | 240 | **2300** |
| conditions | 206 | 1222 → **910** after purge |
| trace coverage | 6% | **61% of all worlds, 92% of those with a source article** |

**Two things the backfill exposed.**

*Rate limiting.* Six sustained workers across ~900 requests drew **HTTP 429**.
The ceiling is real and I had overstepped what I called a courteous client.
Lowered to 4 workers, chunked with a pause between chunks — same total request
count, spread out. Politeness here is not decoration; the atlas depends on
continued access.

*A misfiring rule, caught by reading a generated dossier.* Monopoly's conditions
were: a Hasbro edition announcement, a note about the word being "derisive", and
a remark about Just Visiting. Cause: the BOUNDARY pattern matched a bare
"at least" / "maximum", which is ordinary prose — *"at least not being used as if
it is worth anything"* was filed as a rule of Monopoly. **45% of all BOUNDARY
rows were that noise.** Tightened the pattern to require a number within 40
characters, and purged the 312 unthresholded rows. A boundary with no threshold
is not machine-checkable, which was the stated reason thresholded conditions rank
first — the rule now matches its own justification.

**The traces are earning their keep.** Monopoly's reads `loss=None` while
bankruptcy is the game's defining mechanic, and `horizon=None` for a game that
ends when all but one player is eliminated. That is exactly what the artifact is
for: a structural vector is easy to nod along to, and a concrete event sequence
makes an incoherent one obvious. **Next iteration's target:** worlds whose trace
contradicts their known structure, starting with elimination games classified
`loss_shape=None`.

---

## Iteration 7 — 2026-09-01 ~17:45 UTC (tick 13)

**Harvest.** 939 → 1033 worlds. Crossed 1000.

**Improvement made: `coherence.py` — cross-checking the two independent
derivations of a world's structure against each other.**

The atlas derives structure twice by unrelated routes: the **declared vector**
(weighted keyword scoring over rules sections) and the **conditions table**
(whole sentences matched as win/lose/eliminate/boundary rules, thresholds
parsed). Neither is authoritative, but where they disagree at least one is
wrong — and the disagreement costs nothing to compute. Monopoly motivated it:
explicit elimination rules in its conditions table, `loss_shape` NULL, and a
generated trace showing a game that could never end.

Two modes. `report` lists contradictions and changes nothing. `repair` fills
NULLs where the conditions table is the more specific evidence, never touching a
reviewed or audited world, logging every change to the `reviews` table with
`reviewer='coherence-check'`. **A repair does not promote a world to `reviewed`**
— it is still machine inference, merely corroborated by a second machine route.
Verified: `method='reviewed'` count was unchanged by the 113 repairs.

**The check immediately caught a bug in its own evidence — before I applied it.**

The first run proposed `loss_shape=ELIMINATION` for 47 worlds. Sampling four
before applying:

| world | trigger sentence | real? |
| --- | --- | --- |
| Cucumber | "that player is out of the game" | **yes** |
| Weiss Schwarz | "the cards that are removed from the game" | no — cards |
| Andada | "captured seeds are removed from the game" | no — seeds |
| Anywoli | "those seeds are removed" | no — seeds |

Three of four were **components leaving play, not players**. The ELIMINATE
pattern matched "removed from the game" with no subject requirement, so a
coherence repair built on it would have written `loss_shape=ELIMINATION` across
47 worlds with no player elimination whatsoever — a corruption dressed as a
correction.

Tightened ELIMINATE to require a player/team/participant subject near the verb
(plus "last player standing"). Verified against the sample: all true positives
match, all three component cases rejected. Re-tested every stored trigger
sentence against the new rule — no re-fetching needed, the sentences are stored
— and **purged 131 of 228 ELIMINATE rows (57%)**. The elimination repair fell
from 47 to 15, and those 15 are trustworthy.

**Applied: 113 repairs.**

| repair | field | n |
| --- | --- | --- |
| terminate_without_horizon | horizon → VARIABLE | 65 |
| dice_without_process | exogenous_process → IID | 28 |
| elimination_without_loss_shape | loss_shape → ELIMINATION | 15 |
| race_without_horizon | horizon → RACE_TO_TARGET | 4 |
| deck_without_process | exogenous_process → DEPLETING_DECK | 1 |

Coherence now runs at the end of every tick, and is exposed as
`python crawl.py coherence [--repair]`.

**68 contradictions remain, reported and never auto-repaired** — both sides are
assertions, so silently picking one would manufacture false confidence.

**Next iteration's target, precisely diagnosed:** 44 of the 68 are
`interaction=SOLITAIRE but players_max>1`, and every sampled case is a card game
(Russian Schnapsen, Preferans, Lupfen, Four Color Cards). Cause: the SOLITAIRE
pattern includes `\bone player\b`, which matches "one player deals" and "one
player leads" — phrases in essentially every card-game rules section.

---

## Iteration 8 — 2026-09-01 ~18:10 UTC (tick 14)

**Harvest.** 1033 → 1138 worlds. 657 deepened, 2628 artifacts.

**Improvement made: fixed the SOLITAIRE misfire diagnosed last iteration, and
gave the coherence checker a standing guard against its return.**

The rule was `\bone player\b`. That phrase appears in essentially every
card-game rules section — "one player deals", "one player leads to the first
trick" — so 44 multiplayer card games (Preferans, Lupfen, Russian Schnapsen,
Four Color Cards) read as SOLITAIRE while their own `players_max` said 3–5.

Tightened it to require the phrase to be about how many players the *game takes*,
not which player acts: `for one player`, `one-player game`, `solo variant`,
`played alone`, `patience card game`, `without an opponent`. Verified on a
six-case sample — three genuine solitaire games match, three multiplayer card
games no longer do.

**Order mattered.** Reclassify first, then coherence. Reclassifying with the
fixed pattern *recovers* the right answer from the stored text (Preferans and
Russian Schnapsen both came back COMPETITIVE); coherence only clears the
stragglers it cannot recover. Running coherence first would have nulled all 44
and thrown away recoverable information.

**New standing guard: `solitaire_but_needs_two_players`.** If `interaction` says
SOLITAIRE but the source says the game needs 2+ players, the field is **cleared
to NULL, not guessed**. The player count is enough to know SOLITAIRE is wrong; it
is not enough to know whether the truth is competitive, cooperative or team.
"We do not know" is a truthful cell — "COMPETITIVE" would be a fabricated one,
and the coverage grid is only worth reading if its cells mean something. Lupfen
is the case in point: cleared to NULL, because nothing in its text settles it.

**Effect:**

| metric | before | after |
| --- | --- | --- |
| SOLITAIRE with players_min > 1 | 44 | **0** |
| total contradictions | 68 | **24** |
| SOLITAIRE worlds (genuine) | — | 64 |

Reclassified 661 worlds; coherence applied 24 further repairs (16 clears, 8
`loss_shape=ELIMINATION`).

**Next iteration's target.** The remaining 24 contradictions are now dominated
by two related classes: `exogenous=NONE but randomness present` (13) and
`information=PERFECT but randomness present` (9). Both come from the
determinism-by-absence rule added in iteration 2, which infers "no chance" from
the absence of chance vocabulary across a long article — and then a randomness
source is detected anyway. The rule should defer to positive evidence: if any
randomness source was found, absence-based determinism must not fire.

---

## Iteration 9 — 2026-09-01 ~18:15 UTC (tick 15)

**Harvest.** 1138 → 1188 worlds. 662 deepened, 2648 artifacts.

**My predicted fix was backwards, and looking at the data first caught it.**

Iteration 8 concluded the determinism-by-absence rule was over-firing and should
"defer to positive randomness evidence." Inspecting the 24 contradictions showed
the opposite. The flagged worlds were Tic-tac-toe, Connect Four, Gomoku,
Fanorona, Congkak, Sungka — **all genuinely deterministic perfect-information
games**. The determinism rule was right. Deferring to the randomness detection
would have deleted the correct answer in favour of the wrong one.

**The real defect was a taxonomy error.** `HIDDEN_INFO` and `SIMULTANEOUS_CHOICE`
were listed as *randomness sources*. Neither is a chance device: not knowing an
opponent's hand is an **information** property, and choosing at the same time as
someone else is a **turn structure** property. Both already have their own
fields. Recording them as randomness double-counted the same fact and produced
132 worlds "containing chance", 77 of which had no other source at all.

Removed both from the vocabulary and from the classifier. Removed the
`luck_factor` bonus they carried.

**Two deeper bugs surfaced while verifying the fix.**

*1. Reclassify could never retract.* After the vocabulary change, Gomoku and
Fanorona still carried the dead values: the fresh classification simply omitted
the key, and the update only ever writes keys that are present. A value could be
added or overwritten but **never erased**. List-valued fields are now written
even when empty — absence of evidence has to be able to withdraw a claim, or the
store only accumulates.

*2. `luck_factor` was fabricating a number.* With no randomness sources found it
returned **0.35** — a confident-looking "moderately lucky" for worlds where
nothing had been observed. Gomoku and Fanorona carried 0.35 on that basis. This
module's own docstring says a world with no keyword hits is left NULL rather
than defaulted; `_luck` was the one place violating its own contract. It now
returns **None** when there is no evidence either way, and 0.03 only when
determinism is positively attested. `_depth` was updated so an unknown is not
treated as a low value.

413 of 1188 worlds now carry a NULL `luck_factor`. That is a larger number than
before and a **more honest** one.

**Effect:**

| metric | before | after |
| --- | --- | --- |
| contradictions | 24 | **7** |
| worlds with phantom randomness | 132 | **0** |
| chess `luck_factor` | 0.35 | **0.02** |
| Gomoku / Fanorona `luck_factor` | 0.35 | **NULL** (honest) |

**Next iteration's target.** 7 contradictions left, no longer dominated by any
one class. The more useful target is the `information=PERFECT but randomness
present` remainder (4) — likely `REAL_TIME_PHYSICAL` firing on the word "timer"
in chess-clock contexts, which is a clock, not a randomiser.

---

## Iteration 10 — 2026-09-01 ~18:45 UTC (tick 16)

**Harvest.** 1188 → 1338 worlds. 715 deepened, 2864 artifacts, 984 conditions.

**Improvement made: `REAL_TIME_PHYSICAL` → `PHYSICAL_EXECUTION`, completing the
randomness-vocabulary cleanup begun in iteration 9.**

Printing the actual evidence behind each remaining contradiction showed four
distinct causes converging on one defect:

| world | matched text | verdict |
| --- | --- | --- |
| Bejeweled | "prevent a **timer** bar from reaching the end" | a clock, not chance |
| Perfection | "the **timer** dial is set to 60 seconds" | a clock, not chance |
| GNOME Chess | "Warzone 2100 (a **real-time** strategy game)" | a *different game*, named in passing |
| Oware | "PlayOK. Multiplayer, **real-time** Oware game" | an online-implementation line |

`REAL_TIME_PHYSICAL` matched the bare word "timer". A clock **constrains** play;
it does not randomise it — and `turn_structure=REAL_TIME` and
`horizon=CLOCK_LIMITED` already carry that meaning. Same error class as
HIDDEN_INFO and SIMULTANEOUS_CHOICE last iteration: an information or timing
property filed as a chance device.

Replaced with `PHYSICAL_EXECUTION`, matched only on genuine execution variance —
flicking, toppling, dexterity, steady hand. That *is* stochastic: a flicked disc
does not land where it was aimed. Verified: rejects "timer dial" and "real-time
strategy game", matches "flick a disc" and "the tower may topple". 15 worlds now
carry it, Crokinole among them, which is correct.

**Also fixed: cross-article contamination.** GNOME Chess and Oware inherited
structure from *other games mentioned in their own articles* — a software
listing and an online-play line. Added `online`, `software`, `implementation`,
`port`, `series`, `franchise` and similar to the excluded-section list.

**Second finding: the reachability check was itself too narrow.**

Iteration 5 added a check for vocabulary no rule can set, after `CONTINUOUS` sat
empty for four iterations while being a defect rather than a gap. But it only
iterated `DECLARED_VECTOR` — the eight scalar fields. Extending it to every field
the classifier has rules for surfaced **30 more unreachable values**:

| field | unreachable |
| --- | --- |
| strategies | 15 |
| algorithms | 10 |
| media | 2 (LARP, ESCAPE_ROOM) |
| solved_status | 2 (UNSOLVED, NOT_APPLICABLE) |
| randomness_sources | 1 (EXTERNAL_WORLD) |

The check that was meant to stop this class of problem had the same blind spot
as the thing it was checking. It now covers every field with rules, and the
report says plainly that these must not be read as gaps in what the atlas knows.

**Effect:**

| metric | before | after |
| --- | --- | --- |
| `information=PERFECT but randomness` | 4 | **1** |
| Bejeweled / Perfection randomness | REAL_TIME_PHYSICAL | **[]** (correct) |
| unreachable values surfaced | 0 (check too narrow) | **30** |

**A known limit, stated.** Three worlds still carry dead vocabulary
(HIDDEN_INFO ×3, REAL_TIME_PHYSICAL ×1, SIMULTANEOUS_CHOICE ×1) because they are
`method='reviewed'` and reclassify correctly refuses to touch them. The ladder is
working as designed; the cost is that a vocabulary change cannot reach reviewed
rows without a human. That is the right trade, but it should not be mistaken for
a clean sweep.

**Next iteration's target.** Decide the 30 unreachable values: add rules for the
ones worth having (`UNSOLVED` and `NOT_APPLICABLE` are cheap and would complete
`solved_status`), drop the aspirational strategy/algorithm tags that no source
text will ever contain, and mark the rest as hand-review-only.
