# Salvage fact-finding: common brief for every worker

Issued by Dionysus[m1-3815a3b9] (Phase 3 architect FABLE-5.1) on 2026-10-01.
Authority: the operator's charter at roles/Dionysus/prompts/2026-10-01_charter/.
You are a read-only fact-finder. You do not design anything and you do not
judge whether any old scientific result was true.

## What this is for

Dionysus has frozen a set of requirements and an architecture for Prometheus
Phase 3 (commit a0e3a4d03). The architecture has named SLOTS. Your job is to
find out, for one group of existing Prometheus components, what each one
really does and how well it would fill a slot, so that Dionysus can decide
between keeping, hardening, extracting, rebuilding or retiring it.

The question for every component is:

    Does this satisfy a Phase 3 requirement better than rebuilding it?

It is not "how can this be preserved?". There is no preservation quota. A
sheet that says "small, coupled, untested, rebuild is cheaper" is a good
sheet.

## Read first, in this order

1. docs/phase3/design/FABLE-5.1/REQUIREMENTS.md, sections 1 (definitions)
   and the requirement areas named in your scope file.
2. docs/phase3/design/FABLE-5.1/RSE_ARCHITECTURE.md, sections 3 to 7.
3. Your scope file in this directory.
4. The seat dossiers named in your scope file, under
   docs/phase3/intake/<crawler>/seats/<Seat>.md, and the matching records in
   docs/phase3/intake/<crawler>/engine_index.jsonl.
5. Then the source code itself. The dossiers are a locator. They are not
   ground truth. When a fact matters to fit or cost, open the file.

## Hard rules

- READ ONLY. No git writes of any kind. Do not create, edit or delete any
  file in the repository. Do not run experiments, campaigns, engines,
  services or test suites (some test suites here rewrite tracked files).
  You may run read-only commands: git grep, git log, git show, wc, python
  one-liners that only read and count.
- Work in the worktree you were started in. Do not touch the canonical
  checkout.
- EVERY search must exclude holdout and secret paths. With git grep, append:
      -- ':!**/*holdout*/**' ':!**/nestor_secrets/**'
  Never open a path containing "holdout" or "nestor_secrets". Never open
  files named credentials.py, secrets.py, keys.py, *.env or config files
  that hold credentials. Never print a credential.
- Do NOT read anything under docs/phase3/design/ except FABLE-5.1. Do not
  read roles/Enceladus, roles/Epimetheus or any other architect's material.
  Independence between architects is a condition of this work.
- Wrap git commands in a timeout. The tree has about 69,000 files; a
  filesystem grep -r is too slow, use git grep.
- Paths in your report are repository-relative. No drive letters.
- Pure ASCII in your report. No em-dashes, arrows or other Unicode.

## What to report

For each component in your scope, one sheet in exactly this shape:

    COMPONENT: <plain name>
    PATHS: <repo-relative paths, the few that matter>
    OWNER / DATES: <seat; first and last commit dates touching it>
    WHAT IT REALLY DOES: <2 to 5 sentences. The mechanism, not the label.>
    SIZE: <files, approximate lines of code, number of test functions and where>
    DEMONSTRATED CORRECTNESS: <what shows it works: an independent oracle,
        replay, controls shown able to fail, known-answer cases. Also every
        known defect, with the path or commit that records it.>
    INTERFACE: <how it is called; inputs and outputs; deterministic or not;
        integer-only or floats; snapshot/restore; any model call inside>
    THROUGHPUT / SCALE: <measured numbers only, with where they are recorded.
        If none is recorded, say "not recorded".>
    COUPLING: <what it imports from other seats' code; what imports it;
        host-local or off-repo dependencies; databases; gitignored inputs>
    FIT TO SLOT: <slot name from your scope file; the requirement ids from
        REQUIREMENTS.md it would satisfy as is; the ones it fails; what is
        missing>
    MODIFICATION COST: <S (under 1 day), M (1 to 3 days), L (1 to 2 weeks),
        XL (more, or needs a decision), with the main work items. Then the
        cost of REBUILDING the same function from scratch on the same scale,
        so the two can be compared.>
    VERIFIED BY ME: <which of the above you checked in source yourself, and
        which you took from a dossier without checking>

Then, at the end:

    COMPARISON: a small fixed-width table ranking the components for each
        slot, best fit first, one line of reason each.
    COULD NOT DETERMINE: what you looked for and did not find, and what you
        did not have time to open. Absence is a finding only if you say how
        you searched.
    SURPRISES: anything that contradicts the dossiers or that Dionysus
        should know before deciding (for example: a component that is
        better than its dossier says, or one that does not exist at the
        cited path).

Keep each sheet under about 250 words. Numbers are quoted exactly, never
rounded into nicer ones. Where you infer something from code without
running it, say "code-inferred".

Put the whole report in your final message between the lines

    ===BEGIN REPORT===
    ===END REPORT===

Do not write it to a file. Dionysus deposits it.
