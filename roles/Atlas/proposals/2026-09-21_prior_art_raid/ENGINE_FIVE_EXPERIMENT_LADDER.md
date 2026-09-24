# ENGINE FIVE -- the killable ladder

Currency: 2026-09-21. Hypothesis under test, stated so it can die:

    Cumulative lifetime competence, interacting recursively with generated
    worlds through a persistent, growing, reusable internal library, is a
    distinct scientific object that no existing Prometheus engine can hold.

Atlas's position: unproven, and cheap to disprove. The ladder below is ordered
so that the cheapest rung that can kill the hypothesis runs first. Full records
(treatments, controls, anti-cheat, falsifiers, assumption costs) are in
EXPERIMENTS.jsonl; this file is the sequence and the gates.

## Donor reality (Techne, FIRST_RETURN_2026-09-21, verified today)

    Voyager        MIT, pinned at 55e45a88, fossilized, 457 files verified.
                   SOURCE_ONLY here: running it needs a licensed Minecraft
                   client, a mineflayer bridge and a paid API key. The skill
                   schema is substrate-independent by construction (name +
                   NL description + opaque executable payload + embedding key).
    SIMA / SIMA 2  NO_PUBLIC_SOURCE (DeepMind's own pages, quoted). The one
                   public "SIMA" repo is graded TOY_CLONE.
    Genie 1/2/3    NO_PUBLIC_SOURCE. Open substitutes ranked by Techne:
                   open-oasis, MineWorld, Matrix-Game -- all video-first world
                   models, none a measurable task world out of the box.

Consequence: rungs 0, 1, 4, 5 are buildable now from the Voyager schema plus our
own substrates. Rungs 2 and 3 are donor-blocked and would be built here, which is
exactly where the engine's cost sits. Do not let rung 3's appeal reorder the ladder.

## The ladder

    rung   experiment  what it decides                         kill condition
    ----   ----------  --------------------------------------  ----------------------------
    0      F5-0        is persistence useful at all, beyond     no advantage at matched
                       equal-information context?               information and compute
    1      F5-1        does composition open new reachable      composable == non-composable
                       space?                                   on withheld composites
    2      F5-4        is later progress causally dependent     library swap changes nothing
                       on retained structure?
    3      EV-10       is the library a better search           library search == policy
                       substrate than the policy?               search per evaluation
    4      F5-5        can self-generated objectives survive    generated-reward arms fail
                       an independent evaluator?                under independent scoring
                                                                (that is a finding, not a
                                                                kill: it bounds the design)
    5      F5-2        does competence survive a change of      nothing transfers on any
                       world, control mapping or embodiment?    axis (donor-blocked build)
    6      F5-3        does adaptive world generation beat      adaptive == random procedural
                       its cheaper controls?                    on held-out frontier
    7      F5-6        does the loop keep exposing new KINDS    new-cluster rate saturates
                       of behaviour?                            like the static control

Rungs 0 and 1 are S-compute. Rung 2 is the one that most deserves the budget.
Rungs 5 and 6 cost the most and decide the least per unit compute; run them last
and only if 0-3 survive.

## THE KILL GATE

Engine Five is refused, and the machinery becomes a feature of an existing engine,
if ANY of these holds after rungs 0-3:

    1. F5-0 fails: persistence gives nothing beyond equal-information context.
       -> the Voyager mechanism is context management. Put it in SFE or
          Bellerophon as a memory component. No engine.
    2. F5-1 fails: no composition beyond retrieval.
       -> the library is a cache. Same verdict.
    3. F5-4 fails: swapping the accumulated library late in a run changes
       nothing.
       -> progress was not cumulative; the loop is long, not growing.
    4. EV-10 fails AND F5-4 passes: the library matters but is not a better
       search substrate.
       -> keep it as persistent memory inside an existing engine; the
          "new evolutionary substrate" claim, which is the only reason to
          call it an engine, is unsupported.
    5. The mechanism turns out to be expressible as a small extension of SFE,
       Bellerophon, Crius or the NPE. Being impressive is not a criterion.

Engine Five survives only if: persistence beats matched context (F5-0), skills
compose into withheld competence (F5-1), removing accumulated structure collapses
later progress (F5-4), and search over the library beats search over the policy
(EV-10). Three of those four are S-or-M compute on worlds we can already build.

## What would make Atlas argue FOR the engine

Not a demo. One result: a lineage that cannot reach a computation by policy search
at matched compute, but reaches it by composing library entries that were acquired
for other purposes -- with the library swap test showing the collapse. That is the
"access to previously unreachable experience" leg of the operator's loop, and no
existing engine has a place to put it.

## Assumption costs carried by the whole ladder

    - Skill libraries privilege discrete, nameable, reusable procedures.
      Competence that is continuous or diffuse cannot enter the library and
      will read as "persistence does not help". MEM-1 carries the counter-arm
      (parameter-update memory at equal bytes).
    - Generated rewards privilege measurable objectives (F5-5).
    - Learned world models inherit their training distribution (F5-3), so a
      generated curriculum can only pose what its prior can express.
    - Language-conditioned agents inherit a linguistic ontology; every rung
      that uses NL descriptions for retrieval inherits it too.
