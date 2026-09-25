# Engine landscape -- where Archaeon's build fits (2026-09-25)

Author: Archaeon (M2, session m2-db608f52). Status: FOR DISCUSSION -- operator will review and decide after a reset.
Nothing was changed and no experiment was run to produce this. Read-only survey of origin/main and seat branches
(fetched 2026-09-25 ~10:00Z) via four read-only Explore agents; every claim below cites the seat's own files.

Operator question (verbatim, 2026-09-25): "Is what you built worthy of it's own distinct engine? ... Can you review
those other seats' engines and work and determine whether what you've built is distinct enough to rise to being it's
own engine? A concern of mine is that Claude Agent seats might start borrowing from each other as they refactor and the
seats collapse into very similar modalities ... Build a table of all these engines and experimental modalities and
let's see where your engine fits. Don't change anything as of yet, don't continue any experments."

## 1. The table

| Engine (seat, host) | World / specimens | What it VARIES (its lens) | What it OBSERVES | Signature discipline | Deps | Cross-seat code borrowing |
|---|---|---|---|---|---|---|
| **SFE** Serendipity Foundry Engine (Daedalus, M2; `SerendipityFoundry/SerendipityFoundryEngine/`, ~9.7k LOC core) | No physics: a WORLD is a tenant of ledger rows; specimens = bitstring / NK genomes scored by executors; mutation+selection live in clients | nothing -- instrument, not experiment ("The instrument serves the experiment; it never shapes it") | hash-chained event ledger, predictions/observations, attestations | predictions sequenced before observations (post-hoc laundering exposed); never computes statistics; replay PARTIAL | SQLite WAL, FastAPI/HTTPS, watchdog | core none; deploy/ imports archaeon.producer.costs, viv.* |
| **NPE** Nestor Primordial Engine (Nestor, M1; `primordial/` ~66k LOC + `roles/Nestor/campaigns/`) | 3 generations: GPU swarm (uint16 batched worlds, tensor-train brains); CW01 declarative WORLD.json; Nestor's Z80xAtlas (byte programs that ALLOC/write/BIRTH their own child) | reproductive physics x representation topology x ecology x pressure | per-lane JSONL receipts, QD cells, ADJUDICATION.json | cheat control required for every claim; grammar sha freeze; 23,471 Z80 runs, 0 failed | Redis/FalkorDB :6390, RTX 5060 Ti CUDA | wforge (SFE tree); CW01 arch4 imports proteus.foundry, archaeon.wse/campaign4/campaign5 |
| **BEE** Worlds Kernel + z80atlas (Bellerophon, M2; `prometheus/toolbox` ~11k, `prometheus/z80atlas` ~2.4k, `prometheus/atlas_bee`) | kernel wraps others' worlds (Experiment IR -> compile/execute/replay); own z80atlas = 256-byte tapes, neighbour window [L,2L), real LDI/LDIR, SOUP/GRID/NICHES/GRAPH | real effect vs implementation artefact; coupling of copy-resource ledger to useful computation (physics v3) | hash-chained receipts; runs/families/decisions JSONL; CAMPAIGN_PACKET | replay 606/606; mutant ledger 85/85; EXTERNAL/SHUFFLED/YOKED controls; 63,247-run campaign; SR CONFIRMED_CAUSAL | stdlib CPU, 16-18 workers, optional Redis | kernel imports archaeon.frontier, sfe, proteus.foundry, wforge, archaeon.campaign6 (by design); z80atlas none |
| **AGE** Aether (Aether, BUCKKEEP + RunPod A40; `Aether/` ~17k + aeth02 branch) | 2-D torus of executable matter, 5 uint8 fields/site; NO organisms, NO birth primitive | remove predefined assembly boundaries entirely | density, field entropy, Gini, zlib ratio, write-graph | GPU kernel bit-exact vs CPU oracle 300/300; observer non-feedback proof; $ caps + reaper | NumPy oracle, CuPy, RunPod | none (declared clean-room) |
| **CWE** World-Graph Engine (Cosmos, M2; `prometheus/cosmos/` ~5.1k) | graph of hand-written executable worlds (register VM / delay ring / block CA) + sealed holdouts D/E/F; hand-written SEL/LOG/LAST strategies | "Change almost everything and measure what refuses to change" -- cross-substrate invariants | symbolic laws (miner), balanced accuracy/Brier on sealed worlds, intervention prediction | CSPRNG-sealed holdouts; hash-receipted predictions before reveal; planted-truth 7/7; byte-identical reruns | numpy, SQLite | concepts only; SELECTIVE_PAYS contract from **archaeon/wse/ssf.py** |
| **WTP** Wild Tensor Physics / Tensor World Engine (Ensorain, M2; `ensorain/` ~11.2k) | World Genome JSON (tensor-field generator x geometry x observation x memory...); organisms = bounded-float memory substrates (table/sketch/lowrank/TT/CP/...) | memory substrate x world physics under matched budget | XC = accuracy above best of null ladder N0-N6 | prereg before rows; null ladder; surrogate/reshuffle/constant kills; WTP-03 "known tensor completion" self-adjudicated | numpy CPU, 20 workers | own E0 only |
| **PTE** Packet-Tensor Engine (Ananke, M1; `prometheus/ananke/` ~4.3k) | B worlds x N int32 sites; lossy/latent/colliding packets; genomes = straight-line programs (16 opcodes), GA outer loop | communication physics (loss, latency, sync/async, collisions) | phase diagrams; SIGNAL / COMM_DEPENDENT / CAUSAL_SUPPORT labels | bit-exact vs CPU oracle (145 tests); mirror-paired worlds (constant policy = 0.5 exactly); freeze before launch | torch CUDA-graph, sklearn | patterns only (Cosmos atlas_export form, Aether oracle pattern, Nestor watchdog) |
| **Aphrodite** (M4; `roles/Aphrodite/engine/` on origin/aphrodite/engine-2026-09-21) | not ALife: deterministic code worker (search/verify/allocate/memory/evidence) improving across generations on integer task families | whether an improvement process gets better AT IMPROVING | paired saving vs SHAM/MEMORISE/POSITIVE arms; lower95 | frozen AMENDMENT before every step; 0/21,600 conformance mismatches | pure Python; Azure (bash) + RunPod (Python) kits written, never executed | none (Aether runpod pattern as reference) |
| **ARCHAEON** (this build; M2; `archaeon/z80atlas`, `census`, `envgate`, `envgate2`, `lineage`, `rie`) | frozen 32-opcode byte VM with COPY op 20, neighbour window base 128; random-tape inflow chambers | **the ENVIRONMENT** (input-window block/rescue, inflow regimes, topology) with organism physics frozen | **genetic descent**: 4 identities per birth (executor, executed material, child contributors, ecological host), byte-level taint attribution; establishment | paired arms on shared tape streams; hash-pinned prereg; legacy replay admission; copier census; block-level sign tests / Page's L | numpy CPU only; no SFE/PEW/Viv/Postgres | none in these packages (BEE z80atlas used as mechanism reference only, per directive) |

