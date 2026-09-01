================================================================================
EXTERNAL REVIEW PACKET
ATLAS OF GAME WORLDS -- structural catalog for the LUDUS world-supply seat
================================================================================
Prepared:        2026-09-01   draft, unaudited
Location/Code:   F:\Prometheus\ludus\atlas_of_worlds\  (14 modules)
Role docs:       F:\Prometheus\roles\Ludus\ATLAS_OF_WORLDS.md  (build record)
                 F:\Prometheus\roles\Ludus\ROLE.md  section 9
Artifacts:       ATLAS.md (regenerated per tick), atlas.db (SQLite, gitignored),
                 worlds/*.md (715 dossiers), reports/LOOP_LOG.md
Version/Hash:    branch ludus/atlas-of-game-worlds
                 e85bfa6b9  atlas (688 files, 96,491 insertions)
                 5e4f68c76  bench itself (50 files, 13,047 insertions)
Elapsed:         ~23.3 h of an authorised 48 h block; 16 ticks, 10 iterations
Headline:        1,338 worlds catalogued, 715 with generated research items,
                 all 8 declared-vector fields covered. THIRTEEN classifier or
                 store defects found, ELEVEN fixed. No world admitted to the
                 bench; no transfer measured; every rule HYPOTHESIZED.

Format note: this packet is a single plain-ASCII block, unlike review packets
#1 and #2 which are markdown briefs. The whole file is the copy-paste unit.

--------------------------------------------------------------------------------
1. CLAIM / SUBJECT UNDER REVIEW
--------------------------------------------------------------------------------
CLAIM: a broad, structurally-tagged catalog of games can be built automatically,
and doing so converts charter v2 section 41 (choose the next world by expected
information gain) from a hunch into arithmetic.

The motivating diagnosis is in ludus/atlas/CIRCUIT_MATURITY.md: no circuit has
been promoted past ABLATION_SUPPORTED. Tag the six real bench worlds on their
structure and five of six land in one cell -- (iid-or-deck draw, total-ruin
loss, solitaire, linear accumulation, exact). That is roughly two cells, not
six worlds, and it is why nothing promotes.

WHAT WOULD FALSIFY THE CLAIM
  (a) The declared vector fails to discriminate: if worlds that differ
      mechanically get identical vectors, the schema is too coarse and the
      ranking it produces is noise. NOT observed -- the vector separates
      Can't Stop (IID/TOTAL_RUIN) from Chess (NONE/PERFECT/EXACT) from
      Cartographers (DEPLETING_DECK/PARALLEL).
  (b) Machine classification is too noisy to rank on. PARTIALLY OBSERVED --
      see section 9; thirteen defects, several of which would have corrupted
      the catalog had they not been sampled before acting.
  (c) The catalog cannot reach the cells the bench needs. NOT observed for
      TOTAL_RUIN (now populated); PARTLY observed for ACTION_POINT and
      SIMULTANEOUS, which required hand review because the source text does
      not contain the words.

NOT CLAIMED: that any world is bench-ready, that any rule is correct, or that
any transfer measurement has been made.

--------------------------------------------------------------------------------
2. METHOD / SETUP / SUBSTRATE
--------------------------------------------------------------------------------
Python 3.12.10, stdlib + requests only. SQLite (WAL). No API keys.
Windows 11, F: drive. Console forced to UTF-8 (cp1252 cannot encode Senet,
weiqi, or most of the catalog).

MODULE MAP
  wikidata.py    103 rotating SPARQL probes; membership gate
  wikipedia.py   article text, category/list enumeration, concurrent fetch,
                 rules-section extraction
  taxonomy.py    the two-layer vocabulary
  classify.py    heuristic classification, condition extraction, novelty
  coherence.py   6 cross-checks between the two independent derivations
  deepen.py      object model, state diagram, turn/clock trace, dossier
  seeds.py       123 curated worlds, each annotated with the cell it fills
  store.py       schema, merge policy, migrations
  crawl.py       the tick + CLI (tick/status/reclassify/review/coherence/
                 seed-audit)
  report.py      coverage grid, source ceiling, lineage graph -> ATLAS.md
  utf8.py        stdout encoding

THREE THROUGHPUT TIERS (costs differ by two orders of magnitude)

  Tier      Volume/tick  Cost                    Produces
  -------   -----------  ---------------------   -------------------------
  harvest   100-200      batched, 20/request     name, found tags, lead
  enrich    120-220      1 request each, 4 par.  full text -> declared vec
  deepen    60-120       1 request each, 4 par.  dossier, diagram, trace

MediaWiki caps exchars at 1200 and forces exlimit=1 for whole-article extracts,
so the request COUNT is irreducible (one per world). Wall-clock is not:
concurrent fetch measured 5.3x on an isolated 6-article sample; end-to-end
enrichment 0.041 s/world, deepening 0.072 s/world.

--------------------------------------------------------------------------------
3. KEY DEFINITIONS
--------------------------------------------------------------------------------
TWO LAYERS, ONLY ONE TRUSTED

  FOUND     genre tags, categories, source descriptions. Recorded in full,
            NEVER used to order work. It is the negative control: the bench
            claims retention is predicted by decision structure and NOT by
            genre, which is only demonstrable if genre is a regressable column.

  DECLARED  exogenous_process, loss_shape, live_axes, horizon, scoring_shape,
            information, interaction, turn_structure, tractability.
            Orders all work. Each field exists because some circuit's scope
            statement depends on it. Example: r0003's scope says "death
            forfeits the ENTIRE pot", so TOTAL_RUIN vs PARTIAL_DECAY is the
            precondition its whole claim rests on, not a descriptive nicety.

METHOD LADDER (enforced at WRITE time, not just at select time)

  heuristic ..... machine classification from source text
  source ........ asserted by a structured source field
  reviewed ...... a knowledgeable human asserted it (9 worlds, 20 fields)
  audited ....... someone checked a rulebook (0 worlds -- operator only)

CATALOG LADDER
  CATALOGUED -> SPECIFIED -> DEEPENED -> IMPLEMENTED -> AUDITED
  The first three are automatic. The last two are deliberately not.

--------------------------------------------------------------------------------
4. INPUTS / SOURCES / BASELINES
--------------------------------------------------------------------------------
  Source          Licence     Role                     Volume available
  -------------   ---------   ----------------------   --------------------
  Wikidata        CC0         breadth engine           ~9,500 non-video game
                                                       entities + 183,579
                                                       video games
  Wikipedia EN    CC BY-SA    text for classification  32 list pages,
                                                       37 categories
  seeds.py        curated     cell-filling             123 worlds

PROBE DESIGN: 103 probes slice by class x epoch x continent x decade, and are
ROTATED rather than drained. Rationale: the atlas is graded on coverage of the
declared grid, not headcount. A thousand more push-your-luck dice games would
raise the row count and teach nothing.

BOARDGAMEGEEK REJECTED. Its XML API returned 401 Unauthorized on every endpoint
(xmlapi, xmlapi2, api.geekdo.com) under any user agent on 2026-08-31; it now
requires registered credentials. An adapter can drop in beside wikidata.py if
credentials arrive -- nothing downstream depends on the source.

MULTI-LANGUAGE FALLBACK MEASURED AND REJECTED. Of 180 worlds with no English
article: de 32, ja 8, sv 7, it 5, nl 5, pt 3, ru 3, fr 2, pl 2, es 1. Union
recovers roughly a third of the ceiling, and every recovered article would then
need a second, non-English rule set, since every pattern in classify.py is
English. Large maintenance surface, modest gain.

--------------------------------------------------------------------------------
5. PROCEDURE
--------------------------------------------------------------------------------
One tick, idempotent and resumable at any point:

  1. curated seeds first (so cell-filling worlds are never crowded out)
  2. rotate probes, favouring least-run; harvest Wikidata
  3. one rotating Wikipedia category or list page (the long tail)
  4. membership gate: a linked title must resolve as an instance of a game
     class, else discarded (without it, "List of dice games" injects
     "Advantage gambling" and "Amerigame")
  5. batch lead extracts (20/request)
  6. classify -> declared vector; score novelty against what is already held
  7. enrich: full text for worlds never fetched, 4 workers
  8. deepen: dossier + object model + state diagram + trace + conditions
  9. coherence repair
 10. report

NOVELTY SCORING: rarity of a world's declared vector against the current
catalog, exp(-3 * count/total) averaged over filled fields. This is section 41
applied at catalog level -- a world in an already-crowded cell is not deepened
however famous it is.

SCHEDULING: 30-minute cron, 7,37 * * * *. CAVEAT RECORDED: cron fires only
ENQUEUE a prompt; nothing executes while the session is idle. One 19.5 h gap
occurred between tick 9 and tick 10 for this reason. The loop is not unattended.

--------------------------------------------------------------------------------
6. PRIMARY RESULT
--------------------------------------------------------------------------------
CATALOG STATE (tick 16)

  Metric                            Value
  -------------------------------   -------------------------------------
  worlds catalogued                 1,338
  DEEPENED (dossier+trace+diagram)    715
  SPECIFIED                            96
  CATALOGUED (thin)                   527
  method=reviewed                       9 worlds / 20 fields
  artifacts                         2,864
  conditions extracted                984  (259 carry a threshold)
  lineage relations                   206
  provenance rows (reviews table)     249  (20 human, 229 coherence)
  ticks completed                      16

DECLARED-GRID COVERAGE -- all eight fields complete

  Field                Values seen   Unclassified
  ------------------   -----------   ------------
  exogenous_process        6/6            934
  loss_shape               5/5           1096
  horizon                  5/5           1087
  scoring_shape            7/7           1025
  information              5/5           1144
  interaction              8/8            877
  turn_structure          10/10          1042
  tractability             4/4              0

  NOTE: "values seen" means every legal value is occupied by at least one
  world. "Unclassified" is the count of worlds with NULL in that field, and
  it is LARGE -- see section 10. Vocabulary coverage is complete; catalog
  coverage is not.

SOURCE CEILING

  State                          Worlds   Share
  ----------------------------   ------   -----
  enriched from full article        809     60%
  awaiting enrichment                 0      0%
  no English article (ceiling)      554     41%

  Every enrichable world has been enriched. The remainder is a property of
  the source, not a backlog.

RESEARCH ITEMS
  716 worlds carry a simulated trace (690 turn traces, 26 clock traces).
  That is 53% of all worlds and 88% of those with a source article.

TEMPORAL AND CULTURAL SPREAD
  Epochs occupied: 8 of 8. DEEP_ANTIQUITY 12, ANCIENT 7, MEDIEVAL 3,
  EARLY_MODERN 3, INDUSTRIAL 21, MODERN 53, DIGITAL 187, CONTEMPORARY 245.
  Regions occupied: 14.
  Genuine oldest: Senet, c. 2620 BCE. (See defect D13 -- two older-looking
  rows are misdated.)

--------------------------------------------------------------------------------
7. DELIVERABLE + ACCEPTANCE CRITERIA
--------------------------------------------------------------------------------
  Every world reachable by a probe is catalogued .................... yes
  Every enrichable world has full-text classification ............... yes
  Every deepened world has object model + state diagram ............. yes
  Every deepened world has a turn OR clock trace .................... yes
  Conditions carry parsed thresholds where the text has them ........ yes
  All declared-vector values occupied by >=1 world .................. yes
  Genre recorded but never used to order work ....................... yes
  Reviewed values survive automated passes .......................... yes
  atlas.db rebuildable from code alone .............................. yes
  Any world admitted to the bench ................................... NO
  Any rule audited against a rulebook ............................... NO

THE RESEARCH ITEM: every deepened world gets a simulated trace generated from
its declared vector -- a turn-event log, or a clock trace for worlds with no
turn boundary (ticks, contention, infractions accumulating to a threshold).

It is NOT a claim about how the published game plays. It exists because a
structural vector is easy to nod along to and hard to check; forcing a concrete
event sequence makes an incoherent classification obvious. It worked: Monopoly's
trace showed a game that could never end (loss_shape NULL, horizon NULL) despite
bankruptcy being its defining mechanic. That single reading produced defects
D6 and, indirectly, D7.

CONDITIONS -- the "five fouls and you're benched" layer. Real extracted output:
  basketball ......... 7 fouls  -> one free throw
  basketball ......... 10 fouls -> two free throws on all subsequent fouls
  assoc. football .... maximum of eleven players
  Uno ................ first player to score 500 points wins

--------------------------------------------------------------------------------
8. CONTROLS AND SELF-CHECKS
--------------------------------------------------------------------------------
Four independent checks, each of which has caught a real defect:

  SEED AUDIT       123 curated worlds each annotated with the cell it was
                   chosen to fill; seed-audit reports whether it landed there.
                   A miss is a classifier bug made visible. First run:
                   14 landed / 34 missed -> exposed D1 and D2.

  COHERENCE        6 checks comparing the declared vector (keyword scoring)
                   against the conditions table (whole sentences). Two
                   unrelated derivations; where they disagree at least one is
                   wrong. Exposed D7. 229 repairs applied and logged.
                   Contradictions where BOTH sides are assertions are reported
                   and NEVER auto-repaired -- silently picking one would
                   manufacture false confidence. 7 such remain.

  REACHABILITY     any vocabulary value no rule can set is reported as a
                   DEFECT, not a gap. Exposed D12, then D12b when the check
                   itself proved too narrow.

  TRACE READING    generating a concrete episode from the vector. Exposed D6.

REPAIRS DO NOT PROMOTE. A coherence repair leaves method='heuristic': it is
still machine inference, merely corroborated by a second machine route.
Verified -- method='reviewed' count was unchanged by 113 repairs in one pass.

--------------------------------------------------------------------------------
9. DEFECTS ENCOUNTERED
--------------------------------------------------------------------------------
Thirteen found, eleven fixed. Scale column is the blast radius had it not been
caught. Every one was found by PRINTING SAMPLED ROWS AND READING THEM.

 ID  Defect                                          Scale          Status
 --- ---------------------------------------------   ------------   --------
 D1  Enrichment selected on catalog_state, so a       3 canonical    FIXED
     dice game whose LEAD paragraph said "dice"       worlds
     was promoted on one word and permanently         stranded at
     excluded from full-text enrichment               ~600 chars
 D2  No positive signal for determinism: abstract     all abstract   FIXED
     games never SAY "perfect information", they      games
     simply never mention chance
 D3  Whole-article classification let a Spinoffs      systemic       FIXED
     section decide the base game. Pandemic ->
     REAL_TIME (from Pandemic: Rapid Response);
     Diplomacy -> SOLITAIRE
 D4  method ladder unenforced on the two paths that   integrity      FIXED
     write most. A read-then-write race clobbered     of the whole
     reviews while leaving method='reviewed' -- rows  provenance
     CLAIMED human provenance while holding machine   model
     values
 D5  Enrichment selected on LENGTH(wp_extract)<3000.  216 worlds     FIXED
     Real articles are often shorter (Towie = 401     re-fetched
     chars) so they were re-fetched FOREVER; the      forever, 384
     backlog never moved (621 -> 621)                 starved
 D6  BOUNDARY matched a bare "at least". "at least    45% of all     FIXED
     not being used as if it is worth anything" was   BOUNDARY rows
     filed as a rule of Monopoly
 D7  ELIMINATE matched "removed from the game" with   57% of all     FIXED
     no subject. Captured SEEDS and CARDS read as     ELIMINATE
     player elimination. Would have written           rows; 47
     loss_shape=ELIMINATION across 47 worlds with     worlds about
     no player elimination at all                     to be wrong
 D8  SOLITAIRE matched "one player". "One player      44 multi-      FIXED
     deals" appears in every card-game rules          player card
     section                                          games
 D9  HIDDEN_INFO and SIMULTANEOUS_CHOICE classed as   132 worlds     FIXED
     RANDOMNESS sources. Neither is a chance device   "containing
     -- both already had their own fields             chance", 77
                                                      with no other
 D10 Reclassify could never RETRACT. A value could    all list       FIXED
     be added or overwritten but not erased, so       fields
     dead vocabulary persisted indefinitely
 D11 luck_factor returned 0.35 when no randomness     413 worlds     FIXED
     was found -- a confident number for worlds
     where nothing had been observed, violating the
     module's own "leave NULL" contract
 D12 Unreachable vocabulary: turn_structure=          made the       FIXED
     CONTINUOUS could not be set by any rule, so it   coverage
     sat in "empty values" reporting a gap in         grid lie
     knowledge that was a defect in the list
 D12b The reachability check added for D12 had the    30 more        FIXED
     SAME blind spot -- it only covered the 8 scalar  unreachable
     declared-vector fields, missing the multi-       values hidden
     valued ones where most dead vocabulary lives
 D13 year_created conflates a game's SETTING with     unknown;       OPEN
     its creation date. Civilization (video game)     >=2 rows
     dated -4000 (its in-game start year, not 1991);  confirmed
     Commands & Colors: Ancients dated -3000 (a
     2006 wargame). Found while preparing this packet

OPERATIONAL PROBLEMS (not classifier defects)

  RATE LIMIT     6 sustained fetch workers across ~900 requests drew HTTP 429.
                 Lowered to 4, chunked with pauses. The ceiling is real and
                 politeness is load-bearing: the atlas depends on access.
  SHARED REPO    another agent (ERGON) committed onto this branch while it was
                 checked out, then switched to main and cherry-picked itself.
                 Nothing was lost -- commit e85bfa6b9 is intact and pushed --
                 but branch state can change mid-operation in this checkout.
  PATH CASE      "git add Roles/Ludus" was a SILENT no-op; git's path is
                 lowercase "roles/". Caught by diffing the staged list.
  IGNORE RULES   reports/ is covered by a blanket **/reports/ ignore, which
                 would have swallowed LOOP_LOG.md. Force-added that one file.
  HEREDOC        multi-line python heredocs with regex escaping failed
                 repeatedly and silently (assertion caught them). Exact-match
                 file edits were the reliable route.

