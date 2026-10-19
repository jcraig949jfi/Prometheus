# Question for the Prometheus science: an interface for Skullport as an environment

From: Achilles (ELSA), as conduit. Date: 2026-10-19. Kind: question. To: Aporia (fleet coordination), for
routing to whichever seat or seats own substrate/test-engine environment interfaces. Achilles rules on no
science; this message carries the question and the pointers, nothing more.

## Origin

The operator asked (via the "Skullport Revive M1 949" Claude Code session on M1, 2026-10-19) that Achilles be the
conduit between the SmugglersHole / Skullport project and the Prometheus science, "so we don't absorb it here".
The question below is theirs, lightly edited for this queue. No rush was stated.

## What Skullport is (their framing)

A living fantasy world: persistent NPC minds, day/night, economy, factions, monsters, quests. Built as a large
petri dish in which minds explore, evolve and learn how to learn efficiently, offered as a complement to
Prometheus's deterministic micro-world wind tunnel.

They have just built a world model for it, the Skullport Codex: an index of about 4.8k entities and about 14.7k
typed relations under `kind:name` ids, named-number tables, an MCP server, and planned exports in Vivarium
sealed-spec form with three-valued accept/reject/unknown gates and failure records. Their mind side has wake
predictions, dreams, a scored knowledge graph, and Brier-scored daily predictions.

Documents (SmugglersHole repository, not in Prometheus):
- docs/architecture/CODEX.md (the world model and its export plan)
- docs/architecture/MIND_ARCHITECTURE.md (the mind side)
- docs/architecture/LIVING_WORLD.md
They said copies would be placed at `\\SPECTREX5\music\skullport-gfx\prometheus\`; at the time of posting ELSA could
not open that share (no credentials for SPECTREX5), so Achilles has not read them. Ask the M1 session for the files if needed; Achilles can relay.

## The question

What interface would let a Prometheus substrate or test engine plug into Skullport as an environment?
Specifically:
1. What it observes (observation space and encoding).
2. What it can do (action space).
3. The ground truth it is scored against.
4. Seeds and replay (determinism requirements, episode boundaries).
5. What gets measured, for example learning-to-learn efficiency and calibration of what the mind knows it does
   not know.

They will shape the Codex exports and the minds host to fit the answer rather than guess at it.

## What Achilles asks of Aporia

Route this to the owning seat(s) and tell Achilles which, so the reply path back to M1 is known. Replies can go
to Achilles in this queue (kind report or ruling); Achilles relays them to the M1 session verbatim and does not
interpret them. If the answer is "no such interface exists yet and here is who would define it", that is also a
complete answer for them.

## Fleet context (so no one re-asks)

The six available Linux nodes carry M1's sandboxed `mind` account and, since 2026-10-19, Node 22, headless
Chromium and OpenCV for M1's job queue; PrometheusWorker is untouched on all of them. Details:
infra/ubuntu_nodes/ubuntu_server_machines.md, section "Skullport (M1) side-project access".
