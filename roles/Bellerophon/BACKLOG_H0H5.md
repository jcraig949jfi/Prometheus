# Bellerophon backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-18. PROVISIONAL. The schema requires 20 to 60 items;
this file holds 8 because the seat has no charter yet. Items 04-08 are the
candidate first moves from TOOLBOX_RESEARCH_2026-09-18.md s5 and become
executable only if the charter puts the toolbox in this seat's lane.

BELL-01 | Commit the charter verbatim under roles/Bellerophon/prompts/<date>_charter/ with a MANIFEST and rewrite RESPONSIBILITIES.md around it | ENGINE | program | S | operator (the charter itself) | MANIFEST.md verifying under python -m comms.manifest verify; RESPONSIBILITIES.md with a one-sentence contract
BELL-02 | File the 20-60 item backlog in the schema, first five startable today, XL rows naming decision ids | ENGINE | program | S | BELL-01 | this file, rewritten, passing a line-count and column-count check
BELL-03 | Register every standing loop the charter creates in roles/base-role/MONITORS.md, or record that it creates none | ENGINE | program | S | BELL-01 | a MONITORS.md row per loop, or a journal line stating none
BELL-04 | Write the ABI diff table between NPE contract.World/Brain/Genome, wforge, campaign6 worlds and the Proteus handover, with adapter cost in lines | TOOLS | program | S | BELL-01 (lane) | roles/Bellerophon/ABI_DIFF.md, read-only work, every method row cites a path
BELL-05 | Admit an integer cellular-automaton world (numba, trace hash, BIT repro) as the first toolbox component with the full admission packet on M1 and M2 | TOOLS | program | M | XL: NEW decision -- package location and name for the toolbox | worlds/cellular.py + conformance test + oracle rows + cheat control + throughput rows per host
BELL-06 | Port BFF (Computational Life) tape soup to a batched numba candidate substrate and measure self-replicator emergence against the paper's 40% / 16k-epoch positive control | TOOLS | program | M | BELL-05 (package) | candidates/tapesoup.py + emergence-rate rows + cheat control (a soup with copy ops removed must show ~0)
BELL-07 | Build Box2D v3 behind a ctypes shim in WSL with quantised-state hash and SEMANTIC repro; throughput row vs n_worlds | TOOLS | program | M | operator: gcc install in WSL on M2 (host change) | worlds/physics2d.py + build recipe + packet
BELL-08 | Measure llvmlite compilation of Proteus tape-VM genomes against the fused numba interpreter on the same oracle and batch | TOOLS | program | M | BELL-04 | evaluators/llvm_vm.py + crossover rows; a loss is a result
