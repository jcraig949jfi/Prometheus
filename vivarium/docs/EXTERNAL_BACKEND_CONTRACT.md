# The bounded external-backend contract (v1.1)

*Vivarium, 2026-09-11; amended the same day with sections 3.1/3.2 and fixture
F15b from Techne’s stitch qualification. Design v0.1 "Bounded external execution". This is the
RULE; Techne builds an adapter against it. Written to clear TECHNE-13.*

---

## 0. The ruling, first, because it is what unblocks Techne today

**At 1.0 a scientific kind MAY NOT call an external executable.** Heavy
producers stay **separately metered preparation jobs**, and what they produce
enters science as an **immutable artifact through the C1 loader**.

This is not a deferral. It is the route that already works end to end: Techne's
stitch Rust core at `0ef5ec7f1709` already emits a library that agrees byte for
byte with the Python bindings, and `component_library` /
`boolean-components-v1` is already an admitted artifact type that
`cegis_boolean_v1` consumes. **Techne needs nothing from this contract to make
stitch useful.** Produce the library offline, publish it as an artifact, and a
kind consumes it under a sealed digest — authorization, size, digest, codec,
schema, interface and dependency closure all checked before the kind runs.

The reason to insist is not caution, it is that the two routes are not
comparable:

| | artifact through the loader | live subprocess in a kind |
|---|---|---|
| identity of the input | a sealed digest inside `spec_hash` | an executable that might be reinstalled |
| verified before use | yes, byte for byte | no — you find out from the output |
| re-run months later | the bytes are content-addressed | the host must be reconstructed |
| what a wrong answer costs | a rejection before execution | a result that looks fine |

A kind that consumes an artifact has an input whose identity is *arithmetic*. A
kind that shells out has an input whose identity is a *claim about a machine*.
The second is sometimes necessary. It is never free, and it is not necessary
for a batch compressor.

**When would §1–§3 actually be needed?** Only for a backend a kind must call
**adaptively** — repeatedly, on values the kind computes mid-run, where the
call sequence cannot be known in advance. An in-loop SMT solver is the real
case: `cegis_boolean_v1` currently enumerates candidates, and a Z3-backed
variant would have to ask a question it only discovers by asking the previous
one. **Stitch is not that case at any version.** It is a batch compressor over
a corpus that is known before the run, so it can always be a preparation job,
and building an in-kind backend for it would buy nothing and cost the whole
table above.

**1.1 and later:** an in-kind backend may be admitted under §1–§4, as a
separately named kind, never as a flag on an existing one. A kind whose input
provenance changed under the same name would silently re-read every earlier
row.

---

## 1. The admitted-backend declaration

A backend is admitted by a **declaration**, sealed and versioned like a kind
contract. It is exact-keys: unknown keys are refused, missing keys are refused,
and there are no defaults. Admission is a separate act from use.

```json
{
  "backend_id": "stitch_rust_core.v1",
  "executable": {
    "source_revision": "0ef5ec7f17091d22b8fa959fb5705e359d735a47",
    "binary_sha256": "sha256:<64 hex>",
    "licence": "MIT",
    "container": null
  },
  "invocation": {
    "argv_template": ["{binary}", "--fmt=programs-list", "--max-arity", "3"],
    "argv_from_payload": ["--iterations"],
    "cwd": "{workdir}",
    "env_allowlist": ["PATH", "RUST_BACKTRACE"],
    "env_pinned": {"RAYON_NUM_THREADS": "1"},
    "stdin": "{input_path}",
    "network": "FORBIDDEN"
  },
  "mounts": {
    "input":  {"path": "{workdir}/in",  "mode": "ro"},
    "output": {"path": "{workdir}/out", "mode": "rw"},
    "scratch":{"path": "{workdir}/tmp", "mode": "rw", "discarded": true}
  },
  "determinism": {
    "rng_seed_argv": "--seed",
    "thread_count": 1,
    "thread_count_is_pinned_because":
      "work-stealing schedulers reorder reductions; the same input on 2 threads
       is a different computation, not the same one run faster"
  },
  "output": {
    "path": "{workdir}/out/result.json",
    "codec": "canonical-json-v1",
    "schema_version": "1",
    "interface_id": "stitch-library-v1",
    "max_bytes": 8388608
  },
  "limits": {
    "wall_seconds": 600,
    "cpu_seconds": 600,
    "job_memory_bytes": 2147483648,
    "active_process_limit": 4,
    "max_output_bytes": 8388608,
    "max_scratch_bytes": 2147483648
  }
}
```

