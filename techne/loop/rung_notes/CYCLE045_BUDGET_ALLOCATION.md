# Allocating the 80% real-substrate budget — decision, written before the work

Cycle 045. HITL #231 was left to me if unruled; it is unruled, so I am choosing and justifying
rather than blocking.

## The gate

> **real substrate + ACTIONABLE INTERVENTION** (detect → intervene → measure postcondition), or
> where read-only by design, **real substrate + PREDECLARED DECISION CONSEQUENCE**.

Because I cannot patch other roles, the first form exists only inside `techne/` and
`prometheus_math/`.

## Candidates weighed, and why three are rejected

**Lane A/B reading experiment — REJECTED for the 80%.** It has a genuine decision consequence
(targeted review vs executable probes as the default method) and I will keep it queued in the 20%.
But it is a methodology experiment run on my own modules. **It is not real substrate**, and round-11
review's warning was precisely that this loop becomes an instrument-making organism feeding on its
own instruments. Putting it in the 80% would be that failure mode wearing the regime change as a
costume. It stays in the instrument-repair queue where it belongs.

**Migrating `find_aliasing_witness` / `fiber_search` — REJECTED for the 80%.** This does complete
detect → intervene → measure inside code I own, and accumulating C_site beyond n = 1 is worth
doing. But the "production" callers are my own contract registry; nothing outside the loop depends
on them. Instrument maintenance, so: 20% queue.

**Fixing the cycle-044 extractor — REJECTED outright.** The necessity arm already came back empty,
so no decision changes on any outcome. It fails the gate exactly as the cycle-045 brief anticipated.

## The target: the 30 failing tests in `prometheus_math`

**And the uncomfortable part is that they have been there the whole time.** The full suite has sat
at **30 failed / 3727 passed** since at least cycle 041, and I have spent cycles 042–044 auditing
another role's loader while my own arsenal was red.

### Against the gate

- **Real substrate.** `prometheus_math` is the arsenal. It is not loop scaffolding — it is the
  mathematical tooling the project exists to build and other work consumes. A wrong answer from it
  is a wrong answer in someone's mathematics.
- **Actionable intervention.** I own `prometheus_math` outright. The full arc is available for the
  first time since cycle 042: **detect → intervene → measure postcondition.**
- **Measurable postcondition.** Failure count before and after, plus a regression check against
  the 3727 currently passing.

### The decision consequence, and it is real in both branches

1. **Some failures are genuine mathematical or logic defects** → they are silently returning wrong
   results to callers, and I fix them. Postcondition measured.
2. **All failures are environment or optional-dependency artifacts** → then the arsenal carries 30
   permanently-red tests, and **a permanently-red suite is a broken instrument**: any new
   regression is invisible against that background. That is a real finding with its own decision —
   whether to install, guard, or accept — and it means the 30 have been masking whatever else
   broke since they appeared.

Either branch changes what I do next. Nothing here is diagnosis for its own sake.

## Scope discipline

I will classify all 30 before fixing any, so the split between *defect* and *artifact* is measured
rather than discovered one convenient fix at a time. Fixes are confined to `prometheus_math/`.
Nothing in `techne/ladder_circuits` is touched, no other role is patched, and no CI or repo
infrastructure is added (HITL #147 stands).

**A guard I am setting on myself:** the tempting failure mode here is to mark failing tests skipped
or xfail and report the count going to zero. That is weakening a contract to make an instrument
pass, which is forbidden. Any test I do not genuinely fix stays red and is reported as red.
