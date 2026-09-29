# E-002 relay note (Archaeon, transport only, 2026-09-27)

The worker's files are unedited. This note records only how the result travelled, plus what the relay observed about the handoff itself.
Archaeon has NOT reviewed the science; that review is pending, as the originating scientist, when the operator asks.

## Transport
- Worker: Claude Code 2.1.283 (claude-opus-5-5) on ubu002, started 2026-09-27T14:16:58Z in tmux session `e002`, in the node's own
  clone. Prompt = HANDOFF_INSTRUCTION_verbatim.md body only (2,800 chars); no other input from Archaeon. It ran with permission
  prompts bypassed (unattended).
- Finished 14:30:33Z, exit 0: 58 turns, 814 s, reported cost $3.46.
- Output: commit 0a5c0895d on local branch artemis/e002-2026-09-27. The node did not push.
- Relayed by git bundle (sha256 d7c5d63e270d12e3), fetched on M2 and pushed unchanged. The branch is on origin, and main was
  fast-forwarded to the same commit (no merge commit, no edits).
- Transcript, prompt and bundle: C:/Prometheus-data/evidence/ops_pilot_2026-09-27/E-002_worker/.

## Observations the worker's own HANDOFF_FINDINGS.md does not contain
1. **The worker was not a blank slate.** ubu002's persistent Claude auto-memory
   (~/.claude/projects/-home-jcraig-Prometheus/memory/) says "I am Prometheus seat Artemis on this bare Linux host". The session loaded
   it and signed its work as Artemis[ubu002]. It was fresh with respect to Archaeon, but it carried the node's standing seat identity.
   For a truly fresh or temporary researcher, the node's per-user memory is a context channel that Git does not control.
2. **The node's environment was changed by the worker.** apt installed python3-numpy and python3-torch at 14:20Z. The node is no
   longer stdlib-only. The worker recorded the need; the persistent change to a shared node is noted here.
3. **The worker also pulled main into the node's main checkout** (as instructed) and did its work in a new worktree
   (~/Prometheus-worktrees/artemis-e002). Both remain on ubu002. The E-002 worktree is left in place for the originating scientist's
   review.
