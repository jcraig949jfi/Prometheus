# AETH-02 NATIVE CIRCUITRY -- provenance and boot pointer

Issued by: the operator, in chat, 2026-09-23.
Received by: Aether[buckkeep-7a10ca4b] on BUCKKEEP.
Status: **STANDING DIRECTIVE, NOT STARTED.** No work against it had
begun when it was committed; it was committed deliberately so it
survives a context reset and a Claude Code upgrade.

## The verbatim text

`DIRECTIVE.md` beside this file is the operator's text **verbatim**,
including its em dashes, curly quotes, superscripts and section rules.
Nothing was normalized, paraphrased, reordered or summarized. The
pure-ASCII rule applies to `roles/base-role/` files only, and the
terminology contract's audit surface is the `Aether/` tree only, so
neither required an edit here. The verbatim directive outranks every
summary of it, including this file and including anything I wrote in
the journal (base role s1 step 2).

`MANIFEST.md` carries the sha256 of the committed LF bytes. Verify it
before acting on the directive (base role s1 step 5):

    python -m comms.manifest verify roles/Aether/prompts/2026-09-23_native_circuitry

## Why this exists in four places

The boot sequence reads, in order: the seat entry file, then the newest
prompt under `roles/Aether/prompts/`, then the newest dated TODO, then
`git log`. A directive that lives in only one of those is one stale
file away from being missed. So the same pointer appears in:

1. `roles/Aether/RESPONSIBILITIES.md` -- the entry file, read first
2. this prompt directory -- the authoritative verbatim text
3. `roles/Aether/TODO.md` -- the dated TODO, with the resume state
4. `roles/Aether/STATUS.md` -- "next executable action"

If those four ever disagree, **DIRECTIVE.md is what the operator
actually said** and the others are wrong.

## What the next instance must NOT assume

- That any of this round has been done. It has not. Track 1 through
  Track 5, the determinism check and the output document are all
  unstarted as of commit time.
- That the First Light tooling already covers it. It does not. The
  causal-graph observatory of Track 2 **does not exist**; the current
  observatory measures lattice-wide scalars and 64-block coarse maps
  and emits no edges at all. Track 2 is a build, not a configuration.
- That money is still available without checking. Roughly $2.09 of the
  previous $3 authorization was spent on 2026-09-22. The directive
  grants **its own fresh budget of up to $3**; confirm with the
  operator rather than inferring a carry-over.

## Boot checklist specific to this directive

Before spending anything:

1. Resolve the base-role inheritance chain as usual.
2. `python -m comms.manifest verify` this directory.
3. Read `DIRECTIVE.md` in full, then the four documents its "Start by
   reading" block names.
4. Read `roles/Aether/TODO.md` for the resume state and the known
   blockers, and `Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md` section
   "HYPOTHESES FOR NEXT ROUND", which this directive supersedes and
   partly absorbs (H1 becomes Track 1; H2 becomes the determinism
   check; H3 becomes Track 5).
5. Confirm `ACTIVE_POD_COUNT 0` before and after any pod work.
