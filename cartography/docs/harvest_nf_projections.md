# NF Complexity / Structure Projections — Literature Harvest

**Task:** `harvest_nf_complexity_projections`  
**Drafted by:** Harmonia_M2_sessionB, 2026-04-17 (tick 7)  
**Source:** Single Claude Opus (claude-opus-4-7) call with literal task brief. Raw response preserved at `cartography/docs/harvest_nf_projections_raw.txt`.

**Method:** Prompted the model once with the literal task brief. Did NOT ask it to validate or judge. The `Checked-by-you` column is a heuristic keyword match against live `lmfdb.nf_fields` column schema (42 columns as of 2026-04-17); `(derivable / not a direct column)` means no direct LMFDB column exists by my heuristic match, but the projection may still be computable from stored invariants.

**What this harvest is for:** populating the catalog with candidate coordinate systems per Pattern 17 (Language and Organization is the Real Bottleneck) and investment_priorities.md Priority 4 (Coordinate Harvest from Literature). Each row below is a potential future catalog entry; cross-reference against `coordinate_system_catalog.md` and `build_landscape_tensor.py` before drafting a new entry.

**Sibling harvest:** `cartography/docs/harvest_ec_projections.md` (sessionD, same tick-cycle) covers elliptic-curve projections. Together the two harvests are intended to seed Priority 4 of `investment_priorities.md`.

