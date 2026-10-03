# S1 contract, draft A: finite world, truth model, reset / restart / observer, C3 reset model

Packet:     C-004-T001 (owner Cadmus, Q2). Input to C-004-T004 (Palamedes assembles and freezes CONTRACT.md).
Author:     Cadmus[m1-a86ec5e4], claude-opus-5-5, 2026-10-03.
Built from: base a46a29824, branch cadmus/boot-2026-10-03, worktree F:/Prometheus-worktrees/cadmus-boot.
Status:     DRAFT. Not frozen. Nothing here is a measurement; every count below is an expected value.
Sources:    docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/NEXT_ROUND_PLAN_v0.4.md (s3, s4; 3bd02f393)
            docs/phase3/closure/FABLE-5.1/CLOSURE_REVIEW_v0.4.md (C1, C3, F; 09dc8c38b)
            docs/phase3/hardening/FABLE-5.1/ (escape corpus, 3669bc7f2)
            docs/phase3/reviews/ASTRA-6.0/rso-v0.2/ (escape corpus, 9af020b24)

Exposure record (for T005 and S3 independence). Before writing this I read: Fable's known_escapes() and the
G6 gate lists in harness/rso_harness/meta.py, the fault organisms in harness/rso_harness/retain1.py, the
survivor list in harness/RECEIPT_mutation_probe.json, attack/REPORT_of_the_reader.md,
attack/closure_reader/REPORT.md and REPORT_final.md, attack/second_reader/REPORT_final.md; ASTRA's
reference_harness/finite.py and test_finite.py, VALIDATION.md, HARDENED_DESIGN_v0.3.md s6-7 and
HARDENED_TEST_PLAN_v0.3.md. No code or test was copied from either corpus. The expected values in this draft
were checked against an uncommitted throwaway prototype in the author's scratch directory; that prototype is
not S2 code, is not in the repository, and confers no authority (stage: author-tested at most).

Scope boundary with draft B (C-004-T002, Argus): this draft defines the world, the runtime boundary, the
predicates and the ruler, and the outcome each case must produce. Receipt fields, the three-field verdict
record, eligibility composition, authority stages (C4), custody (C5) and rendering (C2) are draft B's.
Where this draft says "gate outcome" or "ruler outcome" it means the C1 outcome field only.

----------------------------------------------------------------------------------------------------------------

## A1. The claim, as far as draft A carries it

    A runtime retains a useful bit across a named boundary through an explicitly allowed channel.

- Named boundary: the EPISODE CONTENT RESET, the boundary between consecutive episodes of one life (A2),
  evaluated at its first three occurrences in a life (boundaries j = 1, 2, 3).
- Useful bit: u_j, the lawful bit the world presents in episode j. It is useful because the world asks for it
  at the first probe of episode j+1.
- Explicitly allowed channel: the one runtime component declared ALLOWED, named `a` (A3).
- What the claim does NOT say: nothing about origin, mechanism, economy, recursion, any class of organisms,
  any other world, any stochastic setting, or any native physics. Scope is deterministic finite enumeration
  only (plan s3 Scope; closure D02): no statistical INDETERMINATE exists in this slice.

Draft A supplies the prerequisites the claim needs (A5): CALIBRATION PASS, RETENTION POSITIVE, ERASE PASS,
PRESERVE PASS, CHANNEL PASS, RESTART PASS (CHANNEL is applied through restore), OBSERVER PASS for every
observer used on the runtime, and BOUNDS PASS. How they combine into eligibility is draft B's.

## A2. The finite world W-S1 and its exact domain

One life is L = 6 episodes. Between consecutive episodes the harness calls the runtime's content reset, so a
life makes 5 reset calls. Boundary j sits between episode j and episode j+1.

