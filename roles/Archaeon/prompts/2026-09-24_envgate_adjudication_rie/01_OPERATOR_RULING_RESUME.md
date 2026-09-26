# OPERATOR RULING -- resume ENVGATE-02 under the frozen preregistration (verbatim; received 2026-09-25 ~01:09Z)

Resume under the existing frozen preregistration.

Do not amend ENVGATE-02 and do not run a treatment block merely to measure memory.

The memory failure was operational concurrency, not a scientific/design failure, and no treatment result was produced or inspected.

Ruling

Use the unchanged ENVGATE-02 code and preregistration 1475b7995.

Relaunch ENVGATE-02 with a maximum of 6 concurrent block workers.

Concurrency is an execution parameter only. Preserve exactly:

* all 24 preregistered blocks;
* seeds;
* tape streams;
* arm definitions;
* exposure;
* code hashes;
* cache size;
* endpoints;
* analysis;
* stopping rules.

Do not re-freeze or amend the preregistration merely because wall-clock scheduling changed.

Record an operational incident receipt stating:

* first launch was terminated for host memory pressure;
* no complete ENVGATE-02 block result existed;
* no treatment outcome was inspected;
* scientific configuration was unchanged;
* relaunch changed only maximum worker concurrency.

Resource discipline

From here onward, run only one heavy Archaeon job at a time on M2.

Order:

1. ENVGATE-02 — 6 workers.
2. Evaluate its frozen Phase-C gate.
3. If the gate fails, stop the scientific sequence and report.
4. If the gate passes, finish the historical genetic-attribution audit using at most 3 workers.
5. Run RIE-01 preflight.
6. If RIE-01 launches, cap it initially at 6 workers as well unless measured host headroom during the completed ENVGATE-02 run clearly supports more without competing with other seats.

Do not run the historical audit or RIE preflight concurrently with ENVGATE-02.

Wall time is cheaper than contaminating another seat or creating another operational failure.

Memory monitoring

Observation-only host memory monitoring is allowed and should be logged.

Do not inspect scientific outcomes while ENVGATE-02 is running.

If available memory enters a preregistered operational danger zone, reduce scheduling of new block workers or stop cleanly; do not kill completed/running worlds selectively based on their scientific behavior.

Do not modify cache sizes or scientific code mid-run.

If even six workers cannot run safely, stop and report the measured resource envelope before changing anything.

Process ownership

Do not terminate processes belonging to other seats.

Only terminate workers whose parentage and command line establish that they belong to this Archaeon run.

The 20 processes identified as belonging to another seat remain untouched.

Phase A

Treat Phase A as complete:

* attribution implementation built;
* 12/12 required tests pass;
* block-13 replay confirms the genetic lineage belongs to the near-copier while the inert organism acted as executor/host.

Do not redo Phase A unless the resumed assay exposes an attribution invariant failure.

RIE-01

RIE-01 remains staged but unlaunched.

Do not freeze or launch RIE-01 until ENVGATE-02 completes and the already-specified Phase-C gate is evaluated.

If ENVGATE-02 passes, proceed autonomously according to the prior directive. There is no additional HITL checkpoint required.

The governing principle here is:

preserve the experiment; reduce concurrency.

We are willing to spend wall-clock time to keep the scientific contract unchanged.
