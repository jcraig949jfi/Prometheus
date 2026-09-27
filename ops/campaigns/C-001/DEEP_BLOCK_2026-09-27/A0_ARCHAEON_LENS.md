# Archaeon Z80 lens (the SFE-era z80atlas -> ENVGATE -> lineage line) -- reconstruction by Archaeon (first-hand; cited)

Labels: NATIVE = the code/records say it; DERIVED = computed from preserved records; INFERRED = reading.

## WORLD
- Frozen 32-opcode byte VM, 32-byte tapes (archaeon/z80atlas/vm.py; grammar.py FROZEN). NATIVE
- A 256-byte address space: the executor's tape plus a 32-byte neighbour window (the region at pc >= G; vm.py:45-46 exec_foreign). NATIVE
- Ecology of N = 128 cells plus K inflow chambers fed with random tapes (archaeon/lineage/core.py World; grammar.py:36-41). NATIVE
- Each epoch, every occupied cell executes once per input case against one neighbour (core.py step). NATIVE
- Death at max_age 60 or death_rate 0.01; background mutation 0.02 (grammar.py:36). NATIVE
- No energy economy in the ENVGATE configuration; inputs are the only environment variable manipulated. NATIVE

## ENTITY
- The occupant of a cell (tape + oid). Two lineage notions exist side by side (core.py docstring), both NATIVE:
  * parent chain: the child's label = the EXECUTOR's;
  * genetic lineage (glin): continues the template that supplied >= G/2 copied bytes, otherwise a new glin is ORIGINATED.

## REPRODUCTION
- A "birth" is any execution that writes >= copy_min_frac = 0.9 of the neighbour window (core.py step; grammar.py:36). The child
  (with copy noise 0.004) replaces the neighbour occupant. NATIVE
- A birth is NOT necessarily self-copying. Mechanism labels: SELF_COPY / HOST_EXECUTION / NEIGHBOUR_COPY / ORIGINATION (+RECOMBINATION)
  (core.py _birth). NATIVE

## HEREDITY
- Byte material with per-byte material ids (founder fid*32+pos, or new: mutation / input / constant / computed) (core.py). NATIVE
- The executor's own bytes (E) and the occupant's bytes (N) can both enter a child; computed bytes carry contributor sets. NATIVE

## OBSERVABILITY
- Four identities per birth (executor, executed material, contributors, host), NATIVE.
- The taint VM labels every byte and every fetch by material. It is asserted identical to the frozen VM per birth
  (core.py _labels; tests). NATIVE
- Execution location (exec_foreign) and execution material (fetch labels) are both recorded (taint_vm.py:44-54). NATIVE
- Establishment is measured on glins (core.py genetic_establishments). NATIVE
- What remains INFERRED: mechanism of a whole ecology (from per-birth labels); the per-write governing code in 'mixed' executions
  (not recorded per write; E-001 T-005).

## RULER
- Copier census ruler (archaeon/envgate/ruler.py measure; census/): classes such as EXACT_UNGATED / NEAR_COPIER / gated at input bytes,
  from an isolated tape x input sweep. NATIVE
- Endpoint: GENETIC establishment = a glin of random origin, alive 3 x max_age after its root is gone, with peak >= 0.25N or genetic
  depth >= 10 (envgate2/analyze.py docstring). NATIVE
- Paired environmental arms on shared tape streams, frozen preregistrations. NATIVE

## STRONGEST FINDINGS (survived later attack)
1. **Environmental blocking.** Blocking inputs 120..135 suppresses establishment. Replicated across ENVGATE-01 and ENVGATE-02; under
   genetic identity U 24 vs BAND0 5, 12+/2- blocks (envgate2/VERDICT_2026-09-26.md).
2. **Host-mediated reproduction.** An inert host executes a resident copier and emits the resident genome (ENVGATE-01 R2).
   - It survived the material-level check: 2,570 of 3,594 block-15 resident-emitting births run RESIDENT material in place.
   - A second route: 1,024 run HOST material relocated into the neighbour region (E-001 T-004).
3. **Copier incidence is lottery-consistent** (lambda 6.86 vs 1 survivor) and **input-gating is the norm** (postcampaign rulings R2).
4. **No detectable de novo replication in DENOVO-01** (0/80; controls 21/21).

## REINTERPRETATIONS
- **Parent-chain "lineages" were executor labels.** Genetic lineage deflates establishment counts 8-42x (ENVGATE-02), and block 15's
  23 host labels are 1 genetic lineage (FF-1).
- **The Z80xAtlas "spontaneous replication" flags were seeded transplant runs** (postcampaign audit).
- **The ENVGATE-01 rescue claim (C4) was downgraded** to GATING_PARTIALLY_SUPPORTED.
- **The viable-window mechanism failed in ENVGATE-02.**
- **Host-mediated reproduction was refined** into two routes by the code-material check.

## ATTENTION
- **Host dependence:** NATIVE and measured (HOSTING events; 82 cross-lineage + 277 same-lineage hosted births into the block-13
  dominant).
- **Self vs foreign material:** NATIVE (E/N labels).
- **Acquisition vs maintenance:** separated by design. First birth and establishment are different endpoints; ENVGATE manipulated
  the environment and measured MAINTENANCE (establishment), not first acquisition.
- **Code execution vs material inheritance:** NATIVE split (fetch labels vs byte material).
- **Reproductive architecture:** short input-gated copy loops (census).
- **Endogenous vs external:** material SUPPLY is external (random inflow); copying is endogenous. Nothing external copies (EXTERNAL
  reproduction is not used in these worlds).
