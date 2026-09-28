# TH-013 result -- block 13: function vs material through time (Archaeon, 2026-09-28)

Thread: ops/threads/TH-013.md (thr-675074a6b777). Directive 2026-09-28 item 4.

## Run
- **Replay:** one deterministic replay of ENVGATE-01 block 13, BLOCK_128 arm (frozen engine; a World subclass only observes), to
  epoch 20,000.
  * Where: ubu002, commit b2779a772.
  * Wall time: 4,429 s. Births: 655,307.
  * Output: C:/Prometheus-data/evidence/attribution_v0_2026-09-28/th013_out.json (sha256 dbc692128cf2...).
- **Tracked lineage:** glin 1071 (arrival 447,492; founder tape 22592835...863e; first birth epoch 13,955, SELF_COPY).
- **Snapshots:** every 100 epochs, the first 12 living members (by cell index).
- **Per member:**
  * per-locus material: founder material at ANY locus, with its source locus;
  * byte state;
  * copy capability in isolation (zero neighbour, the arm's 255 allowed inputs);
  * the frozen copier ruler class.
- **Analysis:** archaeon/attribution/probes/th013_analyze.py. Machinery is found by full 32-locus knockout on 1-2 members per
  snapshot. The probe's own knockout scanned executed opcode loci only (F4) and is not used.
- **Founder machinery (full knockout):** {3,4,5,6,7,12}. Locus 7 is an operand.

## The diagram: material ancestry -> machinery state -> execution -> reproductive capability, through time

    material ancestry      founder bytes at {3..7,12}
    (IBD, per locus)          | offset copying: each early copy shifts them +3..+5 loci
                              v
                           founder bytes now at {14..18,..} (offset -9..-11), 100% of the members' machinery at epoch 14,300
                              | exact copying; background mutation replaces machinery bytes, and the replacements are then
                              | copied (IBD to RECENT ancestors, not to the founder)
                              v
                           founder share of the members' machinery 1.00 (14,300) -> 0.60 (16,000) -> 0.30-0.33 (19,900)
                           founder share of the whole tape 0.90 -> 0.09 (a stable 3 of 32 bytes from 17,500)

    machinery state        the byte STATE at the founder's loci {3..7,12}: 0.56 -> 0.00 from 14,200 (the machinery MOVED)
    (IBS)                  the machinery relocated as a unit: {2..7,12} -> {5..10,15..17} -> {12..16} -> {15..18} (+0, +4/+8)

    execution              the knockout-defined machinery shrinks: 7 loci (founder) -> 10-12 loci (14,600-16,000) -> 5-7 loci
                           ({0,15,16,17,18} and variants; 17,000-19,900)

    capability (executed,  NEAR_COPIER (founder, no exact self-copy) -> EXACT_GATED (5/9 members at gen ~2) -> EXACT_UNGATED
    isolated)              (11/12 by 14,600; 12/12 at 17,500-19,900). Isolated exact self-copy: 0.56 (14,000) -> 0.83 median
                           -> 1.00 at the end

| epoch | lineage cells | mean generation | founder material, any locus | founder material at founder machinery loci {3-7,12} | byte state = founder at {3-7,12} | members' own machinery (full knockout, 1-2 members) | founder material in members' machinery | dominant offset (source - locus) | isolated exact self-copy | ruler classes |
|---|---|---|---|---|---|---|---|---|---|---|
| 14000 | 9 | 2 | 0.90 | 0.98 | 0.56 | {2,3,4,5,6,7,12}; {2,3,4,5,6,7,12} | 1.00, 1.00 | 0 | 0.56 (n=9) | EXACT_GATED 5, INERT 3, NEAR_COPIER 1 |
| 14100 | 60 | 9 | 0.72 | 0.43 | 0.07 | {5,6,7,8,9,10,15,16,17}; {9,10,11,12,13,14,19,20,21} | 0.89, 0.89 | -5 | 0.58 (n=12) | EXACT_GATED 7, INERT 2, NEAR_COPIER 2, TOUCH 1 |
| 14200 | 25 | 13 | 0.58 | 0.18 | 0.00 | {12,13,14,15,16,17,22,23,24,27}; {10,11,12,13,14,15,20,21,22,25} | 0.90, 0.90 | -8 | 0.67 (n=12) | EXACT_GATED 8, INERT 3, NEAR_COPIER 1 |
| 14300 | 65 | 18 | 0.48 | 0.10 | 0.00 | {12,13,14,15,16}; {12,13,14,15,16,31} | 1.00, 1.00 | -9 | 0.75 (n=12) | EXACT_GATED 9, NEAR_COPIER 2, TOUCH 1 |
| 14600 | 124 | 276 | 0.36 | 0.17 | 0.00 | {13,14,15,16,18,19,21,25,27,28,31}; {6,13,14,15,16,17,18,19,21,25,27,31} | 0.64, 0.58 | -9 | 0.92 (n=12) | EXACT_UNGATED 11, TOUCH 1 |
| 15000 | 123 | 594 | 0.26 | 0.17 | 0.00 | {0,11,13,14,15,16,17,18,31}; {3,6,7,11,13,14,15,16,17,18,28,29} | 0.67, 0.58 | -9 | 0.92 (n=12) | EXACT_UNGATED 8, EXACT_GATED 3, INERT 1 |
| 15500 | 124 | 1012 | 0.22 | 0.17 | 0.00 | {2,6,11,13,14,15,16,17,18,31}; {2,6,11,13,14,15,16,17,18,31} | 0.60, 0.60 | -9 | 0.83 (n=12) | EXACT_UNGATED 10, INERT 1, TOUCH 1 |
| 16000 | 125 | 1442 | 0.22 | 0.01 | 0.00 | {4,6,8,13,15,16,17,18,19,20}; {4,6,8,13,15,16,17,18,19,20} | 0.60, 0.60 | -11 | 0.92 (n=12) | EXACT_UNGATED 11, INERT 1 |
| 16500 | 125 | 1917 | 0.21 | 0.00 | 0.00 | {4,8,15,16,17,18,19,20,24} | 0.56 | -11 | 0.75 (n=12) | EXACT_UNGATED 8, INERT 2, TOUCH 1, EXACT_GATED 1 |
| 17000 | 124 | 2347 | 0.12 | 0.00 | 0.00 | {15,16,17,18}; {0,15,16,17,18} | 0.75, 0.60 | -11 | 0.83 (n=12) | EXACT_UNGATED 10, INERT 2 |
| 17500 | 124 | 2810 | 0.09 | 0.00 | 0.00 | {0,4,15,16,17,18}; {0,15,16,17,18} | 0.50, 0.60 | -11 | 1.00 (n=12) | EXACT_UNGATED 12 |
| 18000 | 126 | 3306 | 0.09 | 0.00 | 0.00 | {0,15,16,17,18}; {0,15,16,17,18} | 0.60, 0.60 | -11 | 1.00 (n=12) | EXACT_UNGATED 12 |
| 18500 | 125 | 3796 | 0.09 | 0.00 | 0.00 | {0,13,15,16,17,18}; {0,4,13,15,16,17,18} | 0.50, 0.43 | -11 | 0.92 (n=12) | EXACT_UNGATED 11, INERT 1 |
| 19000 | 127 | 4285 | 0.09 | 0.00 | 0.00 | {0,9,13,15,16,17,18} | 0.43 | -11 | 0.67 (n=12) | EXACT_UNGATED 8, INERT 4 |
| 19500 | 126 | 4717 | 0.09 | 0.00 | 0.00 | {3,13,16,17,18}; {3,13,16,17,18} | 0.40, 0.40 | -11 | 1.00 (n=12) | EXACT_UNGATED 12 |
| 19900 | 128 | 5102 | 0.09 | 0.00 | 0.00 | {0,1,3,9,13,15,16,17,18}; {0,1,3,6,9,13,15,16,17,18} | 0.33, 0.30 | -11 | 1.00 (n=12) | EXACT_UNGATED 12 |

The earliest rows show the relocation directly. At mean generation 2 the machinery sits at the founder's loci. By generation 9 it
has moved by +3 to +7, and by generation 13 by +8 to +10. The copies carry founder material at displaced positions (offset -5,
then -8/-9, then -11).

## The five hypotheses

| # | hypothesis | verdict | evidence |
|---|---|---|---|
| 1 | functional continuity despite material turnover | **PARTLY SUPPORTED, and "continuity" undersells it** | The capability did not merely persist: it IMPROVED (near-copier -> exact gated -> exact ungated), first on founder material (100% of the machinery at 14,300). Afterwards the founder share of the machinery falls to 0.30-0.33 while isolated exact copying stays 0.83-1.00. Turnover of machinery material is PARTIAL and gradual, not complete |
| 2 | machinery continually reconstructed from descendants | **NOT SUPPORTED** | Replacement material is overwhelmingly `mutation` kind (345 of 348 non-founder loci at 19,700), inherited by copying. World-wide, births are 98.7% SELF_COPY (646,622 / 655,307). Nothing is rebuilt per generation; machinery bytes descend from RECENT ancestors (the fixture case "machinery without founder bytes", heading that way) |
| 3 | copying ability repeatedly reacquired | **NOT SUPPORTED at lineage level; untested per member** | In all 60 snapshots, >= 50% of sampled members copy exactly in isolation (median 0.83). A member-level loss-and-regain cycle cannot be excluded: members are not followed individually |
| 4 | the ruler tracks the wrong material unit | **SUPPORTED (this is what made the deep-block 0.0)** | Same-position founder material is 0.00 from 14,200, while founder material is present at offsets -8..-11: 58% of the tape at 14,200, 100% of the members' machinery at 14,300. The byte STATE at fixed loci is also the wrong unit: IBS at the founder's machinery loci is 0.00 while the relocated machinery conserves the function. The machinery is position-relative |
| 5 | environmental / scaffold continuity | **ORIGIN yes, MAINTENANCE no** | The founder was failing and was rescued by host execution (inert arrival 446,966 from epoch 14,001; ENVGATE01_REVIEW). But from 14,300 on, members copy exactly in isolation (zero neighbour, no host) at 0.75-1.00. The input scaffold (does copying depend on specific inputs?) is TH-015's INPUT_SCAFFOLD row |

## What this changes
- **Deep block D_Z80_SYNTHESIS s3.2** said "Archaeon ... retains 0.0 founder material ... despite 82% exact copies". Already
  retracted as unsupported; now REFUTED.
  * Founder material is conserved and relocated first. The new capability (exact copying) was built on it.
  * Only afterwards does mutation gradually replace it.
  * The Archaeon vs NPE contrast drawn from the 0.0 ("NPE conserves OP_SELF/LDIR as material; Archaeon does not") does not hold
    in that form. Both conserve machinery material early. In Archaeon the conservation erodes under mutation over thousands of
    generations while function holds, and it is invisible to any fixed-position unit.
- **Directive item 4 ("reproductive function persists")** is true, but the stronger observation is that function CHANGED CLASS
  (near -> exact gated -> exact ungated) within about 20 generations, on conserved founder material, and then stayed.

## Limits
- One lineage, one block. At most 12 members per snapshot, the lowest cell indices (not random).
- Machinery comes from 1-2 members per snapshot.
- Capability is isolated-VM on allowed inputs. In-world copying may differ.
- Mean generation is the lineage-generation counter (ggen).

## TH-015 (same tapes)
See TH015_RESULT.md.

## Item 8
See ITEM8_RESULT.md. The item-8 tracking inside this replay was defective (it followed all of a child's material, mostly lineage
material shared with its parent, and matched copier classes by wrong names). It was re-run with probes/item8_block13.py; this
replay's fates are not used.
