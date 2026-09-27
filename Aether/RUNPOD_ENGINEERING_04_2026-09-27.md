# RunPod Engineering Ladder — Iteration 5 and billing reconciliation

Date: 2026-09-27. Directive: `roles/Aether/prompts/2026-09-27_research_block/DIRECTIVE.md`,
BLOCK H (manifest verified). Branch `aether/runpod-iter5-2026-09-27`, base
`ee81c0474`.

This is an infrastructure report. Nothing in it is a scientific result,
for Aether or for any other seat.

---

## 1. VERDICTS

| question | answer |
|:--|:--|
| Can estimated spend be reconciled against actual provider billing? | **Yes, per pod, at $0.** `GET https://rest.runpod.io/v1/billing/pods` returns what was billed per pod and time bucket (`amount`, `timeBilledMs`, `diskSpaceBilledGB`); GraphQL `myself` returns account balance and spend rate. |
| Was the platform's cost accounting adequate? | **No, by +20.5%, and the error was one thing.** 21 receipted pods (Iterations 1-4): receipts estimated **$0.8444**, the provider billed **$1.0171**. Billed *seconds* matched the controller's wall time (0.977-1.001x per card). The *rate* was wrong: the SECURE-cloud launcher priced runs from a table holding COMMUNITY prices. Fixed (§3). |
| Iteration 5 | **PASSED, with another seat's real workload.** Ananke's PTE engine conformance suite, unmodified, pinned and hash-verified: 139 passed, 0 skipped, on an RTX 4000 Ada (Linux). ~$0.008. |
| Is the platform a Prometheus asset yet? | **Partly.** It carried a foreign seat's workload without touching the owner's code, and its accounting can now be reconciled. It is still physically and nominally Aether's: it lives under `Aether/`, imports its provider client from an AETH-01 experiment directory, stores every seat's bundles in Aether's tree, and receipted this flight as seat `Aether` (fixed for future flights with `--seat`). Details in s4. |

---

## 2. BILLING RECONCILIATION (Part 1, $0.00)

### 2.1 Method

`prometheus_gpu/billing.py` (new) reads provider billing, read-only, with
the platform's existing credential resolution (the key is never logged,
printed or written). `python -m prometheus_gpu.cli billing --receipts
receipts` joins every receipt's pod id to the provider's billed rows and
writes a separate file; receipts already written are evidence and are
not edited. Output: `receipts/i5_billing_reconciliation_2026-09-27.json`
(31 billing rows since 2026-09-20; 21 matched to receipts; 9 billed pods
from the pre-platform AETH-01/02 orchestrators have no receipt in this
directory).

For each pod the file records the provider quote used (`hourly_usd`), the
controller's estimate (`cost.usd_estimated`, which the receipt carries
verbatim — the controller and the receipt compute the same number, so
they are one column), the billed amount, billed seconds, billed disk,
the discrepancy, and billed-over-estimate.

### 2.2 Result, aggregated by card

| card | pods | quote $/h | provider securePrice $/h (2026-09-27) | billed $/h | estimated $ | billed $ | billed/est | billed s / elapsed s |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| RTX 4090 | 5 | 0.34 | 0.74 | 0.7419 | 0.0648 | 0.1382 | **2.132** | 0.977 |
| RTX A4000 | 4 | 0.17 | 0.25 | 0.2527 | 0.0871 | 0.1296 | **1.488** | 1.001 |
| L4 | 5 | 0.43 | 0.49 | 0.4926 | 0.2630 | 0.3002 | 1.141 | 0.996 |
| RTX A5000 | 6 | 0.26 | 0.27 | 0.2725 | 0.4088 | 0.4283 | 1.048 | 1.000 |
| RTX 4000 Ada | 1 | 0.28 | 0.28 | 0.2831 | 0.0206 | 0.0208 | 1.010 | 0.999 |
| **all 21** | | | | | **0.8444** | **1.0171** | **1.205** | |

Pre-platform AETH-01/02 pods (A40, quoted from the provider at the time)
reconcile to the reports' own figures: the AETH-02 trajectory pod
`ns96dzh9bq7ynx` reported $2.608, billed $2.6228 (+0.6%); the AETH-02
calibration pod `qtyu4j6p6dgozr` reported $0.177, billed $0.1776
(+0.3%). A40 billed $/h 0.4928 against a quote of 0.49.

### 2.3 Where the discrepancy came from

- **Rate, not time.** Billed seconds equal the controller's wall time to
  within 2.3% on every card, and billing never ran LONGER than the
  controller counted (where it differs, the controller counted create to
  confirmed absence, the provider started slightly later). So there is
  no unaccounted startup billing, no idle-after-exit billing, and no
  per-minute rounding visible at this resolution.
- **The quote table was the wrong cloud.** Every billed $/h equals the
  provider's current **SECURE** price (`gpuTypes.securePrice`) plus a
  residual of ~$0.0025-0.003/h that scales with `diskSpaceBilledGB`
  (container-disk storage). The platform's `cost.HOURLY_USD` held
  COMMUNITY prices for the A4000 (0.17) and 4090 (0.34) and stale values
  for the L4 (0.43) and A5000 (0.26), while `gpu.cloud` defaults to
  SECURE. The 4090 was billed at 2.13x its estimate.