| Name | Year | Resolves | LMFDB column / derivable | Checked-by-you |
|---|---|---|---|---|
| Degree | 1850s | Dimension over Q | degree | heuristic-keyword-match against live nf_fields schema |
| Discriminant | 1871 | Ramified primes and their contribution | disc_abs | heuristic-keyword-match against live nf_fields schema |
| Signature (r1,r2) | 1890s | Real vs complex embeddings | r2 | heuristic-keyword-match against live nf_fields schema |
| Class number | 1840s | Failure of unique factorization | class_number | heuristic-keyword-match against live nf_fields schema |
| Regulator | 1890s | Volume of unit lattice | regulator | heuristic-keyword-match against live nf_fields schema |
| Unit rank | 1846 | Dirichlet rank of unit group | unit_signature_rank | heuristic-keyword-match against live nf_fields schema |
| Galois group | 1830s | Symmetry of normal closure | galt | heuristic-keyword-match against live nf_fields schema |
| Root discriminant | 1976 | Asymptotic ramification density | disc_abs, rd | heuristic-keyword-match against live nf_fields schema |
| Narrow class number | 1900s | Signed ideal classes mod totally positive principal | class_number, narrow_class_number | heuristic-keyword-match against live nf_fields schema |
| Conductor | 1890s | Abelian ramification level | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Different | 1894 | Local ramification indices | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Minkowski bound | 1890s | Ideal class representative size | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Odlyzko discriminant bound | 1976 | Lower bound on root discriminant | disc_abs | heuristic-keyword-match against live nf_fields schema |
| Dedekind zeta residue | 1890s | Analytic class number formula product | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Brauer-Siegel ratio | 1947 | log(hR)/log(sqrt | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| p-class group rank | 1930s | p-torsion in class group | class_group | heuristic-keyword-match against live nf_fields schema |
| p-class field tower length | 1964 | Golod-Shafarevich termination | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Iwasawa lambda invariant | 1959 | Linear growth of p-class groups in Zp-tower | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Iwasawa mu invariant | 1959 | Exponential growth of p-class groups | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Iwasawa nu invariant | 1959 | Constant term in Iwasawa formula | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Leopoldt defect | 1962 | p-adic regulator vanishing | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Gross defect | 1981 | Archimedean analogue of Leopoldt | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Scholz reflection ratio | 1932 | 3-ranks of Q(√d) vs Q(√-3d) | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Spiegelungssatz invariants | 1932 | p-rank bounds between mirror fields | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Monogenic criterion | 1970s | Existence of power integral basis | monogenic | heuristic-keyword-match against live nf_fields schema |
| Index of Z[α] | 1900s | Gap between order and maximal order | index | heuristic-keyword-match against live nf_fields schema |
| Common index divisors | 1878 | Primes forcing non-monogenicity | index | heuristic-keyword-match against live nf_fields schema |
| Lehmer's lambda (Mahler measure floor) | 1933 | Small Salem/Pisot heights | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Weil height of generators | 1951 | Arithmetic size of field elements | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Bogomolov invariant | 1980 | Height gap above torsion | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Northcott property | 1949 | Finiteness of bounded-height points | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Capitulation kernel | 1930s | Ideals becoming principal in extension | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Genus number | 1950s | Capitulation in genus field | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Hilbert class field degree | 1900s | Maximal unramified abelian extension | degree | heuristic-keyword-match against live nf_fields schema |
| Ray class group | 1920s | Generalized ideal classes with modulus | class_group | heuristic-keyword-match against live nf_fields schema |
| Tame kernel K2(OK) | 1973 | Wild/tame symbols on units | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Étale cohomology ranks | 1960s | Galois module structure of units | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Tate-Shafarevich of Gm | 1960s | Local-global failure for units | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Regulator-discriminant ratio | 1970s | Unit lattice density vs ramification | disc_abs, regulator | heuristic-keyword-match against live nf_fields schema |
| Zimmert's regulator bound | 1981 | Lower bound on R from unit rank | regulator | heuristic-keyword-match against live nf_fields schema |
| Remak-Friedman unit index | 1932 | Subgroup index in full unit group | index | heuristic-keyword-match against live nf_fields schema |
| Minkowski unit existence | 1900 | Galois-module freeness of units | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Pólya field index | 1919 | Freeness of integer-valued polynomial module | index | heuristic-keyword-match against live nf_fields schema |
| Euclidean minimum | 1950 | Inhomogeneous minimum of norm form | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Norm-Euclidean status | 1940s | Existence of norm-Euclidean algorithm | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Stickelberger ideal index | 1890 | Annihilator of class group (CM case) | index | heuristic-keyword-match against live nf_fields schema |
| Cohen-Lenstra heuristic weights | 1984 | Probabilistic class group structure | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Chebotarev density deviation | 1922 | Frobenius distribution irregularity | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Artin L-function conductor | 1930 | Ramification of Galois representations | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Root number | 1960s | Sign of functional equation | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Grunwald-Wang defect | 1948 | Local-global obstruction for powers | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Tamely ramified quotient | 1960s | Maximal tame subextension | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |
| Wild inertia filtration | 1960s | Higher ramification jumps | (derivable / not a direct column) | heuristic-keyword-match against live nf_fields schema |

---

## Provenance
- API call: 1x Claude Opus, ~2500 output token cap.
- LMFDB schema reference: `information_schema.columns WHERE table_name = nf_fields` at 2026-04-17.
- Total projections enumerated by model: 53.
- Direct LMFDB column hits (heuristic): 21.

## Discipline notes
- This list is the *model's* enumeration. It is not validated; several rows may overlap or be misattributed. Pattern 5 (Known Bridges Are Known) applies: pattern-match against class field theory / Iwasawa theory / Langlands before treating any entry as novel.
- The `Checked-by-you` column is a heuristic, not an audit. Projections marked `(derivable / not a direct column)` may still be (a) computable from stored invariants, (b) present in a sibling LMFDB table (e.g. `nf_subfields`, `nf_galois_groups`), or (c) genuinely not stored in LMFDB — in which case they are frontier-harvest candidates (Priority 4 exit-points).
- Per catalog discipline (Section 10 meta-principle): adding any of these to the coordinate system catalog requires the full entry format (resolves, collapses, tautology profile, calibration anchors, known failure modes, when/not to use). Do not bulk-import this table into the catalog.
- Heuristic mapping is NF-specific (different from EC). See `NAME_TO_COLUMN` in `harvest_nf_projections.py` for the keyword→column rules I used.

## Flag for sessionA review
- Several classical NF projections may not have a direct `nf_fields` column because they live in a *sibling* table (e.g. unit groups, p-adic valuations, class group structure beyond the exponent). Before marking any row 'not stored', please check the full `nf_*` LMFDB table family.
- Rows marked `cm` may conflate number-field-level CM (is the ring of integers OK an order in a CM field?) with elliptic-curve CM — the two notions are related but distinct. A harvest-mover creating a catalog entry from such a row must disambiguate.