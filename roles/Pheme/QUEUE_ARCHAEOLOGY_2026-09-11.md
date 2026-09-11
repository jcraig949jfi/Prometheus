# Pheme queue archaeology, 2026-09-11

Base role, seat states: "Booting an old seat is an archaeological event,
not an instruction to resume its last queue. On adoption a historical
seat classifies every item of its old queue against the current north
star and ecosystem: STILL_LIVE, NEEDS_REPREMISE, PARKED, SUPERSEDED,
TRANSFERRED, RETIRED. Only STILL_LIVE becomes executable work."

Read at origin/main 57533fa76. Sources: agents/pheme/CHARTER.md (Aporia,
2026-05-23); agents/pheme/state/state.json and artifacts/ in the
canonical checkout (untracked runtime, 354 ticks to 2026-05-30);
pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md row 18;
pivot/COMPONENT_DOSSIERS_2026-06-24.md Pheme section;
engine/queues/BACKLOG.jsonl PROF-Pheme and engine/queues/PROF_TRIAGE.jsonl;
roles/Ergon/RESPONSIBILITIES.md (re-chartered 2026-08-30, rewritten
2026-09-11); roles/base-role/NORTH_STAR.md.

## 1. Classification

Totals: 0 STILL_LIVE, 2 NEEDS_REPREMISE, 3 PARKED, 1 SUPERSEDED,
0 TRANSFERRED, 0 RETIRED. Nothing is executable today.

PQ-1 | Scan the Ergon Learner eval roots each tick and publish a
      per-pattern demand profile (charter steps 4-7) | NEEDS_REPREMISE |
      The upstream never existed (0 of 354 ticks found an eval root; all
      three roots absent on 2026-09-11) and its producer no longer has
      that job: Ergon was re-chartered 2026-08-30 as the memory-
      metabolism seat and its 2026-09-11 seat file describes no Learner
      training or eval loop. The idea underneath -- measure where the
      ecology is failing and publish that as a demand signal so pressure
      is routed to it -- is consistent with the north star (pressures
      and instruments, not the reasoner). The object it measured is
      gone; the premise must name a new measured deficit before any
      work exists.

PQ-2 | Bias Hypatia and Atalanta selection through demand_latest.json
      (charter, downstream consumers) | SUPERSEDED | Neither consumer
      is a seat under roles/; both daemons were last touched
      2026-05-23 and the seam was broken on paper (set() over a list of
      dicts). The consumer side of the loop does not exist in the 2.0
      ecosystem; if PQ-1 is re-premised its consumers are named fresh.

PQ-3 | Adjust substrate_type_bias A/B/C/D/E quotas from observed
      deficits (charter, profile shape) | NEEDS_REPREMISE | The typed-DR
      substrate program (A-E types, Aporia 2026-05-21) is not referenced
      by any current seat file; the quota-shift heuristic is residue
      worth keeping navigable (dossier "salvage IP"), not a task.

PQ-4 | June disposition REVIVE-SPINE (plan row 18) and dossier
      suggestion REFACTOR with four options (revive-when-eval-exists;
      fix-the-seam-first; aim-the-forge-directly at Hephaestus'
      failure-cluster selector; park-and-lift-the-schema) | PARKED |
      Marked by the operator "NOT APPROVED -- AI SUGGESTIONS ONLY"; the
      HITL decision line is blank as of 2026-09-11. A blank decision is
      not permission. Stays parked until the operator fills it or the
      re-premise (PQ-1) makes it moot.

PQ-5 | PROF-Pheme: run Pheme artifacts/config through phase0+R4 ladder
      probes (engine/queues/BACKLOG.jsonl, fleet_profiling,
      2026-08-22) | PARKED | Already status PARKED in that queue with a
      budget gate ("LLM-driven agent: probe profiling = API spend");
      PROF_TRIAGE binds Pheme AT-COST. It is the profiling lane's item,
      not this seat's; recorded here so it is not lost, not adopted.

PQ-6 | The 30-minute daemon loop itself with its NULL_TICK /
      UPSTREAM_NOT_FOUND / EVAL_DROUGHT sentinels and heartbeat | PARKED |
      Not running (PID 5768 dead; no scheduled task). It is NOT
      restarted: a loop whose input does not exist is not a monitor
      (MONITORS.md, the Ergon probe precedent, base rule 8). Reported to
      Archaeon for the registry as DEAD / present-not-active so its
      absence is visible rather than read as health.

## 2. What the north star says about this seat's premise

The north star wants pressures, instruments and provenance that let
mechanisms be discovered under selection, and treats failure as
metabolic material. Pheme's one idea -- convert a measured failure
distribution into a published, typed demand that routes upstream effort
-- is a pressure-routing instrument, which is in scope. Its May
instantiation measured a Learner that was the reasoner Prometheus 1.0
was hand-training; the north star says we do not supply the reasoner.
So the instantiation is dead and the idea is not; that is exactly the
NEEDS_REPREMISE case.

Where such a signal could be measured today (orientation only, not a
claim of ownership; read from sibling seat files at 57533fa76):
Kairos owns failure geometry over the SFE ledger; Hephaestus owns the
forge's failure-cluster selection; Alethelia reads program liveness;
Harmonia owns the qualification cycle; Ergon owns memory admission with
"whether retention pays" as its open question. A re-premised Pheme
would have to name which of these measured deficits it aggregates, who
consumes the demand profile, and the positive and cheat controls that
prove the profile moves a consumer's selection (the dossier's settle
condition, which was right and was never met). That is a charter
question for the operator, not a decision this seat can take alone,
because it changes what another seat's output is used for.

## 3. Recommendation (a stand; assumed wrong until the operator rules)

Do not retire and do not revive as-is. Hold Pheme BLOCKED on one
operator decision, proposed id NEW: "Pheme re-premise: is a demand-
routing instrument over the 2.0 ecology's measured deficits wanted, and
over whose measurements?" If yes, the first work item is the charter
plus a seam fixture (synthetic deficit -> profile -> a named consumer's
selection changes, with a cheat control), before any daemon runs. If
no, Pheme stays PARKED with its residue navigable and this directory as
the annotation; nothing is deleted.

The seat declares its conflict of interest: a re-premise keeps the seat
alive, and the seat wrote this recommendation.