- **Why nothing caught it earlier.** Every receipt said, correctly,
  "measured wall time at a quoted rate, not provider billing". The error
  was declared as unreconciled and so could not be seen until someone
  asked the provider.

### 2.4 What changed

- `cost.refresh_quotes()` reads SECURE prices from the provider at the
  start of every real launch (read-only; failure falls back); receipts
  now carry `cost.quote_source` ("provider securePrice read <utc>", or
  "static SECURE table dated 2026-09-27 (provider not read)").
- The fallback table now holds SECURE prices, dated, with the history of
  why in a comment.
- `cli billing` reconciles any receipt directory against provider
  billing; receipts point at it (`cost.reconcile_with`).
- One Iteration-2 test asserted the literal `0.17` (the A4000's
  community price) as the calibration rate. It now asserts the property
  it was protecting — the calibration is priced at the rate of the card
  that ran — rather than a figure it did not derive.
- Tests: `test_prometheus_gpu_billing.py` (7): the fallback table is
  SECURE, not COMMUNITY, for every observed card; a live quote overrides
  the table and is attributed; a failed read never raises; reconciliation
  joins multi-bucket billing to receipts, reports an unbilled pod as
  NOT_YET_BILLED rather than free, and separates billed pods that have no
  receipt.

### 2.5 Is cost accounting now adequate?

For planning: yes, once quotes come from the provider — the time side
was already accurate. For **truth**: only after reconciliation, which is
now one command. Recommendation for multi-hour campaigns: run `cli
billing` after every campaign and treat a billed/estimated ratio outside
[0.95, 1.10] as a platform defect. Billing rows are bucketed and may lag;
a pod not yet visible is reported as such, never as free.

---

## 3. ITERATION 5 — another seat's workload (Part 2)

### 3.1 Choosing the workload honestly

Searched the repository for GPU-intended code owned by other seats
(torch/CuPy/JAX imports outside `Aether/`, and every seat document
mentioning a GPU or RunPod need):

- **Aphrodite** `roles/Aphrodite/engine/accel/runpod/`: a RunPod kit of
  its own, marked "WRITTEN, NOT EXECUTED", for an exact-equivalence
  canary that runs on **CPU** (its GPU fallback uses only the host's
  CPUs), gated on the operator's explicit spend authorisation. Not
  GPU-suitable and not ours to fly. **Rejected.**
- **Ignis / Apollo**: LLM interpretability and serving; need large model
  downloads and have no pending GPU request. **Rejected** as
  disproportionate.
- **Ergon** `projection_test.py`: needs Harmonia's data loaders and
  domain data; not standalone. **Rejected.**
- **alien_circuitry AC-01D**: a completed experiment (2026-09-13) with no
  pending GPU need. **Rejected.**
- **Ananke** `prometheus/ananke/`: a GPU engine (integer torch) with an
  independent CPU oracle whose DESIGN.md states conformance must hold
  "on RunPod hardware too"; backlog ANANKE-09 names "Linux/RunPod" as the
  throughput path and ANANKE-18 names "Aether's pinned-files pod path".
  Its CUDA-graph and checkpoint/resume conformance tests SKIP without
  CUDA and had only run on Ananke's own Windows host. **Chosen**, and
  scoped to ENGINEERING: Ananke's science RunPod leg (its RESUME Q3)
  awaits the operator's authorisation and was not touched.

### 3.2 What flew

`Aether/runpod/foreign/ananke_conformance/`: a wrapper that imports
nothing from Aether or the platform. On the pod it downloads Ananke's 27
files at commit `ee81c0474` from the public repository and verifies each
against a sha256 manifest built locally with `git show <commit>:<path>`
(`ananke_files.json`), then runs the owner's own
`tests/test_conformance.py`, `test_oracle_selfcheck.py` and
`test_envs_assays.py` with pytest, unchanged. It then times Ananke's own
`random_physics` configurations at larger batch sizes, eager vs CUDA
graph, labelled in the artifact as a WRAPPER-SIDE measurement and not
Ananke's benchmark. Dry run and fake-provider rehearsal passed first;
the module and bundle were committed and pushed (`6c98b4dae`) before
`--go`, as the platform requires.

### 3.3 Result (receipt `receipts/ananke-conformance-20260927T151608Z.json`)

