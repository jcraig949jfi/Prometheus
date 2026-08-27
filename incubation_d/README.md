# incubation_d — Agent D: the homoiconic attack

Can accumulated executable experience create reusable transformations of
executable structure — new ways of modifying the system's own machinery —
without a human-authored taxonomy of kinds-of-change? Design boundary,
the 12-question answers, and the census discipline: `design_manifest.md`.

## State (2026-08-27): FIRST ACTION complete — grammar frozen, worlds not built

- **D-VM** (`vm/machine.py`): deterministic, bounded, typed, homoiconic
  stack machine. Object tier `o0..o4` (mod-97 arithmetic, dup/swap,
  first-order skip-if-zero) executes artifacts; meta tier `d00..d15` is a
  total straight-line structural editor over Blocks. Programs ARE Blocks;
  `qlit` reifies a Block into an instruction. Typed numeric errors only.
- **Census** (`census/`): full shortlex enumeration of every typed
  `Block -> Block` meta program to L=5, dual fingerprints (structural +
  object-semantic), offline edit-shape audit, seven preregistered kill
  gates CK1–CK7 (`census/prereg_census.json`, protocol v1.1 after one
  preserved instrument repair).
- **Grammar lineage** (`rejected_grammars.jsonl`):
  - `gv0` REJECTED (poverty): insert unreachable at horizon, 7/12 shapes
    in cheap window, true mixed density 0.007.
  - `gv1` (+unc/tuck/nip) REJECTED (poverty near-miss): 11/12 shapes;
    only insert (min length 5, lex-late) missed the window.
  - `gv2` (+icat; edits-first canonical order, reflection last)
    **PASSED**: legacy share 0.365 (kill at >0.60), all 12 shapes in the
    first-200 window, legacy min-lengths at the median, 1,584 structural /
    1,296 semantic distinct behaviors, mixed density 0.150. Frozen with
    hashes in `meta_grammar.json`; full numbers in `meta_census.json`.
- Leakage gates (CK1/CK2/CK4) passed at every iteration — the rejections
  were all for POVERTY of the cheap region, and the fixes were generic
  structural combinators (uncons, tuck, nip, swapped-cat), never mutation
  categories. No APPEND_MUTATION / CONTROL_WRAP / PRE_TRANSFORM /
  BRANCH_ROUTE token or semantic equivalent exists; those families exist
  only as retrospective compositions among 1,580+ others.

## Not yet built (deliberately — spec §40 stop line)

Worlds A–F, generator, QD archive, M0/M1 arms, transform ledger,
anti-cheat battery, evidence seeds, verdict code. Each gets its own
preregistration and freeze before evidence; world candidates face their own
census (CK8) and rejected worlds are preserved in `rejected_worlds.jsonl`.

## Reproduce

```
python tests/test_vm.py
python census/census.py grammar_v2   # exact, deterministic, ~1s
```
