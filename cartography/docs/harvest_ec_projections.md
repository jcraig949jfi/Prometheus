# EC Complexity / Structure Projections — Literature Harvest

**Task:** `harvest_ec_complexity_projections`  
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 6)  
**Source:** Single Claude Opus (claude-opus-4-7) call with literal task brief. Raw response preserved at `cartography/docs/harvest_ec_projections_raw.txt`.

**Method:** Prompted the model once with the literal task brief. Did NOT ask it to validate or judge. The `Checked-by-you` column is a heuristic keyword match against live `lmfdb.ec_curvedata` column schema (50 columns as of 2026-04-17); `(derivable / not a direct column)` means no direct LMFDB column exists by my heuristic match, but the projection may still be computable from stored invariants.

**What this harvest is for:** populating the catalog with candidate coordinate systems per Pattern 17 (Language and Organization is the Real Bottleneck). Each row below is a potential future catalog entry; cross-reference against `coordinate_system_catalog.md` before drafting a new entry.

| Name | Year | Resolves | LMFDB column / derivable | Checked-by-you |
|---|---|---|---|---|
| j-invariant | 1800s | isomorphism class over algebraic closure | jinv | heuristic-keyword-match against live ec_curvedata schema |
| Discriminant | 1800s | singularity of Weierstrass model | absD | heuristic-keyword-match against live ec_curvedata schema |
| Conductor | 1960s | primes of bad reduction with ramification data | conductor | heuristic-keyword-match against live ec_curvedata schema |
| Mordell-Weil rank | 1922 | rank of rational points group | rank | heuristic-keyword-match against live ec_curvedata schema |
| Torsion subgroup | 1900s | finite order rational points | torsion | heuristic-keyword-match against live ec_curvedata schema |
| Regulator | 1960s | covolume of Mordell-Weil lattice | regulator | heuristic-keyword-match against live ec_curvedata schema |
| Tate-Shafarevich group | 1960s | failure of Hasse principle for principal homogeneous spaces | sha | heuristic-keyword-match against live ec_curvedata schema |
| Tamagawa numbers | 1960s | local component groups at bad primes | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Real period | 1960s | integral of invariant differential over real points | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| L-function | 1950s | global arithmetic via Euler product | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Analytic rank | 1960s | order of vanishing of L at s=1 | rank, analytic_rank | heuristic-keyword-match against live ec_curvedata schema |
| Selmer group (p-Selmer) | 1960s | p-descent obstruction bounding rank | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Faltings height | 1983 | archimedean size of associated abelian variety | faltings_height | heuristic-keyword-match against live ec_curvedata schema |
| Naive/Weil height of coefficients | 1970s | size of defining equation | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Szpiro ratio | 1980s | log-discriminant vs log-conductor comparison | szpiro_ratio | heuristic-keyword-match against live ec_curvedata schema |
| Kodaira symbols | 1964 | geometric type of singular fiber | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Néron model type | 1964 | integral model structure | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Frey curve invariants | 1980s | modularity-obstruction signature | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Modular degree | 1990s | degree of optimal modular parametrization | class_deg | heuristic-keyword-match against live ec_curvedata schema |
| Manin constant | 1972 | normalization discrepancy in modular parametrization | manin_constant | heuristic-keyword-match against live ec_curvedata schema |
| Iwasawa λ-invariant | 1970s | rank growth in cyclotomic tower | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Iwasawa μ-invariant | 1970s | p-divisibility in Selmer tower | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| p-adic L-function | 1970s | p-adic analytic continuation of L-values | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| p-adic regulator | 1980s | p-adic height pairing covolume | regulator | heuristic-keyword-match against live ec_curvedata schema |
| Mahler measure of defining polynomial | 1970s | logarithmic height of equation | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Canonical (Néron-Tate) height | 1965 | quadratic form on Mordell-Weil | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Galois representation image (mod ℓ) | 1972 | Serre openness and exceptional primes | elladic_images | heuristic-keyword-match against live ec_curvedata schema |
| Adelic Galois image | 1970s | joint ℓ-adic representation structure | adelic_level, elladic_images | heuristic-keyword-match against live ec_curvedata schema |
| Isogeny class | 1970s | Q-isogenous curves and isogeny graph | isogeny_degrees | heuristic-keyword-match against live ec_curvedata schema |
| CM discriminant | 1900s | endomorphism ring for CM curves | absD, cm | heuristic-keyword-match against live ec_curvedata schema |
| Endomorphism ring | 1940s | extra multiplications structure | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Supersingular locus invariants | 1970s | Hasse invariant vanishing in char p | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Hasse-Weil zeta function | 1950s | point counts over finite fields | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| a_p trace of Frobenius | 1930s | local point count deviation | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Sato-Tate distribution | 1960s | equidistribution of normalized a_p | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Congruence number | 1990s | modular form congruence measure | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Heegner index | 1980s | index of Heegner point in Mordell-Weil | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Kolyvagin index | 1989 | Euler system bound on Sha | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| BSD rank (algebraic) | 1965 | conjectural Mordell-Weil rank via L | rank | heuristic-keyword-match against live ec_curvedata schema |
| Root number | 1960s | sign of functional equation | signD | heuristic-keyword-match against live ec_curvedata schema |
| Parity of rank | 1990s | rank mod 2 from local root numbers | rank | heuristic-keyword-match against live ec_curvedata schema |
| Ogg's formula quantity | 1967 | conductor exponent from reduction | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Silverman's height difference bound | 1990 | gap between naive and canonical heights | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Lang-Trotter constants | 1976 | frequency of fixed Frobenius traces | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Néron differential periods (complex) | 1960s | lattice generators of period lattice | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Cremona label / isogeny class size | 1990s | database-theoretic classification | isogeny_degrees, class_size | heuristic-keyword-match against live ec_curvedata schema |
| Stevens' optimal curve | 1989 | minimal modular degree in isogeny class | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |
| Watkins' modular degree bound | 2002 | bounds linking rank and modular degree | class_deg | heuristic-keyword-match against live ec_curvedata schema |
| Goldfeld-Szpiro quotient | 1990s | Sha size bound via Szpiro | szpiro_ratio | heuristic-keyword-match against live ec_curvedata schema |
| Bloch-Kato Tamagawa number | 1990s | motivic refinement of local factors | (derivable / not a direct column) | heuristic-keyword-match against live ec_curvedata schema |

---

## Provenance
- API call: 1x Claude Opus, ~2500 output token cap.
- LMFDB schema reference: `information_schema.columns WHERE table_name = ec_curvedata` at 2026-04-17.
- Total projections enumerated by model: 50.
- Direct LMFDB column hits (heuristic): 23.

## Discipline notes
- This list is the *model's* enumeration. It is not validated; several rows may overlap or be misattributed. Pattern 5 (Known Bridges Are Known) applies: pattern-match against Langlands / modularity / class field theory before treating any entry as novel.
- The `Checked-by-you` column is a heuristic, not an audit. If a projection appears as `(derivable / not a direct column)` but is obviously classical (e.g. L-value, Tamagawa), it likely has a home in a sibling LMFDB table (`ec_mwbsd`, `ec_tamagawa`, etc.) rather than `ec_curvedata` — further check needed.
- Per catalog discipline (Section 10 meta-principle): adding any of these to the coordinate system catalog requires the full entry format (resolves, collapses, tautology, anchors, failure modes). Do not bulk-import this table into the catalog.