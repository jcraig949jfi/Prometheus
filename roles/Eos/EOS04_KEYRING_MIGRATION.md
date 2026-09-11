# EOS-04: migrating the program keyring off a dormant seat's directory

Currency: 2026-09-11. Operator ruling: YES in principle -- a program
credential path must not remain owned by a dormant historical seat. Trace
consumers and propose the smallest safe migration. Do not move credentials
or expose values during the investigation.

NOTHING WAS MOVED. NO VALUE WAS READ, PRINTED OR COMMITTED. The file was
confirmed to exist (1,252 bytes) and nothing else was done to it. Every
finding below comes from reading the CODE THAT READS IT, never the file.

## The trace: 14 code call sites across 9 lanes, not the 5 first reported

Search: `git grep` for the literal path and for the joined-Path form, over
all tracked .py/.md/.sh/.bat/.yaml, excluding roles/Eos/.

CODE (reads the path directly):

    keys.py:20-21                                  the canonical loader
    scripts/llm_cascade.py:29                      auto-loads on import
    scripts/send_brief_email.py:447
    scripts/metis_portfolio.py:48                  (via llm_cascade import)
    agents/aletheia/src/aletheia.py:59
    agents/hermes/src/hermes.py:72
    agents/hephaestus/benchmark_models.py:25       relative '../../agents/eos/.env'
    cartography/shared/scripts/external_research.py:49
    charon/ceiling_v0/reasoner.py:22
    ergon/probe/solver.py:85
    ergon/probe_api_preflight.py:29
    ergon/probe_api_soak.py:44
    forge/_test_nvidia.py:8
    prometheus_llm (per its README: _ENV_FILES includes the path)

DOCUMENTATION that instructs a reader to put credentials there:

    agents/aletheia/README.md:172, agents/hermes/README.md:69,
    agents/pronoia/README.md:57, 420, 473,
    harmonia/memory/architecture/model_zoo_plan_2026-05-29.md:30,
    prometheus_llm/README.md:110, 118, 143,
    prometheus_llm/handoff/M1_to_M2_20260822.md:17,
    pivot/hermes_deprecation_2026-05-17.md:42,
    pivot/PREREG_METABOLIZATION_PROBE_v1.md:131,
    charon/ORCHESTRATION_FORENSIC_MAP_2026-08-31.md:313

CLAUDE.md at the repository root already states the intended design: "All
API keys are loaded via keys.py at the repo root. Scripts should
`from keys import get_key` rather than reading key files directly." Thirteen
of the fourteen call sites do not follow it. forge/llm_client.py:87 has
already migrated and left the note explaining why, which makes it the
worked example.

## Why the obvious migration is the wrong one

The obvious move is to move the file and update the readers. That breaks 13
call sites simultaneously, across 9 lanes owned by 9 different seats, and
every one of them fails the same way: silently, by falling back to "key not
found" and degrading to a disabled provider. This program has already paid
for that failure mode once -- prometheus_llm/README.md:143 records
`get_key("NVIDIA")` failing SILENTLY because the key lived in this file and
the loader did not know.

prometheus_llm/README.md:110 names the second hazard: a fix that "teaches
it to search agents/eos/.env will not propagate by git" -- the path is
replicated in per-machine working copies, so a coordinated move is not
atomic across M1, M2, M3 and M4.

## The proposal: route first, move second. Three phases, each reversible.

### Phase 0 -- ROUTE. No credential moves at all.

Every direct reader stops reading the path and calls `keys.get_key(...)`
instead. keys.py keeps reading both of its current sources, unchanged. At
the end of Phase 0 exactly ONE file in the repository knows where
credentials live.

- Each lane makes its own change; Eos does not edit another lane's code.
  Eos supplies this list and the worked example (forge/llm_client.py).
- Verifiable without any secret: a test asserting that no tracked file
  except keys.py contains the literal path. That test is the deliverable,
  and it can be written today.
- Risk: a lane whose call site is on an unpushed machine-local copy.
  Mitigated by keys.py continuing to read the old path throughout.

### Phase 1 -- MOVE. One line, one file.

With keys.py the only reader, the file moves to a path named for what it
is rather than for a seat that was dormant for four months. Recommended:
a repository-root `.env` (already keys.py's FIRST source and already
gitignored), or a dedicated `config/credentials.env` if the root file is
wanted for something else. keys.py keeps `agents/eos/.env` as a DEPRECATED
fallback for one cycle, with a dated comment naming the removal date.

- The move itself is done by the operator, on each host, by hand. Not by
  this seat, not by a script, not through git.
- The precedence order in keys.py already prefers the root .env, so a host
  that has not yet moved keeps working and a host that has moved works
  immediately. No flag day.
- Verifiable: `keys.get_key` returns a value on each host before and after
  (a boolean, never the value).

### Phase 2 -- REMOVE the fallback.

After one cycle with no host reporting a miss, the `agents/eos/.env` entry
leaves keys.py with a dated supersession note, and the 13 documentation
references are corrected in the same commit so no future reader is told to
put a credential in a seat directory.

## What Eos has already done, and what it will not do

DONE on this pass, and it is a precondition for any of the above: the root
.gitignore now re-includes `agents/eos/` WITHOUT a `/**` glob, with an
`agents/eos/.gitignore` that keeps `.env`, `.env.*`, `*.key`, `*secret*`,
`*credential*` and `reports/` out. Two regression tests hold it:
test_env_file_stays_ignored and test_reports_dir_stays_ignored. Before
this, the seat's files were force-added individually and a future
re-inclusion done carelessly would have made the keyring trackable.

WILL NOT DO: move the file, read it, copy it, print any value from it, or
edit another lane's call site. Phase 0 is thirteen small changes owned by
thirteen lanes; Eos's contribution is the list, the example and the test.

## Recommendation in one line

Do Phase 0 first and do not move anything until it is finished; the value
of the move is entirely in there being one reader, and that value is
available without touching a credential.

## Open decision for the operator

Which destination for Phase 1: the repository-root `.env` (zero new
concepts, already first in keys.py's precedence) or a dedicated
`config/credentials.env` (clearer name, one more path to teach). Eos
recommends the root `.env` on the grounds that it requires no change to
keys.py's search order and no new documentation.