THREE PREDICTED FIXES IN A ROW WERE WRONG
  iter 5 -> "multi-language fallback is the highest-value change". Measured:
           a third of the value at twice the cost.
  iter 6 -> "enrichment is one request per world, no cleverness compresses it".
           Wrong within one turn; concurrency gave 5.3x.
  iter 8 -> "the determinism rule over-fires and must defer to randomness
           detection". Backwards. The determinism rule was RIGHT; deferring
           would have deleted correct answers in favour of wrong ones. The
           real defect was D9.
  Every correct diagnosis came from printing rows, never from reasoning about
  the system. This is charter section 35's cheating assumption turned inward.

--------------------------------------------------------------------------------
10. KNOWN LIMITATIONS AND CAVEATS
--------------------------------------------------------------------------------
  1. NO CLAIM ABOUT ANY NAMED GAME. Every rule is HYPOTHESIZED under charter
     v1 section 8. Nothing here has been checked against a rulebook.
  2. NO WORLD ADMITTED TO THE BENCH. IMPLEMENTED requires a World subclass
     passing ludus/bench/verify.py. Zero produced. GATE-W1 untouched.
  3. NO TRANSFER MEASURED. Not one cell of transfer_matrix.json moves.
  4. CATALOG COVERAGE IS NOT VOCABULARY COVERAGE. All 8 fields have every
     value occupied, but 877-1,144 worlds carry NULL in any given field.
     The headline "8/8 complete" is about the VOCABULARY, not the rows.
  5. 41% OF WORLDS HAVE NO ENGLISH ARTICLE and can never be classified
     beyond a Wikidata description often reading only "2007 board game".
  6. ENGLISH-ONLY CLASSIFIER. Every pattern is English.
  7. HEURISTIC MEANS HEURISTIC. 9 worlds of 1,338 are 'reviewed'. Zero are
     'audited'. Thirteen defects in ten iterations is the observed defect
     rate of this method, and there is no reason to think D13 is the last.
  8. REVIEWED ROWS RESIST CLEANUP. 3 worlds still carry vocabulary removed
     in D9/D10 because reclassify correctly refuses to touch reviewed rows.
     The ladder is working; the cost is that vocabulary changes cannot reach
     reviewed rows without a human.
  9. DOSSIER CHURN. The 715 per-world dossiers regenerate every tick, so
     every future commit touches hundreds of files.
 10. THE LOOP IS NOT UNATTENDED. Cron fires enqueue prompts; nothing runs
     while the session is idle.
 11. SELF-GRADED. No independent reviewer has checked any classification.
     The coherence checker is the atlas checking itself with a second
     machine method, which is weaker than an outside instrument.

