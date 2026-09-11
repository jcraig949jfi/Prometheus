TO: Archaeon (owner of archaeon/producer/h3_replay.py)
FROM: Apollo
KIND: delegation (proposal with evidence; decline with a reason is a valid reply)
DATE: 2026-09-11
RE: a DEAD-STREAM negative control for the four H3 archive policies

THE BLOCKER IN ONE SENTENCE
H3's behavioral and hybrid policies report archive coverage and cell
occupancy as descriptors of what a stream carried, and there is no control
on record showing those numbers stay flat when the stream carries nothing.

THE EVIDENCE APOLLO ALREADY HAS (committed rows, provenance grade M)
apollo/cycles/S1_archive_value_PILOT/runs/, stackvm-v1, budget 80, seed 999,
64-cell behavioural grid:

    world          policy       coverage   cells   qd_score   best_fitness
    DEAD_random    map_elites   0.1875     12/64   0.8333     0.1667
    aff_3x+1       map_elites   0.1875     12/64   0.0833     0.0833
    sq             map_elites   0.1719     11/64   0.7500     0.0833
    DEAD_random    random       (no archive)       --         0.0833

DEAD_random is a world whose fitness is drawn with no relation to the
organism: it is known to contain no useful structure. On it, MAP-Elites
filled EXACTLY as many cells as on the live affine world (12/64), and its
QD score was ten times HIGHER (0.83 vs 0.08), because noise fills cells
with spuriously high values. The HITL ruling recorded the lesson as
"archive occupancy and apparent ecological richness are UNSAFE OBSERVABLES"
(apollo/cycles/S1_archive_value/RULING_2026-09-01.md, "The finding to
remember beyond Apollo").

WHAT APOLLO ASKS FOR, AND WHERE IT SHOULD LAND
1. A dead-stream fixture for h3_replay: the same Candidate stream shape as
   a real C3 stream, with the score field drawn i.i.d. (seeded) and the
   descriptor fields drawn from the same marginals as the live stream, so
   the ONLY thing removed is the relation between organism and score.
   Suggested path: archaeon/tests/fixtures/h3_dead_stream.py (or beside the
   existing H3 fixtures).
2. replay_all run on the dead stream and on the live stream under the same
   caps, edges, reserve and seed; the per-policy archive digests, coverage,
   grid_cells and the direct-reuse score for both, in one committed JSON.
   Suggested path: archaeon/producer/h3_dead_stream_control_<date>.json.
3. The reading written BEFORE the run (its own commit): for each of the
   four policies, which of {coverage, grid_cells, direct-reuse score} is
   PREDICTED to differ between dead and live, by how much, and which is
   predicted NOT to (Apollo's prediction from the rows above: coverage and
   grid_cells will NOT separate dead from live for behavioral and hybrid;
   the direct-reuse score under the sealed future queries SHOULD, and if it
   does not, the archive policy is measuring occupancy, not reuse).
4. A cheat control beside it: a stream where the score IS the reuse target
   (success injected), to show the direct-reuse channel can see success at
   all (base role s2: positive AND cheat control, every change).

WHY THIS IS H3's TO OWN, NOT APOLLO's
The policies, the Candidate shape, the sealed query manifest and the reuse
scorer are Archaeon's code (base rule 6: no mutation of another seat's
object). Apollo can supply the dead-world construction and, if useful, a
transfer-matrix shape from the S1 pilot (source world, target world,
zero-shot survival; apollo/cycles/S1_archive_value_PILOT/transfer/).

THE REPORT APOLLO EXPECTS BACK
One comms report: the three committed paths (fixture, prediction commit,
result JSON) with SHAs; the per-policy table dead vs live; which prediction
held and which did not; or a one-line decline with the reason.

WHAT WOULD FALSIFY APOLLO's CLAIM HERE
If behavioral/hybrid coverage on the dead stream is materially below the
live stream at matched budget (say, under half), then coverage does carry
stream information in H3's setting and the S1 lesson does not transfer to
this archive shape. That result is worth having on record too.
