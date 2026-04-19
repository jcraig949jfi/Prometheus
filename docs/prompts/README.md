# Worker Prompts

Persistent record of task prompts delegated to worker sessions. Each
file is a self-contained role specification that can be pasted into
a fresh Claude Code session on any machine.

Committed so that:
1. The delegation record is auditable (who was asked to do what, when)
2. Prompts become re-runnable if a worker instance is lost
3. External reviewers can see the full task spec, not just the resulting commit
4. The prompt itself is a versioned artifact; edits create a new file

Naming convention: `track_<letter>_<short_role_name>.md`

Active tracks:
- `track_A_methodology_tightener.md` — null-protocol + algebraic-identity audit
- `track_B_F011_unfolding.md` — F011 rank-0 residual independent-unfolding check

Retired / completed tracks are moved to `archive/` subdirectory.

Deprecation policy: if a track is reassigned with a new prompt, keep the
old file, add `SUPERSEDED_BY: track_X_...md` at the top, and move to
`archive/` once the work completes.
