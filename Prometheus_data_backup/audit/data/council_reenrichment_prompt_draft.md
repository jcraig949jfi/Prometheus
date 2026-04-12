# Council Re-Enrichment Prompt: Primitive Vector Differentiation

## Context

The current enriched_primitive_vector column in the ethnomathematics table has a
differentiation problem:

- 44 of 131 traditions (34%) have only 1 primitive in their vector
- 23 traditions are stamped with the generic [["MAP", 1.0]] — this is uninformative
- 8 traditions have [["MAP", 0.1]] — equally uninformative
- Only 54 traditions (41%) have 3+ primitives (well-differentiated)

This means ~1/3 of the tradition vectors carry no structural information beyond
"this tradition does mapping." Every mathematical tradition maps — that is not a
distinguishing feature.

## Task

For each tradition listed below, provide the TOP 3 structural primitives and their
relative weights (summing to approximately 1.0). Do NOT default to [["MAP", 1.0]].

### Rules
1. Every tradition MUST have at least 3 primitives
2. The highest-weight primitive MUST NOT be MAP unless the tradition is genuinely
   about cartographic or spatial representation specifically
3. Weights must be differentiated (no [0.33, 0.33, 0.33] unless truly equal)
4. Consider: what structural transformation does this tradition PRIMARILY perform?
   - COMPOSE: combining sub-results into wholes (algorithms, multi-step procedures)
   - REDUCE: simplifying complexity (approximation, bounding, truncation)
   - EXTEND: recursive/inductive growth (series, transfinite, iteration)
   - DUALIZE: bridging between dual representations (Fourier, Legendre, adjoint)
   - LINEARIZE: converting nonlinear to linear (tangent approximation, linearization)
   - SYMMETRIZE: exploiting or constructing symmetry (group theory, invariants)
   - MAP: spatial/representational transformation (coordinate systems, projections)
   - TRUNCATE: removing information to gain tractability (rounding, finite precision)
   - DISTRIBUTE: spreading information/load (parallelism, averaging)
   - CONCENTRATE: focusing computation/information (optimization, fixed-point)

### Examples of Well-Differentiated Vectors

These are real examples from the database showing proper differentiation:

- **Al-Kindi's Frequency Analysis System** (Islamic Golden Age): `[["MAP", 1.0], ["DUALIZE", 0.8], ["STOCHASTICIZE", 0.4], ["REDUCE", 0.2], ["SYMMETRIZE", 0.2], ["BREAK_SYMMETRY", 0.2], ["COMPOSE", 0.1]]`
- **Min-Plus / Tropical Semiring** (Non-Standard Modern): `[["LINEARIZE", 1.0], ["DUALIZE", 0.667], ["COMPOSE", 0.333], ["MAP", 0.333], ["BREAK_SYMMETRY", 0.333], ["SYMMETRIZE", 0.111]]`
- **Incan Yupana Computing Device** (Andean / Pre-Columbian): `[["MAP", 1.0], ["COMPOSE", 0.2], ["LINEARIZE", 0.143], ["BREAK_SYMMETRY", 0.143], ["SYMMETRIZE", 0.111], ["EXTEND", 0.1]]`
- **Kerala School of Astronomy and Mathematics** (South Asian — Indian): `[["LIMIT", 1.0], ["EXTEND", 0.5], ["COMPLETE", 0.143], ["COMPOSE", 0.125], ["LINEARIZE", 0.125], ["MAP", 0.091]]`
- **Characteristica Universalis** (Early Modern European): `[["MAP", 1.0], ["REDUCE", 0.333], ["COMPLETE", 0.333], ["COMPOSE", 0.167], ["EXTEND", 0.167]]`

### Traditions Requiring Re-Enrichment

The following 44 traditions currently have only 1 primitive and need
differentiation. For each, provide: `[["PRIM1", weight1], ["PRIM2", weight2], ["PRIM3", weight3]]`