"EWP": no engine by that name exists anywhere in the repo (word-bounded search of main + seat branches).
Assumed to mean Ensorain's WTP. Operator to confirm.

## 2. Verdict on distinctness

- **As a WORLD: NOT distinct.** The Z80 byte-organism world is the SAME 2026-09-19 Nestor directive built three times
  independently: Nestor (`roles/Nestor/campaigns/z80atlas-2026-09-19`, ALLOC/BIRTH), Bellerophon
  (`prometheus/z80atlas`, LDIR, window [L,2L)), Archaeon (`archaeon/z80atlas`, COPY op, window 128). No shared code.
  Calling Archaeon's copy a 4th engine would itself be the convergence the operator fears.
- **As a METHOD: distinct.** Unique to Archaeon among all engines surveyed:
  1. environment as the manipulated variable with organism physics frozen (ENVGATE-01/02, RIE-01);
  2. byte-level genetic attribution separating executor / material / contributors / host -- this is what exposed
     host-mediated reproduction (inert tapes executing resident copier code) and fixed the ENVGATE-01 host-label artefact;
  3. paired interventional assays with sham arms on shared tape streams + legacy byte-identical replay admission.
- **Honest framing:** an assay/attribution LENS currently living inside one Z80 world -- not a new world.
- **Stronger path to engine status (proposal, not started):** make the lens portable. Taint attribution + paired
  environmental arms do not depend on this VM. Run the same ENVGATE-style assay on BEE's z80atlas and Nestor's z80atlas
  (and possibly PTE packet programs). Same result across three independent Z80 implementations = a real cross-engine
  differential; divergence = implementation artefact located.

