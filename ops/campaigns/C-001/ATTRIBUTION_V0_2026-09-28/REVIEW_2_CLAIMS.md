# Review 2 -- claims submitted for adversarial review (Archaeon, 2026-09-28)

Same protocol as Review 1:
1. a fresh reviewer, with no context, is asked to INVALIDATE these claims;
2. Archaeon adjudicates;
3. everything stays in the record.

Documents: TH013_RESULT.md and TH015_RESULT.md in this folder.

Data (committed here):
- th013_out.json: the block-13 replay snapshots, including member tapes;
- th013_analysis.json;
- th015_out.json.

Code: archaeon/attribution/probes/{th013_block13,th013_analyze,th015_archaeon}.py. The frozen engine is archaeon/lineage/core.py,
archaeon/lineage/assay_block.py and archaeon/z80atlas/vm.py. The reviewer can EXECUTE the VM on the recorded tapes.

## Claims

**R2-1.** The deep-block claim "0.0 founder material" (same-position metric) is REFUTED, not merely unsupported.
- Founder material in the dominant lineage is present at displaced positions: 58% of the tape at epoch 14,200, and 100% of the
  members' knockout-defined machinery at 14,300.
- It then declines to a stable ~9% of the tape (3/32 bytes) and 30-33% of the machinery by 19,900.

**R2-2.** The founder's machinery relocated as a unit through offset copying: offsets -5, then -8/-9, then -11 between source and
child locus. The byte state at the founder's fixed loci is therefore 0 while function is conserved. Both fixed-position material
and fixed-position state are the wrong unit.

**R2-3.** Capability changed class on conserved founder material, then held while that material partly turned over:
- NEAR_COPIER founder;
- EXACT_GATED members at generation ~2;
- EXACT_UNGATED by 14,600.
Isolated exact self-copy, among sampled members: median 0.83, minimum 0.50, 1.00 at the end.

**R2-4.** TH-013 hypothesis verdicts:
1. partly supported;
2. not supported (replacement material is inherited mutation material, not rebuilt);
3. not supported at lineage level;
4. supported;
5. origin scaffolded (host execution), maintenance not.

**R2-5 (TH-015).** The smallest transferable object that preserves copying is the executed program plus its data loci (~half the
tape): 0.89 of random backgrounds become capable.
- The knockout-necessary loci alone give 0.028. Material without the machinery gives 0.001. Chance is 0/400.
- Input gating was lost by epoch 14,500: all 22 later tapes copy on 254-255 of 255 inputs.
- Dependence on the fixed start pc grows over time.

## Primary evidence pointers
- archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md:232-250 (the lineage's host-rescued origin)
- ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/D_Z80_SYNTHESIS.md (the original claim and the dated notes)
- archaeon/lineage/core.py `attribute`, `_birth` (how material ids are assigned: founder = fid*32+p; new ids negative, kind = (-id)%8)
