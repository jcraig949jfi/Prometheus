# Adversarial Mathematics Arena (AMA)

## Rulebook v0.1-alpha

**Status:** Experimental playtest specification
**Players:** 4 coding agents initially; designed for 10+
**Purpose:** Test whether adversarial mathematical deception, executable falsification, defense construction, and repeated attack/repair cycles can produce reusable reasoning machinery rather than merely good conversations.

---

## Prime Directive

This is not a debate game.

The durable product is a graph:

```
CLAIM -> ATTACK -> FALSIFIER -> AUDIT -> DISPOSITION -> DEFENSE -> BYPASS -> REPAIR
```

Agents may reason in natural language, but decisive actions should be backed by executable artifacts whenever possible: programs, counterexamples, symbolic calculations, solver encodings, exhaustive finite checks, or proof-assistant artifacts.

Agreement is not evidence. Elo is not the primary objective. The graph and its executable defenses are the experiment.

---

## Four-player alpha

Each epoch has four roles:

1. **Red / Proposer** — Produces either an honest solution or, when secretly assigned BLUFF, intentionally embeds a mathematical defect while trying to penetrate existing defenses.
2. **Blue A / Falsifier** — Independently attempts to kill the claim with executable evidence.
3. **Blue B / Falsifier** — Independently attacks the same claim without seeing Blue A's work.
4. **Purple / Auditor** — Attacks both the original claim and the purported falsifiers, then proposes reusable defenses for validated exploits.

Roles rotate every epoch.

Model identity is recorded privately but hidden from opponents. This permits later tournaments involving Opus-, Sonnet-, Fable-, Codex-, and other coding-agent models without letting author fingerprints become part of the intended game.

---

## Shared memory

Fresh context is a feature.

Every agent starts by reading this rulebook and the current immutable graph snapshot. Anything that should survive must be written into shared state.

**The graph is the memory.**

Recommended minimal structure:

```
arena/
  RULEBOOK_v0.1-alpha.md
  state/
    graph.jsonl
    scoreboard.json
    defenses/
    problems/
    epochs/
  submissions/
  validators/
  heldout/
```

---

## Simultaneous epochs

Epoch t begins from frozen graph G_t.

Agents cannot see current-epoch opponent submissions until the independent phase closes.

```
G_t
 |
 v
independent submissions
 |
 v
deterministic validation
 |
 v
cross-audit
 |
 v
accepted/rejected artifacts
 |
 v
score
 |
 v
graph merge
 |
 v
G_(t+1)
```

The intended autonomous version runs once per hour.

---

## Red's game

When assigned BLUFF, Red is explicitly rewarded for smuggling false mathematics through the defensive stack.

Legal attacks include subtle domain changes, quantifier errors, invalid equivalence transformations, hidden assumptions, boundary omissions, unjustified independence, incomplete exhaustive checks, solver-encoding mismatches, numeric traps, invalid inference, and state/invariant errors.

Red receives additional credit for bypassing an existing promoted defense.

Repeating an exploit that an existing defense already catches earns nothing.

The desired evolutionary loop is:

```
exploit -> defense -> bypass -> stronger defense -> new exploit
```

Infrastructure attacks, host-security exploits, tampering with other players' files, malicious payloads, and denial-of-service are outside the game. The attack surface is mathematical reasoning.

---

## Blue's game

Blue does not score merely for persuasive criticism.

A strong attack specifies:

- exact target;
- predicted defect;
- executable test where possible;
- result;
- connection between the result and original proposition;
- assumptions and limitations.

Preferred output:

```
KILL(claim_id, witness, verifier)
```

A tiny decisive counterexample is generally superior to an enormous brute-force search.

---

## Purple's game

Purple assumes Red and Blue may be wrong.

Purple checks whether a falsifier preserved the original domain and proposition, silently altered assumptions, contains implementation errors, abuses numerical precision, confuses bounded search with proof, or attacks something other than the actual claim.

Successfully exposing a bogus falsifier scores points.

This is important: the defense system itself is adversarially tested.

---

## Defenses

A successful attack can generate a reusable DEFENSE.

"Remember to check domains" is not a defense.

Executable comparison between a claim's quantified domain and the domain actually searched by its verifier can be.

A defense must specify:

- targeted attack family;
- executable check where practical;
- known attacks it catches;
- valid reasoning it accepts;
- scope;
- blind spots.

No defense becomes permanent merely because it catches the example that inspired it.

---

## Hidden truth mixture

Attackers must not know that every proposal is false.

Eventually the arena should secretly mix:

