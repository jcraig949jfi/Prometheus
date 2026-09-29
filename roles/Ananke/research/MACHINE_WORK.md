# Research blocks for any idle machine (no oral history needed)

Each block is multi-hour, scientifically consequential and self-contained.
None needs the M1 GPU. PTE runs on CPU. Read this setup once, then open
the block's file.

## Setup (Linux or Windows)
    git clone <prometheus repo>; cd Prometheus
    python3.12 -m venv .venv && . .venv/bin/activate
    pip install numpy==2.2.6 torch  # a CPU wheel is fine; CUDA is optional
    python -m pytest -q prometheus/ananke/tests          # expect all pass on CPU
PTE dependencies: numpy + torch only (plus scipy if a block says so).
Specimens live in git (roles/Ananke/pte/c1_rows/cells.jsonl.gz). Run state
goes outside git. Rules: roles/Ananke/research/handoffs/COMMON_RULES.md +
COMMON_RULES_ARC3.md (plan before running; log every attempt; no
commits; report in the final message or hand the report file to the
seat principal). Leases: Fabric only (MWO-0001; cutover 8370083ae), on any
host: `python -m fabric lease acquire <host>:<res> --as Ananke --purpose ...`
(roles/Ananke/research/lease.py is a thin frontend onto the same row). No
host lease files, no comms lease records. Portable CPU blocks should be
submitted as Fabric Tasks (`python -m fabric submit ... --thread <thr-id>`,
ids in research/THREADS.md).

## Blocks (maturity: research-ready)
B-1 DESIGN, DON'T EVOLVE (T-WA-2). Use the zero-parameter echo model
    (workers/W-A/echo_model.py) to choose physics and pipeline depth that
    cover a TARGET gap set (e.g. {4, 12}, two lags at once through S1/S2),
    then verify in the engine. Question: can the model design what search
    never found? CPU ~2-3 h. Evidence: designed_echoes/ (calibration),
    workers/W-A/.
B-2 SCAR ANATOMY (T-RET-3). Where do the permanent cue-signed traces sit
    (which sites, which stores), and what writes them? Specimens and
    raw data: workers/W-E/out/, and W-G's outputs once deposited. CPU ~3 h.
B-3 MIXTURE vs JOINT (T-CT-3). In "JOINT" cells site_acc + chan_acc ~ 1.
    Does the per-trial split follow latency jitter, duplication or wake
    parity? Raw data: workers/W-F/out/census_table.csv; instrument:
    prometheus/ananke/lens.py carrier_table. CPU ~3 h.
B-4 CA CARRIER MODEL (T-X-5). Herakles EvCA density-classification rules
    (herakles/evca/, on origin/main): run a domain/particle filter
    (Crutchfield-Hanson) and compare "particle carries the bit" with PTE's
    carrier-swap logic. A cross-engine lens, no PTE compute. CPU ~4 h.
B-5 COMPUTATIONAL-MECHANICS READING OF PTE TRACES (T-INS-5 variant).
    Reconstruct causal states (CSSR, or a local-causal-state filter) from
    single-cue-twin difference fields of 3 specimens (echo, latch,
    source-presence) and ask whether causal-state structure separates the
    carrier classes the swap assay finds. CPU ~4 h. Prior art:
    PRIOR_ART_temporal_distributed_computation.md s7-8.
B-6 ROUTING-AWARE ECHO MODEL (T-WA-1). Extend echo_model with the measured
    per-site routing weights of the fresh2/3 champions. Prediction: residual
    MAE < .02. Also tests whether routing carries the cue sign. CPU ~2 h.

## ARC3 additions (2026-09-28; research-ready)
B-7 T-RET-SEL SELECTIVE RETENTION. A preregistered selectivity criterion
    (lag-n agreement minus the maximum at other lags, lo99 > 0) + an
    anti-integrator distractor variant + budget scaling. Evidence:
    workers/W-L (nback.py, plants P1S/P1K/P2S). GPU for searches; the CPU
    parts first.
B-8 T-INS-6 MIXTURE TEST. Replace the sum test with phi; add a single-trial
    swap; promote workers/W-I/traj.py (batched arms + two-axis profile)
    into lens with known-answer tests (designed_echoes/ E2 as a fixture).
    CPU.
B-9 T-CT-3' SLACK -> LATENCY TOLERANCE. A preregistered dose-response
    (+1/+2/+3 latency) on W-I's 20-cell panel; 78f3b0ec is the named
    exception. CPU/GPU.
B-10 T-SWAP-LOWACC. A relative swap verdict for champions below ~.8 normal
    (W-L, W-F ELSEWHERE cells). Validate on the lens test plants. CPU.
B-11 T-WJ-2 4-OPERATOR FINGERPRINT. Evaluate any champion under sum /
    saturate / aloha / arb (workers/W-J/arb.py). A reader-invariance class
    per champion. CPU.
B-12 T-H3 FLATTENING COMPILER. R rule variants -> one select-dispatched
    program; measure the instruction overhead per switching champion
    (workers/W-H). CPU.
