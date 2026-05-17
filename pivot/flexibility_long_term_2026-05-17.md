# Long-term flexibility goals — multi-machine, hybrid, cloud, GitHub

**Date:** 2026-05-17
**Author:** Aletheia, after James's 2026-05-17 conversation on orchestration flexibility.
**Status:** v0 reference doc. Not blocking current work. Captures the direction without committing to a timeline.

---

## The principle

The Prometheus codebase should run identically wherever there's Python + network + (when needed) GPUs. No machine should be load-bearing because it's a particular machine; it should only be load-bearing because it's *currently running the work*. When a new rig joins the fleet or an old one drops out, the workload should be reroutable without code changes.

James's stated framing: "flexibility seems to be a priority." That doesn't mean abandoning current Windows-on-M1-M4 reality; it means *making sure today's choices don't lock in tomorrow's constraints*.

## What's already portable (good news)

- All Python scripts use `pathlib`, `subprocess`, `datetime`, `os.environ` — no Windows-specific APIs.
- `scripts/portfolio_monitor.py`, `metis_portfolio.py`, `send_brief_email.py`, `intelligence_loop.py`, `weekly_recap.py`, `agora_persist.py` all run identically on Linux/macOS/Windows.
- The agora client (Redis-py + psycopg2-binary) is cross-OS.
- The Postgres + Redis services on M1 are cross-OS-accessible (LAN-reachable, standard protocols).
- Dashboard (`docs/index.html` + state.json) is static; serves from any HTTP server.

## What's NOT portable today (technical debt)

- `apollo/launch.bat` and `scripts/start_intelligence_loop.bat` are Windows-specific. Each needs a `.sh` companion for Linux/macOS.
- `pythonw.exe` references in the .bat files. Linux equivalent is `nohup python ... &` or `systemd-run --user`.
- Apollo's GPU affinity is hardcoded for an NVIDIA setup with specific VRAM ceiling — works on M2 (SpectreX5) today, would need adjustment for cloud GPU rentals (AWS A100s, vast.ai instances, etc.).
- `agents/metis/src/metis.py` is gitignored at the `agents/` level — code propagation across machines requires manual sync, not git pull. The `call_llm` cascade in particular should be extracted to a tracked location so any machine can use it.

## Stages of flexibility

### Stage 1 — Now (do this, no big commitments)

- Keep `intelligence_loop.py` as the universal daemon. It's already cross-OS in code; just needs supervisor wrappers per OS.
- Add `scripts/start_intelligence_loop.sh` next to `.bat`. Same logic, OS-appropriate.
- Extract `call_llm` from `agents/metis/src/metis.py` into `scripts/llm_cascade.py`. Tracked location; propagates via `git pull` to any machine. Imports stay the same shape; just changes the source-of-truth.
- Pipeline manifests at `pipelines/*.yaml` stay descriptive (current state).

**Outcome:** Code runs identically on Linux/macOS/Windows. Adding a Linux rig to the fleet means `git clone + pip install + run`. No additional architecture.

### Stage 2 — Soon (when a second rig in a different OS actually joins)

- Promote pipeline manifests to load-bearing. A thin `scripts/run_from_manifest.py` reads `pipelines/<name>.yaml` + a new `machines/<hostname>.yaml` (defines which pipelines this machine should run) and dispatches the work.
- Each machine has its own `machines/<hostname>.yaml`. Easy to add when a new rig joins; easy to retire when a rig drops.
- Daemons report which pipelines they're running to Agora (heartbeat already does this; just need to include "active_pipelines" in the status_json).
- Cross-machine handoff: pipelines that depend on each other's output (Nous → Hephaestus today) use Agora streams as the bus, not filesystem polls. This is the unimplemented Path C from the Nous RESUME.

**Outcome:** New rigs declare their capabilities; orchestration routes accordingly. Moving a pipeline from M3 to M2 (or to a cloud rental) means editing one YAML, not rewriting code.

### Stage 3 — When cloud GPU actually gets rented

- Containerize the load-bearing components. Apollo, Hephaestus, Nous each get a Dockerfile that bundles its dependencies. Image build is part of the repo's CI.
- Container can run on cloud GPU instances (vast.ai, AWS, GCP) the same way it runs on M2.
- Agora Redis + Postgres remain on a home machine OR move to a managed cloud DB. The pipelines don't care which.
- Cloud-rental decision becomes purely an economic + workload-fit question. The orchestration absorbs it without code changes.

