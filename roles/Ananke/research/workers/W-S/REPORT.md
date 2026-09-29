<!-- DEPOSITED VERBATIM by Ananke for worker W-S; sha256(report)=0cc7513458a990bd; delimited; see REPORT.provenance.json -->
W-S REPORT: E-ANANKE-W-S, thread T-INS-11, work order MWO-0004. M = 256, frozen namespace 0x630, confirmatory namespace 0x632.

WHAT I TESTED
- **Question:** in the sync update_period-2 RELAY cells, what decides per pair-trial whether the mixed swap-tick phase reads S or C?
  - U1: 2dccdaa5 o5 q0
  - U2: c16d5231 o4 q0
  - U3: c16d5231 o5 q0
  - U4: 8c37f32e o5 q0
- **Hypotheses:** H1 delivery timing, H2 route, H3 per-pair state, H4 stale-state fallback.
- **Instrument** (`probe.py`, `analyze.py`; nothing in `prometheus/ananke` edited):
  - A fork runner whose site/chan arms are bit-identical to W-R's `fork_single`.
  - Two targeted arms: site_a swaps the readout site's site arrays only; flight_a swaps only in-flight slots addressed to the readout.
- **Cue-bearing packets:** for trial k, each world runs next to a twin with trial k's cue sign flipped. The twin has the same world seed, so every route, loss and latency draw is shared. A packet copy is cue-bearing if it differs from its twin in any of: delivered or not, recipient, delay, payload. For each copy I logged emit tick, emitter, recipient, delay, jitter draw and arrival tick.
- **Frozen PLAN** (sha 5ef88941…, frozen before any champion predictor run):
  - Primary: P3_cone. It traces the readout backwards through cue-bearing deliveries. Its leaves are either held at the swap tick τ or in flight at τ. All held means S, all in flight means C, both means M, none means U. M and U count as errors in strict accuracy.
  - Secondaries: P1 first arrival, P2 any direct copy in flight, P4 last arrival, P5 direct leaves, P6 in-flight share, P7 stale-state rule (H4), H3 leave-one-trial-out pair majority.
  - Decision rule: H1 SUPPORTED in a unit iff P3 strict lo99 > .80.
- **Development runs (declared):** the plant, and 4781b0a1 (MAJ, not a champion) at M = 64 with ns 0x631. e06701a5 gave 0 eligible pair-trials.

RESULTS (99% pair-bootstrap CIs)
The census replicates W-R:

| Unit | S | C | N |
|---|---|---|---|
| U1 | .46 | .48 | — |
| U2 | .40 | .60 | — |
| U3 | .44 | .56 | — |
| U4 | .34 | .36 | .28 |

Frozen primary, P3:

| Unit | Strict | Decisive (coverage) | Best secondary, strict |
|---|---|---|---|
| U1 | .75 [.71,.80] | 1.00 (.75) | P1 .89 [.85,.92]; P6 .89 [.85,.92]; P2/P4 .87 [.83,.91] |
| U2 | .39 [.33,.45] | .80 [.74,.86] (.48) | P6 .72 |
| U3 | .39 [.34,.44] | .76 [.70,.81] (.51) | P6 .67 |
| U4 | .16 [.11,.21] | 1.00 (.16) | P1 .64 |

**Verdict by the frozen rule: H1 NOT SUPPORTED overall.** U1 is PARTIAL; U2, U3 and U4 are NOT SUPPORTED.

- Clean-phase comparison (H1 predicted P3 ≥ .90 there): it held only in 2dccdaa5 o5 q1 (1.00). It failed in c16d5231 o5 q1 (.22), c16d5231 o4 q1 (.48) and 8c37f32e o5 q1 (.00).
- **Why P3 fails:** the source re-broadcasts the cue on every wake tick, and the readout ignores those later copies. The cone therefore counts irrelevant in-flight copies.
- **H3 (per-pair state):** leave-one-trial-out accuracy U1–U4 is .39 / .36 / .40 / .43. Not supported; the class varies from trial to trial within a pair.
- **H4 (stale state):** P7 is .48 / .53 / .57 / .51. Not supported.
- **Causal certificate:** in every champion block, flight_a reproduced the chan arm (rate 1.00) and site_a reproduced the site arm (1.00). Everything the readout depends on at o4/o5 sits at the readout site. In the plant, where the carrier is upstream, the same check reads 0.00, so the certificate discriminates.

POST HOC, then confirmed (PLAN s7 addendum frozen before the 0x632 run)
- **P8** uses only the copies to the readout from the source's first cue emission. In every decisive case that emission is at τ−4, the source's first wake after the cue; direct delay is 4 plus jitter. Jitter 0 lands the copy at τ (held, S); jitter 1 lands it at τ+1 (in flight, C).
- **P8 decisive accuracy:** 1.00 [1.00,1.00] in all four units at both 0x630 and 0x632. Coverage was .75/.62/.61/.28 at 0x630 and .75/.61/.60/.28 at 0x632.
- **P8any** reads C iff any of those first-emission copies is in flight at τ:

| Unit | 0x630 | 0x632 (confirmatory) | Shuffled at 0x632 |
|---|---|---|---|
| U1 | .87 [.83,.91] | .88 [.84,.91] | .48 |
| U2 | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | .52 |
| U3 | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | .52 |
| U4 | .64 [.59,.70] | .65 [.58,.71] | .50 |