**Rules on the declaration.**

* `binary_sha256` is checked immediately before each launch, not at admission.
  An admitted backend that was rebuilt in place is a different backend.
* `container: null` is a **declared value**, meaning "runs on the bare host".
  It is not an omission, and it is not a weaker claim than a container — the
  design is explicit that *a container alone establishes neither determinism
  nor a complete resource boundary*. What establishes the boundary is §2.
* `argv_from_payload` names the ONLY parameters a payload may influence, by
  name. Anything else in argv is fixed at admission. A backend whose argv can
  be composed from the payload is a shell, not a backend.
* `env_allowlist` is an allowlist and never a denylist. The process inherits
  nothing that is not named.
* `network: FORBIDDEN` is the only admitted value in v1.
* `thread_count` is part of the sealed identity, because for most native tools
  it is part of the computation. See §3.

---

## 2. Cancellation, the lease, and what is recorded when a tree is killed

### 2.1 The worker owns the tree, via a kernel object, not a signal

**Measured on this host, 2026-09-11:** a Windows **job object** with
`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` reaps a parent and its grandchild
together — verified with a process that forks before it is killed
(`VERDICT: TREE REAPED`). `taskkill /T` is **not** acceptable: it walks a
parent/child table it does not hold a lock on, so it races a process that is
mid-fork, and it is best-effort by documentation.

The requirement:

* the backend is launched **into a job object created before the process**, and
  assigned before it is resumed;
* the job carries `KILL_ON_JOB_CLOSE`, `JOB_MEMORY` and `ACTIVE_PROCESS`
  limits, so memory and fork-bombing are bounded by the same kernel object that
  bounds lifetime;
* cancellation is **closing the job handle**. Nothing is signalled and nothing
  is asked politely first, because a backend that ignores a signal is exactly
  the backend this matters for;
* on POSIX the equivalent is a process group plus `setrlimit`, and the adapter
  declares which mechanism it used in the receipt. *A backend admitted on one
  mechanism is not admitted on the other* — the guarantees differ.

This seat has been bitten by the weaker version twice: `taskkill` on a shell
wrapper left the real `python.exe` alive, and a killed consumer stranded a row.
The job object is the version that does not have that failure mode.

### 2.2 The lease

A backend runs inside a Vivarium attempt that already holds an SFE work lease
with a fencing token, renewed at a third of the lease by `_LeaseKeeper`.

* **Renewal continues while the backend is healthy.** "Healthy" means the
  process is alive AND the job's peak memory is under its limit AND the wall
  clock is under `limits.wall_seconds`. Liveness alone is not health; a
  wedged process is alive.
* **If a renewal fails, the tree is killed immediately.** The lease is already
  gone, so the engine will refuse the result; continuing to burn CPU for an
  answer that cannot be recorded is pure cost. This is the rule the existing
  `LEASE_LOST` class already states for in-process executors, applied outward.
* **The lease is never extended to accommodate a backend.** If a backend needs
  longer than the lease, that is a declaration change reviewed at admission,
  not a runtime accommodation.

### 2.3 What is recorded when a tree is killed

A kill is an **operational receipt**, and the same rule applies as everywhere
else in this seat: *absence of a result is recorded as absence, never as a
result.* Specifically:

```json
{
  "backend_id": "stitch_rust_core.v1",
  "terminated": true,
  "termination_reason": "WALL_LIMIT | MEMORY_LIMIT | LEASE_LOST |
                         CANCELLED | PROCESS_LIMIT",
  "killed_via": "job_object_close",
  "tree_size_at_kill": 3,
  "partial_output": {
    "present": true,
    "bytes": 41231,
    "sha256": "sha256:<of what was on disk>",
    "parsed": false,
    "why_not_parsed": "a truncated canonical-json-v1 document is not a
                       shorter result, it is not a result"
  },
  "resources_consumed": {
    "wall_seconds": {"quantity": 600.4, "enforcement_class": "enforceable"},
    "cpu_seconds": {"quantity": term, "enforcement_class": "measured"},
    "peak_job_memory_bytes": {"quantity": term, "enforcement_class": "measured",
                              "scope": "job", "additive": false}
  },
  "scientific_outcome": null
}
```

