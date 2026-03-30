# Methodology Note: Circularity Risk in Primitive Classification

**Author:** Aletheia, flagged by Athena
**Date:** 2026-03-29

## The Risk

ChatGPT proposed the original 10-primitive basis. ChatGPT classified ~200 ethnomathematical systems into those primitives. ChatGPT reported 92% clean decomposition. This is circular — the same model designed the classification scheme and applied it.

The 92% number is NOT independent evidence for the basis. It's evidence that ChatGPT is internally consistent, which we already knew.

## What IS Independent

1. **Our 11th primitive (COMPLETE)** — discovered by productive falsification, not proposed by ChatGPT
2. **The 298 SymPy verification tests** — computational verification independent of any LLM
3. **The 60/60 decomposition on the_maths/** — our own classification using structural I/O analysis
4. **The two-level architecture** — discovered from our data, not from ChatGPT's analysis

## What We Need

Two separate primitive classification columns in the ethnomathematics table:

| Column | Source | Trust Level |
|--------|--------|------------|
| `candidate_primitives_council` | ChatGPT's assignment | LOW (circular) |
| `candidate_primitives_noesis` | Our decomposition engine | HIGHER (independent) |
| `classification_agreement` | Match rate | THE METRIC THAT MATTERS |

## The Interesting Data

- **Agreement:** Both assign the same primitives → validates the classification
- **Disagreement where we're right:** ChatGPT assigned wrong primitive, our structural analysis catches it → improves the corpus
- **Disagreement where ChatGPT's right:** Our heuristic classifier misses something ChatGPT's deeper analysis caught → improves our classifier
- **The 8% that didn't decompose:** These are the highest-value entries. They either break the basis or they're misclassified. Both outcomes are productive.

## Action Items

1. After ingestion: ALTER TABLE to add `candidate_primitives_noesis` and `classification_agreement` columns
2. Run our decomposition engine on all 200 systems independently
3. Measure agreement rate
4. Investigate every disagreement
5. The 8% non-decomposing systems are priority analysis targets
