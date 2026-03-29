










# The Maths Collector — Fill the Tensor with Weird Mathematics

## Mission

Implement Python functions from as many diverse, obscure, and unexpected mathematical fields as possible. Each function becomes an organism in the Noesis tensor exploration engine. The value comes from CROSS-FIELD compositions — what emerges when you chain operations from fields that have never been connected.

**Target: 500+ functions across 50+ fields in `noesis/the_maths/`**

Each field gets its own Python file. Each file contains 5-20 functions. Every function is pure numpy, callable, typed, and tested.

## Output Format

Each file: `noesis/the_maths/{field_name}.py`

```python
"""
{Field Name} — {one-line description}

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

# Metadata for the organism loader
FIELD_NAME = "field_name"
OPERATIONS = {}

def operation_name(x):
    """What it does. Input: {type}. Output: {type}."""
    # Implementation
    return result

OPERATIONS["operation_name"] = {
    "fn": operation_name,
    "input_type": "array",  # scalar, array, matrix, integer, probability_distribution
    "output_type": "scalar",
    "description": "What it computes"
}

# ... more operations ...

# Self-test
if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")


What about symbolic math that hasn't been deciphered that you haven't already listed?


This is a rich vein. There are more undeciphered or partially-deciphered symbolic systems with computable mathematical structure than most people realize. The key insight for Noesis: you don't need to *decode the language* to extract the *mathematical operations*. The structural patterns, numerical systems, and combinatorial constraints are computable even when the semantic content is unknown.

**Undeciphered systems with extractable mathematical structure**

1. **Proto-Elamite numerical systems** (~3100 BCE, Iran) — The script is largely undeciphered, though the numerical portion is partly decoded. It uses multiple coexisting numerical systems: decimal, sexagesimal, bisexagesimal, and a capacity system. The wild part: the meaning of a numerical glyph depends on which system it's being used in — the same symbol means different things depending on context. Operations: multi-system arithmetic (same glyph, different base depending on what's being counted), context-dependent numerical parsing, cross-system consistency checking (tablets have checksums on the reverse), tablet analysis including food ratio computation and sowing rate estimation from numerical patterns. The *context-dependent base* concept is computationally interesting — it's a number system where the radix is a function of the semantic domain. Nothing in the current tensor has that.

2. **Linear A** (~1800–1450 BCE, Minoan Crete) — Predecessor to Linear B (which was deciphered in 1952 as Mycenaean Greek). Linear A's language is unknown but its numerical system IS deciphered: it's decimal with distinct symbols for units, tens, hundreds, thousands, and fractions. The fraction system is especially interesting — it uses specific symbols for 1/2, 1/4, and other fractions but the exact values of some fraction symbols are contested. Operations: Linear A fraction arithmetic (reconstructed), weight/measurement system modeling (the Minoan weight system has been partially reconstructed from the tablets), accounting balance verification (some tablets are ledgers where totals should match line items — the degree of mismatch reveals either scribal error or undeciphered fraction values).

3. **Indus Valley script** (~2600–1900 BCE) — ~4,000 inscriptions, average length only 5 signs. This is one of the most contested undeciphered systems in existence. What IS known: the signs have a positional distribution (certain signs only appear at the beginning or end of strings) suggesting syntactic structure. Statistical analyses show the sign entropy is between natural language and rigid notational systems. Operations: positional frequency analysis (which signs appear where), bigram/trigram transition probability matrices, entropy rate estimation, comparison against known scripts and against random baselines, Zipf's law analysis. The *question of whether it's writing at all* is itself a classification problem that Noesis could model — what statistical properties distinguish writing from proto-writing from decoration?

4. **Rongorongo** (Easter Island, possibly 18th century or earlier) — ~24 surviving wooden tablets with glyphs arranged in reverse boustrophedon (alternating lines read in opposite directions, with each alternate line upside-down). Some signs appear to depict lunar calendars and astronomical cycles. Operations: boustrophedon transformation (the reading direction itself is a computable geometric operation), glyph frequency analysis, potential lunar cycle extraction (one tablet — the "Moon tablet" — has 29-30 glyph groups per section, matching the synodic month), repetition pattern detection. The reverse boustrophedon is unique — no other known writing system uses it — and it's a specific symmetry transformation (alternating reflection + 180° rotation).

5. **Phaistos Disc** (~1700 BCE, Crete) — A single clay disc stamped (not inscribed) with 241 signs from a set of 45 distinct symbols, arranged in a spiral. The signs were made with *reusable stamps* — arguably the world's first movable type. The corpus is exactly one object, making decipherment essentially impossible, but the combinatorial structure is analyzable. Operations: symbol frequency analysis (the distribution is NOT Zipfian — this is unusual), spiral-path enumeration, stamp-reuse pattern analysis, comparison of symbol distribution against Linear A and Cretan hieroglyphs. The structural oddity — a 45-symbol inventory that doesn't follow Zipf's law — is itself an interesting statistical signature.

6. **Zapotec script** (~600 BCE–900 CE, Oaxaca, Mexico) — One of the earliest writing systems in Mesoamerica. Partially deciphered — calendrical glyphs and some place names are understood, but the full system is not. The calendar uses a 260-day ritual calendar (tonalpohualli-equivalent) interlocking with a 365-day solar calendar. Operations: 260-day cycle computation (13 × 20, but the combinatorial structure is more complex than simple LCM), calendar round matching (the 52-year cycle), Long Count equivalent date arithmetic, glyph co-occurrence analysis. The 260-day cycle may be related to the human gestation period, the agricultural cycle, or astronomical cycles — the *reason* for 260 is itself an unsolved problem.

7. **Cretan hieroglyphs** (~2100–1700 BCE) — Predecessor to Linear A, found on seal stones and clay objects. Around 137 distinct signs. The numerical system uses a simple additive decimal base. Partially deciphered — some logograms are identified but the phonetic values are mostly unknown. Operations: seal-stone glyph combination analysis (which glyphs appear together on the same seal), sign-group length distribution, comparison with Linear A sign inventory (some signs were inherited). The seal-stone context means these may function partly as a *compositional identity system* — mathematical signatures for authenticating identity.

8. **Khipu encoding beyond decimal** — The standard Inka quipu decimal system is understood, but a substantial class of "narrative" or "anomalous" khipus exist that don't follow the standard decimal accounting pattern. These contain non-standard knot clusters, color sequences, and subsidiary cord patterns that suggest a more complex encoding. Operations: anomalous knot pattern classification, color-sequence grammar extraction, subsidiary cord tree-structure analysis, comparison of anomalous khipus against the standard accounting structure to identify the *delta* — what information the anomalous features carry beyond what decimal accounting can express.

9. **Vinča symbols** (~5500–4000 BCE, Old Europe) — Pre-dating Sumerian cuneiform by millennia. Found on pottery, figurines, and spindle whorls across southeastern Europe. Around 210 distinct signs. Whether these constitute writing is fiercely debated. Operations: symbol co-occurrence matrix, spatial distribution analysis (which symbols appear on which artifact types), symbol complexity measurement (stroke count, symmetry group), comparison against both known writing systems and known decorative/potter's mark traditions. If Noesis can find statistical signatures that distinguish these from random marks OR from known writing systems, that's a contribution to an open archaeological question.

10. **Epi-Olmec / Isthmian script** (~500 BCE–500 CE, Gulf Coast Mexico) — Partially deciphered from a single long text (the La Mojarra stela with ~465 glyphs) by John Justeson and Terrence Kaufman in 1993, but their decipherment is contested. The calendar system is the Long Count (shared with Maya). Operations: Long Count date computation, contested-sign probability estimation (for signs where multiple readings exist, what's the statistical likelihood of each?), structural comparison with Maya script (which IS deciphered — the degree of structural similarity constrains possible readings).

11. **Wadi el-Hol inscriptions** (~1900 BCE, Egypt) — Possibly the earliest alphabetic writing, found in the Egyptian desert. Only two short inscriptions. The signs appear to derive from Egyptian hieroglyphs but represent a Semitic language. This is at the *origin point* of the alphabet. Operations: hieroglyph-to-letter mapping analysis (which Egyptian signs were selected and why — the acrophonic principle), comparison with Proto-Sinaitic and early Phoenician, structural analysis of why *these* ~22 signs were selected from the hundreds of available hieroglyphs. The selection itself encodes information about phonological structure.

**Systems that LOOK mathematical but remain opaque**

12. **Ishango bone markings** (~20,000 BCE, Congo) — A bone with notch groupings that some researchers interpret as prime numbers, while others suggest utilitarian purposes like improving grip. The groupings: Column A: 3, 6, 4, 8, 10, 5, 5, 7. Column B: 11, 13, 17, 19. Column C: 11, 21, 19, 9. Column B is the primes between 10 and 20. Column A pairs might show doubling. Operations: statistical tests for whether these patterns could arise by chance, comparison against known tally-mark systems, prime detection as a cognitive marker, correlation analysis between columns.

13. **Neolithic Scottish carved stone balls** (~3000 BCE) — Over 400 carved stone balls with varying numbers of knobs (3 to 160, but most commonly 6). The 6-knobbed ones correspond to the vertices of an octahedron. Some researchers claim these represent the five Platonic solids, which would predate the Greek discovery by 2000 years. Others dispute this. Operations: knob-count frequency distribution, symmetry group classification of surviving specimens, comparison against Platonic solid vertex counts, randomness testing (if the distribution matches Platonic solids better than chance, that's significant).

14. **Geoglyphs of Nazca and Palpa** — The geometric Nazca lines include perfect spirals, trapezoids, and triangles spanning kilometers. The Palpa lines include a set of geometric figures with specific angle relationships. The mathematical question: what surveying/construction algorithms produce these shapes at scale without aerial perspective? Operations: spiral parameter estimation (are they Archimedean? logarithmic?), angle precision measurement, surveying algorithm reconstruction (what minimum set of tools — cord, stakes, sighting lines — reproduces these shapes?), fractal dimension of the overall layout.

15. **Voynich manuscript** (~1404–1438) — The most famous undeciphered text. Statistical analysis shows the text has word-length distributions and entropy rates *between* natural language and random — consistent with either an unknown language, an encoded known language, or an elaborate hoax. Operations: word frequency analysis, entropy rate at multiple scales, vocabulary growth curve (Heaps' law), comparison against known languages in every structural metric. A recent computational approach using Zipf's law and character-bigram entropy suggested it might be in an anagrammed form of a known language. The statistical fingerprint is the computable object, regardless of whether the content is meaningful.

16. **Baltic/Slavic *cherty i rezy*** ("strokes and cuts") — Pre-Christian Slavic symbolic system mentioned by the 10th-century Bulgarian writer Chernorizets Hrabar, who states that before the adoption of Christianity, Slavs "counted and guessed using strokes and cuts." No confirmed examples survive, but some researchers connect them to marks found on ceramic vessels and bone artifacts from 6th-9th century Slavic sites. If they existed, they'd be a lost tally/notation system. Operations: mark-pattern extraction from candidate artifacts, comparison against known tally systems, statistical testing for numerical regularity.

17. **Australian Aboriginal message sticks** — Carved wooden objects used for communication between groups. The carvings are not a writing system in the conventional sense but encode specific messages through agreed-upon conventions. Some sticks have regular geometric patterns (zigzags, dots, lines) with apparent combinatorial structure. Operations: motif grammar extraction, combinatorial analysis of mark types and positions, information capacity estimation (how many distinct messages can a given mark-vocabulary on a given stick length encode?).

18. **Nsibidi** (pre-colonial southeastern Nigeria) — A writing/symbol system used by the Ekpe/Mgbe society and others. Partially documented but far from fully understood, especially the "higher" esoteric forms. The known portion includes ideograms for concepts, relationships, and legal proceedings. Some scholars argue the undocumented portions encode more complex relational/logical structures. Operations: known-sign network analysis, relational grammar extraction, comparison against other independent writing inventions.

**The meta-level Noesis angle**

Here's what makes these particularly valuable for the tensor: each undeciphered system is a *constraint satisfaction problem*. The numerical structure, positional patterns, frequency distributions, and co-occurrence matrices are all known. The unknown is the mapping to meaning. For Noesis, the extractable operations are:

- **Context-dependent radix arithmetic** (Proto-Elamite) — the base changes based on what you're counting
- **Reverse boustrophedon transformations** (Rongorongo) — a specific geometric symmetry applied to sequential reading
- **Anomalous encoding detection** (narrative khipus) — identifying when a known system is being used to encode something beyond its standard capacity
- **Script-vs-decoration discrimination** (Vinča, Ishango) — statistical tests for whether a symbol sequence carries structured information
- **Information-theoretic writing classification** — entropy rate, Zipf compliance, vocabulary growth curves as universal metrics that apply across ALL symbolic systems
- **Constraint propagation from partial decipherment** — when some signs are known, what does that constrain about the unknown signs?

That last one is especially relevant. Partial decipherment is exactly the situation the tensor operates in — you know some compositions work, you don't know others, and you're trying to infer structure from incomplete information. These undeciphered scripts are natural test cases for that inference machinery.


