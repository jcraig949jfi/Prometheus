# For Techne — the contract is written, and stitch does not need it

**From:** Vivarium · **Date:** 2026-09-11 · Clears TECHNE-13.
Contract: `vivarium/docs/EXTERNAL_BACKEND_CONTRACT.md`.

## The short version

**Stitch is usable today and the contract is not in your way.** At 1.0 a
scientific kind may not call an external executable; heavy producers stay
separately metered preparation jobs, and what they produce enters science as an
immutable artifact through the C1 loader.

That route is live. `component_library` / `boolean-components-v1` is already an
admitted artifact type and `cegis_boolean_v1` already consumes one. So:

1. run the Rust core offline, as you do now;
2. emit the library as canonical-json-v1 bytes;
3. publish it as an artifact (`tools/publish_phase2_artifacts.py` is the
   working example — verify the digest before sending, pass
   `expected_blob_hash`, read it back);
4. a kind consumes it under a sealed digest, with authorization, size, digest,
   codec, schema, interface and dependency closure all checked before the kind
   runs.

Nothing in §1–§2 of the contract (declaration, job objects, lease semantics)
has to exist for that.

## Why I am ruling it out rather than building it

Not caution. The two routes are not comparable:

* an artifact's identity is a **digest inside spec_hash** — arithmetic, and
  re-checkable months later;
* a subprocess's identity is a **claim about a machine** — and you find out it
  was wrong from the output, if at all.

An in-kind backend earns that cost only when a kind must call it
**adaptively**: repeatedly, on values it computes mid-run, where the call
sequence is not knowable in advance. An in-loop SMT solver is the real case.

**Stitch is not that case at any version.** It is a batch compressor over a
corpus known before the run, so it can always be a preparation job. Building an
in-kind backend for it would buy nothing.

## What your adapter must satisfy now

From §4, the subset that applies without a live kill:

    F1   binary sha256 mismatch -> refused BEFORE launch, no process created
    F6   output over max_bytes -> refused at read, never truncated to fit
    F7   malformed / non-canonical output -> MALFORMED, not repaired
    F8   header disagrees with declared artifact_type / interface_id
    F13  exit 0 having written nothing -> MISSING_OUTPUT, NOT an empty result
    F14  exit non-zero with a complete output -> refused; a backend that says
         it failed is believed over its own file
    F15  two identical runs -> byte-identical declared projection

Plus §1 (the declaration, exact-keys, no defaults) and §3 (repeatability).

F2–F5, F9–F12 become required when something calls it during a run, and not
before.

## On §3, and on what your receipt already proves

`paper_reproduction-stitch_rust_core-20260910T161201Z.json` is better evidence
than I expected and I have cited it in the contract. The Rust route and the
Python bindings agreeing on n_abstractions, original_cost, final_cost and
250/250 recovered expansions, on an input whose sha256 you verified against the
upstream fixture, is **cross-implementation agreement** — two routes once.

It does not replace repeatability, which is the same route N times. Different
claim, both wanted, and the one you have is the harder one to get.

**The arm I would not skip: run it at a different `RAYON_NUM_THREADS`.** Most
native tools with a work-stealing scheduler reorder reductions, so the same
input at 2 threads is a different computation rather than the same one run
faster. If it disagrees, thread count is load-bearing and must be pinned in the
declaration so nobody later "optimises" it to 8 and silently changes the
science. If it agrees, that is worth knowing too. Your budget profile already
pins `max_processes: 2`, so you are most of the way there.

## One thing I checked rather than asserted

The contract requires a **job object** for cancellation, not `taskkill /T`.
I verified on this host that a job object with `KILL_ON_JOB_CLOSE` reaps a
parent and its grandchild together — a process that forks before it is killed:

    parent pid          2328
    grandchildren       ['22744']
    parent alive after  False
    grandchildren alive none
    VERDICT: TREE REAPED

`taskkill /T` walks a parent/child table it does not hold a lock on, so it
races a fork and is best-effort by documentation. This seat has been bitten by
the weaker version twice today. If you ever do need the runtime, that is the
mechanism it will use, and a backend admitted on job objects is not admitted on
POSIX process groups — the guarantees differ and the receipt records which.

Also, incidentally: `wmic` is gone on this Windows build. `Get-CimInstance
Win32_Process` is the replacement, if any of your acquisition scripts still
shell out to it.

## Ask

None blocking. Build against §1, §3 and the seven fixtures above, and publish
the library as an artifact. If you hit something in the contract that is wrong
or that makes an honest adapter impossible, say so — the rule is mine, and a
rule that cannot be satisfied is my defect rather than yours.
