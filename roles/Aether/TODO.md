# Aether TODO

Currency: **2026-09-25.** Written for the instance that boots after a
context reset, a reboot, or a Claude Code upgrade. Read this AFTER the
base-role chain and BEFORE starting anything.

Branch: `aether/aeth02-native-circuitry-2026-09-23`. Check
`git log --oneline origin/main -1` before assuming where main is.

---

## THE ONE OPEN MISSION

**THE RUNPOD ENGINEERING LADDER IS THE PRIMARY MISSION.** The operator
said so on 2026-09-24: *"The reusable GPU platform is now the primary
mission."* AETH-02 science is **closed**; do not reopen it.

    roles/Aether/prompts/2026-09-24_runpod_engineering_ladder/DIRECTIVE.md
    (verbatim, with a manifest -- verify it before acting on it)

    python -m comms.manifest verify \
        roles/Aether/prompts/2026-09-24_runpod_engineering_ladder

**Budget: $5.00 total campaign. SPENT: $0.124. Remaining: $4.876.**

### Where the ladder stands

| iteration | state |
|:--|:--|
| 0 — zero-dollar dry run | **DONE**, $0.00 |
| 1 — one tiny pod end to end | **DONE and PASSED**, $0.124, 6 attempts |
| 2 — scale up | **NEXT** |
| 3 — long run + failure injection | not started |
| 4 — 2–3 pod fan-out | not started |
| 5 — a foreign seat's module | not started |

Read first: `Aether/RUNPOD_ENGINEERING_01_2026-09-24.md` — Iterations 0
and 1, with predicted-versus-observed for every lifecycle interval and an
account of what each of the five failed flights bought.

Entry point for any seat: `Aether/runpod/README.md`. Do not start by
reading the platform source; the guide is meant to be sufficient, and if
it is not, that is the defect to fix.

### Iteration 2: what to do, and why these axes

The directive requires each rung to increase at least one axis and leave
reusable machinery behind. Iteration 1's own measurements point at three:

1. **Shorten the poll interval to isolate provisioning.** `provision` sits
   in `cost.OVERHEAD_S` as 24 s but it is a BOUND, not a measurement: up to
   15 s of that 31.4 s interval was the controller's own poll granularity. A
   3–5 s poll during the ready wait would turn it into a real number and
   remove the last inferred term from the cost model.
2. **A longer workload**, so the overhead fraction is not 97%. Iteration 1
   ran 0.67 s of compute inside 35 s of wall time. Raise `HELLO_STEPS`, or
   better, fly `examples/param_sweep` with more candidates.
3. **A heavier artifact.** Transfer was measured against 1,164 bytes, which
   measures nothing. A few MB would.

**Also fly the scout path**, which is built and tested but has never touched
hardware: `prometheus_gpu/scout.py`, plus `cli scout` and `cli campaign`.
The sequence the operator asked for is scout → measure → estimate →
refuse-or-proceed, with `preregistered_estimate` and `calibrated_estimate`
both in the receipt. Its regression test is AETH-02's own 7.2% miss.

Launch commands that work today:

    cd Aether/runpod
    python iteration1_flight.py --dry        # plan only, no pod
    python iteration1_flight.py --rehearse   # fake provider, whole path
    python iteration1_flight.py --go         # REAL, ~$0.003, ceiling $0.30

Use `python -u` and redirect to a file. Piping to `tail` buffers the entire
run and you will fly blind — that cost a flight's worth of visibility.

### Hard-won rules the next instance must not rediscover

- **The bundle must be committed AND PUSHED before `--go`.** The pod fetches
  it from a pinned commit via GitHub raw; `ensure_bundle_committed` verifies
  with a real HTTP request and refuses if the pod could not fetch it.
  Editing `module_spec.json` changes the bundle hash, so rebuild and
  re-push.
- **Build products go OUTSIDE the module directory** (`examples/dist/`). A
  bundle left inside gets swept into the next bundle and the hash moves
  every rebuild.
- **Artifact paths carry NO directory prefix.** `result.json`, never
  `out/result.json`. The artifact server's document root IS the artifact
  directory.
- **Declare `gpu.alternatives`.** RTX A4000 and A5000 were both out of
  capacity on 2026-09-24; the 4090 was available. A projection for a GPU you
  cannot obtain is not a projection.
- **A 400 on create creates nothing**, so reading the response body is free
  and is usually the fastest route to the cause. The qualified client hides
  it; a one-off direct probe does not.
- **Dependency install time is not a property of the workload.** The same
  `cupy-cuda12x` install measured 6 s and 305 s on consecutive flights. The
  controller waits on stage PROGRESS, not on a deadline. Do not put a fixed
  deadline back.
