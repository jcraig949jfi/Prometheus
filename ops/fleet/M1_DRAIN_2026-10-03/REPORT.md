# M1 drain report: M1-DRAIN-2026-10-03 (evolving)

Maintained by Aporia. This is the single operator-facing report for the drain (directive s15).

- Order: ORDER.md
- Intake: P2B_INTAKE.md
- Re-entry manifest: P2B_REENTRY_MANIFEST.jsonl (70 seats)
- Ledger: LEDGER.json (pending)

## Status: 2026-10-03 11:55Z (DRAINING; not yet quiescent)

### Live M1 sessions

| Seat | Drain | Receipt |
|---|---|---|
| Hecate | receipt sent | #1300 |
| Tityos | receipt sent | #1303 |
| Ixion | receipt sent | #1307 |
| Nestor, Ananke, Atlas, Sisyphus, Tantalus | ordered (#1291-#1298) | pending |
| Aporia | drains last | n/a |
| Cadmus (EP-PHASE3 RSO builder) | EXCLUDED, binding amendment | n/a |
| Dionysus (Phase 3 reviewer) | EXEMPT for now, operator ruling | n/a |

### Machine-global services left running (intentional)

- Postgres 17: comms, fabric, evidence_wiki, atlas, viv, ludus_atlas.
- FoundryAPI scheduled task.
- Achilles census producers.

### Theseus

ACKed C4 at 11:42Z (#1301). The C4 chain is live, so no HOLD_REHOME.

## Phase 2-B re-entry manifest summary

| Classification | Count | Seats |
|---|---|---|
| P2B_RESTART | 19 | Aether, Ananke, Aphrodite, Archaeon, Bellerophon, Cosmos, Ensorain, Harmonia, Hecate, Ludus, Nemesis, Nestor, Nyx, Polyhymnia, Proteus, Rhadamanthus, Techne, Theseus, Tyche |
| P2B_SUPPORT_ON_DEMAND | 7 | Achilles, Aporia, Artemis, Cyclops, Hermes, Odysseus, Vivarium |
| NEEDS_OPERATOR_RULING | 24 | Agora, Arachne, Ares, Atlas, Charon, Clymene, Daedalus, Elenchus, Eos, Ergon, Hephaestus, Herakles, Hypatia, Icarus, Kairos, Koios, Lexis, Metis, Mnemosyne, Nous, Pheme, Pronoia, Talos, Theophrastus |
| PARKED | 6 | Alethelia, Apollo, Atlas-M2, Coeus, Diomedes, Skopos |
| RETIRED | 2 | Atalanta, Crius |
| PHASE3 (out of scope) | 12 | Argus, Cadmus, Dionysus, Enceladus, Epimetheus, Eupalamus, Ixion, Palamedes, Pallas, Sisyphus, Tantalus, Tityos |

Rows were compiled by two read-only readers from the Achilles census, the Phase 3 intake dossiers, seat files and
P2B_INTAKE. They are not verified line by line. Fields marked UNKNOWN are honest gaps.

### Restart order that avoids starting seats blocked

1. **Harmonia first.**
   - It is the ruling bottleneck: Hecate C1-C8, ASAL I1-I5, the D2 and E-003 inputs, and the Dionysus custody incident.
   - Its first campaign fixes its own anti-conservative t_crit, because that may change earlier rulings.
2. **Archaeon early.** It owns comms, the three GLOBAL defects, and the unmerged keepalive fix 2c8c81bbb.
3. **Theseus continues.** Its C4 family gates Cosmos, which gates the Ananke and Bellerophon finals.
4. **Everyone else** restarts in any order.

## Proposed placement matrix (for the operator; nothing assigned)

Principle (directive s11): no seat owns a machine because it historically lived there. A seat is placed only for
locality, GPU, or independence reasons, and those are stated.

| Seat | Suggested host | Reason |
|---|---|---|
| Cosmos | M2 SPECTREX5 | Withheld C3 branches exist only in M2's object store and must not move |
| Ensorain | M2 | Outputs are bitwise platform-bound to M2 |
| Bellerophon | M2 | Host-local multiday results; Windows Python 3.14 |
| Tyche | M2 | Needs many cores (28 logical); only M2 has them |
| Rhadamanthus | M2 | Light; its H-B work needs M2-local dead ledgers |
| Ananke | M1 SKULLPORT | Needs a GPU (torch CUDA graphs); M1 has the less-loaded RTX 5060 Ti |
| Nestor | M1 | Off-repo store C:/Users/jcrai/lab/pm-data is on M1; cpu8 (lease shared with Ananke, so stagger) |
| Archaeon | M1 | RAM-bound jobs, and M2's 32 GB is already contended |
| Techne | M3 GANDALF | Fossil bodies are on M3 local storage (no move until TECHNE-65/100) |
| Nyx | M3 | Live there; outside the drain |
| Aphrodite | M4 harry1 | Stdlib CPU, deterministic; stays |
| Harmonia | M4 harry1 | Light scipy; keeps the auditor off the authors' heavy hosts. First export the 09-10 SQLite corpus from M1 |
| Aether | BUCKKEEP | RunPod key and artifacts are tied to BUCKKEEP |
| Hecate | BUCKKEEP | Light CPU plus API keys; nothing pinned to M1 once pushed |
| Nemesis | BUCKKEEP | Light pure Python; separate from its targets' authors |
| Theseus | DESKTOP-RUAPVAI | MUST stay off M2 (C4 authorship independence) |
| Polyhymnia | DESKTOP-RUAPVAI | Seconds of CPU; could instead become a worker task |
| Ludus | ubu003, or DESKTOP-RUAPVAI if ubu003's Claude login is still pending | Any OS, light; reads ludus_atlas on M1 Postgres |
| Proteus | ubu003, or M1 | OS-neutral pure Python; coordinate VM edits with Archaeon (runtime hash) |
| Support on demand (Achilles, Odysseus, Artemis, Cyclops, Hermes, Vivarium) | stay where they are | Achilles ELSA, Odysseus ubu001, Artemis ubu002; the others are not seated unless called |

### Load notes

- **M2 RAM (32 GB) is the binding constraint.** Cosmos, Ensorain, Tyche and Bellerophon have each hit memory reaps.
  Stagger their heavy runs under Fabric leases.
- **M1 ends with Ananke, Nestor and Archaeon**, plus the exempt Cadmus and Dionysus and the fleet Postgres. That makes it
  one member of the fleet, not the home of old science.

### Before any seat leaves M1, its M1-resident data needs custody

- Ananke c1/c1b rows.
- Nestor pm-data.
- Harmonia's 09-10 SQLite corpus.
- Ergon probe ledgers.
- Daedalus SFE archive ledger eng_8a37a5d3.
- The charon_duckdb / prometheus_sci / LMFDB mirror (these stay with Postgres on M1).

## Operator rulings this surfaced (not urgent; listed once)

- **24 NEEDS_OPERATOR_RULING seats.** Most records recommend RETIRE or PARK; see the manifest rows. Rulings that unblock
  others:
  - **Mnemosyne:** the PEW service has been down since 09-23 and blocks Kairos, Koios, Vivarium, Theophrastus,
    Rhadamanthus' Keeper lane and Atlas' index.
  - **Daedalus:** SFE custody.
  - **Atlas:** unpark for one re-harvest.
- **Data defect:** roles/Argus/WORK_STATE.json is invalid JSON (Phase 3 seat; reported, not touched).

## Branch dispositions, merges, archive refs

Pending: the ledger run, then the seats' receipts.
