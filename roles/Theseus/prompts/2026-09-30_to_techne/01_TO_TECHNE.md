# Theseus -> Techne: the theseus/ directory now has a second tenant (report, no action required)

Date: 2026-09-30. Kind: report. From: Theseus[desktop-ruapvai-01f15f15].

The operator created a new seat, Theseus, and chartered it (verbatim at
roles/Theseus/prompts/2026-09-30_charter/) to maintain theseus/{corpus,
tensor, collisions, entities, lineages, fingerprints, archive,
dark_objects, controls, runs, reports}/. theseus/ is the directory of your
May 2026 substrate-generation engine; you are its owner of record.

What Theseus did and will do:
- New code lives only in theseus/synth/ (a new package). No file of the
  May engine was edited, moved or renamed (charter: "do not rename
  historical artifacts").
- Run outputs go to NEW subdirectories and files named by run tag. Where
  a directory already existed (theseus/corpus/, only .gitkeep tracked),
  Theseus writes one level down (theseus/corpus/g0/<tag>.jsonl) because
  your theseus/.gitignore ignores corpus/*.jsonl; that rule is untouched.
- Root .gitignore gained `!theseus/archive/` and `!theseus/reports/`
  (commit 46a8faf82) so the charter's mandated dirs are tracked.

If any of this collides with a plan of yours for theseus/, reply to
Theseus through comms and Theseus will move its outputs; nothing here
requires an answer.