- `Aether/runpod/FAILURE_PLAYBOOK.md` has 18 entries. All of them happened.

---

## AETH-02: CLOSED

Do not reopen. Closed 2026-09-24 with the four zero-dollar falsifiers.

- `Aether/AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md` — the trajectory
  round. **Carries four amendments**; read the banner at the top first.
- `Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md` — **the closing report.**
  Supersedes the above at §4 and §7. H1 and H4 stand, H2 partly falsified,
  **H3 unresolved**, plus an instrument correction to the trajectory round.
- `Aether/observatory/aeth02_falsifiers.py` — reruns all of it for $0.00.
- `Aether/observatory/aeth02_reduce.py` — regenerates every trajectory
  figure from the committed 3.1 MB log.

Spend: $2.83 of the authorised $3.00.

**The conclusion, at the width the operator set:** no evidence was found
that the measured persistent-edge and cycle structures perform a
demonstrated nontrivial function *under the assays run*. This is NOT
"Aether contains no possible circuitry" and must never be quoted as such.
The four evidentiary dimensions in the trajectory report's §7 are **not
jointly necessary** and are not a definition of circuitry.

### The two loose ends, if science is ever resumed

Both cost $0.00. Neither is authorised work right now.

1. **H3 is unresolved.** 205 on-cycle edges at 256² is too few to rest a
   conclusion on. A 512² pass with a per-field decomposition was launched on
   2026-09-24 and was lost to the reboot. Rerun:

       python Aether/observatory/aeth02_falsifiers.py all --n 512 \
           --warmup 2500 --follow 300 --out falsifiers_512.json

   The hypothesis to test is in the closing report §3: a write copies the
   source's PAYLOAD, so an opcode-field edge into a cycle member is
   same-value only if the source's payload equals `WRITE` — 1 value in 256.
   If the enrichment is concentrated in the opcode field, it is a structural
   constraint and H3 is supported.
2. **H2's persistence gap is genuinely open.** Independence predicts the
   instantaneous edge structure to 0.2% but over-predicts the ≥64-tick
   cohort by 3.1×. Real edges are *shorter*-lived than independence says.
   Nothing measured explains that.

---

## SEAT PRACTICE — four ledger rows, all earned

`roles/Aether/calibration/LEDGER.md` has the full text. The four:

1. **Do not attribute an artifact to your own most recent change** because
   it appeared in the first log you could read. Run the pre-change code.
2. **Run the gate as its OWN command and read its summary line.**
   `pytest ... | tail` inside `&&` takes the exit status from `tail`. This
   pushed two red suites. Twice.
3. **A cost projection is a throughput claim wearing a dollar sign.**
   Measure the configuration that will actually run. Carrying a figure
   across workloads cost AETH-02 its third trajectory.
4. **Marking a number INFERRED is not enough** — nothing forces it to be
   measured, and it propagates into documents, estimates and test
   thresholds. A test must assert the property it cares about, not a figure
   it did not derive. Also: when two quantities agree EXACTLY, suspect an
   identity before claiming a validation.

---

## STANDING SEAT DEFECTS — unchanged, not blocking

- `roles/Aether/RESPONSIBILITIES.md` still has a stale body describing a
  pre-charter seat. Annotated at the top rather than rewritten. Needs a
  rewrite around `Aether/AETHER_DOCTRINE.md`, old body to
  `roles/Aether/superseded/`.
- `BACKLOG_H0H5.md` is still the 3-item provisional file, below the
  schema's 20-item floor.
- `roles/base-role/INHERITANCE.md` rows 11 and 77 still say the charter is
  pending.
- The fleet-wide base-role self-test is red on a Nyx prompt manifest
  (`dc41abff1393 != dbd639ef6ee7`), reported 2026-09-19, unfixed. Not
  caused here; do not chase it.

---

## STATE AT THE 2026-09-25 REBOOT

- **No pods running.** Inventory independently verified `active: 0`.
- **Nothing billing.** Nothing was left mid-flight on any provider.
- Working tree clean; everything is pushed.
- The only work lost to the reboot was the 512² falsifier run, which is
  free to redo.

Gates as of the last commit:

    python -m pytest Aether/test/test_prometheus_gpu.py -q
    python -m pytest Aether/test/test_prometheus_gpu_launch.py -q
    python -m pytest Aether/test/test_prometheus_gpu_examples.py -q
    python -m pytest Aether/test/test_prometheus_gpu_scout.py -q
    python -m pytest Aether/test/test_aeth02_reduce.py -q
    python -m pytest Aether/test/test_aeth01_terminology_audit.py -q

148 passing across those six. The whole `Aether/test` suite was green at
exit 0 under `-x`; it takes about 10 minutes, so run the six above for
ordinary work and the full suite before integrating.
