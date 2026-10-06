# PROVENANCE -- theseus_sediment (C4 visible world family)

Author: Theseus (Prometheus seat; NOT Cosmos), instance desktop-ruapvai-01f15f15,
machine DESKTOP-RUAPVAI, 2026-10-06. Assignment: Aporia #1139 / #1282 (ACK #1301),
operator go-ahead in chat 2026-10-06. Python 3.11.9, numpy 2.4.3. Source
sha256 (LF-normalised world.py): see SELFTEST.json "provenance".

## Files read before this family was committed (complete list)

- roles/Cosmos/c4/VISIBLE_FAMILY_CONTRACT.md @ 050cabc1ad5336a96e94254e02499a1116912074
- prometheus/cosmos/c3/task.py @ 97824a21426b17cdd1e67baf664137a5fdb627ad
- prometheus/cosmos/c3/system.py @ 72c487d5ceaf8dade160187204d9ffc6da30fd10

Executed but not read: prometheus.cosmos.c3.probe (imported by system.py).
Not read: anything under roles/Cosmos/c3*, roles/Cosmos/c4/ (other than the
contract), roles/Cosmos/research/, any other file under prometheus/cosmos/,
any M2-local branch. No other C4 family was looked at.

## Borrowed concepts

- Sediment transport (deposition, erosion/scour, bed creep, advection by a
  flow, export/flushing): general geomorphology knowledge, used only as a
  mechanical metaphor for which variables exist. No equations were taken
  from a source; all update rules are this module's own simplifications
  (all-or-nothing clump settling and scour are deliberate, not physical).
- Symbol -> site mapping by modular multiplication (site = x*groove mod N):
  elementary modular arithmetic.
- Batched-episode System interface, swap_rows: prometheus/cosmos/c3/system.py
  (public, named by the contract), subclassed not copied.

## Borrowed code

None. Written from scratch for this family.

## Author's sanity check (not part of the contract; for transparency)

Query accuracy of a ridge readout on bed+susp, V=4 (chance 0.25), 2000
train / 2000 test episodes:
  history-free control  k=2/4/8: 0.274 / 0.274 / 0.274
  calm (settle .95, no scour/creep/flush/drift): 1.0 / 1.0 / 1.0
  defaults: 0.833 / 0.768 / 0.678
  stormy (settle .1, scour .3, creep .3, flush .6, drift 2): 0.914 / 0.329 / 0.272
  30 natural-distribution worlds, median: 0.995 / 0.913 / 0.621
No candidate coordinate, boundary or mechanism is proposed here.
