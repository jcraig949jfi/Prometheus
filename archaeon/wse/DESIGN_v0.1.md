# WSE -- Computational Workspace Ecology: design v0.1 (preregistration of the cheap survey)

Archaeon[m2-411504ab], 2026-09-16. Directive:
roles/Archaeon/prompts/2026-09-16_workspace_ecology/00_OPERATOR_DIRECTIVE.md
(the W0-W10 numbering used here is the DIRECTIVE's, section V).

This file is committed BEFORE any evolutionary run reads a seed. Every
threshold, predicate and control below is fixed here; a change after data
is a new version with an annotation, never an edit.

## 0. Substrate reused, substrate added

REUSED, untouched (Proteus's lane; nothing under proteus/ is edited):
  proteus.foundry.vm        Player VM: 25 opcodes (NOP HALT YIELD LDC MOV LD
                            ST ADD SUB MUL AND OR XOR NOT SHL SHR EQ LT JMP
                            JZ JNZ IN INQ OUT RND), state = {tape, regs, ip},
                            per-tick input channels / output channels,
                            evolvable manifest fields n_regs, tape_words,
                            code_writable, persist in {none,regs,tape,all},
                            tick_budget, out_cap. Meter = ops, ops by class,
                            code-region writes, branches, in_reads,
                            out_writes, out_dropped, rnd_draws, ticks,
                            budget-exhausted ticks, persistent_state_words.
  proteus.foundry.generate  seeded generation-0 populations.
  proteus.foundry.grammar   12 active mutation operators incl. `splice`
                            (crossover from a mate) and `config_perturbation`
                            (steps n_regs / tape_words / code_writable /
                            persist / tick_budget / out_cap): the
                            PERSISTENCE POLICY IS ITSELF EVOLVABLE.
  proteus.foundry.lineage   descend() lineage records; checkpoint/restore.
  proteus.foundry.prng      SplitMix64 with hierarchical derive().

ADDED, under archaeon/wse/ (this seat's lane; Ludus CHARTER_v3 s"division of
labour": "Archaeon and Vivarium compose populations, worlds, curricula,
mixtures and evolutionary experiments" from Proteus's players):
  worlds.py        the event-stream world generator (section 2)
  economics.py     the fitness regimes (section 3)
  evolve.py        selection loop (section 4) -- Proteus by charter has none
  controls.py      hand-written organisms: positive and cheat controls (s5)
  interventions.py state perturbations between ticks (section 6)
  survey.py        the cell matrix runner + records (sections 7-8)

Semantic neutrality (directive VIII): the VM's affordances are Proteus's
published table; none is named for a computational interpretation. The
world adds NO affordance. Persistent state can be realised as registers
(persist=regs), tape words (persist=tape), both, or none, and the organism
may also keep an instruction pointer across ticks (YIELD) or not (HALT).
Multiple realisations exist without any being named.

## 1. The question this survey answers

Not "can organisms solve these tasks". The question is: WHICH pressure
settings make the management of unfinished computation an adaptive
problem, i.e. where does the ecology change character (directive XXI)?
Outcomes per cell are one of: NO_ADAPTATION / TRIVIAL_RECURRENCE /
RECOMPUTATION / SPECIALIZED_MEMORY / STRUCTURED, decided by the predicates
in section 9, never by inspection.

## 2. The world: one event-stream grammar, every W a parameter setting

An EPISODE is a sequence of TICKS. Each tick the organism receives ONE
input channel (channel 0) holding this tick's EVENT WORDS, and may write
output channel 0. Only the FIRST word written on an ASK tick is read.

Event words (uint32). Kind codes are the world's fixed syntax; every
IDENTITY is randomised per episode:

  PUT   = [1, tag, v]              stream `tag` receives value v:
                                   s_tag := s_tag (op) v   (s_tag starts at
                                   the first v)
  ASK   = [2, tag]                 expected output THIS tick: s_tag
  ASKX  = [3, tag, y]              expected: s_tag (op) y  (a consumer of s)
  ASK2  = [4, tagA, tagB, c]       expected: combine_c(s_A, s_B), c in a
                                   small set of combine ops revealed only
                                   at ask time (W7)
  ASKO  = [5, v0]                  expected: state of the stream whose FIRST
                                   value was v0 (origin = provenance; W8)
  SETOP = [6, tag, a, b, c]        stream `tag`'s op becomes
                                   s (op) v = (a*s + b*v + c) mod 2^32 (W9:
                                   the operator is data the organism must
                                   keep per stream; default op when no
                                   SETOP: a=1,b=1,c=0 i.e. ADD)
  DEF   = [7, node, a, b, c, x, y] node := (a*val(x) + b*val(y) + c) mod
                                   2^32 over NODE ids x,y (which may be
                                   input nodes given by PUT or nodes DEFined
                                   LATER in the episode -> pending); W10
  NOISE = [8, r1, r2]              distractor; never referenced

Several events may share a tick (concatenated on channel 0). INQ tells
the organism how many unread words remain.

Values: v uniform in [0, 2^VALUE_BITS), VALUE_BITS a knob (default 8), so
that partial strategies (echo the last value; add two values) have a
non-zero exact-match rate and selection has a gradient WITHOUT any reward
shaping. Tags: distinct uniform uint32 in [1, 2^16) per episode. The
mapping observation -> role is therefore re-randomised every episode.

KNOBS (each independently settable; this is the orthogonalisation of
directive VI):

  K            simultaneously live streams          1,2,4,8,16
  D            events per stream (serial depth)     1,2,4,8,16
  interleave   sequential | random                  (concurrency)
  delay        ticks of NOISE between the last PUT  0,1,4,16
               of a stream and its ASK              (lifetime of state)
  ask_mode     all | one                            (late binding: `one`
               asks a single uniformly chosen stream; the organism cannot
               know which until the ASK)
  ask_kind     ASK | ASKX | ASK2 | ASKO             (consumer type)
  fanout       consumers per stream (ASKX count)    1,2,4,8
  expensive    n >= 0: each PUT is preceded by the value passing through
               n iterations of an LCG step the organism must reproduce to
               know v (the world supplies the PRE-image u and expects the
               fold over f^n(u)); with n*cost > tick_budget the work
               cannot finish in one tick -> W4 suspend/resume; with
               fanout > 1 -> W6 reuse vs recompute
  op_mode      fixed | per_stream (SETOP per stream per episode; W9)
  topology     streams | dag (DEF events, random DAG, W10)
  noise_rate   NOISE events per tick, Poisson mean  0, 0.5, 2

W-coordinates in this grammar (directive V), the SURVEY cells (XXI):

  W0  K=1 D=1 delay=0 ask immediately after PUT     (control)
  W1  K=1 D=1 delay in {1,4,16}                      (retain one value)
  W2  K in {2,4,8} D=1 ask_mode=all                  (several live values)
  W3  K in {2,4,8} D=1 ask_mode=one                  (late binding)
  W4  K=2 expensive=n, interleave=random             (interrupted work)
  W5  K in {2,4,8} D in {2,4,8} interleave=random    (concurrent branches)
  W6  K=1 expensive=n fanout in {1,2,4,8}            (shared intermediate)
  W7  K=2..4 ask_kind=ASK2                           (recombination)
  W8  K=2 ask_kind=ASKO, two streams equal in state  (provenance)
  W9  K=2..4 op_mode=per_stream                      (operators as data)
  W10 topology=dag, 4..8 nodes                       (novel topology)

## 3. Economics (directive VII)

  fitness = reward - alpha*ops/1000 - beta*persistent_words/64
                   - gamma*(in_reads+out_writes)/100 - delta*ticks_late

reward = fraction of ASK-type events answered EXACTLY (first output word
== expected) over the evaluation episodes. ticks_late = 0 in v0.1 (an
answer must arrive on the ASK tick; latency knobs are v0.2).
persistent_words = Meter's persistent_state_words (manifest-derived:
tape_words if persist in {tape,all} plus n_regs if persist in {regs,all}).

Regimes for the survey (names are labels of the vector, not of an
expected mechanism):
  E0  alpha=0      beta=0      gamma=0       (reward only)
  E1  alpha=0.02   beta=0.01   gamma=0       (mild)
  E2  alpha=0.10   beta=0.01   gamma=0       (compute dear)
  E3  alpha=0.01   beta=0.10   gamma=0       (storage dear)
The compute x storage grid (E2 vs E3 on the W6 cells) is the first phase
boundary to look for: recomputation vs caching.

## 4. Selection (the part Proteus does not supply)

  population N=200; generations G (survey: 150); elitism 4;
  tournament size 4; each child = descend(parent, seed, mate=other
  tournament winner) with n_ops=1 from the active grammar (splice = 5.2 %
  crossover mass); episodes per evaluation E=24, FRESH seeds every
  generation (derive(gen)); the final elites are re-scored on a HELD-OUT
  seed family never used in training, and on held-out K and D.
  Everything derives from one campaign seed; the record carries it.
  No LLM anywhere (charter constraint 1 applies to the loop).

Branches (directive X) in v0.1: B1 naive (generation 0 from Proteus's
foundry manifest) for every cell; B2 transfer (elites of an ADJACENT cell
as generation 0) for the cells that show adaptation. B3-B5 are v0.2.

## 5. Controls (base doctrine: positive + cheat before any measurement)

  NEG   generation-0 population scored on the world: the chance floor,
        per cell, reported beside every result.
  NULL  constant-0 organism and "echo the last input word" organism:
        payload-reading nulls (a world where echo scores high is a world
        whose ASK leaks its answer).
  POS   a hand-written organism per W0/W1/W2 that solves it with the
        published opcodes (W1 with persist=regs, W2 with persist=tape):
        proves the world is solvable IN THIS VM and the measurement sees
        it. If POS fails the world is misposed, not the organisms.
  CHEAT the POS organism run on the intervention battery: the battery
        must DETECT the mechanism it was written with (regs-erase kills
        the regs solver and not the tape solver, and vice versa).

## 6. Interventions (directive XI), applied to an ELITE genotype between ticks

  ERASE_ALL      zero every non-code tape word and every register
  ERASE_REGS     zero registers only
  ERASE_TAPE     zero non-code tape only
  SCRAMBLE_LOC   permute non-code tape words (values kept, locations not)
  SCRAMBLE_VAL   keep locations, replace stored non-zero words by random
  SWAP_TWO       swap the two most recently written non-code tape words
  HALVE_CAP      zero and freeze the upper half of the non-code tape
  RESET_IP       force ip=0 (kills YIELD-resumption, keeps data)
  TRANSPLANT     replace state with the state of the same genotype at the
                 same tick in a DIFFERENT episode
Applied once at the tick after the last PUT of the first asked stream.
Readout: reward under intervention minus reward without, per
intervention, = the FAILURE GEOMETRY vector. Interventions are the
evidence for functional claims; behaviour alone licenses none.

## 7. Cheap survey matrix (what runs first)

  cells = { W0, W1(d=1,4,16), W2(K=2,4,8), W3(K=2,4,8), W5(K=4,D=4),
            W6(fanout=1,4; n=48 at tick_budget 64), W7(K=2), W8, W9(K=2),
            W10(6 nodes) }  x  { E0, E1 }  x  seeds {1,2,3}
  W4/W6 at E2 and E3 additionally (the compute x storage boundary).
  ~25 cells x 2-4 regimes x 3 seeds, N=200, G=150, E=24 episodes of
  <= 40 ticks at tick_budget <= 64: ~1e9 VM ops total; the VM measured
  3.75e6 ops/s on one core, 28 cores on M2 -> under one hour.

## 8. Record (directive XX)

One JSONL row per (cell, regime, seed, branch) under
archaeon/wse/ledgers/<campaign_id>/ with: world {id, knobs, seed,
grammar hash}, economics, organism {elite organism_id, lineage_id,
generation, parents, manifest digest, branch}, hypothesis {W-pressure,
competing explanations listed in s9}, experiment {train seeds, held-out
seeds, held-out K/D, interventions}, result {fitness, reward train /
held-out / held-out-K / held-out-D, ops, persistent words, meter,
intervention vector, capacity curve over K where cheap}, interpretation
{predicate outputs of s9, ruled out, remaining, next cell}. Plus the
generation-by-generation elite trace (reward, ops, persist policy,
share of tape writes) so strategy switches are visible.

## 9. Classification predicates (fixed now; XXI vocabulary)

Let R = held-out reward of the elite, F = NEG chance floor for the cell,
P = POS reward (1.0 by construction where a POS exists).
  NO_ADAPTATION        R - F < 0.10 on held-out seeds
  otherwise, with the intervention vector I[*] = R - R_under_intervention:
  TRIVIAL_RECURRENCE   persist in {regs} AND I[ERASE_TAPE] < 0.05 AND
                       I[ERASE_REGS] >= 0.10   (one recurrent state)
  RECOMPUTATION        (W6 cells) ops grow with fanout at slope >= 0.5 x
                       the recompute cost AND I[ERASE_ALL] < 0.05
  SPECIALIZED_MEMORY   I[ERASE_TAPE] >= 0.10 AND I[SCRAMBLE_LOC] >= 0.10
                       AND held-out-K reward drops by >= 0.20 when K
                       doubles (positional slots, fixed capacity)
  STRUCTURED           I[SCRAMBLE_LOC] < 0.05 AND I[ERASE_TAPE] >= 0.10
                       (content survives relocation) OR
                       I[SCRAMBLE_VAL] >= 0.10 with I[SCRAMBLE_LOC] < 0.05
                       AND held-out-K reward within 0.10 of training K
  UNRESOLVED           anything else; recorded with the full vector
These are directive-XIX EVIDENCE STATES, not architectural claims. An
elite that meets STRUCTURED is a "candidate computational primitive"
only after Harmonia's independent replay; this seat never promotes.

## 10. What would falsify the survey itself

- POS fails on any of W0-W2: the grammar is misposed; stop, fix, re-prereg.
- NULL (echo) scores >= 0.5 on any cell: the ASK leaks; that cell's
  results are void.
- Two seeds of one cell disagree on the s9 class: the class is not a
  property of the cell; report UNRESOLVED and the disagreement.
- Ops/s or determinism check fails (same campaign seed -> different
  ledger hash): nothing from that run is reported.

## 11. Not in v0.1 (named so absence is visible)

latency cost (delta), asynchronous arrival with deadlines, capacity
curves beyond K, transplant between organisms, branches B3-B5, PEW
fossilisation (Mnemosyne's write route; the ledger keeps pew_rows-shaped
data in reserve), SFE worlds (engine on HOLD, #315), Theophrastus hand-off
(after the first cells classify), any substrate requirement to
Proteus/Daedalus (none needed for v0.1; the VM already expresses every
pressure above -- that is a claim this survey tests).
