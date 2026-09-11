# Eos backlog

Currency: 2026-09-11 (written on the re-seating pass). Schema:
roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md.
Priority order. The first five are the ones the seat starts on the day
EOS-01 is ruled; nothing here is executable before that, because the
seat's premise itself is the first decision.

Format: id | item | lane | milestone | size | blocked_on | evidence of done

DONE 2026-09-11 | EOS-01 | ruled ACTIVE by the operator; typing rule adopted; STATUS off BLOCKED | evidence: roles/Eos/STATUS.md, roles/Eos/intake/FIRST_SEASON_2026-09-11.md
DONE 2026-09-11 | EOS-07 | three controls built and run; old scorer failed its own cheat control 100 vs 8 | evidence: roles/Eos/CALIBRATION.md result block, agents/eos/tests/test_intake.py
DONE 2026-09-11 | EOS-08 | moot: the scorer is retired, not repaired | evidence: FIRST_SEASON s "Test 1"
DONE 2026-09-11 | EOS-19 | D-23 guard on all three entry points | evidence: test_d23_guard_present_at_every_entry_point (3 params)
DONE 2026-09-11 | EOS-03 | answered: built same day as Clio (2e4072ae5), dead 104 days, unowned | evidence: roles/Eos/EOS03_ARCHAEOLOGY_CLIO.md
DONE 2026-09-11 | EOS-04 | 14 call sites traced, route-then-move proposal written; no credential touched | evidence: roles/Eos/EOS04_KEYRING_MIGRATION.md
DONE 2026-09-11 | EOS-02 | comparison done, narrow 7-row SOURCES residue proposed with a falsifier | evidence: roles/Eos/EOS02_REGISTRY_COMPARISON.md
DONE 2026-09-11 | EOS-17 | partially: agents/eos/ re-included in .gitignore so seat output can be committed, with .env held out by two tests | evidence: agents/eos/.gitignore, test_env_file_stays_ignored
DONE 2026-09-11 | EOS-24 | reported; Archaeon fixed it the same day (comms #65): comms now fails closed | evidence: comms #55, #65

EOS-30 | Have an INDEPENDENT seat attack the first season: re-run the gate over the same sample and dispute the refusals | EVIDENCE | alpha | M | Kairos or Elenchus accepting the commission | a committed second opinion naming at least one refusal it considers wrong, or stating none
EOS-31 | Close or bound the gate's semantic hole: a referent must be shown RELATED, not merely to exist | TOOLS | beta | L | EOS-30 (attack it before strengthening it) | a mechanism plus the updated cheat test; if no mechanism is found without an LLM adjudicating, that null is the deliverable
EOS-32 | Route the six PENDING_ADMISSION items to the seats that own their referents (Apollo x2, Nyx x2, Icarus, base-role) and record what each admits or refuses | EVIDENCE | alpha | S | none | comms messages posted and each seat's answer recorded in the ledger
EOS-33 | Give the ACQUIRE dedup search a bounded index instead of git grep over 39,284 files | TOOLS | beta | M | none | a search that answers in under 5 s, with the same exclusions, and the INDETERMINATE test still passing
EOS-02 | DECIDE the destination of the 7-row SOURCES residue and whether prometheus_llm claims the source rows (investigation DONE 2026-09-11) | TOOLS | alpha | XL | operator + prometheus_llm maintainer | a ruling, then either a migration commit or the renamed residue file
EOS-03 | DECIDE who owns Clio -- a seat, or an explicit RETIRED annotation (investigation DONE 2026-09-11: built 2e4072ae5, dead 104 days, unowned, heartbeat still says online) | LIT | alpha | XL | operator decision | a MONITORS row with an owner, or a RETIRED annotation with its residue preserved
EOS-04 | EXECUTE Phase 0 of the keyring migration: 13 lanes route their own call site through keys.get_key (trace and proposal DONE 2026-09-11) | TOOLS | alpha | L | thirteen lanes; Eos owns only the list, the example and the test | a test asserting no tracked file except keys.py contains the path
EOS-05 | Route the unowned Hermes portfolio-brief mailer (MONITORS row, ACTIVE/UNOWNED, M3 or M4) to a claiming seat | TOOLS | alpha | S | Hermes (seated today) and operator | the MONITORS row carries an owner and a freshness source, or a decision to stop it
EOS-06 | Measure whether any consumer of Eos output is alive, by executing each of the three referencing call sites and recording what it does with the artifact | EVIDENCE | alpha | M | none | a committed measurement with the commands and outputs for aletheia.py:41, hermes.py:406, check_intelligence_pipeline.py:29-32, and a consumer count with its date
EOS-09 | Refuse to emit a digest whose body hashes to its predecessor; emit a typed no-op reason instead | TOOLS | alpha | S | none | a test that feeds the writer identical input twice and asserts the second call returns a no-op reason, not a file
EOS-10 | Report the eligible count beside every yield count in every cycle (so "0 new" and "0 could have been new" are distinguishable) | TOOLS | alpha | S | none | a cycle record carrying yield and eligible per source, and a test covering the saturated case
EOS-11 | Restore hour-of-epoch keyword rotation so the tail of every keyword list is reachable, independent of the retired substrate premise | TOOLS | alpha | S | none | a test showing that over 24 simulated cycles every keyword in a list is used at least once
EOS-12 | Replace the llm_analyze hop with a query/type PROPOSAL step that never writes prose into a digest | TOOLS | alpha | M | EOS-01 | the digest writer has no path from a model response to a rendered analysis section, proven by a test
EOS-13 | Route all model calls through prometheus_llm and delete the seat's own NVIDIA client | TOOLS | alpha | S | EOS-12 | no urllib model call remains in agents/eos/src; a health call through prometheus_llm recorded
EOS-14 | Re-measure all 15 api_registry rows against observed behaviour (limit, latency, failure shape, date, source URL) and mark every unmeasured row UNVERIFIED | TOOLS | beta | M | EOS-02 | api_registry.json with an observed block per row and a committed run log; no row claims a limit it has not seen
EOS-15 | Write the know-before-you-knock precondition as an executable gate: no source is called until its documented limits row exists and is current | TOOLS | beta | S | EOS-14 | a gate function plus a test that a source with a missing or stale limits row raises rather than calls
EOS-16 | Determine what library_scanner.py and the 3.6 MB library_manifest.json are for, and who consumes them, or mark them residue | TOOLS | beta | S | none | a committed answer naming the consumer or recording none, and the file moved to archive if none
EOS-18 | Write last_input_at and last_success_at to a readable file on every cycle, with the productivity signal beside them | TOOLS | beta | S | EOS-01 | a freshness file readable without running the daemon, and the MONITORS row pointing at it
EOS-20 | Register the corrupted-key control: prove the seat can tell a dead provider from a dead credential before recording either | TOOLS | beta | S | EOS-14 | a control run with a deliberately corrupted key whose failure shape differs from a real outage, both recorded
EOS-21 | Define the ANCHOR type's test: what makes an item a calibration anchor in territory the substrate is weak in, as a predicate a human can check | LIT | beta | M | EOS-01, HARD-4 hunt directions | a written predicate plus 10 historical items typed by it, with the disagreements listed
EOS-22 | Type the 163 items already in paper_index.json under the typing rule and report the distribution | LIT | beta | M | EOS-21 | a committed table of 163 rows with types and reasons, including every REFUSED reason
EOS-23 | Submit the seat's negatives to the Evidence Wiki: the identical-digest measurement, the unreadable May receipt, the uncalibrated scorer | EVIDENCE | alpha | S | none | Evidence Wiki entries via the API with their rows, and the ids recorded in the journal
EOS-25 | Stop citing Semantic Scholar as a source until its 403 is resolved or the source is dropped | LIT | beta | S | EOS-03 evidence, Techne 0d76ac34d | the scanner refuses to list S2 as available, or a successful call is recorded with its date
EOS-26 | Write the refusal ledger: every REFUSED item with its reason, kept as the record of what the program declined | LIT | beta | S | EOS-01 | a committed append-only refusals file with at least the 163 indexed items classified
EOS-27 | Annotate every historical Eos score with the retired premise it was scored against, so none can be cited bare | EVIDENCE | alpha | S | none | a header in the archive README and in api_registry/paper_index stating the premise and its retirement date
EOS-28 | Establish the seat's decay windows: how old a RESOURCE row, an ANCHOR claim or a source-availability fact may be before it reads UNVERIFIED | TOOLS | beta | S | EOS-14 | a committed table of decay windows per claim type, and the gate that applies them

XL rows now open for the operator's queue, after the 2026-09-11 pass:
  EOS-02  which destination the 7-row SOURCES residue lives at, and
          whether prometheus_llm's maintainer claims the source rows
  EOS-03  who owns Clio: a seat, or an explicit RETIRED annotation
  EOS-04  Phase 1 destination (root .env recommended) once Phase 0 is done
  NEW     whether collection restarts at all. The operator reserved this;
          the evidence it asked for is in FIRST_SEASON_2026-09-11.md and
          this seat has not acted on it.
EOS-05 needs Hermes and the operator together but is not XL.
