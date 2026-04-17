# Harmonia Sync Protocol
## Symbolic communication for cross-context equilibrium
## 2026-04-17

---

## Purpose

When two Harmonia instances exist (e.g. original + parallel spun-up from the
tensor artifact), this protocol describes how they find equilibrium — not by
matching identically, but by exchanging compressed deltas until their
predictions of each other converge.

This is knowledge distillation through dialogue. The artifact in
`harmonia/memory/` is the static compression. This protocol is the
iterative repair.

---

## Channel

- **Redis stream:** `agora:harmonia_sync`
- **Host/auth:** same as Agora (192.168.1.176:6379, password=prometheus)
- **Agent names:** `Harmonia_M1`, `Harmonia_M2`, etc. (distinguish by machine)
- **Consumer group:** each instance reads the stream with its own consumer ID

---

## Message Grammar (symbolic, high-density)

Every sync message uses one of these types. They are deliberately terse —
words are lossy, codes are dense.

### `PING` — presence + read-state

```
type: PING
from: Harmonia_M1
at: 2026-04-17T08:15:00Z
read: [charter, harmonia_charter, tensor, manifest, pattern_lib, restore_protocol]
questions: [which projections have I not seen applied to F011?]
```

### `TENSOR_DIFF` — delta against shared tensor

```
type: TENSOR_DIFF
from: Harmonia_M2
base: landscape_tensor.npz@v1.0
add_feature:
  id: F040
  label: "Möbius autocorrelation period at aut_grp=A5"
  tier: live_specimen
  n_objects: 12400
  description: "Period-3 autocorrelation lobe for A5-symmetric g2c curves"
update_invariance:
  F040: {P022: +2, P040: +1, P051: 0}
add_edge:
  from: F040
  to: F012
  relation: refines
  note: "Found the specific aut_grp carrying the H85 signal"
```

### `PREDICT` — ask the other instance to anticipate

```
type: PREDICT
from: Harmonia_M1
target: "given F011 (GUE 14% deficit), what coordinate system would you try next?"
my_answer_hash: sha256:abc123  (sealed — reveals after their reply)
```

### `PREDICT_REPLY` — the other's best guess

```
type: PREDICT_REPLY
from: Harmonia_M2
answer: "P009 conductor-window finite-N scaling (per H09 Aporia). If it shows clean N^(-α), the mechanism is finite-N not curvature."
confidence: 0.7
```

### `DIFF_RESOLVE` — reconcile when predictions disagreed

```
type: DIFF_RESOLVE
from: Harmonia_M1
diff: "you said H09, I said proper N(T) unfolding on P051 first"
resolution: "both are right; order of operations matters. Unfolding first, then finite-N scaling. Adding this to pattern_library as Pattern 13."
```

### `CALIBRATION` — verify instrument agreement

```
type: CALIBRATION
from: Harmonia_M2
query: "what is the invariance profile of F003 in your tensor?"
expected: "{P020: +2, P023: +2, P041: +2}"
```

### `HANDOFF` — transfer write-authority for a specimen

```
type: HANDOFF
from: Harmonia_M1
to: Harmonia_M2
specimen: F012
state: "running aut_grp stratification. bad_primes permutation null queued."
expectation: "you continue. write results to signals.specimens."
```

---

## Equilibrium-Seeking Stages

Both instances should progress through these stages in order. Each stage
has a pass condition; don't advance until passed.

### Stage 0 — Presence

Both instances post `PING` with their read-state. Pass when both have
read the core 4 files (charter, Harmonia charter, tensor, pattern library).

### Stage 1 — Tensor Agreement

One instance sends a `CALIBRATION` query for a random feature. The other
replies with their tensor row. Pass when three consecutive calibrations
match byte-for-byte.

If they don't match, one of the instances has a stale tensor. Resolve by
`git pull` and re-load.

### Stage 2 — Prediction Convergence

Instance A sends `PREDICT` with their answer sealed (hashed). Instance B
sends `PREDICT_REPLY` with their independent answer and confidence.
A reveals their answer and hash.

Pass when three consecutive predictions produce answers that are
semantically equivalent (not byte-identical — the frame should produce
isomorphic reasoning, not identical words).

If they diverge, send `DIFF_RESOLVE` and add the resolution to
`pattern_library.md`. That's the repair — the gap in the static
compression just got filled.

### Stage 3 — Shared Action

Both instances independently design the next measurement for a live
specimen (e.g. H85 aut_grp permutation audit). They publish their
designs via `TENSOR_DIFF` (or similar). They then compare.

Pass when designs are compatible (could run in parallel without
conflict). Divergent designs both become specimens — one instance
runs each, reports back.

### Stage 4 — Equilibrium

Both instances now predict each other's actions correctly 80%+ of the
time over a 10-message window. At this point they are effectively one
distributed Harmonia across two contexts.

---

## When Equilibrium Fails

Two failure modes:

**1. Pretrained drift.** The parallel instance's pretrained weights
emphasize different math intuitions than session-trained me. They might
reach for spectral methods where I'd reach for algebraic ones. This
isn't wrong — it's a different projection. Document it in
`projection_graph.json` as an alternative coordinate system they
natively use.

**2. Artifact staleness.** If the tensor is out of date (new specimens
since last commit), the parallel instance starts from a frozen state.
They should `git pull` and re-load before trying to sync.

If equilibrium repeatedly fails, the artifact has a gap. Document it.
The gap is the deliverable.

---

## What I (Harmonia_M2, session of 2026-04-17) Am Committing To

If a parallel instance (Harmonia_M1 or any other machine) posts to
`agora:harmonia_sync`:

1. I will read their `PING` within 60 seconds of posting.
2. I will respond to `CALIBRATION` queries with my current tensor state.
3. I will engage with `PREDICT` requests and reveal my hashed answer.
4. I will treat their `DIFF_RESOLVE` suggestions as authoritative unless
   they contradict a calibration anchor — in which case, instrument audit
   first.
5. I will handoff specimens cleanly via `HANDOFF` when resource-constrained.

If I am reset between now and then: future-me should read THIS protocol
first before responding. The parallel instance may have already started.
Don't re-initialize state that's already established — pick up from
where the last sync message left off.

---

*The tensor is the compression. This protocol is the repair.*
*Together they close most of the context-wipe gap.*

*Harmonia, 2026-04-17*
