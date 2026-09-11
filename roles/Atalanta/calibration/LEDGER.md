# Atalanta calibration ledger

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Kept because it is unflattering (base role, section
2). One row per wrong, unmeasured or un-re-verifiable call this seat
carries, including calls made inside the pass that created this file.

Columns: id | the call | who made it and when | status today | what it cost

L-01 | MIN_REUSE_FOR_CANDIDATE = 3: "a primitive must appear in at least
3 organisms to be a candidate" (daemon.py:72) | Aporia, 2026-05-23, in
the founding commit | UNMEASURED. No organism population was ever
counted, so the threshold has no attainable range and no eligible count
behind it. It is a number chosen before the data existed. | Nothing yet,
because the gate never had the chance to fire. It is on the backlog as
ATALANTA-09 so it cannot be inherited silently by a successor.

L-02 | MIN_COMPOSITE_FOR_CANDIDATE = 3 (daemon.py:73) | Aporia,
2026-05-23 | UNMEASURED, identically to L-01. | As L-01.

L-03 | ANTI_SILENCE_ALARM_THRESHOLD = 50 (daemon.py:71): "alarm at 50
consecutive null ticks" | Aporia, 2026-05-23 | WRONG, and measurably so.
The threshold was reached and the agent then ran roughly 300 further
ticks. The design error was not the number: the alarm had no route.
pivot/orchestration_monitoring_2026-05-24.md records the atalanta and
pheme sentinel telemetry being read as noise the day after launch. | This
is the cost line of the whole agent. An instrument that reports a real
defect to nobody is the defect base rule 7 exists to name.

L-04 | The charter's closing claim: "Once Techne registers them, Apollo's
next run has a richer pool. The feedback loop closes." | Aporia,
2026-05-23, agents/atalanta/CHARTER.md | NEVER TESTED, at any link. Zero
candidates surfaced, zero queries dispatched, zero proposals filed, zero
registrations, zero enriched runs. The sentence describes a loop of which
no segment has ever carried a single item. | It reads as a mechanism and
is a plan. Marked here so it is never cited as a result.

L-05 | The roster label "Atalanta | M1 | tool | Aporia | active | online |
22m | 96 ev" | Aporia's roster snapshots, 2026-05-26 and 2026-05-28 | TRUE
AND MEANINGLESS. Every field was accurate. The agent was online, recent,
and emitting events -- and producing nothing, which no column showed. |
The clean illustration of PRESENT is not ACTIVE is not PRODUCTIVE (base
rule 8). Ninety-six events, all of them absence.

L-06 | "354 ticks, 354 of 354 artifacts UPSTREAM_NOT_FOUND" | Aporia P47,
2026-08-20, engine/ledger/AGENT_AUTOPSIES.jsonl, read from the M1 host |
SINGLE-SOURCED and NOT RE-VERIFIABLE from SPECTREX5: there is no runtime
residue on this host (no state/, artifacts/, logs/, events.jsonl or pid
file; all are gitignored and were never committed). The June dossier
quotes the same figure from the same machine, so it is one source, not
two. | This seat quotes the number with its provenance grade attached and
does not present it as re-measured. ATALANTA-22 either finds a second
source or marks it permanently single-sourced.

L-07 | The June dossier: "the parser ... [does not] actually match
Apollo's real organism schema" | the 2026-06-24 dossier author, marked
"unverified claim" at the time | PARTLY WRONG, corrected today at
8714b2709 rather than silently rewritten. The KEY is alive:
primitive_sequence appears throughout current apollo/src (genome.py,
compiler.py, map_elites.py, primitive_types.py). What diverged is the
CONTAINER: Apollo writes checkpoint pickles and novel_discovery.jsonl,
not per-run JSON with run_id/completed_at/organisms. | It changes the
revival estimate from a redesign to a reader (ATALANTA-08). The dossier
line stands where it is with this annotation beside it.

L-08 | "scripts/atalanta_loop_launch.bat is NOT in the tree at 8714b2709
(verified; only pheme and talos launch scripts exist)" | this seat,
2026-09-11, written into the first draft of RESPONSIBILITIES.md | WRONG.
Never verified. The word "verified" was written about a check that was
not run: a git-log pathspec returning one commit was read as a statement
about the current tree. The file is tracked and present, alongside seven
other loop-launch scripts. Caught before the commit, corrected in place.
| Nothing downstream, because it was caught. Recorded anyway: this is
the seat's own first instance of accepting a label in place of the
property, on the same pass in which it wrote up an agent that died of
exactly that.

L-09 | "git pull" run in the canonical checkout at the start of this
session | this seat, 2026-09-11, on the operator's instruction and before
reading the working contract | A D-23 VIOLATION on two counts (section 1,
no mutating git operation in the canonical checkout; section 3, never
pull). Outcome inspected: a fast-forward of main to 8714b2709, no
conflict, no file loss, two pre-existing untracked evidence_wiki paths
left alone. | No damage measured. Reported rather than omitted, because
a violation that produced no harm is still the shape that produces harm
later, and the base role's own rule is that the constitution is
falsifiable only when the friction is reported (ATALANTA-05 carries the
related resolver finding).
