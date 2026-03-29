# Council Prompt: Comprehensive Survey of World Mathematical Traditions

**Purpose:** Extract every documented mathematical tradition, system, notation, and computational method from all cultures and historical periods. Output must be structured for automated processing by an agentic tool that will hunt down verification details for each entry.

**Context:** We are building a structurally grounded tensor of mathematical transformations. We have identified 11 structural primitives (COMPOSE, MAP, EXTEND, REDUCE, LIMIT, DUALIZE, LINEARIZE, STOCHASTICIZE, SYMMETRIZE, BREAK_SYMMETRY, COMPLETE) that generate all mathematical transformations tested so far — verified across 298 SymPy tests, 44 derivation chains, and 1,714 operations at 100% decomposition rate. We need to test this basis against EVERY known mathematical tradition, not just the European canon.

---

## Output Format (STRICT — one entry per system, machine-parseable)

For EACH mathematical tradition or system, output a JSON object. Do NOT summarize or group — give every distinct system its own entry. Aim for 200+ entries.

```json
{
  "id": "MAYAN_VIGESIMAL",
  "tradition": "Mesoamerican — Maya",
  "system_name": "Mayan Vigesimal Number System",
  "region": "Mesoamerica (present-day Mexico, Guatemala, Belize, Honduras)",
  "period": "~300 BCE — 1500 CE",
  "description": "Base-20 positional number system with true zero. Three symbols: dot (1), bar (5), shell (0). Used for calendar calculations, astronomical prediction, and trade.",
  "key_operations": [
    "Base-20 positional arithmetic",
    "Long Count calendar date computation",
    "Astronomical cycle prediction (Venus, lunar eclipses)",
    "Vigesimal-to-modified-vigesimal conversion (18×20 for Tun in calendar)"
  ],
  "structural_features": [
    "True zero (earliest known independent invention)",
    "Modified base in calendar system (18×20 = 360 instead of 20×20 = 400)",
    "Positional notation (vertical, bottom-to-top)"
  ],
  "candidate_primitives": ["COMPOSE", "MAP", "REDUCE"],
  "unique_aspects": "Modified vigesimal for calendar (360-day Tun) introduces a BREAK_SYMMETRY from pure base-20 — the regularity of the positional system is deliberately broken to approximate the solar year.",
  "verification_difficulty": "LOW — well-documented, arithmetic is reconstructable",
  "key_references": [
    "Lounsbury, F. — Maya Numeration, Computation, and Calendrical Astronomy",
    "Ifrah, G. — The Universal History of Numbers",
    "Closs, M.P. — Native American Mathematics"
  ],
  "formalization_status": "FORMALIZABLE — complete arithmetic rules are known",
  "open_questions": [
    "Did the Maya develop any form of algebraic manipulation?",
    "Are there undeciphered mathematical glyphs in lesser-known codices?"
  ]
}
```

---

## Extraction Categories (cover ALL of these)

