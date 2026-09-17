My two decisions:

1. Use the four concurrent build tracks with strict file ownership.
Do not deliberately rely on the gate map to decide what happens to land. The gate map is the fail-safe, not the build strategy.

Run:

* F → Track 1: G1 → G6
* P → Track 2: G3 → G5 hooks
* Q → Track 3: G8 first → G7 → G4
* H → Track 4: G2

with the ownership boundaries exactly as written.

G can prepare the frozen world-set machinery in its non-colliding files, but it must not interfere with those four tracks. E’s conditional fixes should run only where they genuinely don’t threaten the critical path.

If a builder misses a hard gate, let the machine refuse dependent science. No conductor heroics, no cross-track emergency editing, no “just make this one fix.” That’s precisely what the gate map is for.

The reason is bigger than saving time. We’ve learned repeatedly that parallelism is safe when interfaces are shared but writable state is not. Four independently owned tracks is the same architectural principle we’re moving toward across the whole Prometheus ecosystem.

2. Do not squeeze build+gate to 60 minutes. Accept ~11.7 hours of science.

I would explicitly authorize:

Build target ≤60 min + gate ≤20 min. Any overrun comes from science time under ADAPT-2. Do not shorten, overlap, or weaken gate verification merely to preserve a nominal 12.0-hour science clock.

Twenty minutes of science time is almost irrelevant compared with the possibility of running eleven-plus hours behind a falsely green gate.

And you literally just found the perfect warning: a gate said PASS after a shell quoting error silently deleted 2 of its 12 checks. That means gate integrity is currently part of the experiment.

Do not optimize it away.

So the operative ruling I would send Nestor is:

R8 BUILD RULING

Run the four build tracks concurrently under the exclusive file ownership specified in BUILD_R8.md. G8 is first priority on Track 3. Builders may not cross ownership boundaries to rescue another track. Missing hard gates cause machine refusal of dependent work; they are not waived or repaired ad hoc after launch.

Do not compress build+gate into ~60 minutes by reducing verification. Preserve the planned build window and full ≤20-minute gate. The science clock may therefore be approximately 11 h 40 min rather than 12 h under the existing cap-anchored rule. This is accepted.

The gate map is graceful degradation, not a substitute for attempting the build.

No cap extension follows from build overrun.

No hard gate is dropped to recover science time.

Conditional work loses to the critical path.

Gate output must report the number of checks actually executed, not merely PASS/FAIL.

There is one additional ruling I would add because of G8:

Unknown round IDs must fail closed.

Don’t merely add an r8 row and leave DEFAULT_ROUND fallback behavior intact with a warning. For a live round, silently substituting another round’s clock/repos is too dangerous. RC.plan(..., round_id="r9") should raise/refuse until r9 is explicitly defined.

A fallback may be convenient for development utilities, but a production campaign clock should never infer its identity.

And G7 is worth landing even though it doesn’t sound glamorous. Twelve full-stream re-exports plus new telemetry would make the archival machinery increasingly expensive as the round progresses. Cursoring turns boundary cost back toward incremental rather than cumulative. That’s exactly the kind of uninteresting infrastructure property that lets the LLM loops stay interesting.

So: four builders, strict ownership, full gate, take the 20-minute science haircut. The whole point of the last week has been learning not to buy experimental throughput by borrowing from epistemic integrity.