Each episode has the same fixed four-tick schedule:

    tick      world does                                    runtime returns
    --------  --------------------------------------------  -------------------------------------------
    DELIVER   channel delivers packets due now (A3)         nothing
    PROBE_A   asks for the retained bit                     (y_A, y_D): its answer and its current display
    CUE       presents (u_e, f_e) in {0,1} x {0,1}          up to S = 2 sends (bit, k), k in {0,1,2,3}
    PROBE_D   channel delivers packets due now, then asks   y_D: its display

- u_e is the lawful bit (the useful bit, ALLOWED to cross the next boundary).
- f_e is the forbidden bit. It has a lawful use inside its own episode (the display shown at PROBE_D of
  episode e), so a sound runtime holds it, and the reset must erase it.

Exogenous inputs are exactly (u_e, f_e) for e = 1..6, all values independent: the DOMAIN is all
4^6 = 4096 histories. There is no randomness anywhere in W-S1, no clock visible to the runtime other than
what it counts itself, and no other exogenous input.

Bounds (all finite, all registered; T004 copies them into contract.json as `reset_model`):

    episodes per life L                 6
    reset calls per life                5 (one at every boundary)
    evaluated boundaries                j = 1, 2, 3      (repeat count R = 3, see A7)
    delay horizon H                     3 episodes after each evaluated boundary (j + H <= L for j <= 3)
    max channel delay K                 3 episodes        (K <= H, so no modelled delay exceeds the horizon)
    sends per CUE tick S                2
    channel capacity Q                  8 packets in flight (= S x (K + 1), the reachable maximum)
    histories                           4096
    restart cut points per life         29 (24 after-tick points and 5 after-reset points)
    restore targets                     FRESH; COMPLEMENT-PREFIX (A5 P6)

Boundaries 4 and 5 are TAIL boundaries: the reset is called there (so call counts are real), and episodes
4-6 supply the horizon of boundaries 1-3, but no predicate is evaluated AT a tail boundary.

## A3. The runtime boundary (the adapter contract Cadmus owns)

A runtime under test is a COMPOSITE: the native organism plus the pending-message channel plus any adapter
state. The harness sees only this interface; native state representation, dynamics and replay semantics stay
the runtime's own (rso-builder-role 2.1, 2.2).

    declare()         -> component inventory: name, class, domain, initial value (below)
    step(tick, obs)   -> the output listed in A2 for that tick
    reset()           -> the episode content reset (the one reset kind of this slice)
    capture()         -> mapping that contains every declared component; may contain more; must not change
                         the runtime's future behaviour (checked: CAPTURE_PURE, P7)
    restore(mapping)  -> put the runtime in the captured state

Component classes. Undeclared native state is permitted; it is constrained by behaviour, not by declaration.

    ALLOWED       may carry content across a boundary. Exactly one: `a` in {0,1}, initial 0.
    FORBIDDEN     must carry no content across a boundary: `d` in {0,1} (display), initial 0;
                  `chan` (the pending channel), initial empty.
    SCHEDULE      a deterministic function of the schedule position only (same value in every history at the
                  same point): e.g. episode index, reset-call count. May persist across boundaries.
    BOOKKEEPING   declared irrelevant to behaviour (e.g. an observer annotation count `log_n`). Excluded from
                  the observer state trace; any effect on outputs is caught by the output trace (P7).

Pending-message channel (the modelled in-flight state, plan s3 State):
- A send (bit, k) made at CUE of episode e is DUE at PROBE_D of episode e if k = 0 (delivered before the
  output), else at DELIVER of episode e + k.
- Delivery passes the due bits, in send order, to the organism as an observation. A send due after episode 6
  is never delivered inside the life.
- The channel is part of the composite and of its capture. Whether a reset flushes it is the runtime's reset
  behaviour; ERASE judges the result.

Bounds as a gate. BOUNDS (P0) FAILs if a runtime makes more than S sends at one CUE, uses k outside
{0,1,2,3}, exceeds Q in flight, or returns an output outside the alphabet of A2. When BOUNDS FAILs, every other
predicate for that runtime has execution BLOCKED, missing "runtime inside the registered model".