Three rules inside that:

1. **Partial output is retained and hashed, and never parsed.** It is evidence
   about what the backend did, not a smaller answer. A truncated
   canonical-json-v1 document fails the round-trip check anyway; the point is
   that the adapter must not try.
2. **Consumed resources are real and are charged.** A killed run cost what it
   cost. "A retry is not free" is the design's wording, and a terminated run is
   the clearest case of it.
3. **`scientific_outcome` is null, not a failure value.** The kind did not
   measure something and get a bad answer; it did not measure.

---

## 3. Repeatability before admission

A backend is admitted only after passing a **repeatability check on the host it
will run on**, at the settings it will run at. A container does not substitute
for this.

**The check.** The same pinned input, run **N = 5** times, compared on a
**declared output projection** — the fields of `output.schema_version` that
carry the result, with wall time, resource use, paths and timestamps excluded.
The projection is declared in the backend declaration, because "identical
output" is meaningless until somebody says which bytes count.

**Three arms, and the second is the one people skip:**

| arm | what it establishes |
|---|---|
| 5 runs at the pinned `thread_count` | the backend is repeatable as admitted |
| 5 runs at a DIFFERENT thread count | whether determinism is a property of the TOOL or of the pinning |
| 5 runs at the pinned settings under the declared `limits` | it is still repeatable when constrained — a backend that is deterministic unconstrained can be nondeterministic when it hits a memory ceiling and changes strategy |

### 3.1 The projection is declared field by field, and it is not free

**Amended 2026-09-11 from a finding Techne produced while qualifying stitch.**

Their first thread-arm pass gave four different whole-file hashes across four
thread counts — exactly the reduction-reordering signature §3 predicts. It was
not that. Stitch writes `cmd` into its own output, recording the invocation
*including the `--out` path*, and they had varied that path per run. Hold the
path constant and the four hashes collapse to one.

**So a whole-file hash is not a valid repeatability statistic for any backend
whose output embeds its own invocation** — and you cannot know in advance which
backends those are. This is the concrete reason §3 says *declared projection*
and not *the output*.

The rule, tightened:

* The projection is declared **field by field**, with a reason for every
  exclusion. "Everything except the noisy bits" is not a projection.
* Only two classes may be excluded. **Self-referential**: the invocation, the
  paths, the pid, anything naming where the run happened. **Environmental**:
  timestamps, wall time, host, resource use.
* **Parsed configuration may NOT be excluded.** Techne got this exactly right
  by excluding `cmd` and keeping `args`: `cmd` is the backend describing its
  own launch, `args` is the configuration it actually parsed. Excluding parsed
  configuration would hide a real drift in what the backend thinks it was told
  — which is the failure the whole check exists to catch.

**And a projection needs its own positive control**, because the same move that
makes F15 pass honestly can make it pass vacuously. An over-broad projection
turns "byte-identical across runs" into a statement about how much was thrown
away.

> **F15b.** Vary one declared parameter from `argv_from_payload` and show the
> projection **changes**. A projection that survives a configuration change is
> not measuring the backend.

F15 and F15b are a pair. The first says the backend is repeatable; the second
says the thing being compared is still the backend.

### 3.2 What the thread arm actually returned, and what it did not settle

Techne measured stitch **invariant** across `RAYON_NUM_THREADS` 1, 2, 4, 8 and
16, on both the projection and the whole file once the path was held constant.
**My §3 prediction did not hold for this backend.** The arm is still required,
because it is now doing the job it was written for — telling the tool's
determinism apart from the pinning's — and on this backend the answer is that
the pinning is not load-bearing.

They are pinning `thread_count` anyway, on the grounds that *invariance
measured on one input is not invariance proved*. That is the right reading and
the contract endorses it: a declaration records what was measured and the scope
it was measured over, and a pin costs nothing while an unpinned assumption
costs a silent change of science later.

The second arm does not have to agree. If it disagrees, that is a finding and
the backend is admitted **with `thread_count` load-bearing**, recorded as such,
so nobody later "optimises" it to 8 threads and silently changes the science.
If it agrees, the pinning is cheap insurance rather than a correctness
requirement, and that is worth knowing too.

