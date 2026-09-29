# Ensorain defect register (MWO-0001 s12). Append-only.

## DEF-ENS-001: the LM01 frozen launch gate cannot accept an MWO archive file as the recorded launch directive

- Recorded: 2026-09-29T02:50Z by Ensorain[m2-32b65655], during MWO-0001 adoption (operator boot instruction, check 2).
- Identifiers:
  - MWO-0001 (archive sha256 007054adfdb1e6d7..., publication commit 7e4c09f2c);
  - Thread thr-ens-lossless-memorizer; Campaign C-ENS-ARC3; Experiment E-ENS-LM01 (WTP-LM01 v0.3.2);
  - no Fabric Task or Attempt (nothing was executed).
- Frozen / base SHA: LM01 freeze ee8cbe0c8cb1ef131e6bc8181c8272656eaa5a6e; worktree base bd48fac9b5d51262e84b76d0ca16b8d9054eb5f1.
- Work that exposed it: a dry verification (no launch, no seed derived). ensorain.lm01.launch_gate.campaign_seeds() was
  called with the path ops/work_orders/archive/MWO-0001_2026-09-28.md.
- Expected (MWO-0001 s7): an operator-approved MWO containing the exact line "LAUNCH WTP-LM01 using frozen prereg <prefix
  of ee8cbe0c8>" is a valid carrier for the launch authorization, replacing the operator-direct-chat requirement of the
  2026-09-26 ruling item 6.
- Observed:
  - The TEXT check works: is_operator_launch() accepts that line, with or without a trailing period.
  - It correctly REJECTS MWO-0001's text, which contains no launch line.
  - But the RECORD check (_verify_recorded) requires a comms-style MANIFEST.md in the directive's own directory.
    ops/work_orders/archive/ has none: MWO integrity is carried by the PUBLICATIONS.md sha256 of the LF git blob plus the
    publication commit. So ANY MWO archive file is refused.
  - The refusal surfaces as an unhandled FileNotFoundError (missing MANIFEST.md), not a clean PermissionError.
  - Also relevant: on this Windows checkout the working-tree archive file hashes differently (CRLF) from the LF blob in
    PUBLICATIONS.md. An MWO-aware check must hash `git show <commit>:<path>`, not the working file.
- Science blocked? NO. Safety blocked? NO. The gate fails CLOSED: it can only refuse, never launch wrongly. LAUNCH is
  blocked for an MWO-carried authorization, and only that.
- Not hidden, not worked around. launch_gate.py is a FROZEN file (in FREEZE.json), so changing it re-freezes LM01 and
  changes the hash an MWO must carry. Resolution options, for the operator / next MWO:
  - (A) TRANSCRIPTION, no code change. When a launch MWO is published, Ensorain records that MWO's text verbatim under
    roles/Ensorain/prompts/<date>_lm01_launch/.
    - It first verifies the MWO against PUBLICATIONS.md: git-blob sha256 and publication commit, both named in the
      recording's README.
    - It then writes a MANIFEST, which the frozen gate accepts.
    - This is the recording procedure the 2026-09-26 ruling item 6 already prescribes ("record that directive verbatim
      with its hash/provenance").
    - Needs: the MWO to state that option A is acceptable.
  - (B) GATE REPAIR. Add an MWO carrier to launch_gate.py: read the path at the PUBLICATIONS.md commit, hash the git blob,
    match it against the register row, then apply the same phrase check.
    - Requires a v0.3.3 re-freeze (launch mechanics only; no scientific change). The launch MWO would then carry the
      v0.3.3 hash.
  - Ensorain recommends (A): it preserves the reviewed freeze ee8cbe0c8.
- Status: OPEN. Recorded in roles/Ensorain/WORK_STATE.json (blocked_on, operator_decisions_required).

## DEF-ENS-002: the legacy WTP-01 engine records replay_ok but never gates REPLICATED on it

- Recorded 2026-09-29T03:00Z. Source: Artemis R-08 (comms #882; a worker claim), verified by Ensorain.
- Identifiers: MWO-0001; thread thr-ens-lossless-memorizer (legacy Foundry lineage); experiments WTP-01/02/03 (closed
  campaigns); no Fabric Task.
- Base SHA: bd48fac9b.
- Expected: a REPLICATED label requires an identical replay of the original run.
- Observed:
  - ensorain/wtp/campaign.py:146 sets state = REPLICATED from hits >= 3 alone; replay_ok is recorded (line 150) but not
    used.
  - ensorain/wtp3/campaign3.py:339 has no replay check in its REPLICATED rule, and the WTP-02/03 rows carry no replay_ok
    field.
- Impact check on the committed rows: WTP-01 has 35 rows with replay_ok, 0 of them false, so NO WTP-01 REPLICATED
  label was affected. WTP-02/03 cannot be assessed (no replay recorded). Their REPLICATED labels rest on independent
  seed hits, not replay identity.
- Science blocked? NO (closed campaigns; verdicts REDESIGN / PARK / known physics). LM01 does not use this code path.
- Status: RECORDED. A fix belongs to any future WTP-04/Foundry revival (gate REPLICATED on replay_ok). No retroactive
  relabel is needed for WTP-01.
