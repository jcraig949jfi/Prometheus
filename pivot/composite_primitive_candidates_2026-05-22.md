# Composite Primitive Candidates — 2026-05-22

Symbol-pair co-occurrences mined from recent Theseus corpus. Pairs that co-appear in many records signal a relationship the substrate is implicitly testing — candidates for composite primitives `(Sym_A ∘ Sym_B)` that codify the relationship.

- batches scanned: **5**
- records scanned: **500,000**
- pairs above threshold (≥5): **24**

## Top 24 candidate pairs

| count | sym_a | sym_b | info_density_mean | verdict_breakdown |
|---|---|---|---|---|
| 15000 | `ec.rank` | `knot.crossing_number` | - | REJECTED:5184, SHADOW_CATALOG:9816 |
| 14998 | `ec.conductor` | `knot.determinant` | - | REJECTED:6338, SHADOW_CATALOG:8660 |
| 14997 | `ec.rank` | `knot.trace_field_class` | - | REJECTED:4891, SHADOW_CATALOG:10106 |
| 14816 | `ec.rank` | `knot.determinant` | - | REJECTED:5298, SHADOW_CATALOG:9518 |
| 14814 | `ec.torsion` | `knot.determinant` | - | REJECTED:6155, SHADOW_CATALOG:8659 |
| 14793 | `ec.torsion` | `knot.trace_field_class` | - | REJECTED:5954, SHADOW_CATALOG:8839 |
| 14780 | `ec.conductor` | `knot.crossing_number` | - | REJECTED:5484, SHADOW_CATALOG:9296 |
| 14751 | `ec.torsion` | `knot.crossing_number` | - | REJECTED:5975, SHADOW_CATALOG:8776 |
| 14730 | `ec.torsion` | `knot.signature` | - | REJECTED:5495, SHADOW_CATALOG:9235 |
| 14710 | `ec.rank` | `knot.signature` | - | REJECTED:4175, SHADOW_CATALOG:10535 |
| 14694 | `ec.tamagawa_product` | `knot.signature` | - | REJECTED:4804, SHADOW_CATALOG:9890 |
| 14674 | `ec.tamagawa_product` | `knot.three_genus` | - | REJECTED:4996, SHADOW_CATALOG:9678 |
| 14671 | `ec.conductor` | `knot.trace_field_class` | - | REJECTED:4967, SHADOW_CATALOG:9704 |
| 14627 | `ec.conductor` | `knot.signature` | - | REJECTED:4873, SHADOW_CATALOG:9754 |
| 14586 | `ec.tamagawa_product` | `knot.determinant` | - | REJECTED:6479, SHADOW_CATALOG:8107 |
| 14536 | `ec.tamagawa_product` | `knot.crossing_number` | - | REJECTED:5543, SHADOW_CATALOG:8993 |
| 14497 | `ec.rank` | `knot.three_genus` | - | REJECTED:4089, SHADOW_CATALOG:10408 |
| 14463 | `ec.conductor` | `knot.three_genus` | - | REJECTED:4683, SHADOW_CATALOG:9780 |
| 14458 | `ec.torsion` | `knot.three_genus` | - | REJECTED:4522, SHADOW_CATALOG:9936 |
| 14436 | `ec.tamagawa_product` | `knot.trace_field_class` | - | REJECTED:5258, SHADOW_CATALOG:9178 |
| 4392 | `ec.conductor` | `knot.nf_class_number` | - | REJECTED:2152, SHADOW_CATALOG:2240 |
| 4379 | `ec.torsion` | `knot.nf_class_number` | - | REJECTED:1023, SHADOW_CATALOG:3356 |
| 4346 | `ec.tamagawa_product` | `knot.nf_class_number` | - | REJECTED:1908, SHADOW_CATALOG:2438 |
| 4212 | `ec.rank` | `knot.nf_class_number` | - | REJECTED:1035, SHADOW_CATALOG:3177 |

## How to read this

Each row is a (Sym_A, Sym_B) pair where Sym = `catalog.invariant`. The substrate emitted `count` records claiming a relation between those two symbols. High kill counts mean the relation usually fails (substrate doesn't believe in this specific bridge); high SHADOW_CATALOG counts mean it usually holds (candidate bridge-of-truth).

Composite-primitive candidates: pairs with **mixed verdicts** (both kills and confirmations in non-trivial numbers) are the most informative — they reflect a relation that's true SOMETIMES, which means there's an unknown subset structure worth naming as a new primitive.