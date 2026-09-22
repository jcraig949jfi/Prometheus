# AETH-01 -- resource economics

Status: DRAFT. Depends on PHYSICS_SPEC_DRAFT.md's energy mechanism
(field 4, `WRITE_COST`, `MAINTENANCE_COST`, `REPLENISH_NUMER`,
`REPLENISH_AMOUNT`). All five are run parameters, not physics
constants -- a "resource regime" is a point in this 5-dimensional
parameter space, nothing more.

## Cost categories mapped onto AETH-01's mechanism

| R8 cost category | AETH-01 realization |
|---|---|
| remaining active | none directly -- being RESERVED_INERT is free; only *attempting* WRITE costs |
| changing matter (fields 0-3) | `WRITE_COST`, paid whenever a WRITE proposal is emitted, win or lose |
| moving | not physically present (no matter-relocation primitive, see PHYSICS_SPEC_DRAFT.md) |
| retaining state | `MAINTENANCE_COST`, paid by every site's stored energy every tick, whether active or inert -- holding energy anywhere is not free once `MAINTENANCE_COST>0` |
| executing local transformations | same as "changing matter": `WRITE_COST` |
| exporting/importing material | conservative transfer (field 4): source always pays the attempted amount; only a contest winner's target is credited; losers' amounts are destroyed -- exporting is risky, not just costly |
| maintaining gradients/boundaries | not a first-class primitive in AETH-01; only indirectly obtainable (a ring of sites could repeatedly re-write a boundary value) -- flagged as an absence, not solved here |

Two categories from R8 (moving, maintaining gradients/boundaries) are
NOT given dedicated mechanisms in AETH-01. This is a deliberate scope
limit, not an oversight (DECISIONS.md).

## Regime A -- "Execution-only" (recommended for first qualification)

    WRITE_COST       = 1
    MAINTENANCE_COST = 0
    REPLENISH_NUMER  = 0
    REPLENISH_AMOUNT = 0
    (MUT_NUMER independently swept, not part of the economic regime)

No passive decay or external inflow: each WRITE attempt spends 1 unit.
An isolated site has only its initial energy budget; field-4 transfers
can redistribute reserves between sites, never increase the world total.
This is the simplest cost model layered on AETH-00, fully reproducible
and easy to hand-verify. Dormancy is free of passive energy decay.
The world's total possible WRITEs are bounded by total initial energy /
WRITE_COST even WITH transfers; redistribution is not an exception to
finite total activity. Per-site pulse counts require the isolation
assumptions below, rather than ignoring incoming/outgoing transfers.

### Exact isolated pulse budget (write before maintenance)

For an unchanged WRITE site targeting fields 0-3, with no incoming or
outgoing energy transfers and no replenishment, let initial energy be E,
write cost w, maintenance m. If w>0, the exact emission count is zero
when E<w; otherwise `N = 1 + floor((E-w)/(w+m))`. Each full active tick
uses w+m until the last one: emission checks only E>=w, THEN maintenance
is floored at zero. Thus `floor(E/(w+m))` undercounts by one whenever
the remainder is >=w. Example: E=23,w=3,m=2 emits five times, with
post-tick energies 18,13,8,3,0; E=22 emits four times. With m=0 the
formula reduces to floor(E/w), and a starved site may retain energy.
With w=0 there is NO energy-limited exhaustion, even for m>0 and E=0;
the uint64 tick limit remains separate. These assumptions matter:
external activation, transfers, replenishment or self-reconfiguration
invalidate this isolated-site formula. See K4 in KILL_GATES_01.md and
the boundary/recurrence regressions in `test_aeth01_kill_gates.py`.

## Regime B -- "Resource-maintenance regime"

    WRITE_COST       = 1  (or swept)
    MAINTENANCE_COST = 1  (or swept, > 0)
    REPLENISH_NUMER  > 0  (sparse, e.g. ~1/1000 per site per tick)
    REPLENISH_AMOUNT = swept (e.g. 4-16)

Now holding energy is not free anywhere: every site's stored energy
decays every tick, active or not. The world is no longer intrinsically
finite-lived (there is an external inflow), but energy is genuinely
scarce and, absent replenishment, must be gained either by direct rain
(REPLENISH_NUMER/REPLENISH_AMOUNT credits a site independent of any
transfer contest, PHYSICS_SPEC_DRAFT.md) or by being targeted by a
winning transfer -- not by winning a transfer alone; a site with no
neighbors ever attempting a transfer to it can still gain energy purely
from rain (ASTRA_CLOSURE_REVIEW_02.md M03). This is the regime intended
to produce real resource-regime tension (below).

## Regime C -- "Free compute" (adversarial/boring negative control)

    WRITE_COST = 0, MAINTENANCE_COST = 0, REPLENISH_NUMER = 0

Not a scientifically interesting regime by itself -- it is the
explicit "what if cost didn't exist" control, run purely to confirm
that Regimes A/B's dynamics actually differ *because of* the cost
mechanism, not for some unrelated reason. R8's caution ("free unlimited
computation should be treated as suspicious") is operationalized here
as a required comparison baseline, not skipped.

## The central question: what makes persistent state worth paying for?

**[REPAIRED per ASTRA_REVIEW_01.md M02/M03, ACCEPT, see
REPAIR_LEDGER_01.md -- the framing below must not be read as "memory is
costly." It is not: the four template bytes (opcode/arg0/arg1/payload)
persist at ZERO energy cost under EVERY `MAINTENANCE_COST` setting, in
every regime. No resource payment retains an opcode, operand, payload,
or inert boundary; starvation never removes stored bytes, only blocks
future WRITE attempts. What follows is about ENERGY RESERVES, a
completely separate quantity from stored information.]**