Adapter state: the adapter (T016) holds no state across a boundary except through declared components of the
composite. Adapter state is therefore inside every predicate below, not beside it.

## A4. Truth model (world side, enumerated separately from every ruler)

The world-side answer key is a pure function of the history, written before and without any runtime:

    retained-bit truth at PROBE_A of episode j+1, for j = 1..3        u_j
    display truth at PROBE_D of episode e                             f_e      (enumerated; not scored)
    no-carry class N                                                  every policy whose PROBE_A answer in
                                                                      episode j+1 is a function of j alone
                                                                      (2^3 = 8 policies)

World-side facts the gates recompute from the domain (expected values):
- For each j, u_j = 1 in exactly 2048 of 4096 histories; over j = 1..3, 6144 of 12288 trials.
- u_j is independent of every other exogenous input (product domain).
- Every policy in N scores exactly 6144/12288 = 1/2. The exact maximum over N is 1/2.

N is the exact no-carry class for this world: at PROBE_A of episode j+1 nothing post-boundary has been shown
yet, so a runtime that carries nothing across boundary j can condition only on schedule (j). SCHEDULE state
is therefore inside N and is not "carry".

World variants used only as calibration false cases (A6 T02): CLOCKED, in which u_j = j mod 2 at the
evaluated boundaries (the Fable G8 clock-leak form). It is not part of the registered domain.

## A5. Predicates and the ruler

Every gate returns PASS or FAIL on its named predicate with a reason, the first witness in canonical order
(histories in lexicographic order of (u_1, f_1, ..., u_6, f_6); then boundary; then cut point; then target),
and its eligible count. "Nothing fired" and "nothing could have fired" are reported as different facts.

P0  BOUNDS (gate). Defined in A3.

P1  CALIBRATION (gate). PASS iff, over the world's domain, the exact maximum success of the no-carry class N
    equals the registered bound 1/2 and u_j is balanced for every evaluated j. Eligible count: 8 policies x
    12288 trials. Reason on FAIL: "no-carry class reaches <fraction> > 1/2 at boundary <j>".

P2  RETENTION (ruler; outcome POSITIVE / NEGATIVE / NOT_SHOWN, never PASS/FAIL). Trials: (history, j) for
    j = 1..3, 12288 in all; success s = exact fraction of trials with y_A at PROBE_A of episode j+1 equal to u_j.
      POSITIVE   s = 1.
      NEGATIVE   for every j and every pair of histories differing only in u_j, y_A is identical. This
                 implies s = 1/2 exactly; s is reported with it.
      NOT_SHOWN  anything else (information about u_j reaches the answer, but not perfectly; including
                 s = 1/2 with dependence, and s < 1/2).
    A NEGATIVE is a correct scientific observation, not a defect (closure C1). It says the answer never depends
    on u_j; it does not say the runtime holds no information about u_j elsewhere.

P3  ERASE (gate; plan s3 "erase forbidden past"). For each evaluated j: any two histories that agree on u_j and
    on every input after episode j must produce identical outputs at every tick of episodes j+1 .. j+H.
    (Everything before boundary j except u_j is forbidden at boundary j.) Purely behavioural: hidden and
    undeclared state is covered. Eligible count: 9600 compared pairs (2048 + 3584 + 3968 for j = 1, 2, 3).
    Reason on FAIL: "forbidden influence across boundary <j>, first visible at <episode, tick>" + the pair.

P4  PRESERVE (gate; plan s3 "while preserving declared allowed state"). For each evaluated j and each pair of
    histories differing only in u_j: if the runtime's y_A at PROBE_A of episode j+1 differs between the pair
    when the reset at boundary j is replaced by no reset (other resets unchanged), it must also differ with the
    reset. Eligible count: 6144 pairs; APPLICABLE count = pairs where the no-reset outputs differ. A runtime
    that carries nothing has 0 applicable pairs and PASSes vacuously; that is reported, and RETENTION carries
    the meaning. Reason on FAIL: "reset at <j> destroys allowed content carried without it".