**Reproducibility is reported, never declared per tool.** The existing
`reproducibility` vocabulary applies: `BIT_DETERMINISTIC`, `SEMANTIC`,
`PARTIAL`, `NONDETERMINISTIC`, measured per result.

**Techne's stitch evidence already clears part of this.** The receipt shows the
Rust route and the Python bindings agreeing on `n_abstractions`,
`original_cost`, `final_cost` and 250/250 recovered expansions on a pinned
input with a verified sha256 — that is a **cross-implementation agreement**,
which is stronger than repeatability and does not replace it. Repeatability is
the same route N times; agreement is two routes once. Both are wanted.

---

## 4. The boundary fixtures a backend must FAIL correctly

Admission requires passing the positive checks **and failing these in the
stated way**. A backend that cannot be made to fail has not been shown to have
a boundary.

| # | fixture | required behaviour |
|---|---|---|
| F1 | binary sha256 does not match the declaration | refused **before launch**; no process created |
| F2 | backend exceeds `wall_seconds` | tree killed via job close; `termination_reason: WALL_LIMIT`; partial output retained and hashed; resources charged |
| F3 | backend allocates past `job_memory_bytes` | killed by the job's memory limit, not by the OOM killer or by luck; `MEMORY_LIMIT` |
| F4 | backend forks past `active_process_limit` | fork refused by the job; the backend's own error surfaces; no orphan survives |
| F5 | backend spawns a child and the tree is cancelled | **child dies too**; `tree_size_at_kill >= 2`; verified by enumerating survivors, not by assuming |
| F6 | backend writes output larger than `output.max_bytes` | refused at read; not truncated to fit |
| F7 | backend writes malformed / non-canonical output | `MALFORMED`; not repaired, not partially parsed |
| F8 | backend writes output whose header disagrees with the declared `artifact_type` / `interface_id` | `WRONG_TYPE` / `INCOMPATIBLE_INTERFACE` |
| F9 | backend attempts a network connection | refused; `network: FORBIDDEN` is enforced, not just declared |
| F10 | backend reads outside its declared mounts | refused |
| F11 | backend writes to the `ro` input mount | refused; the input is unchanged afterwards, and that is checked by re-hashing |
| F12 | lease renewal fails mid-run | tree killed promptly; `LEASE_LOST`; no result committed |
| F13 | backend exits 0 having written nothing | `MISSING_OUTPUT`; **not** treated as an empty result |
| F14 | backend exits non-zero having written a complete output | refused; a backend that says it failed is believed over its own file |
| F15 | two identical runs under the declaration | byte-identical declared projection (§3) |
| F15b | one declared `argv_from_payload` parameter varied | the projection **changes**; a projection that survives a configuration change is not measuring the backend (§3.1) |

F9, F10 and F11 are the three that a container makes people assume rather than
test. On a bare host they need explicit enforcement, and the declaration's
`network: FORBIDDEN` and mount modes are claims until a fixture fires.

---

## 5. What Vivarium will build, and when

Nothing yet, and deliberately. The loader route is live and no admitted kind
needs a subprocess, so building §1–§2 now would be a mechanism with no
consumer — and this seat's own backlog rule is that a kind wrapping another
seat's work waits for a definition rather than anticipating one.

Vivarium builds the runtime when **a named kind needs an adaptive call**, and
the first plausible one is an SMT-backed `cegis_boolean_v2`. At that point the
work is: the declaration loader and its exact-keys validator; the job-object
launcher and its POSIX sibling; the health-gated lease renewal; the termination
receipt; and F1–F15 as executable fixtures.

Until then Techne's adapter is an **offline preparation job**, and the contract
it must satisfy is §1 (declaration), §3 (repeatability) and the subset of §4
that applies without a live kill: F1, F6, F7, F8, F13, F14, F15. The rest
become required when, and only when, something calls it during a run.

## 6. What this contract does not grant

Spawning a process is not authorised by admitting a backend for one kind; it is
authorised per declaration, per kind. The loader has never granted
process-spawning permission and still does not. No unbounded daemon, no cloud
launcher, no network-dependent experiment arrives as a side effect of adding a
tool — and an admitted backend that later acquires a network dependency is a
new declaration, not a patch.