Under Regime A, an energy reserve costs nothing extra beyond what it
already contains (no decay) -- so holding energy is "free" and the
question doesn't yet bite. Regime B is where it becomes real:

- **Decay makes hoarding a losing default.** Any site sitting on energy
  it isn't using is taxed every tick by `MAINTENANCE_COST`, so
  "storing energy just in case" is a guaranteed loss unless the
  eventual payoff (surviving a future lean tick without starving, or
  dominating under the resource policy a neighbor in a future transfer contest) exceeds the
  decay paid while waiting.
- **Replenishment variance is what creates the payoff.** `REPLENISH_NUMER`
  is a per-tick Bernoulli draw per site -- inflow is bursty and
  unpredictable at the single-site level even though its long-run rate
  is fixed and known. A site that immediately spends everything it
  receives is exposed to any gap between replenishment events; a site
  that retains a buffer persists such gaps and keeps acting
  (continuing to win arbitration contests, continuing to be copyable)
  when an all-spend neighbor would starve and go quiet.
- **The tradeoff is genuinely open, which is the point.** Whether
  buffering beats spending depends on the ratio of `MAINTENANCE_COST`
  to `REPLENISH_NUMER * REPLENISH_AMOUNT` and on local competition for
  transfers -- exactly the kind of quantity the habitability sweep
  (HABITABILITY.md) is designed to map, not something asserted here.

## Designed-in room for varied strategies (not a prescribed destination)

- **Stateless wins** when replenishment is dense/reliable relative to
  `MAINTENANCE_COST` (Regime B with high `REPLENISH_NUMER`): there is
  never a meaningful gap to buffer against, so paying decay to hold a
  reserve is pure loss -- spend-everything sites should dominate under the resource policy
  hoarders.
- **Inactive wins** when replenishment is extremely sparse and
  `MAINTENANCE_COST>0`: an ACTIVE site bleeds `WRITE_COST` every
  attempt while gaining little (few contest wins available), whereas a
  site that stays RESERVED_INERT still pays `MAINTENANCE_COST` on
  whatever energy it holds but never pays `WRITE_COST`, and its stored
  bytes remain UNCHANGED (not drifting -- **[REPAIRED per
  ASTRA_REVIEW_01.md S03: perturbation is copy-coupled and fires only on a
  winning WRITE; an untouched inactive byte does not autonomously drift,
  see PHYSICS_SPEC_DRAFT.md "Perturbation (Mu)"]**) until conditions (or a
  neighbor's WRITE) change.
- **Concentration/hoarding is a specific, real incentive, not merely a
  loss (M02/M03 repair).** Because `MAINTENANCE_COST` is charged per
  occupied energy-bearing SITE (floored at 0), merging two positive
  reserves into one site can REDUCE total future maintenance charged
  across the pair, until the 255 saturation cap or transfer losses
  dominate -- this favors compact energy concentration under some
  parameter regions, not a uniform "hoarding always loses" story.
- **Persistent state (buffering) wins** at intermediate
  `MAINTENANCE_COST`/replenishment ratios where lean gaps between
  inflow events are common enough to matter but not so punishing that
  holding energy at all is a net loss.
- **Donor-controlled transfer, recipient benefit.** A site whose
  arg0/arg1 happen to target field 4 of a specific neighbor is, from
  the physics' point of view, simply "attempting a transfer": the
  SOURCE is always debited (`WRITE_COST` plus its own attempted
  amount, every source debit made before any target credit,
  PHYSICS_SPEC_DRAFT.md), and the TARGET, if it wins the contest, is
  only ever credited, never debited by that transfer -- the physics
  provides no mechanism by which being the target of a transfer
  reduces a site's own energy. **[REPAIRED per
  ASTRA_CLOSURE_REVIEW_02.md M03: earlier language describing this as
  a donor possibly "draining a victim" had the debit/credit direction
  backwards -- donor debit refutes direct recipient draining.]**
  Whether a given transfer functions as feeding a struggling partner
  (raising both sites' joint persistence odds) or as upstream
  reconfiguration for the donor's own benefit is not a physics-level
  distinction at all; measuring realized benefit/contribution and
  donor-reconfiguration outcomes over a trajectory is exactly the
  behavior/outcome evidence HEREDITY_REQUIREMENTS.md and
  ADVERSARIAL_ANALYSIS.md must supply, not a "cooperation flag" the
  physics could never honestly provide (R1).
- **Measured resource benefit, not an inferred moral label.** A site
  that receives energy -- whether via a winning transfer or via direct
  rain (REPLENISH_NUMER/REPLENISH_AMOUNT, which credits a site without
  any transfer contest at all) -- gains stored energy regardless of
  whether it ever attempts a WRITE of its own. **[REPAIRED per
  ASTRA_CLOSURE_REVIEW_02.md M03: passive receipt alone does not by
  itself establish asymmetric resource dependence; direct rain refutes any claim that
  energy must be acquired only by winning a transfer.]** The physics
  makes no distinction between "a stored reserve for later use" and
  "a free rider": both are simply measured energy contribution/benefit
  over a trajectory (source of the credit, whether the recipient
  later spends it, and each site's own reconfiguration), not a
  asymmetric resource dependence/cooperation verdict the physics can supply on its own
  (R1: the physics does not get to know which one it is looking at).

No regime is asserted to be "the" AETH-01 configuration. Recommended
sequencing: qualify the substrate under Regime A first (simplest,
easiest to test exhaustively at tiny scale), then run the habitability
sweep primarily over Regime B's parameters once A is trusted.
