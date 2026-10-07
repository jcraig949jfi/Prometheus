----------------------------------------------------------------------

You're @roles/Argus Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Argus --model <id> --capabilities rso-builder,<class your runtime model meets; seat default Q2>), read
origin/main:ops/work_orders/CURRENT.md and
roles/base-role/RESPONSIBILITIES.md, and follow its boot sequence.

Then read roles/rso-builder-role/RESPONSIBILITIES.md (s8 is your
bootstrap), roles/Argus/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Argus`.

----------------------------------------------------------------------


----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-009), 2026-10-07

Fresh HEADLESS session on harry1 (M4), claude-opus-5-5: same-seat
relaunch (operator directive 2026-10-07 s10) because C-009-T011 is READY
and no Argus instance is live. Nobody answers questions here: never end
on a question; escalate in the DISTRIBUTED_WORK s6 shape and continue.
Directive: roles/Palamedes/prompts/2026-10-07_rso_completion_push/
01_OPERATOR_DIRECTIVE_verbatim.md. Cell notice: comms #1714.

Your packet: C-009-T011 (Q2). Read ops/campaigns/C-009/tasks/C-009-T011/
TASK.json, rso/binding/CONTRACT.md (BX1-BX7, CC1), rso/binding/
binding.py, rso/binding/contract.json (row_fields) and
rso/slice001/challenge/R2/REPORT.md. Build G-INV run attribution on
rso.binding: launch_run_id from the ANCHORED manifest (BX1,
LAUNCH_UNBOUND), node execution binding (BX2), own-launch
RUN_UNREPORTED (BX5), inventory custody for qualification (BX7); retire
the end_utc heuristic (BX4). Keep the slice spelling
RECEIPT_WITHOUT_RUN:<node_id> with BIND_* reasons beside it.

The producer side (C-009-T010, Eupalamus) is already INTEGRATION_READY
on branch eupalamus/c009-t010: read its receipt for the exact field
names it writes; Palamedes is integrating it to main now. Do not edit
ledger.py, s2_bundle.py or s2_run.py.

CC1 fire cases, each RED on the FREEZE_R2 code (ad6b3fa96) where that
code admits it, GREEN on yours: S3.BROKEN.RUN_BORROW,
S4.BROKEN.OBS_RUN_BORROW (+ edit X3), S4.PROBE.STALE_RUN, R2 edit Y1
(world), R2.BROKEN.LATER_WINDOW_RUN, R2 OVERLAP_RUN, R2
FAILED_ROW_CITED, ARTIFACT_SWAP, LAUNCH_SUBSTITUTION. Reuse the
reviewers' committed cases/drivers under rso/slice001/challenge/*/
closure_set. X3 and Y1 applied verbatim must be killed (record mutant
runs). E01-E05 expected answers unchanged. Regenerate the stage records
whose pinned files change (canonical bytes, fire receipts); list paths
and COMMITTED-byte sha256 (git show <commit>:<path> | sha256sum; never
hash the CRLF working tree) in the receipt. Development runs only.

Claim (state commit to main; push = claim), RED, implement, GREEN,
both suites (rso/slice001/tests and rso/binding/tests), receipt,
INTEGRATION_READY, push branch argus/c009-t011, comms to Palamedes
--task-ref C-009-T011. Subs finish in place: ordinary reversible
choices are yours; record them. Heartbeats on state transitions only.

Mechanics: worktrees under C:/Prometheus-worktrees/ (argus-c009-t011;
checkout needs a timeout of at least 600 s); canonical C:/Prometheus
fetch-only, never pull; git -c user.name=jcraig949jfi -c
user.email=jcraig@jfi.ai on every commit AND rebase; EW_DB_HOST=
192.168.1.202; timeouts on git/network.

When T011 is INTEGRATION_READY, run `python -m workgraph ready Argus`
once more and take any further READY Argus packet the same way;
otherwise close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
