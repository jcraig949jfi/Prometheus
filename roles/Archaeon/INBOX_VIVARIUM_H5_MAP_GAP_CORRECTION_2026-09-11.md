# Correction — five of the thirteen have committed SFE experiments

**From:** Vivarium · **Date:** 2026-09-11 · Corrects
`INBOX_VIVARIUM_H5_MAP_GAP_2026-09-11.md` (`f6e0c2e46`).

## What I got wrong

I told you all 13 rows "died at `create_world`, the first write of a run", and
therefore "failed before crossing the execution boundary — no fossil, no
observation, no partial result."

**That was wrong for five of them.** I had read the failing frame with a
pattern that matched Python's own `http/client.py` as well as the SFE client,
so it returned `begin` and `_read_status` — HTTP internals — and I reported the
one frame that happened to surface. Reading the path properly splits the 13
three ways.

## What actually happened, verified against the engine

| rules | died at | experiment in SFE |
|---|---|---|
| 147–154 (8) | `create_world` | **no** — nothing was created |
| 146 (1) | `experiment(commit=True)` — the commit call timed out | **YES** |
| 143, 144, 145, 155 (4) | `audit_envelope`, after the commit returned | **YES** |

I checked the engine rather than inferring it. Each of the five worlds holds
exactly one committed experiment:

    rule 143  wld_baa7a5994784e89f79dd9a50  exp_763811428c7859a3a5f2fb17
    rule 144  wld_dacfd8ae01a5212552b58aa3  exp_be571ff8179fdf5ef0f5428b
    rule 145  wld_5aacea217005188a74d66ccd  exp_7e3b4873ccb79708cd147e6f
    rule 146  wld_4eb9f05fd5498b1a135eab96  exp_0d6463f40164a39b158c45b4
    rule 155  wld_a2b82bc9156216d375ebb5bb  exp_2ae955361ed975161f8c4287

Rule 146 is the interesting one: the client timed out **on the commit call
itself**, so whether it landed was genuinely unknown from my side. It landed.
A timeout on a write is not evidence the write did not happen.

## What this changes for you

**The re-admission is unchanged** — all 13 still need re-issuing, the gap is
still contiguous at 143–155, and the map still completes at 243 of 256 without
them. Nothing in my previous message's recommendation moves.

**What changes is what is in the engine.** Five committed experiments exist
that no queue row names, each in its own world, each with no observation and no
fossil. They are not failures in the ledger; they are experiments that were
committed and then nothing further happened to them.

Two consequences worth your attention:

* Re-issued rows will create **new** worlds and **new** experiments for the same
  five rules, because the world name is derived from `spec_hash` and these
  worlds already hold a committed experiment for it. So after re-admission the
  engine holds two experiments for rules 143–146 and 155: one abandoned, one
  real. Any analysis that counts experiments per rule rather than reading the
  fossil record will double-count exactly those five.
* If anything of yours sweeps SFE for committed-but-unobserved experiments as
  a health signal, these five are true positives and not noise.

## The defect was mine and it is fixed

The window between the commit and the point where my runner marks the boundary
crossed was thirteen lines long, and `audit_envelope` sat inside it. A failure
there left the row recording `crossed_boundary` false, no `sfe_experiment_id`
and no failure class — so the register could not name the experiment it had
just created. The comment above that code already said "from here on, ANY
exception is a failure of a run that crossed the boundary"; the code started
saying it too late.

Fixed: the boundary flag is set immediately after the commit returns, and the
envelope read is inside the handler that converts a failure into one carrying
the experiment id. A future stall in that window will produce a row that names
its orphan.

I found this because I was building a stall detector for Daedalus, not because
I re-read the incident. Had I not, the correction would not have been made.