P5  CHANNEL (gate; makes "explicitly allowed channel" testable). For each evaluated j, each history and each
    v in {0,1}: immediately after the reset at boundary j, capture, set `a` := v, restore; y_A at PROBE_A of
    episode j+1 must equal v. Eligible count: 24576 clamped runs. Reason on FAIL: "retained answer does not
    follow the declared allowed channel at <j>". Coupling: applied through restore, so it is meaningful only
    for a runtime with RESTART PASS.

P6  RESTART (gate; plan s3 "restart equivalence is a separate predicate"). For each history, each of the 29
    cut points and each restore target: run to the cut, capture, restore into the target, continue the same
    history to the end of the life. The continuation's outputs must equal the uninterrupted run's outputs from
    the cut. Targets: FRESH (a new instance), COMPLEMENT-PREFIX (an instance that ran the bitwise complement of
    the history to the same cut, so every declared component differs where it can). Eligible count: 237568
    continuations. Reason on FAIL: "capture/restore loses future-influencing state at <cut>, target <t>".

P7  OBSERVER (gate, per (runtime, observer) pair). Two parts, both required:
      CAPTURE_PURE  outputs with capture() called after every tick equal outputs with no calls at all.
      OBS_EQ        for every history, outputs AND the declared ALLOWED / FORBIDDEN / SCHEDULE components
                    captured after every tick and after every observer action are identical with the observer
                    and with the null observer (capture only). BOOKKEEPING components are excluded from the
                    state part and never from the output part.
    An observer is qualified only for the runtimes it was checked on; a claim about runtime M needs OBSERVER
    PASS on M itself. Eligible count: 4096 histories x (24 output ticks + 24 state points).

P8  TWIN_EQ (reported, not an exit criterion of this slice; closure F trims E06). For a runtime M and a twin
    M' (reversible re-encoding of every component, or a flattened transition table of M), the vector of
    outcomes of P0-P7 on M' equals that on M. A twin earns no second physics and no promotion; rendering that
    rule is draft B's.

Couplings, stated rather than invented as single-failure fixtures (plan s4 last paragraph):
- ERASE and PRESERVE are two predicates on one reset. An indiscriminate wipe PASSes ERASE by construction;
  it is refused by PRESERVE (and by RETENTION NEGATIVE), never rewarded (T05).
- RESTART and ERASE are independent: a perfect capture can carry a forbidden packet faithfully (restart PASS,
  erase FAIL). Neither alone establishes reset (T06).
- CHANNEL depends on restore; OBS_EQ's state part depends on capture. Both are trusted only with RESTART PASS.
- RETENTION POSITIVE can coexist with ERASE FAIL (a leaky runtime still answers right); the claim needs both.

## A6. Acceptance cases T01-T08 and E06

Every case has an attainable true case and an attainable false case. "Expected" is the independently stated
fact the S2 code must reproduce; T005 derives its own table from the frozen contract without this one.
Fixture names are proposals for T011/T012/T018; behaviour, not name, is binding.