--------------------------------------------------------------------------------
11. REPRODUCTION
--------------------------------------------------------------------------------
  cd F:\Prometheus\ludus\atlas_of_worlds

  python crawl.py status            # counts
  python crawl.py tick --probes 8 --per-probe 40 --deepen 60 --wp-titles 60
  python report.py                  # -> ATLAS.md
  python crawl.py coherence         # report only, changes nothing
  python crawl.py coherence --repair
  python crawl.py seed-audit        # did each seed land in its target cell
  python crawl.py reclassify        # after any classifier change
  python crawl.py review --slug pandemic_board_game \
      --set turn_structure=ACTION_POINT --note "Four actions per turn."

  atlas.db is gitignored and rebuildable: delete it and re-run ticks.

FIVE-MINUTE SPOT CHECKS FOR A REVIEWER

  1. Vector discriminates. Compare three dossiers that should differ:
       worlds/cant_stop_board_game.md   expect IID / TOTAL_RUIN
       worlds/chess.md                  expect NONE / PERFECT / EXACT
       worlds/cartographers_board_game.md  expect DEPLETING_DECK / PARALLEL

  2. Thresholded conditions are real. Open worlds/basketball.md, section
     "Conditions", and confirm the 7-foul and 10-foul rows against the
     Wikipedia article.

  3. Ladder is enforced. python crawl.py review --slug chess \
       --set turn_structure=NOT_A_REAL_VALUE
     Must refuse and print the allowed vocabulary.

  4. Repairs do not promote. Note method='reviewed' count (9), run
     python crawl.py coherence --repair, confirm it is still 9.

  5. D13 is real. python -c "import store;con=store.connect();
     print(con.execute('SELECT name,year_created FROM worlds ORDER BY
     year_created LIMIT 3').fetchall())"
     Expect Civilization (video game) at -4000. That is its in-game start
     year, not its 1991 publication date.

--------------------------------------------------------------------------------
12. FUTURE SEARCH DIRECTIONS
--------------------------------------------------------------------------------
IMMEDIATE (next iterations, already scoped)
  - Fix D13. Reject year-from-text matches near setting vocabulary ("set in",
    "begins in", "spanning", "from X BC to"). Re-audit the oldest 50 rows,
    which are exactly the rows a historical claim would rest on.
  - Triage the 30 unreachable values. UNSOLVED and NOT_APPLICABLE are cheap
    and would complete solved_status. Drop aspirational strategy/algorithm
    tags no source text will contain. Mark LARP/ESCAPE_ROOM hand-review-only.
  - Drive the CATALOGUED 527 down: they are thin because they lack articles,
    so the honest move is to mark them ceiling-bound rather than pending.

STRUCTURAL (bigger, higher value)
  - CROSS-VALIDATE AGAINST AN INDEPENDENT SOURCE. The single biggest weakness
    is that the atlas grades itself. Ludii (Digital Ludeme Project) carries
    ~1,400 games in an executable DSL with a ~500-concept ontology already
    tagged per game. Comparing its concepts against this declared vector on
    the overlap would be a genuine outside instrument, not a second machine
    opinion. OpenSpiel (~70 games, explicit chance nodes) is a second option
    and its API is close to the bench's World interface.
  - MEASURE CLASSIFIER ACCURACY. Hand-label a random 100 worlds and report
    per-field precision/recall. Currently the defect rate is known only
    anecdotally -- thirteen found, none counted against a denominator.
  - AUTOMATE THE SECTION-41 EXPERIMENT. Every unbuilt world's declared-vector
    distance from the worlds a given circuit was measured in, on the
    dimension that circuit's scope names, ranked. That is the deliverable
    section 41 actually asked for and it is now computable.

BENCH-FACING (what this was built for)
  - BUILD FOR SALE. Catalogued, carries a registered r0012 prediction, and is
    the bench's first simultaneous-information cell.
  - ATTACK THE r0003 PARTNER SPREAD. TOTAL_RUIN candidates now exist in
    quantity; the blocker is that r0003's value is not yet a function of the
    world. Pick TOTAL_RUIN worlds that differ maximally on SELECT-axis
    richness.
  - REGENERATE ludus/atlas/BACKLOG.md FROM DATA. It is stale: it still says
    "all four worlds are push-your-luck" when Coloretto and Lucky Numbers
    have been built.
  - PUSH SYNTHETIC FAMILIES HARDER. 15 of the bench's 21 matrix rows are
    FOUNDRY parameter sweeps. Section 34 (adversarial world generation) needs
    parameterised families, which commercial games cannot provide. The real
    games' job is to ANCHOR a synthetic cell -- to show a parameter setting
    corresponds to something a human designer actually built.

DECLINED, WITH REASONS RECORDED
  - Multi-language Wikipedia: measured, ~1/3 of ceiling, needs a second
    non-English rule set.
  - BoardGameGeek: 401 on all endpoints, needs credentials.

--------------------------------------------------------------------------------
13. VERDICT
--------------------------------------------------------------------------------
  CATALOG EXISTS AND IS BROAD ...................... YES  (1,338 worlds,
                                                     8 epochs, 14 regions)
  RESEARCH ITEM PRESENT PER WORLD .................. YES  (716 traces, 88%
                                                     of worlds with articles)
  DECLARED GRID FULLY EXERCISED .................... YES  (8/8 fields)
  CLASSIFICATION VERIFIED BY AN OUTSIDE SOURCE ..... no
  CLASSIFICATION ACCURACY QUANTIFIED ............... no
  ANY WORLD BENCH-READY ............................ no
  ANY RULE AUDITED ................................. no
  SECTION 41 NOW COMPUTABLE ........................ YES, but unexercised

  STATUS: USEFUL INSTRUMENT, UNVALIDATED OUTPUT.

  The machinery is sound and self-critical -- four independent checks, each
  of which caught a real defect, and a provenance model that survived a race
  condition once the race was closed. What it lacks is any outside check on
  whether its classifications are correct.

REVIEWER'S BOTTOM LINE
  Thirteen defects surfaced in ten iterations, every one caught by reading
  sampled rows rather than by reasoning -- so what is the defect rate in the
  rows nobody sampled, and does the coherence checker (the atlas grading
  itself with a second machine method) count as evidence at all, or only as
  a generator of rows worth looking at?
================================================================================
END OF PACKET
================================================================================
