# cw01-e01 — ENGINEERING LEDGER (XIII)

Experiment 1 of 10. Disposition **COMPLETE**. Wall: RECONCILE 16:54 → disposition ~17:22, ≈28 min
of a 24 h timebox. Science cost: 7.6 s for the minimal form, 24.5 s for five replicates.

The point of this file is the *factory*, not the science. What did running experiment 1 teach us
about making Nestor instantiable, operable and disposable?

---

## STARTUP

**What had to be created (none of it existed):**
- `MACHINE_PROFILE.json` — the first capability declaration in this ecosystem. Nothing previously
  reported what a host could do; capability was discovered by `try/except ImportError`.
- `CAMPAIGN_STATE.json` — campaign-level recovery (XV). A *round* clock existed; a campaign ledger did not.
- `DEFECTS.jsonl` — one append-only ledger for all ten experiments.
- `lib/seeds.py` — one deterministic seed definition.
- `lib/localrun.py` — **the highest-leverage artifact**: a shipped Redis-free execution contract.
- The experiment itself: `world_e01.py`, `execute_e01.py`, `replicate_e01.py`, `WORLD.json`.

**What unexpectedly already existed:**
- A whole containerized execution path — **8 `prometheus-fossil-*` images** already built in WSL's
  Docker (octave, i386, simh, legacy, hw, lang, goexplore, c). Found only because I listed images to
  avoid a pull. I nearly authored a second, parallel container story (CW01-D008).
- **WSL2 Ubuntu running Docker 29.8.0**, with GPU visibility (RTX 5060 Ti) and host-Redis
  reachability (`PONG`), and the repo bind-mountable at `/mnt/f`. The Windows host has no container
  runtime at all; the Linux one was one probe away.
- `wforge` resolves *inside* the worktree (`soup/b1/common.py:14-20`), so it is not a cross-drive
  dependency — but any sparse checkout must include `SerendipityFoundry/`.

**What had to be configured by hand:** `PM_TAG` (invented: `m1-cw01a001`) and `PM_LANE`. `RowWriter`
refuses without them. Nothing discovers or generates them.

**What failed qualification (and would have corrupted the science):**
| Predicate | Failure |
|---|---|
| Q7 | The spec contradicted itself — declared 0.40 of items exceed one step, distribution implied 0.346 |
| Q8 | Uncheckable (no recurrence *gap* specified), then revealed as a **free lunch** — retention won at every swept price |
| Q3 | The I1 sham charged **+39%** while erase charged **−3%**; the dependence test was measuring my pricing error |
| Q4 | Passed as a **false green** — three empty strings compared equal because a bash path was handed to Windows Python |

**Machine-specific assumptions hit:** Redis hardcoded at `127.0.0.1:6390` with no `PM_*` override
(CW01-D001); `F:` drive paths throughout; `ops/round_clock.py:45-54` bakes one machine's worktree
layout into the frozen round table, and `ops/residue.py` will classify any worker outside it as
`FOREIGN_REPO` and stop it.

---

## EXECUTION

**Components actually used:** `RowWriter` + `commit_path`; `envelope.example/admit/prepare_row`;
`selftest_jobs.emit_n` (as the QUALIFY smoke); numpy. That is all.

**Components that are "how things are done" here and were entirely unnecessary:** the broker, the
worker, consumer groups, `pm:rows:<lane>`, `schtasks`, `launch_lane.ps1`, the epoch controller, the
round clock, and Claude lane sessions. **Zero of them were needed to produce 128 durable,
git-committed rows.** Reusing the fabric would have *imported* the `F:`-path coupling above.

**Bottlenecks:** none. The full pre-registered minimal form runs in 7.6 s. The instrument, not the
compute, was the constraint — six defects had to be fixed before a single number could be trusted.

**Missing telemetry:** per-generation wall time is not recorded (timed externally). Worth adding
before any experiment where compute is actually the constraint.

---

## TEARDOWN

