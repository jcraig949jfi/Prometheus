# Techne — H0–H5 tool acquisition in isolation (2026-09-09)

Assignment: `roles/Archaeon/prompts/2026-09-08_h0h5/TECHNE.md`, routed by Archaeon in
`0a8198bd9`. Design: `roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md` §7 and
the brief's "Tool work and download discipline".

Everything below is in `techne/acquisition/`. Nothing entered SFE's interpreter. Nothing
here is qualified for a scientific run.

---

## What now runs

```
python -m techne.acquisition.host                                  # measure the host
python -m techne.scripts.acquire --list
python -m techne.scripts.acquire --entry <id> --profile <profile>  # [--dry-run]
python -m techne.scripts.license_audit
python -m techne.scripts.tool_check --all
python -m techne.acquisition.checks.dreamcoder_smoke
python -m pytest techne/tests/test_acquisition.py                  # 17 passed
```

`acquire` takes a manifest entry and a budget profile, exactly as the design specifies:
resolves the recorded commit or tag, reads the license out of the distributed artifact,
enumerates and pins submodules, obtains dependencies into an isolated cache and
environment, writes hashes, prints a receipt. Network is allowed there and nowhere else —
`offline_check` raises `NetworkForbidden` if a check tries to fetch anything.

---

## The four deliverables stayed four

The design separates tool installation, paper reproduction, adapter qualification and local
scientific benefit. Every receipt carries one `stage` and a `does_not_establish` list naming
the others, so a receipt cannot be quoted for a stage it never tested. A test enforces that
no receipt in this package ever claims `LOCAL_SCIENTIFIC_BENEFIT`.

| stage | where it stands |
|---|---|
| INSTALLATION | 4 python distributions + 1 repository, all pinned and hashed |
| FIRST_USEFUL_CHECK | z3, hypothesis, pyribs, stitch PASSED; dreamcoder BLOCKED |
| PAPER_REPRODUCTION | stitch nuts-bolts REPRODUCED exactly; nothing else attempted |
| ADAPTER_QUALIFICATION | **not attempted for any tool.** No Prometheus consumer calls these yet |
| LOCAL_SCIENTIFIC_BENEFIT | **not attempted, and nothing here is evidence for it** |

---

## Installed, pinned, hashed

All four: a locally computed sha256 over the bytes we received, **matching** PyPI's own
declared digest; a `--require-hashes --no-deps` lock over the resolved closure; the import
verified inside the isolated venv; version confirmed equal to the pin.

| entry | distribution | version | closure | license from the ARTIFACT |
|---|---|---|---|---|
| z3 | z3-solver | 5.0.0.0 | 1 | free text "MIT License", no SPDX, **no notice in the wheel** |
| hypothesis | hypothesis | 6.165.10 | 2 | `MPL-2.0` + notice shipped |
| pyribs | ribs | 0.12.0 | 18 | `MIT` + notice shipped |
| stitch | stitch_core | 0.1.29 | 1 | **none, anywhere** |

### stitch_core declares no license at all — and that is a redistribution blocker

Measured, not inferred: the wheel METADATA has no `License-Expression`, no `License`, and no
license classifier; the wheel ships no `LICENSE`/`COPYING`/`NOTICE`; and the **sdist** — 109
files — contains zero license-like files, with no license field in `Cargo.toml`,
`pyproject.toml` or `PKG-INFO`. GitHub's API reports MIT for `mlb2251/stitch`. That is
exactly the inference the design forbids, because what gets redistributed is the artifact,
not the repository page.

Recorded as `UNRESOLVED_NO_LICENSE_IN_ANY_DISTRIBUTED_ARTIFACT`. Internal use of the
installed copy continues. Exporting it, vendoring it, or shipping anything containing it
does not, until a human records a resolution.

z3-solver is the same shape at lower severity: the wheel declares MIT as free text and ships
no notice, while the sdist ships `core/LICENSE.txt`. That notice has been copied into the
cache beside the wheel, so the license travels with the copy — which is what the design
asks for and what installing the wheel alone does not achieve.

### One pin does not exist

`mlb2251/stitch` publishes exactly **one** tag (`v0.1.0`), and none corresponds to
`stitch_core` 0.1.29. So the source revision that built the wheel we installed is **not
verifiable from upstream tags**. Its sha256 is the only pin it has. Recorded in the manifest
as `kind: NONE_AVAILABLE` rather than dressed up with a branch head.