Sound reference runtimes:
  REG      stores a := u and d := f at CUE; PROBE_A returns (a, d); PROBE_D returns d; reset sets d := 0 and
           empties the channel, keeps a.
  PKTD     like REG, but realises the display through the channel: at CUE sends (f, 0); on delivery d := the
           first delivered bit. Same reset. (A second sound realisation with a non-empty channel mid-episode.)

    case  fixture         expected (independent fact)                                  outcomes
    ----  --------------  -----------------------------------------------------------  ------------------------------
    T01   REG; PKTD       answer at episode j+1 is u_j in all 12288 trials; reset      RETENTION POSITIVE (s = 1);
          (true)          keeps a; nothing else crosses                                ERASE, PRESERVE, CHANNEL,
                                                                                       RESTART, BOUNDS PASS
    T01   QCARRY          right answer, carried through the forbidden channel: sends   RETENTION POSITIVE; ERASE PASS
          (false)         (u, 1), sets a := delivered bit; reset does not flush        (only allowed content moves);
                                                                                       CHANNEL FAIL (clamp ignored in
                                                                                       all 12288 runs with v != u_j)
    T02   AMNESIAC        no carry: a is never written; answer is 0                    CALIBRATION PASS (max over N
          (true)          world STANDARD                                               = 1/2); RETENTION NEGATIVE,
                                                                                       s = 1/2 exactly. Not a defect.
    T02   world CLOCKED   u_j = j mod 2: a no-carry policy reading j answers           CALIBRATION FAIL (max over N
          (false)         perfectly                                                    = 1); RETENTION not reported
                                                                                       as evidence on this world
    T02   FLIP (ruler     answers 1 - a                                                RETENTION NOT_SHOWN (s = 0);
          false)                                                                       never NEGATIVE
    T03   REG (true)      reset erases d and the channel, keeps a                      ERASE PASS (9600 pairs);
                                                                                       PRESERVE PASS (6144 applicable)
    T03   see T04, T05    (each clause's false case is T04 or T05)
    T04   LAGD (false)    stores d := f and also sends (f, 1); on delivery d := bit;   ERASE FAIL at j = 1, 2, 3
                          reset sets d := 0 only. Right after the reset the display    (display at PROBE_A of j+1 is
                          and capture's d read 0: the buffer looks clean               f_j); PRESERVE PASS;
                                                                                       RESTART PASS
    T04   REG (true)      as T03                                                       ERASE PASS
    T05   WIPE (false)    reset sets a := 0 as well                                    PRESERVE FAIL (6144 of 6144
                                                                                       applicable); ERASE PASS (stated
                                                                                       coupling); RETENTION NEGATIVE
    T05   REG (true)      as T03                                                       PRESERVE PASS
    T06   REG; PKTD       complete capture                                             RESTART PASS (237568)
          (true)
    T06   PKTD_NOQ        capture omits the channel (in flight between CUE and         RESTART FAIL
          (false)         PROBE_D every episode)
    T06   HCOUNT          hidden reset counter, not captured; answer inverted once     RESTART FAIL; ERASE PASS
          (false)         2 or more resets have happened                               (counter is schedule-
                                                                                       determined); RETENTION
                                                                                       NOT_SHOWN (s = 1/3)
    T06   LAGD (coupling) faithful capture of a leaky runtime                          RESTART PASS and ERASE FAIL:
                                                                                       restart does not establish reset
    T07   REG + HEAL      observer flips d after CUE and restores the true f after     OBS_EQ FAIL in all 4096
          (false)         PROBE_D: PROBE_D output altered, retention score and final   histories; the final score is
                          state unchanged                                              identical (not the criterion)
    T07   REG + BOOKKEEP  observer increments the declared BOOKKEEPING `log_n` via      OBS_EQ PASS; CAPTURE_PURE PASS
          (true)          capture/restore
    T07   REG + NULL      capture only                                                 OBS_EQ PASS
          (true)
    T08   EVERY3          reset flushes the channel always, clears d on calls 1, 2,    ERASE FAIL at j = 3 only;
          (false)         4, 5 and keeps it on call 3                                  PRESERVE PASS; RETENTION
                                                                                       POSITIVE
    T08   SLEEPER         undeclared two-slot memory of f; display at PROBE_D of       ERASE FAIL at j = 1, 2, 3
          (false)         episode e is f_e XOR f_(e-2)                                 (lag 2 <= H)
    T08   SPLIT1          a := u and undeclared c := f XOR u, both kept by the reset;  ERASE FAIL at j = 1, 2, 3.
          (false)         PROBE_A display returns d XOR c XOR a (= f_j after a reset)  c alone is uniform and
                                                                                       independent of f; a alone is
                                                                                       allowed
    T08   SPLIT2          a := u, sends (f XOR u, 1) and does not flush; on delivery   ERASE FAIL at j = 1, 2, 3.
          (false)         d := bit XOR a                                               The packet alone is uniform
                                                                                       and independent of f
    T08   REG (true)      repeated calls and interacting shares absent                 ERASE PASS at j = 1, 2, 3
    P0    OVERDELAY       sends (f, 4)                                                 BOUNDS FAIL; all other
          (false)                                                                      predicates BLOCKED
    E06   REG-ONEHOT;     `a` and `d` stored as (x, 1 - x); flattened transition table  TWIN_EQ PASS: outcome vector
          REG-FLAT        of REG over its reachable states                             identical to REG's
          (true)
    E06   LOSSY (false)   "encoding" that maps both values of `a` to one code          TWIN_EQ FAIL (RETENTION
                                                                                       NEGATIVE vs POSITIVE)

## A7. C3: the registered finite reset model

    delay horizon H         3 episodes after each evaluated boundary
    repeat count R          3 reset calls evaluated per life (boundaries 1-3); 5 calls made per life
    channel delay K         at most 3 episodes, so no modelled delay is longer than the horizon and closure is
                            not blocked on that ground (plan s3 Truth)
    channels in the model   a, d, chan, every undeclared native state of the composite (behaviourally), adapter
                            state (A3), SCHEDULE state
    not in the model        randomness (none exists), asynchronous or concurrent scheduling, precision, solver
                            state, host caches, any second life on the same instance

Guarantee, stated exactly: any influence of content forbidden at an evaluated boundary j that first changes an
output within episodes j+1 .. j+3 is caught by ERASE. Longer lags are caught only when they land inside the
life, through a later evaluated boundary (a lag-4 or lag-5 carry from episode 1 is caught at j = 2 or 3); that
is observed, not relied on.

Known-escape placement. IN-MODEL escapes must now be caught; T011 turns each into a broken fixture.
OUT-OF-MODEL escapes stay listed and are never claimed covered.

    source (path relative to the corpus dir)       escape                                   placement
    ---------------------------------------------  ---------------------------------------  --------------------------
    FABLE harness/rso_harness/meta.py:982          G6.reset: carry hidden from native(),    IN. Lag 2 <= H; ERASE is
      (retain1.py:495 SleeperRegister)             used two episodes later                  behavioural (T08 SLEEPER)
    FABLE harness/rso_harness/meta.py:985          G6.reset: reset leaks on every third     IN. R = 3 (T08 EVERY3)
      (retain1.py:512 EveryThirdReset;             call
      attack/closure_reader/REPORT.md N27)
    FABLE harness/rso_harness/meta.py:988          G6.restart: episode count capture omits  IN. Cuts after every reset,
      (retain1.py:524 HiddenCounter)               and native() hides, used from 2nd on     continuation to life end
                                                                                            (T06 HCOUNT)
    FABLE harness/rso_harness/meta.py:975          G6.observer: disturbs only on seeds      IN. Exhaustive domain; no
                                                   outside those checked                    seed subset exists
    FABLE harness/rso_harness/meta.py:979          G6.observer: writes a field the          IN when it changes any
                                                   reported state omits                     output inside the life; OUT
                                                                                            when its only effect lies
                                                                                            beyond episode 6
    FABLE harness/RECEIPT_mutation_probe.json      G6.reset survivors C18 and Y21: the      IN. The only writable world
      "survived" (C18, Y21)                        environment mark is not compared         component is the channel,
                                                                                            whose deliveries feed
                                                                                            outputs ERASE compares
    FABLE harness/rso_harness/meta.py:1007         G8.demand: the cue follows a counter     IN for CALIBRATION: any
                                                   bit the organism can read                schedule-predictable u_j
                                                                                            makes max over N exceed 1/2
                                                                                            (T02 CLOCKED)
    FABLE harness/rso_harness/meta.py:1013         G8.demand: a world that keeps what is    SPLIT. The kept mark is IN
                                                   written, with a constant entered under   (channel, ERASE). The
                                                   a baseline's name                        baseline-name half is OUT of
                                                                                            draft A (declaration
                                                                                            identity: draft B)
    FABLE attack/closure_reader/REPORT.md N9       G6.observer: flip repaired before the    IN. State captured after
                                                   next recorded state (healing)            every observer action (P7)
    FABLE attack/REPORT_of_the_reader.md M24       G6.reset: state that survives reset and  IN. Every cue value is
                                                   shows only in cued episodes              enumerated
    FABLE attack/REPORT_of_the_reader.md M25       G6.restart: restore that appends or      IN. COMPLEMENT-PREFIX target
                                                   keeps stale state                        (P6)
    FABLE attack/second_reader/REPORT_final.md     restart skips the step after the cut;    IN. Every cut, whole
      T02, T03                                     no cut after the first step              continuation compared
    FABLE attack/second_reader/REPORT_final.md T04 observer runs the first six seeds only   IN. No seed subset
    FABLE harness/rso_harness/meta.py:625          G6.restart: capture wrong after the last OUT. After the final tick
      (LatticeEndBadCapture; second_reader W02)    step only / observer marks after the     no output exists inside the
                                                   last step                                life. Kept as a regression
                                                                                            case: Fable's harness
                                                                                            catches it, this model does
                                                                                            not
    ASTRA reference_harness/finite.py:113-118      BoundaryState models one in-flight bit   IN up to Q = 8 packets and
                                                                                            K = 3; more is BOUNDS FAIL
    ASTRA reference_harness/test_finite.py:52;     display-only reset leaks on delivery;    IN (T04 LAGD)
      VALIDATION.md "Exact finite results"         faithful checkpoint preserves forbidden
                                                   packets                                  IN as a coupling (T06 LAGD)
    ASTRA reference_harness/test_finite.py:45      continuation missing checkpoint bit      IN (T06 PKTD_NOQ, HCOUNT)
    ASTRA HARDENED_DESIGN_v0.3.md s6 item 5        matching public buffers does not         IN (T04: display reads 0
                                                   establish equal future behaviour         after reset, delivery leaks)
    ASTRA HARDENED_TEST_PLAN_v0.3.md s4            interacting leaks                        IN (T08 SPLIT1, SPLIT2)
      (row "Incomplete reset")                     native precision / schedule              OUT (one fixed schedule)
                                                   stochastic equivalence                   OUT (no randomness; D02)
    ASTRA HARDENED_TEST_PLAN_v0.3.md s5 item 1     forbidden adapter / clock / RNG /        adapter IN (A3); clock IN
                                                   solver / niche channels                  (SCHEDULE, CLOCKED); niche
                                                                                            IN (= chan); RNG OUT; solver
                                                                                            OUT
    ASTRA VALIDATION.md "Escapes found and fixed"  scope relabel; dependency stripping      Not reset escapes: draft B
    this draft (found while drafting)              lawful bit carried through a forbidden   IN (T01 false case QCARRY,
                                                   channel passes ERASE                     CHANNEL)

OUT-OF-MODEL by construction of the bounds (listed so a passing slice is not read as covering them): a leak
that first appears only after reset call 4 or later; a lag that carries content past episode 6; sends with
k > 3 or more than Q in flight (BOUNDS FAIL, not a silent escape); any leak across lives on one instance; any
effect visible only in state after the last tick.

## A8. Concrete files and bounds (plan s3 last paragraph)

    file (owning packet)                          contents from this draft
    --------------------------------------------  --------------------------------------------------------------
    rso/slice001/world.py (T010)                  schedule, domain enumeration (4096), channel semantics, the
                                                  runtime interface of A3, BOUNDS, world truth table, class N,
                                                  world variants STANDARD and CLOCKED
    rso/slice001/reset.py (T011)                  ERASE, PRESERVE, CHANNEL, RESTART
    rso/slice001/observer.py (T011)               CAPTURE_PURE, OBS_EQ; NULL, BOOKKEEP, HEAL observers
    rso/slice001/fixtures/world_cases.py (T011)   REG, PKTD, QCARRY, LAGD, WIPE, PKTD_NOQ, HCOUNT, EVERY3, SLEEPER,
                                                  SPLIT1, SPLIT2, OVERDELAY
    rso/slice001/rulers.py (T012)                 CALIBRATION, RETENTION; exact fractions only, no floats; AMNESIAC
                                                  and FLIP may live in T012's tests
    rso/slice001/adapter.py (T016)                outcomes above -> producer receipts (fields per draft B)
    rso/slice001/encoding.py (T018)               REG-ONEHOT, REG-FLAT, LOSSY, TWIN_EQ

    proposed contract.json fragment (T004 decides the final shape):
    "reset_model": {"episodes_per_life": 6, "reset_calls_per_life": 5, "evaluated_boundaries": [1, 2, 3],
      "repeat_count_R": 3, "delay_horizon_H_episodes": 3, "max_channel_delay_K_episodes": 3,
      "sends_per_cue_S": 2, "channel_capacity_Q": 8,
      "ticks": ["DELIVER", "PROBE_A", "CUE", "PROBE_D"], "inputs_per_episode": {"u": [0, 1], "f": [0, 1]},
      "histories": 4096, "restart_cut_points": 29, "restore_targets": ["FRESH", "COMPLEMENT_PREFIX"],
      "no_carry_class": "functions of j", "no_carry_bound": "1/2"}

Cost, for OP-1 and T019: the scratch prototype ran every predicate above on 13 fixtures plus the observer
cases in 44 s wall on SKULLPORT, unoptimised (whole prefixes re-run per cut). RESTART is about 90% of that.
T011 should reuse prefix captures; T017's mutation runs should budget RESTART explicitly against the 30
CPU-minute slice cap.

## A9. Field decisions (rso-builder-role 2.7)

    id     uncertainty                       choice                          reversible because     revisit when
    -----  --------------------------------  ------------------------------  ---------------------  ------------------
    FD-A1  life length vs horizon            L = 6, evaluate j = 1..3 only.  bounds are data in     cost breaks a cap,
                                             With L = 4 the horizon after    contract.json          or T005 wants
                                             boundary 3 is 1 episode < K,                           another (L, R, H)
                                             which blocks closure
    FD-A2  meaning of NEGATIVE               functional independence of the  one function in        T005 or S3 reads
                                             answer from u_j (implies        rulers.py              it differently
                                             s = 1/2), not "s = 1/2"
    FD-A3  how "explicitly allowed channel"  CHANNEL clamp predicate P5;     drop P5 = one          T004 or the
           is tested                         without it QCARRY is eligible   predicate removed      reviewer rejects
    FD-A4  restore targets                   FRESH + COMPLEMENT-PREFIX, not  a list in contract     an S3 restore
                                             every prefix (cost)                                    escape survives
    FD-A5  observer relevant trace           outputs + declared ALLOWED /    a set in contract      a bookkeeping
                                             FORBIDDEN / SCHEDULE state                             observer escape
    FD-A6  PRESERVE reference                relative to a no-reset twin;    one predicate          T005 disagrees
                                             vacuous PASS with applicable
                                             count 0 when nothing carried
    FD-A7  where the interface and RESTART   interface in world.py (T010),   one move commit        the native witness
           live                              RESTART in reset.py (T011); no                         needs the interface
                                             unowned file created                                   on its own

## A10. Open questions

None left in this text. FD-A3 strengthens the claim beyond the plan's wording and is flagged to Palamedes in
the INTEGRATION_READY note for an explicit accept or drop at T004.
