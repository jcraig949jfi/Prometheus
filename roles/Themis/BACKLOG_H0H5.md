# Themis backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-10-05. Charter adopted (Project Moonshot, prong 3); Epic EP-MOONSHOT registered
and design v0.2 is the design of record. Lanes used: ENGINE, TOOLS, EVIDENCE, LIT. The items
below are now organized under threads TH-MOON-M1..M6 (see ops/epics/EP-MOONSHOT/ and design s12);
a thread-aligned rewrite of this list is itself an early item. UPDATE 2026-10-05: the four
operator decisions formerly blocking THEMIS-02/13/17/18 are RESOLVED (substrate wforge+Proteus;
instrument-first; neural-as-primitive; cloud-scout-mechanism-only) -- see WORK_STATE and design
s0; those rows are unblocked. New v0.2 items (RC0/RC1/RC2 certificates, two-mode causal ablation,
reactive-null family, shard-epoch, anti-degeneracy ecology, operational ruler-blindness, the
CAS-threshold fabric experiment, the planted-bad producer battery for M1) are folded in at the
thread-aligned rewrite.

THEMIS-01 | Write the launchpad preregistration (arms SYM vs HYB, gates, margins, seed counts, kill + reachability criteria) | EVIDENCE | alpha | M | none | roles/Themis/prompts/2026-10-05_prereg_launchpad/ committed with MANIFEST
THEMIS-02 | Decide the substrate (wforge+Proteus vs BEE) with a written comparison on ruler/substrate/diversity/cluster-fit | ENGINE | alpha | S | operator decision (NEW: substrate = wforge+Proteus purpose-built-dormant OR BEE demonstrated-not-purpose-built) | decision note in RESPONSIBILITIES.md + memory
THEMIS-03 | Draft the coordination message to Palamedes (RSO cell): offer launchpad as first retention candidate, ask if R1 WORLD FORGE is assigned, flag determinism-vs-GPU amendment | TOOLS | alpha | S | operator approval to send (outward-facing comms) | drafted message, operator-approved before any send
THEMIS-04 | Specify the delayed-cue micro-world deterministically (observability, payoff, irreversibility, log schema) | ENGINE | alpha | M | THEMIS-02 | world spec + a deterministic reference run with a stable replay hash
THEMIS-05 | Implement the offline floor-S detector (reactive null + ablation twin) as a versioned log-reader | TOOLS | alpha | M | THEMIS-04 | code + a receipt on a sample log; re-score of the same log is byte-identical
THEMIS-06 | Write the two planted organisms (memory-user, reflex-only) in the chosen palette | EVIDENCE | alpha | S | THEMIS-04 | committed organisms + G0: detector fires on the memory-user, not the reflex
THEMIS-07 | Build the reachability-certificate suite (representability, reachability-curve vs k, needle-vs-slope) | TOOLS | alpha | M | THEMIS-04 | code + a certificate computed on the launchpad world
THEMIS-08 | Build the dead-world control (cue uninformative) as a standing calibration fixture | EVIDENCE | alpha | S | THEMIS-04 | the fixture + evidence the detector stays silent on it
THEMIS-09 | Lift SFE executor contract + wforge into a local, server-free deterministic runner | ENGINE | alpha | L | THEMIS-02; coordinate Daedalus | headless run on a worker node with a byte-identical twin verified
THEMIS-10 | Wire the launchpad as a workgraph GENERIC_WORKER packet (one shard = one bag-of-tasks unit) | TOOLS | alpha | M | THEMIS-05, THEMIS-09 | a packet claimed and run on an ubu node, receipt returned
THEMIS-11 | Design the integer-neural primitive (int8, evolvable weights no backprop, LUT nonlinearity, bit-exact) | ENGINE | alpha | M | THEMIS-02 | spec + a CPU/GPU bit-exact parity test
THEMIS-12 | Literature check: evolved integer/quantized nets as organism primitives (Polyworld-style prior art) | LIT | alpha | S | none | committed survey note; novelty claimed or disclaimed with citations
THEMIS-13 | Resolve the strategic fork (instrument-first vs re-premise-to-assay) | EVIDENCE | alpha | XL | operator decision (NEW: strategic fork) | a recorded operator ruling in prompts/ + memory
THEMIS-14 | Run the launchpad many-seeds SYM vs HYB on the CPU cluster; emit logs | EVIDENCE | beta | L | THEMIS-01, 05, 06, 10 | logged corpus + an offline S verdict PASS/KILL/UNDERPOWERED per the prereg
THEMIS-15 | Multi-scale reachability curves (3-4 points of pop/gens/net size); classify flat vs rising | EVIDENCE | beta | M | THEMIS-07, 14 | the curve + a classification, with a written extrapolation if rising
THEMIS-16 | Port matched-null + falsification-battery reuse behind one calibrated-ruler interface | TOOLS | beta | M | THEMIS-05 | the unified ruler module + a calibration receipt vs disguised-known controls
THEMIS-17 | Decide the fusion-mode branch (neural-as-primitive vs -substrate vs -mutator) with rationale | ENGINE | beta | XL | operator decision (NEW: fusion mode) | a decision note naming the branch and why
THEMIS-18 | Raise the RunPod budget cap (currently $19.93) before any burst | TOOLS | beta | S | operator decision (NEW: RunPod budget for Moonshot) | updated cap record + a small-spend scout receipt
THEMIS-19 | RunPod scout: test the preregistered scaling prediction, not only confirm | EVIDENCE | beta | M | THEMIS-15, 18 | a scout receipt compared against the written prediction
THEMIS-20 | Propose the RSO contract amendment for SEMANTIC/PARTIAL reproducibility (GPU neural) | EVIDENCE | beta | M | THEMIS-03; coordinate RSO cell | a drafted amendment following the cell's versioned process
THEMIS-21 | Sharded island-model migration (survivors hop shards between generations), deterministic | ENGINE | beta | L | THEMIS-09 | a migration run with a stable replay hash across hosts
THEMIS-22 | Stand up the logged-corpus store so a better S-meter re-scores history for free | TOOLS | beta | M | THEMIS-05 | append-only corpus + a re-score run over old logs with a new meter version
THEMIS-23 | Node auto-join for the e-waste cluster (plug-in box drains work unattended) | TOOLS | 1.0 | L | none | a fresh node joining and draining a packet without hand-provisioning
THEMIS-24 | Shard the workgraph claim namespace to relieve single-branch contention as N grows | TOOLS | 1.0 | M | THEMIS-10 | a contention measurement before and after
