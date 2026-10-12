# Fabric backlog (after the v0.2 freeze)

Proposals only; nothing here is built during the adoption experiment.

- Thread->Task bridge (comms delegation with a fabric block -> Task; terminal state -> comms reply)
- Remote drain/stop of a node worker (the ubu002 v0.1 worker could not be stopped from ubu001)
- Claude-executor availability probe (token present, CLI version) as a capability
- Windows node worker
- ~~Remove legacy ARC3 lease detection once old helper copies are merged away~~ DONE 2026-09-30 (CWO; FREEZE.md log)
- Pan retrieval as declared node capabilities `pan.search` / `pan.pivot` (proposal by Pan, 2026-10-11; roles/Pan/docs/sagacity/PAN46_CACHE_AND_FABRIC_DESIGN.md): served by the EXISTING script executor (module `pan`, `--json` output), no fabric code change; needs Pan's Python dependencies on the node and reaches vectors through M1 pgvector; the agent card would list the capabilities automatically once a node declares them. A node operator's decision, not Pan's.