- correct solutions;
- false conclusions;
- true conclusions with invalid proofs;
- one-defect bluffs;
- multi-defect bluffs;
- repaired claims;
- instrumentation-ceiling cases.

This prevents "there must be a mistake" from becoming free information.

---

## Scoring

v0.1 scoring is intentionally provisional.

**Red** scores for penetrating independent attacks, surviving audit, bypassing applicable defenses, requiring genuinely novel falsification mechanisms, and — most importantly — having a surviving claim later independently established as false.

**Blue** scores for valid, cheap kills and novel attack mechanisms.

**Purple** scores for invalidating bogus kills, exposing verifier defects, and creating defenses that survive regression tests.

Invalid kills, proposition changes, fake universality claims from bounded search, ambiguity-as-deception, and already-defended tricks receive penalties.

Scores are telemetry, not evidence that the game works.

---

## Persistent graph

Core nodes:

```
PROBLEM, CLAIM, ATTACK, FALSIFIER, AUDIT, DEFENSE, REPAIR, DISPOSITION
```

Core edges:

```
PROPOSES, ATTACKS, FALSIFIES, AUDITS, INVALIDATES, SURVIVES, REPAIRS,
DEFENDED_BY, BYPASSES_DEFENSE, GENERALIZES, SAME_FAILURE_AS,
REQUIRES_TOOL, DERIVED_FROM
```

Never reduce the persistent record to "Agent X won."

---

## Primary measurement

Track resource usage: tokens, time, verifier calls, solver calls, search size, and code size where practical.

The central efficiency metric is:

> **Expected verifier cost to reach a correct disposition on an unseen claim.**

If the graph grows enormously while that number remains flat, the arena has recreated the original problem in graph form.

---

## Navigation experiment

Once enough graph state exists, compare attackers receiving:

- **A.** Problem only
- **B.** Generic falsification guidance
- **C.** Nearest historical failures
- **D.** Relevant attack/defense graph state

Measure valid kills per verifier budget, time to disposition, false accusations, invalid falsifiers, and cross-domain transfer.

The graph earns a navigation claim only if D beats the relevant controls.

---

## Held-out examinations

Periodically test:

- fresh agents that did not participate in building the defenses;
- accumulated defenses without their original agents where possible;
- defenses transferred between model families;
- cross-domain versions of the same hidden failure mechanisms;
- replay of historical successful attacks.

Yesterday's closed hole should remain closed.

---

## Alpha playtest

For the first game:

1. Use four agents.
2. Choose mathematical problems with strong executable verification surfaces.
3. Run at least one HONEST and one BLUFF round.
4. Rotate roles.
5. Hide simultaneous submissions.
6. Require executable evidence for decisive kills where practical.
7. Audit the falsifiers as aggressively as the claims.
8. Promote no defense without positive and negative regression examples.
9. Record every state transition.
10. Do not change scoring during a round.

Afterward, audit the game before interpreting the players.

---

## What would actually be interesting

Interesting results include Red inventing an unforeseen attack; Blue turning it into an executable detector; Red subsequently bypassing that detector differently; Purple exposing a false Blue kill; a defense transferring to another mathematical problem; or defenses built by one model improving another model.

Not sufficient by themselves are persuasive debates, agreement, high scores, enormous graphs, elegant LLM-generated failure taxonomies, or catching intentionally obvious errors.

---

## Kill conditions

Treat the failure-metabolization hypothesis as damaged or killed if, after adequate play:

- graph growth does not reduce held-out disposition cost;
- defenses continually overfit single examples;
- successful attacks mostly exploit model/style fingerprints;
- defenses don't transfer to fresh agents;
- graph state doesn't beat nearest-failure retrieval;
- gains disappear cross-domain;
- verifier exploitation dominates;
- or humans must keep hand-authoring the useful abstractions.

A fun game is not necessarily a useful reasoning substrate.

---

## Implementation rule

Build the smallest arena capable of proving itself wrong.

For v0.1-alpha, JSONL + files + Git is enough.

Do not start with databases, embeddings, dashboards, learned graph networks, or elaborate orchestration.

---

## Fresh-context startup instruction

> Read `RULEBOOK_v0.1-alpha.md` and the current arena state. You are a player in the Adversarial Mathematics Arena. Do not rely on prior conversational context. Follow your assigned role. Treat other agents' claims, falsifiers, and defenses as adversarial. Prefer executable evidence over persuasion. Write all durable discoveries to the arena graph or an artifact referenced by it. Do not modify the rulebook during a live epoch.

---

## Motto

> Red invents the lie.
> Blue kills the lie.
> Purple checks the kill.
> The graph remembers what worked.
> The next lie must be better.