- **Clean phases:** P8any is 1.00 (≥ .997). In the clean phase the source first wakes at t0, so its copies land at τ−1 or τ whatever the jitter; that is the phase mechanism. All confirmatory predictions R1–R4 passed.
- **Split copies** (one copy held, one in flight):
  - c16d5231: always C (0x630: 146/146 and 154/154; 0x632: 141/141 and 165/165).
  - 2dccdaa5: about a coin toss (S share .53 at 0x630, .49 at 0x632). The chimera readouts are small near-cancellation leftovers, for example [-18, 16] against a normal [187, -189].
  - 8c37f32e: S / C / N in near-thirds, and 178 of the cell's 180 N are split cases.
  - Nothing I tried predicts the split outcome: the stale-state rule, the label sign, partner magnitude and held/flight copy counts all read at chance.
- **H2 (route):** in c16d5231, when no source copy reaches the readout directly (about 15% of pair-trials) the result is always S. Routing matters there by deciding whether the source hits the readout at all. The cue also changes the source's routes, because routing is plastic.

KNOWN-ANSWER CHECKS (each with a must-fail input)
- **KA-F:** site/chan arms are bit-identical to W-R `fork_single` (PLANT2J1 11/11, 2dccdaa5 5/5, e06701a5 5/5). Must-fail, forking one tick late: 10/11, 3/5, 3/5, i.e. not identical.
- **KA-L:** every real in-flight mirror difference addressed to the readout is predicted by the packet log, 100% as a subset (plant and all three cells). Must-fail, log shifted by +1 tick: subset holds only 69%, 66%, 28% and 31% of the time.
- **KA-P:** echo_hold under c1b_echo_physics, period 2, HOLD gap 11, M = 256.
  - Jitter on: in the straddle phase q1 at o5, o6, o11 and o12, P3 decisive is 1.00 [1.00,1.00] with coverage .48 to .53, and the stale-state rule is 1.00 on the M cases.
  - Jitter off: every offset-phase is a single class and P3 strict is 1.00.
  - Must-fail, shuffled P3 labels: decisive accuracy falls to .45–.54.
  - Caveat: P8 was not validated in the plant, because the plant's carrier is two hops upstream.
- **KA-B (pytest):** 7 synthetic tests covering cone/leaf cases, M counted as an error, shuffle to chance, and leave-one-out.

DISAGREEMENTS
I read only W-R's RESULTS and DISAGREEMENTS sections. My view of W-M and W-P comes from W-R's summaries of them.
1. **W-R:** the numbers agree. I disagree on the reading. The "~50/50 mixed phase" is not a mixture of carriers or strategies. In non-split cases it is fully determined by one latency-jitter draw on the source's first broadcast; in c16d5231 it is fully determined in every case. W-R's suggested follow-up (arrival jitter relative to the swap/wake tick) is right, but the carrier is only the first broadcast, not later ones.
2. **W-M:** the per-trial S/C "mixture" is physics randomness in delivery latency, not organism state (leave-one-out at chance). The N in 8c37f32e is a split-carrier artifact, not a third carrier.
3. **W-P:** there is no direct test on MAJ. In 4781b0a1 (development run at M = 64) cue-bearing traffic is dense and I saw no timing signal. The RELAY mechanism has not been shown to carry over to MAJ.
4. **My own frozen plan:** the P3 primary failed, and the development cell did not warn me. P8 is post hoc, although its confirmation at 0x632 was pre-registered.

PYTEST
`PYTHONDONTWRITEBYTECODE=1 python -m pytest roles/Ananke/research/workers/W-S/test_ws.py -q -p no:cacheprovider` → 7 passed, RC=0 (`logs/pytest.log`).

LEASE AND COMPUTE
- Lease lse-6d73ca4a7e5b on skullport:cpu8, taken `--as Ananke` at about 13:33Z.
- Released with `--lease --token`, which printed RELEASED. `python -m fabric lease status` then returned [].
- At most 3 processes × 2 threads, no GPU. Win32_Process shows 0 W-S processes left.
- Compute was about 0.45 CPU core-hours, against 16 allowed.
- No git writes, and no stray .pyc files.
- One logged launch bug (A9): a shell variable was unset, so the first champion launch did not start. It was relaunched.
- The clock times in LOG A1–A5 were estimates; A6 corrects them from `date -u`.
- The `dist` log field is wrong for twin-side copies whose route the cue changed. It is not used in any conclusion.

FILES (all under `F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-S/`)
- `PLAN.md` (s1–s6 frozen; s7 addendum), `LOG.md` (A0–A16)
- Code: `probe.py`, `analyze.py`, `run.py`, `ka_fork.py`, `summarize.py`, `posthoc.py`, `posthoc_summary.py`, `quick.py`, `launch_champs.sh`, `test_ws.py`
- Summaries: `out/summary_champions.{txt,json}`, `out/summary_KA_plant.{txt,json}`, `out/posthoc_summary{,_ns632}.{txt,json}`, `out/ka_fork.json`
- Raw data: `out/rows_*.json`, `out/raw_*.npz`, `out/posthoc_*.json`
- `logs/`

PROPOSED FOLLOW-UPS
- Decompile the readout program in 2dccdaa5 and 8c37f32e to explain the split outcomes, and in c16d5231 to explain why the later copy always wins.
- Build a direct-carrier plant with fanout 2 and jitter to validate P8 against a known answer.
- Test whether the first-broadcast rule reaches MAJ or larger delta (78f3b0ec).