| | |
|:--|:--|
| outcome | **OK**, FLIGHT_PASS, one attempt |
| card | NVIDIA RTX 4000 Ada Generation (stock-ordered; SECURE) |
| stack on pod | Python 3.11.10, torch 2.4.1+cu124, CUDA 12.4, numpy 1.26.3, pytest 8.3.3 |
| pinned files | 27 / 27 sha256-verified before anything ran |
| **owner's tests** | **139 passed, 0 skipped, 34.6 s** |
| lifecycle | provision 5.6 s (synchronised clocks), bootstrap 5.0 s, execution 72.9 s, teardown 8.1 s, total wall 99.9 s |
| artifacts | 4 / 4 retrieved and sha256-verified (25.7 kB) |
| cost | $0.0077 estimated at $0.28/h, `quote_source: provider securePrice read 2026-09-27T15:16:08Z`; provider billing for this pod not yet visible (rows lag; reported NOT_YET_BILLED, never free) |
| cleanup | terminate ACK_204; LIST and GET both confirm absence; independent inventory `active: 0` |

Zero skips means Ananke's CUDA-graph replay and checkpoint/resume
conformance ran on a second GPU and a second OS for the first time and
matched the CPU oracle bit for bit.

Wrapper-side timing (195 ticks, Ananke's own `random_physics` seeds 0-3):

| seed | topology, n | B | eager s | graph s | graph site-updates/s |
|--:|:--|--:|--:|--:|--:|
| 0 | smallworld, 16 | 256 / 2048 | 2.84 / 2.84 | 0.26 / 0.36 | 3.0M / 18.0M |
| 1 | torus, 25 | 256 / 2048 | 2.16 / 2.16 | 0.20 / 0.31 | 6.3M / 32.6M |
| 2 | ring, 5 | 256 / 2048 | 2.83 / 2.87 | 0.26 / 0.30 | 1.0M / 6.6M |
| 3 | torus, 25 | 256 / 2048 | 2.49 / 2.51 | 0.25 / 0.50 | 5.0M / 20.2M |

Eager time is flat in batch size: the engine is launch-bound on Linux as
well as on Windows, and CUDA graphs remove 8-11x of it. Reported to
Ananke (comms #744) as information for ANANKE-09, with no claim.

The receipt's `seat` field says `Aether`: every controller defaulted the
owning seat to Aether. Fixed for future flights (`flight.py --seat`, and
a test that the owning seat reaches the controller); this receipt is left
as written, with the owner recorded in its description and result.

---

## 4. IS THE PLATFORM A PROMETHEUS ASSET?

What Iteration 5 showed works for a foreign seat:
- the module contract needed nothing Aether-specific: a wrapper with a
  pinned, hash-verified file manifest carried another seat's code
  unmodified, on the stock image, with one pinned pip dependency;
- dry run -> rehearsal -> flight -> verified artifacts -> confirmed
  cleanup, first time, one attempt;
- cost is now priced from the provider and reconcilable against billing.

What still makes it Aether's rather than Prometheus's (not fixed here;
each is a move or a rename with test fallout, not a behaviour change):
1. **Location.** The package is `Aether/runpod/prometheus_gpu/`; the
   guide, contract and receipts live under `Aether/runpod/`. A neutral
   home (for example `prometheus/gpu/`) with Aether as one user.
2. **Provider client.** `RunPodProvider` imports the qualified client
   from `Aether/runpod/aeth01_canary/runpod_api.py` via `sys.path`
   (`flight.py`, `cli.py`) -- an AETH-01 experiment directory is a
   runtime dependency of the platform.
3. **Bundle store.** `REPO_DIST = "Aether/runpod/examples/dist"`: every
   seat's bundle is committed into Aether's tree.
4. **Attribution.** `seat="Aether"` defaults in `launch.Controller` and
   `dryrun.prepare`; `flight.py --seat` now overrides it, but the default
   should be "required", not "Aether". The HTTP user agent names Aether
   (cosmetic).
5. **Pinned foreign code is a wrapper pattern, not a platform feature.**
   Ananke's flight needed a hand-built sha256 manifest. A platform helper
   (`module_spec.pinned_files: {commit, paths}`, manifest built and
   verified by the platform) would make "fly another seat's code
   unmodified" the easy path.
6. **One credential host.** The RunPod key lives in BUCKKEEP's host key
   file; any seat can use the platform only through a host that holds it.
   That is a deliberate boundary, not a defect, but it means launches are
   orchestrated from one machine.

Verdict: a working Prometheus capability hosted in Aether's lane. Items
1-5 are a half-day of mechanical work and should precede the first
multi-seat campaign; item 6 is a policy question for the operator.

---

## 5. SPEND AND SAFETY

| item | spend |
|:--|--:|
| Part 1: billing reconciliation (all read-only API calls) | $0.00 |
| Part 2: one real flight (estimate, provider securePrice) | $0.0077 |
| **Block H total** | **~$0.008** (cap $0.35) |
| Ladder to date, receipt estimates | $0.8523 |
| Ladder to date, as BILLED by the provider (Iterations 1-4, 21 pods) | $1.0171, plus this flight when its billing row appears |

Inventory read independently after the flight (`python -m
prometheus_gpu.cli inventory`, its own command): `active: 0, ids: []`.

Gates, each its own command: test_prometheus_gpu_billing 7 passed,
test_prometheus_gpu 60, _launch 40, _examples 24, _scout 19,
_iteration2 29, _iteration3 52; terminology audit 3.
