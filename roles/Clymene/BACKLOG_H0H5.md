# Clymene -- backlog (PROVISIONAL, below the schema floor)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Base SHA 8714b2709ffa3f1a5d55781d476c3eba4c97a898.

THIS FILE DOES NOT MEET THE BACKLOG SCHEMA and says so rather than
padding. The schema
(roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md) requires
at least 20 items in priority order, with the first five being what the
seat starts today. This seat has no charter and no lane, so it has
nothing it may start today; inventing 20 acquisition items to fill a
quota would be exactly the throughput-satisfying-itself behaviour that
killed the March mission. The file is filed anyway so the operator's XL
queue is derivable from the union of the seats' XL rows, per the
schema's own rule.

Format: ID | item | lane | milestone | size | blocked_on | evidence of done

CLY-01 | Rule whether Clymene is chartered at all, and if so for
  provenance rather than acquisition (the two tests in STATUS.md
  section 3) | EVIDENCE | program | XL | operator decision, NEW: "Does
  the program want an external-artifact provenance seat, and does the
  51 GB vault on M2 stay, move, shrink or go?" | a decision row in
  archaeon/docs/expansion/DECISIONS.md, or an operator line in this
  seat's prompts directory

CLY-02 | Measure reconstructability of the 26 vault repository trees:
  for each, does the registry's recorded upstream commit plus URL
  reproduce the tree on disk | EVIDENCE | alpha | M | CLY-01 | a
  committed per-row ledger (26 rows, YES/NO/INDETERMINATE with the
  command and the diff summary) plus the eligible count, under
  roles/Clymene/ledgers/

CLY-03 | Measure consumption: enumerate every path and Hugging Face id
  by which the 9 real vault models could be reached, and whether any
  live code reaches them | EVIDENCE | alpha | S | CLY-01 | a committed
  consumer census naming each hit with file and line, and an explicit
  zero with its search command if the answer is zero

CLY-04 | Propose the vault registry (three tables, 40 rows, the only
  surviving provenance for the vault trees) to Mnemosyne as a substrate
  question, or record the declination | EVIDENCE | alpha | S |
  Mnemosyne | a comms delegation with its sha256 and Mnemosyne's reply
  in this seat's journal

CLY-05 | Record the two gated-model 403 failures as a credential-shaped
  acquisition failure class, with the keys.py route named, so a future
  acquisition does not rediscover it | EVIDENCE | alpha | S | none |
  a committed failure-shape note under roles/Clymene/ (no credential
  read, printed or committed)

CLY-06 | Report to Archaeon that agents/pronoia/README.md documents an
  entry point (pronoia.py) that is not in the tree, so the pipeline
  spec advertises a host that no longer exists | TOOLS | program | S |
  none | a comms report with its sha256; the defect belongs to that
  lane, not this one

Items deliberately NOT listed: anything that acquires, re-clones,
downloads, prunes or deletes. This seat holds no acquisition authority
and will not create work that presumes it.