### 1. Ancient & Classical Number Systems
Every known numeral system and its arithmetic. Include:
- Egyptian (hieroglyphic AND hieratic — they're different systems)
- Babylonian (sexagesimal, cuneiform)
- Chinese (rod numerals, counting board, suanpan)
- Greek (Attic AND Ionic/alphabetic)
- Roman
- Indian (Brahmi, Devanagari, Kerala school)
- Mayan (vigesimal)
- Aztec (vigesimal variant)
- Incan (quipu — knot-based)
- Ethiopian (Ge'ez numerals)
- Armenian
- Hebrew (gematria as mathematical system)
- Arabic-Islamic (multiple regional variants)
- Sumerian (proto-cuneiform tokens)
- Indus Valley (undeciphered — include with honest assessment)

### 2. African Mathematical Traditions
- Yoruba base-20 arithmetic (subtractive system — "20 less 5" for 15)
- Ishango bone (possible prime/doubling sequences, ~20,000 BCE)
- Egyptian multiplication (doubling and addition)
- Egyptian fractions (unit fractions only — unique constraint)
- Akan gold-weight system (geometric and algebraic patterns)
- Bamana sand divination (binary system predating Leibniz)
- Shona/Great Zimbabwe geometric patterns
- Ethiopian multiplication (Peasant multiplication / Russian multiplication variant)
- Tshokwe sona drawings (graph theory in sand)
- Kpelle geometric classification systems
- Any others documented in ethnomathematics literature

### 3. Indigenous Mathematical Systems
- Aboriginal Australian (base-5 systems, spatial/kinship mathematics, songline navigation)
- Polynesian navigation mathematics (star compass, wave pattern analysis, dead reckoning)
- Inuit spatial/geographic mathematics
- Native American (various — Pomo basket-weaving geometry, Navajo symmetry systems, Zuni color/direction algebra)
- Amazonian (Pirahã and Munduruku — approximate number systems, debates about mathematical cognition)
- Papuan counting systems (body-part tally systems, various bases from 2 to 27)
- Maori meeting house geometry
- Tongan navigation mathematics
- Any documented oral mathematical traditions

### 4. Asian Mathematical Traditions (beyond standard coverage)
- Chinese remainder theorem (original formulation and context)
- Japanese wasan tradition (sangaku temple geometry problems)
- Korean mathematics (Joseon dynasty computational methods)
- Vietnamese mathematical traditions
- Tibetan calendar mathematics
- Jain mathematics (concepts of infinity, very large numbers, combinatorics)
- Vedic mathematics (Atharvaveda computational sutras — separate from modern "Vedic math")
- Kerala school (Madhava — series expansions predating Newton/Leibniz)
- Balinese calendar mathematics (complex multi-cycle system)
- Southeast Asian textile mathematics (symmetry groups in weaving)
- Chinese magic squares and combinatorial traditions
- Chinese rod calculus and matrix methods (Jiuzhang Suanshu)

### 5. Islamic Golden Age (granular — not "Islamic math" as one entry)
- Al-Khwarizmi's algebraic system (original, not modern algebra)
- Al-Kindi's cryptanalysis (frequency analysis as mathematical method)
- Omar Khayyam's geometric algebra and cubic solutions
- Al-Haytham's optics mathematics
- Al-Biruni's geodesy calculations
- Thabit ibn Qurra's amicable numbers and infinitesimal methods
- Al-Samawal's algebraic notation
- Al-Tusi's trigonometric methods
- Decimal fraction systems (al-Kashi)
- Combinatorial methods (Ibn Munim)

### 6. Pre-Columbian & Mesoamerican
- Mayan Long Count calendar mathematics
- Mayan eclipse prediction tables (Dresden Codex)
- Aztec tributary arithmetic
- Aztec calendar round calculations
- Incan quipu recording and calculation system
- Incan yupana (possible computing device)
- Any documented mathematical content from other pre-Columbian cultures

### 7. Ancient Computational Devices & Algorithms
- Abacus variants (Roman, Chinese suanpan, Japanese soroban, Russian schoty, Mesoamerican nepohualtzintzin)
- Antikythera mechanism computational model
- Astrolabe computations
- Napier's bones
- Slide rule mathematical model
- Pascaline and Leibniz wheel
- Jacquard loom (mathematical content of weaving programs)
- Difference engine algorithms

### 8. Symbolic & Notation Systems
- Leibniz's characteristica universalis
- Frege's Begriffsschrift
- Peano's notation
- Polish notation (Łukasiewicz)
- Lambda calculus notation (Church)
- APL notation (Iverson)
- Diagrammatic reasoning systems (Peirce's existential graphs)
- Feynman diagrams as computational notation
- Penrose graphical notation (tensor diagrams)
- Category theory string diagrams
- Knuth's up-arrow notation
- Conway's surreal number notation

### 9. Esoteric & Boundary Mathematical Systems
- Gematria (Hebrew letter-number mysticism — IS there mathematical structure?)
- Chinese I Ching (binary system — verified mathematical content)
- Pythagorean number mysticism (separate actual math from philosophy)
- Combinatorial aspects of divination systems (Ifá, I Ching, geomancy)
- Vedic square (modular arithmetic patterns)
- Magic squares across cultures (Lo Shu, Dürer, Islamic)
- Sacred geometry traditions (separate verifiable geometry from mysticism)
- Musical tuning systems as mathematical structures (Pythagorean, just intonation, equal temperament, gamelan pelog/slendro)
- Textile symmetry groups (17 wallpaper groups realized in cultural artifacts)

### 10. Undeciphered & Partially Understood
- Indus Valley script (mathematical content if any)
- Proto-Elamite (accounting/mathematical tablets)
- Rongorongo (Easter Island — possible mathematical content)
- Minoan Linear A (partial mathematical content)
- Zapotec numerals
- Etruscan numerals (partially understood)
- Phaistos Disc (speculative mathematical content)
- Any other systems where mathematical content is suspected but unconfirmed

### 11. Non-Standard Modern
- Constructive mathematics (Brouwer — different axioms, different operations)
- Ultrafinitism (Yessenin-Volpin — rejection of actual infinity)
- Non-standard analysis (Robinson — infinitesimals made rigorous)
- Surreal numbers (Conway)
- Tropical mathematics (min-plus algebra)
- p-adic number systems
- Quaternions, octonions, sedenions (hypercomplex hierarchies)
- Fuzzy set theory mathematics
- Paraconsistent mathematics (mathematics with contradictions)
- Univalent foundations / HoTT

---

## Critical Instructions

1. **EVERY system gets its own entry.** Don't combine "African mathematical traditions" into one entry. Yoruba arithmetic, Egyptian fractions, and Tshokwe sona drawings are three separate entries.

2. **Be honest about verification difficulty.** Use: FORMALIZABLE (complete rules known), PARTIALLY_FORMALIZABLE (some rules known, gaps exist), SPECULATIVE (mathematical content suspected but not confirmed), UNDECIPHERED (symbols exist, meaning unknown).

3. **Include the weird stuff.** If there's debate about whether something IS mathematics (Pirahã approximate counting, quipu as recording vs computation, sand divination as binary system), include it and note the debate. We'd rather filter later than miss something.

4. **Don't Western-wash.** Describe each system in its own terms first, then note connections to Western mathematics. "The Yoruba system uses subtraction from base-20 landmarks" not "The Yoruba system is like Western base-10 but..."

5. **Give us enough for the agent.** The key_references field should have enough specificity that a search agent can find the actual sources. Author + title, not just "various sources."

6. **200+ entries minimum.** If you're under 200, you're grouping things that should be separate. The Japanese soroban and the Chinese suanpan are different entries. Egyptian hieroglyphic and hieratic numerals are different entries. Al-Khwarizmi's algebra and Omar Khayyam's geometric algebra are different entries.

7. **Flag potential 12th primitives.** If any system contains a transformation that seems genuinely resistant to decomposition into our 11 primitives, flag it explicitly. This is the most valuable possible finding.

---

## What We'll Do With This

An agentic tool will take each entry and:
1. Search for the most detailed available source material
2. Extract the specific mathematical operations/transformations
3. Attempt 11-primitive decomposition on each operation
4. Classify into tier: VERIFIED (SymPy-testable), FORMALIZED (rules known but not yet coded), DOCUMENTED (described but not formalized), SPECULATIVE
5. Flag any decomposition failures as potential primitive basis challenges

The output populates the comprehensive survey (Tier 1 of the three-tier pipeline). Only verified entries advance to the tensor.