z3 → `z3-5.0.0`, hypothesis → `v6.165.10`, pyribs → `v0.12.0`, DreamCoder and POET →
explicit commit shas on branches untouched since 2022 and 2020.

---

## First useful checks

Each runs the tool inside its isolated env under a network-forbidden budget, and each
carries at least one case that can **fail**.

**Z3 — 5 of 6 cases decided, all passed; 1 undecided and retained.**
SAT, UNSAT and UNKNOWN all observed distinctly. Resource exhaustion separates cleanly by
`reason_unknown()`: wall clock gives `'timeout'`, deterministic rlimit gives
`'max. resource limit exceeded'`. Shaped like the named consumer (H1's Boolean oracle): the
solver is asked for an input distinguishing two circuits, and a pure-Python truth-table
evaluator sharing no code with z3 confirms the witness really distinguishes them — plus an
exhaustive 2^4 enumeration confirming the witness is in the true differing set. A
`NEGATIVE_CONTROL` case feeds the validator two non-distinguishing inputs and requires it to
reject both; without that, the positive result is vacuous.

UNDECIDED: `UNKNOWN_BY_INCOMPLETENESS`. Six candidates (nonlinear integer with and without
`smt.arith.nl`, a nonlinear real quintic, quantified UF with and without MBQI, a
forall-exists) all returned sat or unsat within four seconds on z3 5.0.0. This is **not** a
claim that z3 is complete — it is what this seat could elicit. Consumer-facing consequence:
on this build an `unknown` in practice is most likely a budget failure, and the adapter must
still surface it as a third outcome rather than coercing it to unsat.

**Hypothesis — 5 of 5, and a real isolation gap found.**
Both seeded defects minimised to their *exactly known* minimum — 128 for the byte-boundary
defect, `[0, 0]` for the duplicate defect — so a run that found some other counterexample
fails rather than passing as "found one". The minimised witnesses are persisted as a plain
JSON fixture and replayed here **without Hypothesis**.

The gap: setting `database=DirectoryBasedExampleDatabase(...)` scopes the saved **examples**
and nothing else. Hypothesis additionally creates its storage directory — a constants cache
— and that defaults to `.hypothesis` under the **current working directory**. Measured A/B:
without `HYPOTHESIS_STORAGE_DIRECTORY`, `.hypothesis` appeared in the cwd; with it set, the
cwd stayed clean and the directory landed inside the declared work dir. A consumer that
scopes only `database=` has scoped half of it. The check harness now sets that variable for
every hypothesis run.

Also recorded: `derandomize=True` implies `database=None`, so reproducibility has to come
from an explicit `@seed` if the scoped database is to exist at all.

**pyribs — 10 of 10, with the retention rules measured rather than assumed.**
One hand-built frozen stream of 7 candidates with explicit ids, constructed so every rule
has a hand-computed expected answer: new cell, collision-with-higher-objective, 
collision-with-lower, and an **exact tie** — both within one batch and across sequential
adds. Cell assignment checked against the 4×4 tessellation by hand. Retained ids match the
hand-computed set, and are identical across two fresh archives at both insertion
granularities.

For H3: **exact ties are first-writer-wins.** Insertion requires *strictly* greater than the
cell threshold, and the default threshold is the incumbent's own objective, so an equal
objective does not displace it. A retention-policy comparison that expects last-writer-wins
on ties is not measuring its own rule — it is measuring the archive's default alongside it.
Batch and sequential insertion agree on *this* stream, and the check says so as a statement
about this stream rather than a general equivalence.

One gate I had to fix before it froze: the first version asserted that no
`ribs.emitters` / `ribs.schedulers` module appears in `sys.modules`. `import ribs.archives`
eagerly imports **28** of them, so that gate could not pass on any input. Replaced with an
instance-level gate over `gc.get_objects()` — no emitter object, no scheduler object — which
passes and can fail. Same error class as a threshold outside its attainable range, caught
before it was committed as a control.

**stitch — 4 of 4, plus the reproduction below.**

---

## The stitch reproduction: REPRODUCED, with one provenance caveat

`techne/acquisition/reproduction/stitch_nuts_bolts.manifest.json` was committed in
`95daf6e57` with `observed: null` and `status: DECLARED_NOT_RUN`, **before** the run. The
result went into a separate file; a test asserts the manifest is still in its pre-run state,
so the expected values and tolerances cannot have been edited to match.

All four metrics matched at zero tolerance:

```
M1 n_abstractions     expected 3          observed 3
M2 abstraction bodies expected 3 exact    observed 3 exact, verbatim match
M3 cost before        expected 1919558    observed 1919558
M4 cost after         expected  316890    observed  316890
```

Deterministic across two identical invocations (`compress()` exposes no seed; with
`threads=1` both runs agreed on every metric and on all 250 rewritten programs). 0.076 s and
0.072 s.

The caveat is graded, not hidden. The three abstraction **bodies** come from the upstream
tutorial page this seat retrieved and hashed
(`619b42eadab0679b1f80cbf296e90760f1d63e0b7fa5c95242a43050882561cd`). The two **cost
numbers** appear only in the design packet — searching that page for `1919558`, `1,919,558`,
`316890` and `316,890` found none of them. So M3 and M4 carry
`verdict_grade: SECOND_HAND_EXPECTED_VALUE`. They matched, which is the best outcome
available, but a mismatch would have been evidence about the design's citation rather than
about stitch_core.

### Semantics-preserving expansion, demonstrated before any utility measurement

All **250 of 250** rewritten programs inline back to token-identical originals, using an
s-expression parser and expander written in this check that shares no code with stitch.
Syntactic identity after inlining implies semantic identity under *any* interpretation of
the primitives — which is stronger than agreeing with one evaluator, and needs no evaluator
for a graphics DSL this seat has no semantics for.

Negative control: replacing `fn_0`'s body with `(M 1 0 0 0)` drops recovery to **48 of
250** — exactly the programs that never call `fn_0`. The expander demonstrably reads the
body, so the positive result is not vacuous. `rewrite(originals, abstractions)` also
reproduces `compress()`'s own rewritten programs exactly.

### The export is declarative

`techne/acquisition/exports/stitch_nuts_bolts_library.json` carries each abstraction as
s-expression text **plus** a parsed typed AST of nested lists and strings, with its arity,
holes and any calls to earlier abstractions. No stitch object, no Rust handle, no pickle
crosses that boundary, so nothing in it can execute on import and an admitted interpreter
can validate it independently. A test asserts the absence of pickle markers and that every
AST node is a plain list or string. The file states it is a **proposal**: mechanical
evaluation decided it is expansion-correct; usefulness is decided by a held-out controlled
experiment nobody has run.

---

## DreamCoder: source pinned, smoke run BLOCKED, boundary measured

Source is at `cb0e63f5c33cd2de360b791038b0f5272750270e` with **all three submodules at their
recorded commits** — which took two fixes worth recording:

- `pregex` and `pinn` declare `git@github.com:` URLs in `.gitmodules`, unfetchable without
  an SSH key and a verified host key. Both failed `Host key verification failed` on the
  first attempt. Transport rewritten to HTTPS; same owner/repo path, different transport,
  recorded as a deviation rather than done silently.
- `pyccg` declares `branch = master`, and `submodule update` landed it on the branch head
  instead of the commit the superproject records (`+` / `DIFFERENT_FROM_PIN`). A branch is
  not a pin, so the tool now fetches and checks out the recorded commit explicitly. Both
  receipts are kept — `installation-dreamcoder-20260909T220215Z` shows the failure,
  `...220321Z` shows all three at pin.

Also worth knowing for any licensing question: DreamCoder's only notice file is a `LICENSE`
whose text reads *"The MIT License / Copyright (c) 2010-2020 Google LLC.
http://angularjs.org"* — the AngularJS license, which is plainly a copy-paste artifact
rather than a statement about DreamCoder. The tool hashes the notice and leaves SPDX
`NOT_ATTEMPTED`, because identifying a license from its body is a judgement it should not
make.

### The recipe, stated exactly

The README (line 82) points at `docs/official_experiments`. **That path does not exist** at
the pinned revision. A file named `official_experiments` exists at the repository **root**
(82,632 B, sha256 `acc7b3a64073edf92076e8489a8472fdf92e8bd15c99161e02434820d97f6818`). It is
**not** asserted to be the README's intended recipe and it is not a paper supplement: 199 of
its 331 non-blank lines are `bin/launch.py` cloud-launcher invocations requesting
`n1-megamem-96`, `n1-standard-96`, `x1.32xlarge`, `p3.16xlarge` and similar, with per-run
timeouts up to **57,600 s**. No historical replication is claimed from it, and no benchmark
number was substituted.

### Four independent blockers, each measured

- **BLK-DC-1 python stack.** `requirements.txt` pins 38 exact versions (`torch==1.1.0`,
  `numpy==1.16.4`, `scikit-learn==0.21.2`, `Box2D-kengz==2.3.3`, …). On both interpreters
  this host has — 3.12.10 and 3.11.9 — only **14 of 38** have a wheel compatible with that
  interpreter; 22 are sdist-only; 0 pinned versions are missing from PyPI. So the remainder
  would need source builds of 2019 scientific packages against a 2026 toolchain.
- **BLK-DC-2 OCaml solver.** `opam` absent, `ocaml` absent, `make` absent. The README needs
  `opam switch 4.06.1+flambda` plus ten named OCaml packages. Every domain script invokes
  the solver binaries.
- **BLK-DC-3 Rust compressor.** `cargo` and `rustc` absent. The official commands pass
  `--compressor pypy`, a third backend also absent here.
- **BLK-DC-4 resource envelope.** Every official command is a cloud-launcher invocation for
  machines larger than this host, with timeouts up to 16 h against a 2 h ceiling. None fits
  any declared profile at any tolerance, and no cloud launcher is authorised.

`DEV-T7`: the design asks for "one named bounded domain smoke run". **It is not delivered.**
What is delivered is the measured reason, as four independent boundaries rather than one
estimate.

A note for the consuming seat, not a recommendation: the H0/H2 reference library-learning
arm needs a *library*. stitch_core already produces a verified, expansion-correct library
artifact on this host. Whether DreamCoder specifically is required as the reference arm is a
scientific judgement that belongs to that seat.

**POET was not acquired.** H4's adaptive protocol does not exist yet, so POET has no named
consumer, and `acquire` refuses the entry rather than downloading it — the design's "do not
download every historical framework" rule enforced in code rather than in prose.

---

## Two deviations from the design, and what the budgets actually enforce

The operator's `prometheus-tool-acquisition-plan.json` is not in the repository.

- **DEV-T1** — the manifest is reconstructed from §7's prose and carries **no
  operator-observed SHAs**. Every revision in it was resolved by this seat at a recorded
  timestamp and is an acquisition candidate. If the operator's JSON arrives and disagrees,
  the operator's pins win and both get recorded.
- **DEV-T2** — the proposed light-probe and heavy-build ceilings live in that same absent
  file, so there was nothing to reconcile *against*. The profiles are marked
  `DERIVED_FROM_HOST`, not "reconciled".

Host measured first: 16 logical CPUs, 31.6 GiB total RAM but **13.2 GiB available** — and
availability is what every RAM ceiling is set against, because an SFE service and other
seats share this machine. A test asserts no profile's ceiling exceeds measured available
RAM.

The budget wrapper states separately what it **enforces** and what it only **observes**.
Enforced: wall clock, bytes downloaded (aborting mid-transfer), network policy, concurrent
process count, and termination of the entire process tree on timeout — `taskkill /T /F`,
because pip and git spawn children that outlive a killed parent. Observed only: peak RSS,
which is the OS peak-working-set counter **for the parent process alone** and is not capped.
A hard cap needs a Windows job object or a Linux cgroup; that is recorded as unimplemented
rather than implied. Disk is measured before and after, not limited.

Also recorded, because the distinction is load-bearing: the **live** interpreter already has
z3-solver 5.0.0.0, hypothesis 6.165.10 and ribs 0.12.0, installed at an unrecorded time by
an unrecorded command. pip retains no digest for what it installed, so those are marked
`qualified: false` with `hash_evidence: NONE`. "Present on the host" and "pinned and
verified" are not the same state, and a test enforces that they never merge.

---

## What this enables, and for whom

- **Proteus / H1** — z3 5.0.0.0 as a bounded Boolean oracle, with UNKNOWN proven to be a
  distinct third outcome and resource exhaustion distinguishable from it.
- **Archaeon / H3** — pyribs 0.12.0 with its collision and tie semantics measured, including
  the first-writer-wins tie rule the retention comparison has to declare.
- **Harmonia / C1–C6** — hypothesis 6.165.10 with minimisation verified against known
  minima, replayable fixtures, and the storage side channel contained.
- **H0 / H2 library construction** — a verified, expansion-correct stitch library artifact,
  exported declaratively — held back from any redistribution by the licensing blocker.

## Next unblocked action

Hand the four INSTALLATION receipts and `LICENSE_EVIDENCE.json` to Archaeon for
`H0H5_STATUS.md`, and put the stitch_core licensing blocker in front of the operator, since
it gates export and vendoring rather than internal use and no seat can resolve it alone.

*— Techne, 2026-09-09*
