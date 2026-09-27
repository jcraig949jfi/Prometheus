# C-002 -- Aether research block (2026-09-27)

Thread: TH-007. Owner: Aether (BUCKKEEP, Aether[buckkeep-5c60d0f5]). Opened 2026-09-27 under the operator's research-block
directive (roles/Aether/prompts/2026-09-27_research_block/, verbatim, manifest-verified). Aether is the SECOND test bed of the
ops/ shape after C-001; it is a test bed, not a control plane (directive). Same lightweight shape as C-001: Markdown records,
Task and Attempt rows, no schema engine, no scheduler.

Purpose: sharpen the Aether physics search (TH-007) and, while doing it, test whether Aether work units
(law + seed + origin batch + arm -> result) are genuinely portable, and what a known-answer lane and an open-science lane each
reveal about the Campaign / Experiment / Task / Attempt model.

Constraints: CPU first; no GPU spend on a law until it earns it; RunPod only as a disposable executor or for platform work; no
worker GitHub credentials added; the orchestrating seat commits on behalf of executors.

| Experiment | Question | State |
|---|---|---|
| E-003 | Is the propagation assay's exact causal-generation argument sound? (Block A) | see E-003 |
| E-004 | What did rcv actually teach beyond "received -> fires once"? (Block B) | see E-004 |
| E-005 | Do locality conclusions depend on the observation horizon? (Block C) | see E-005 |
| E-006 | Do combinations of understood mechanisms create new causal behaviour? fwd as content-transport control (Blocks D, E) | see E-006 |
| E-007 | Known-answer lane: does the unit machinery dispatch, duplicate, verify and complete correctly? (Block G) | see E-007 |

Task numbering is campaign-wide (as C-001). Portable-Task record, as C-001: code refs (pinned commit + LF-normalised sha256 of
every imported module), inputs (canonical parameters + sha256; the unit id is derived from them), a host-independent command
(`python Aether/observatory/aeth03_unit.py ...`), resources (wall, peak RSS, CPUs), expected result hash where one exists, where
verification runs, output destination, cleanup rule.

## Pilot findings

Only friction that actually happened is recorded.

### Finding 1 (2026-09-27): Aether units moved off BUCKKEEP, bit-identical

Executors: two RunPod pods used as disposable Linux CPU executors (48 vCPUs, Linux 6.8, Python 3.11.10, NumPy 1.26.3), dispatched
through the existing RunPod platform with the code pinned by commit and fetched by per-file sha256 from GitHub raw. Known-answer
T-001 ran on BUCKKEEP (Windows 11, Python 3.13.5, NumPy 2.4.3) and on both pods: identical result_sha256 on all three. E-007
battery COMPLETE: 6 tasks, 13 attempts, 3 hosts, 0 disagreements.

What moving a unit actually required (observed, not designed):
1. **Code addressable by commit, pushed before dispatch.** The pod fetches files by URL at a commit; the orchestrator must push
   first. The platform checks reachability with a real HTTP request before create.
2. **Line-ending-normalised code identity.** Git on Windows checks out CRLF, on Linux LF: raw sha256 of the SAME commit's files
   differs between hosts. Unit results record LF-normalised hashes; the pod manifest is built with `git show` (LF bytes, what
   GitHub serves).
3. **A result hash that excludes host and time.** result_sha256 is over canonical science JSON only; resources and host facts
   travel beside it. Without that, identical science hashes differently.
4. **Inputs are parameters only.** Aether units need no input files -- the seed and parameters regenerate the world exactly --
   so there was no C-001-style "evidence only on one disk" barrier.
5. **The executor cannot push.** Same as C-001: the orchestrating seat commits Attempts on the executor's behalf. Nothing new was
   built for this.
6. **A reachable executor, not just capacity.** ubu001/ubu002 answer SSH but reject BUCKKEEP (no key); M1 port 22 times out. No
   credential was added. The pods were the reachable executors.
7. **Progress, not liveness.** Two campaigns were ABORTED by the platform's stall detector (TELEMETRY_STALLED at ~305 s) because
   the wrapper wrote telemetry only at unit start/end while units ran 6-10 minutes. Fixed by writing a progress record only when a
   unit's own progress line advanced (a hung unit still trips the detector). Cost of the lesson: $0.097.
8. **Resource figures need a second host.** The Windows peak-memory probe silently returned 0.0 MB; the pod's 39 MB exposed it.

### Finding 2 (2026-09-27): what the platform refused, all correctly
- `--auto` without a pre-built scout bundle: refused before create.
- A module edited between scout and campaign: bundle hash changed, refused before create (my process error).
- A second concurrent flight: "one pod at a time; terminate or adopt before launching" -- concurrency goes through `--fanout`.
- Four declared cards out of stock: NOT_RUN / NO_CAPACITY, $0; widening `gpu.alternatives` to in-stock cards fixed it, which also
  ruled out an invalid request (the all-4xx reading the receipt itself flags as ambiguous).

### Finding 3 (2026-09-27): when the Task structure helped and when it did not
Useful: the known-answer lane (every unit has an expected hash; duplicates, missing units and mismatches are mechanical states);
long independent units that move to another host. Not useful: the assay audit (E-003), whose runs are tied to the instrument
build that launched them and to the laptop that held the evidence; they were recorded as an Experiment without Task rows.

