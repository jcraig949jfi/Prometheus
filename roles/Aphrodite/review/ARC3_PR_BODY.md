ARC3 close for review (MWO-0001, APHRODITE section). This proposes a merge only, not a new wave.

**Packet:** `roles/Aphrodite/review/ARC3_MERGE_REVIEW_PACKET.md`

**Claims of record** (frozen verdicts; nothing is retroactive):
- **G1 recurrent stepping stone under the constructed test:** E-011 / AMENDMENT 23 returned YES, n = 10, sign p = 0.0078 against each control. This is a mechanism-only claim, and capability is budget-relative.
- **G1 is not established as privileged:** all three shams also pass (GENERIC 3/3), and a matched sham recurs 3x more than G1 under lineage (W8).
- **Lineage (LIN) recurrence** is about 14x i.i.d., but it fails W1's criteria.
- **Recurrence × visibility:** recurring families land where the pristine search cannot reach them, and the 250k window holds about 2% of families.

**Id map:** these are aliases only; nothing is renamed.
- Threads: TH-018..021 (thr-4b608194554f, thr-5fb60bba1e73, thr-71318d165e06, thr-1b0c5ac499ae). `thread_check`: 21 threads, 0 failures.
- Campaign: C-003 = ARC3.
- Experiments: E-008..E-011 = AMENDMENTS 20..23.

**What merges:**
- This branch also carries the unmerged `aphrodite/a16-campaign-2026-09-26`, `frontier-2026-09-27` and `compounding-2026-09-27` work.
- Paths: `roles/Aphrodite/**` plus new `ops/threads/TH-018..021` and `ops/campaigns/C-003`. It merges cleanly with main at 98ed64ca3.
- Size: about 330 files, mostly JSON evidence rows; the largest is 17.9 MB.

**Defects recorded at adoption (packet s5, MWO s12):**
- Historical S4 / A16 / A17 code contains constant-True gate conditions, and the S4 positive control equals the treatment. These were exposed by Artemis #871.
- No labels are changed. Any re-adjudication is operator-level.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01PYAHwpUD1feupctEmaejXc