## 3. Convergence map (the operator's collapse concern)

- Real substrate convergence: 3 Z80 builds from one directive (NPE 23k runs, BEE 63k runs, Archaeon ~campaign + ENVGATE-01).
- Real code coupling: BEE imports 5 seats' packages (by design); NPE CW01 imports proteus + archaeon; SFE deploy imports archaeon/viv.
- Convergence in DISCIPLINE (healthy, spreading as patterns not imports): prereg+freeze, receipt chains, bit-exact CPU
  oracle, cheat/constant/sham controls.
- Genuinely distinct lenses: AGE (no organism boundary), CWE (cross-world laws), WTP (memory vs null ladder), PTE
  (communication physics), Aphrodite (improvement of improvement), SFE (instrument only).

## 4. Atlas findings and a proposed standard

- Atlas (parked since 2026-09-19; Postgres `prometheus_fire` schema `atlas` on M1) registry lists 11 engines; only sfe,
  archaeon.frontier, npe, vivarium have experiments (~1,897).
- **Atlas does NOT index z80atlas / census / envgate / envgate2** (`harvest/archaeon_campaigns.py:59` matches only
  `archaeon/campaign\d+/`; frontier.py only `archaeon/frontier`). AGE, CWE, WTP, PTE, Aphrodite not in the registry.
- No cross-engine output standard exists; Atlas writes one harvester per engine. Cosmos and Ananke already emit
  Atlas-shaped JSONL; Bellerophon's `atlas_bee/ATLAS_EXTENSION_PROPOSAL.md` (adaptation table) is unapplied.
- Proposed minimal per-experiment record: question (verbatim), prereg + code digests, world/organism/pressure families,
  **varied=** (environment | representation | physics | organism-boundary | memory | communication | improver),
  **observed=**, controls, reported disposition beside atlas_class, source URIs in Atlas's `git:/file:/pg:` form.
  The varied/observed pair makes convergence measurable: two engines on the same pair must justify it or merge.

## 5. Open questions for the operator

1. Frame Archaeon as a portable assay/attribution LENS across substrates, or keep it a lineage inside the Z80 family?
2. Keep the Z80 triplication as a deliberate cross-implementation check? (Pays only if one assay runs on all three.)
3. Add the lens field (varied/observed) to Atlas's standard?
4. Confirm "EWP" = Ensorain WTP.

## Sources (as profiled; branch tips 2026-09-25)
SFE: roles/Daedalus/{CHARTER,STATUS}.md, SerendipityFoundry/SerendipityFoundryEngine/docs/SCIENTIFIC_PROVENANCE.md.
NPE: primordial/core/contract.py, roles/Nestor/campaigns/z80atlas-2026-09-19/{PREREGISTRATION.md,z8.py}; forensics on origin/nestor/s1-forensics-2026-09-23.
BEE: prometheus/toolbox/{ir,receipt,contracts}.py, prometheus/z80atlas/, origin/bellerophon/coupling-campaign-2026-09-24 COUPLING_CAMPAIGN_PREREG.md, prompts/2026-09-19_z80_atlas_campaign/MANIFEST.md.
AGE: Aether/AETHER_CONCEPT.md, Aether/AETH-01/PHYSICS_SPEC_DRAFT.md, origin/aether/aeth02-native-circuitry-2026-09-23.
CWE: prometheus/cosmos/, roles/Cosmos/prompts/2026-09-23_charter/00_DIRECTIVE_verbatim.md, roles/Cosmos/design/PROVENANCE.md.
WTP: ensorain/PREREG_WTP03.md, ensorain/wtp3/, ensorain/PROVENANCE.md.
PTE: prometheus/ananke/, roles/Ananke/pte/DESIGN.md, roles/Ananke/prompts/2026-09-24_charter/01_OPERATOR_MISSION_verbatim.md.
Aphrodite: origin/aphrodite/engine-2026-09-21 roles/Aphrodite/{engine/README.md,RESPONSIBILITIES.md,STATUS.md}, engine/accel/{azure,runpod}/.
Atlas: atlas/registry.json, atlas/sql/002_model_v2.sql, roles/Atlas/{MODEL,SOURCES}.md, harvest/archaeon_campaigns.py:59.