- **Stopped cleanly:** everything. e01 ran in-process and owned **0** runtime resources; there was
  nothing to stop. The Redis namespace `pm:cw01:*` used by the backend counterfactual was deleted
  in-process and verified empty afterwards.
- **Resisted:** nothing.
- **Survived that shouldn't have:** **53 ghost consumers on `pm:swarm`** — not created by this
  campaign, but my RECONCILE scanned only `pm:jobs:*` and then reported the listener check complete
  (CW01-D017). Cleaned where I looked, claimed clean everywhere. Same shape as the process sweep that
  keyed on cwd and missed 38 wrappers.
- **Could not be attributed to an owner:** consumer names identify a *session* (`m1-23be3a04`), not an
  experiment attempt, so ownership is unreadable after the fact (CW01-D002).
- **Preserved manually:** the full r8 Redis residue (51 keys, 1.13 MB) was dumped to disk *before* any
  cleanup, including the unconsumed `w8000036` replication trigger which still carries an open
  operator decision.

---

## PORTABILITY

e01 requires: a git worktree, `PM_TAG`, Python, numpy. **No GPU. No Redis** (only the optional IX
backend check touches it). No container runtime. That is the most portable an experiment in this
ecosystem currently gets, and it happened by *avoiding* the existing fabric rather than by fixing it.

| Target | State | Obstacle |
|---|---|---|
| M1 native | **QUALIFIED** | ran here |
| M2 native | **LIKELY** | nothing in e01's own code is machine-specific; needs repo + venv. Untested — not claimed. |
| Podman | **UNQUALIFIED** | absent on host *and* in WSL |
| Docker (WSL) | **LIKELY** | engine running, repo visible at `/mnt/f`, host Redis reachable. No container executed. |
| Cloud CPU | **LIKELY** | CPU-only, no substrate required |
| Cloud GPU | **N/A** | e01 declares `needs_gpu: false` |

Every obstacle found is **accidental, not fundamental**: a missing `nvidia-container-toolkit`
(CW01-D007), a hardcoded Redis literal (CW01-D001), a hardcoded path table (CW01-D006).

---

## COMPRESSION

**Landed this experiment:**
- `lib/localrun.py` — one Redis-free execution contract replacing a stub ctx re-invented per caller
  (three separate in-tree precedents found).
- `lib/seeds.py` — one seed definition; verified reproducible across processes and hash seeds.
- `MACHINE_PROFILE.json` — one capability report instead of scattered `try/except ImportError`.

**Identified, not yet built:**
1. **One residue scanner** used by *both* RECONCILE and VERIFY ABSENCE, enumerating all streams with a
   type guard — so the two phases cannot disagree (CW01-D017).
2. **A reachability probe as a gate** — hand-build a best-case and worst-case organism and confirm the
   measured effect can go both ways, before spending budget (CW01-D015). This caught a free-lunch
   world that a data-only predicate had passed.
3. **An executable disposition rule** derived from the pre-registration rather than hand-written per
   experiment (CW01-D016). My own driver awarded COMPLETE on one seed while the pre-registration
   demanded replication.
4. **A mechanism-fires + matched-arms gate** (CW01-D013): assert the measured mechanism is non-zero,
   and that disabling it makes arms identical.
5. **An experiment manifest schema** — `WORLD.json` is currently bespoke; it should be a versioned,
   loadable format.

**What can disappear entirely:** for CPU experiments of this shape, the broker/worker/consumer-group
path and the entire `schtasks → powershell → launch_lane.ps1` launcher.

---

## THE HONEST HEADLINE

The science came out clean — +9.70% ancestor-relative, dependence −10.21%, 5/5 replicates, exact
determinism from `attempt_id`. But **six defects had to be found and fixed before any of those
numbers meant anything**, and four of them (D009, D010, D014, D016) would each have produced a
publishable-looking false positive. The instrument, not the compute and not the idea, was the whole
cost of experiment 1.

Experiment 2 should therefore be cheaper in exactly the way the campaign predicts: `seeds.py` and
`localrun.py` are reusable as-is, and the five gates above are the difference between "I checked" and
"the machine checked".