**Outcome:** Renting an A100 for Apollo for a week is `docker run` + `machines/cloud-a100.yaml`. No architectural change.

### Stage 4 — GitHub Actions as the always-available backbone

- After `call_llm` is tracked (Stage 1), the reporting pipeline (`portfolio_monitor` + `metis_portfolio` + `send_brief_email` + `weekly_recap`) can run on GitHub Actions runners with API keys as repo secrets.
- Cron triggers replace the local daemon for *reporting* — operational and reflective artifacts always get generated, even if all home rigs are off.
- Forge / Apollo work stays on home or cloud GPU rigs (Actions runners aren't suited for hours-long compute).
- M1 Postgres/Redis needs to allow external access from GitHub's IP ranges, OR a tailscale tunnel, OR migrate to a managed DB.

**Outcome:** Reporting layer is independent of home-rig availability. Computer hardware churn doesn't affect James's daily/weekly feedback loop.

### Stage 5 — Optional, far future

- Kubernetes / cloud-native orchestration if scale demands it.
- Multi-region resilience if Prometheus ever serves anything time-critical (currently doesn't).
- Federated workers if other researchers want to contribute compute.

These aren't current concerns. They're listed only so the architecture decisions made today don't preclude them.

## What this means for current work

**Nothing critical to act on right now.** The architecture is already at Stage 1 + most of Stage 1's prereqs. The cleanup work (extract `call_llm`, add `.sh` companions) is opportunistic — do it when convenient, don't rush it.

**Most important rule going forward:** Don't add Windows-specific or M-specific dependencies in new code. Every new script gets written cross-OS from the start. Every new launcher gets a `.bat` AND a `.sh` companion at the same time, even if only one is used initially.

**Second most important rule:** Code that needs to propagate to multiple machines lives in tracked locations (`scripts/`, `pipelines/`, top-level Python files), not in gitignored directories (`agents/`, `roles/`).

## On GitHub Codespaces, Actions, and similar

| Mechanism | Good for | Not good for |
|---|---|---|
| **Actions cron** | Scheduled reporting, daily/weekly artifacts, small periodic tasks | Long-running compute (Apollo evolution, Hephaestus continuous forge) |
| **Actions on push** | CI, linting, manifest validation, auto-publish dashboard | Anything that needs persistent state across runs |
| **Self-hosted runners** | Same scheduling as Actions but on your hardware | Adds complexity; only worth it if you want GH's scheduling abstraction without GH's compute |
| **Codespaces** | Interactive dev environment, demos, exploring the repo from any device | Background jobs, scheduled work, anything that should run unattended |
| **Pages** | Hosting the static React dashboard | Anything dynamic |

Pragmatic order of adoption: Pages (already enabled or close to it) → Actions for reporting → Actions for CI → self-hosted runners if needed → Codespaces for ad-hoc dev access.

## Apollo specifically — when cloud GPU matters

Apollo's per-generation cost is the relevant metric for "should this run on rented compute." Today: ~hours per generation on M2's local GPUs, $9 DeepSeek balance at last run (April 9), generation rate ~15-20K/day target.

If Apollo demonstrates measurable coalition-value lift (per the ChatGPT-grounded "does Apollo find organisms whose marginal behavior > sum of parts" test from yesterday's conversation), the next question is: does *faster Apollo* (rented A100, 5x generations/day) prove the premise faster, or just burn money?

That's a value-prop-vs-rate question that gets settled by Apollo's first 5K generations on M2 producing coalition-value evidence. Apollo's value prop doc (`pivot/apollo_value_proposition_2026-05-17.md`) names the falsification conditions for the premise itself.

## Summary

Today's choices don't preclude tomorrow's architecture. Stages 2+ are all reachable from where we are with minor refactoring (extract `call_llm`, add `.sh` wrappers, promote manifests to load-bearing). The orchestration layer doesn't need to be sophisticated for the current scale — `intelligence_loop.py` is sufficient. The discipline is "don't write yourself into a corner" rather than "build the eventual architecture today."
