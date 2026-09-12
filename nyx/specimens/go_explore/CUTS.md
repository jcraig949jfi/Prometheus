# Go-Explore -- the cut

Currency: 2026-09-12. Ledger: cuts.json. One cut by design (PREREG s6).

## Flow log (K1; sequential; no def-grep)

W1 goexplore.py 1-380: pools (loky / sync) and seeded map (scaffolding); Discretizer family
   (GridDimension floor((v+off)/div), GridEquality, SingleCell, GridLambda) turning a
   position object's attributes into a tuple KEY; Cell record: score, trajectory_len,
   restore (an opaque blob), exact_pos, real_cell, traj_last, cell_frame, plus four
   counters (seen, chosen, chosen_since_new, action) each with a _diff for merging
   across subprocesses; PosInfo, TrajectoryElement; RotatingSet of recent frames;
   FormerGrids (archives pickled to disk, popped for recompute); Explore.__init__:
   grid = defaultdict(Cell); initial cell from the reset state; a DONE cell.
W2 381-760: make_env/reset/step delegate to a module-global ENV; get_dynamic_repr:
   frame -> imdownscale(shape, pix) -> bytes, recursively through split rules;
   try_split_frames: SEARCH over (shape, pix_val) proposals (geometric jumps around
   the best), scoring a candidate representation by the NORMALISED ENTROPY of the
   occupancy distribution of recent frames divided by sqrt(|n_cells - target|/target
   + 1), keep the best; maybe_split_dynamic_state: when due, adopt the new
   representation and REBUILD the archive by re-keying every former grid, admitting
   with should_accept_cell and merging counters; get_pos/get_cell: real position
   (domain knowledge) or dynamic repr; get_restore -> ENV.get_restore(); restore(val)
   -> ENV.restore(val); run_explorer: act, step, record TrajectoryElement with
   PosInfo(restore blob per step).
W3 761-1124: process_cell (in a SUBPROCESS): if the cell has a restore blob, ENV.restore
   it, else reset; run the explorer for explore_steps; run_cycle: selector.choose_cell
   -> batch of cells -> pool.map(process_cell) -> for each returned trajectory: update
   counters; for each step: candidate key = the step's cell; if not in grid or
   should_accept_cell(score higher, or equal and shorter trajectory, or random
   override): write score / trajectory_len / RESTORE BLOB / traj_last / frame into
   the cell; selector.cell_update. should_accept_cell = the fitness definition.
   save_checkpoint: pickles the grid WITHOUT restore blobs and frames; experience
   arrays for the demo generator (the OUT phase).
W4 randselectors.py: WeightedSelector: per-cell weight = sum over (seen, chosen,
   action, chosen_since_new) of w * 1/(count+1)^p, plus positional bonuses (missing
   neighbours in x/y, score-frontier terms, door/grip terms for Fetch), times a
   level weight; incremental cache of weights; choose_cell = np.random.choice
   proportional to weight; a self-check block gated by random() < 0.0 (dead).
W5 explorers.py: random action; random action repeated a geometric number of times
   ("sticky"); drift for robots; do-nothing. basics.py: imports and a memoize.
W6 env (entered at the named call sites only): generic_atari_env.get_restore =
   (ale.clone_state(), frame stack, elapsed_steps); restore = reset() then
   ale.restore_state(full_state) and put the bookkeeping back; montezuma adds
   score/steps/pos/room_time/death/objects/lives to the blob; get_pos returns a
   position parsed from RAM (domain knowledge). The SAVE/RESTORE CAPABILITY IS
   THE EMULATOR'S (ALE clone_state / restore_state); Go-Explore stores the token
   and hands it back.
NOT entered: main.py, utils.imdownscale body (named), policy_based/*, atari_reset,
gen_demo, the papers.

## Fishing log
- impulse: open policy_based/goexplore_py/archives.py to see the "other" archive -- NOT opened (second variant, named)
- impulse: open utils.py imdownscale to judge the image-specific family -- NOT opened (the call signature (frame, shape, pix) is enough; the family is image-specific by its arguments)
- impulse: read arXiv 2004.12919 for the authors' own decomposition -- NOT opened (T2; would import inherited boundaries from prose)

## CUT-1 candidates (14), origin stamped at drawing; duplicate control against the inventory BEFORE any organ

    id  origin      disp             one line
    c01 DISCOVERED  RECURRENCE       archive admission: keep the best-known entry per key; replace on higher score, or equal score and shorter path; united across should_accept_cell + the write block in run_cycle + the recompute path. TEMPTED. Duplicate control: organ.map_elites cell replacement by fitness in a behaviour-keyed archive -- same mechanism; the (score desc, length asc) fitness and the restore payload are POLICY/DATA riding on it, not new mechanistic behaviour
    c02 INHERITED   POLICY           selection weights: sum of w/(count+1)^p over four counters + positional bonuses, sampled proportionally; the sampling is trivial, the table is the content; count-based bonus is textbook. TEMPTED briefly; refused: no independent behaviour beyond the table
    c03 DISCOVERED  COUPLED_CLUSTER  "deterministic reset": capture an opaque restore token per step (get_pos_info), store it with the elite (c01 write), hand it to ENV.restore before exploring (process_cell). The CAPABILITY is the emulator's (clone_state/restore_state, OUT); what the IN files hold is a token-carrying POLICY plus the STATE ASSUMPTION that the world is exactly resumable. Inseparable here; a PRESSURE is extracted from it (P-A)
    c04 INHERITED   ORGAN            representation selection: search a family of key functions over recent observations for the one whose partition has near-uniform occupancy at a target granularity (normalised entropy / sqrt(|n - target|/target + 1)); coincides with def try_split_frames. TEMPTED and ADMITTED at CUT-1: inventory has descriptor-keyed niching with DECLARED descriptors (MAP-Elites; Vivarium #182 "never learned"); this LEARNS the key function -- materially new. Independent behaviour SPECIFIED, NOT RUN (no pin)
    c05 INHERITED   SCAFFOLDING      archive rebuild under a new key (re-index every former grid through c01)
    c06 INHERITED   POLICY           explorer: random action with geometric repeat ("sticky actions"); textbook
    c07 INHERITED   SCAFFOLDING      four counters with _diff merging for subprocess results
    c08 INHERITED   SCAFFOLDING      experience arrays for the demo generator (feeds the OUT phase)
    c09 INHERITED   POLICY           domain-knowledge cell: discretised room/x/y/level/objects -- the human prior about "the same place"
    c10 INHERITED   POLICY           DONE cell at zero weight; ignore_death do-nothing probe
    c11 INHERITED   SCAFFOLDING      pools, pickling minimisation, FormerGrids on disk, checkpoints
    c12 INHERITED   POLICY           the fitness definition (score desc, trajectory_len asc) + prob_override (rides on c01)
    c13 INHERITED   POLICY           the return-then-explore schedule: batch of starts, explore_steps each, then admit (the loop shape; a schedule, as Lean c08 / shrinker c05 were)
    c14 INHERITED   DATA             restore token contents (emulator state + wrapper bookkeeping): DATA produced by the env, opaque to Go-Explore

Deterministic reset, answered (PREREG s4): PRIMARILY A PROPERTY DEMANDED OF THE WORLD
(environmental affordance: ALE clone/restore) + a STATE ASSUMPTION (exact resumption)
+ a POLICY (carry the token with the elite and resume from it rather than replay
actions). No mechanism in the IN files performs the reset. Preserved as COUPLED_CLUSTER
c03; the world-side requirement becomes pressure P-A.