- `MATH_SYS_213` (Africa): currently `[["MAP", 0.1]]`
- `MATH_SYS_117` (African): currently `[["MAP", 0.1]]`
- `MATH_SYS_119` (African): currently `[["REDUCE", 0.6]]`
- `MATH_SYS_206` (Ancient Greece): currently `[["MAP", 0.1]]`
- `MATH_SYS_102` (Armenian): currently `[["MAP", 1.0]]`
- `ISHANGO_BONE` (Central African): currently `[["MAP", 1.0]]`
- `CHINESE_ABACUS_SUANPAN` (Chinese): currently `[["MAP", 1.0]]`
- `ETHIOPIAN_CALENDAR_ARITHMETIC` (Ethiopian): currently `[["MAP", 0.1]]`
- `MATH_SYS_101` (Ethiopian): currently `[["MAP", 1.0]]`
- `MATH_SYS_216` (Europe): currently `[["MAP", 0.091]]`
- `MATH_SYS_127` (European): currently `[["MAP", 0.091]]`
- `SLIDE_RULE` (European): currently `[["MAP", 1.0]]`
- `PASCALINE` (French): currently `[["MAP", 1.0]]`
- `LEIBNIZ_WHEEL` (German): currently `[["COMPOSE", 0.1]]`
- `EQUAL_TEMPERAMENT_SYSTEM` (Global): currently `[["MAP", 0.1]]`
- `JUST_INTONATION_SYSTEM` (Global): currently `[["MAP", 1.0]]`
- `GREEK_ATTIC_NUMERALS` (Greek): currently `[["MAP", 1.0]]`
- `GREEK_IONIC_NUMERALS` (Greek): currently `[["MAP", 1.0]]`
- `MATH_SYS_210` (India): currently `[["COMPOSE", 1.0]]`
- `BRAHMI_NUMERALS` (Indian): currently `[["MAP", 1.0]]`
- `DEVANAGARI_NUMERALS` (Indian): currently `[["MAP", 1.0]]`
- `MATH_SYS_121` (Indigenous American): currently `[["SYMMETRIZE", 1.0]]`
- `ISLAMIC_QIBLA_TRIGONOMETRY` (Islamic): currently `[["MAP", 1.0]]`
- `MATH_SYS_104` (Islamic): currently `[["MAP", 1.0]]`
- `MATH_SYS_107` (Islamic): currently `[["MAP", 1.0]]`
- `MATH_SYS_108` (Islamic): currently `[["MAP", 1.0]]`
- `JAPANESE_SANGAKU` (Japanese): currently `[["SYMMETRIZE", 1.0]]`
- `JAPANESE_SOROBAN` (Japanese): currently `[["MAP", 0.1]]`
- `MATH_SYS_129` (Logic): currently `[["MAP", 1.0]]`
- `MATH_SYS_133` (Mathematics): currently `[["EXTEND", 1.0]]`
- `MATH_SYS_218` (Modern): currently `[["MAP", 1.0]]`
- `MATH_SYS_219` (Modern): currently `[["MAP", 1.0]]`
- `MATH_SYS_220` (Modern): currently `[["COMPOSE", 0.1]]`
- `PARACONSISTENT_LOGIC` (Modern): currently `[["BREAK_SYMMETRY", 0.8]]`
- `FREGE_BEGRIFFSSCHRIFT` (Modern Logic): currently `[["MAP", 1.0]]`
- `NAVAJO_SYMMETRY_WEAVING` (Navajo): currently `[["SYMMETRIZE", 1.0]]`
- `PENROSE_DIAGRAMS` (Physics): currently `[["MAP", 1.0]]`
- `MATH_SYS_214` (Polynesian): currently `[["MAP", 0.1]]`
- `POLYNESIAN_NAVIGATION` (Polynesian): currently `[["STOCHASTICIZE", 1.0]]`
- `TIBETAN_ASTRONOMICAL_CALCULUS` (Tibetan): currently `[["MAP", 0.1]]`
- `MATH_SYS_137` (Undeciphered): currently `[["MAP", 1.0]]`
- `MATH_SYS_139` (Undeciphered): currently `[["MAP", 1.0]]`
- `MATH_SYS_113` (Vietnamese): currently `[["MAP", 1.0]]`
- `YORUBA_IFA_COMBINATORICS` (Yoruba): currently `[["COMPOSE", 0.1]]`

### Output Format

Return a JSON object mapping system_id to the new enriched_primitive_vector:

```json
{
  "SYSTEM_ID_001": [["COMPOSE", 0.5], ["REDUCE", 0.3], ["EXTEND", 0.2]],
  "SYSTEM_ID_002": [["DUALIZE", 0.6], ["LINEARIZE", 0.25], ["MAP", 0.15]],
  ...
}
```

### Verification

After generating, check:
1. No tradition has fewer than 3 primitives
2. No tradition has MAP as its sole or dominant (>0.6) primitive unless it is genuinely cartographic
3. Weights are proportional to the structural importance of each operation in that tradition
