# Concept Seed Sources — 2026-04-06
## External databases that can seed our concept bridge layer

---

## DOWNLOADED

### 1. Wikidata Mathematical Concepts (Q24034552)
**File:** convergence/data/wikidata_math_concepts.json
**Objects:** 2,166 concepts with QIDs, labels, descriptions, aliases
**Examples:** infinity, Mandelbrot set, function, axiom, Fibonacci number, integral, coordinate system
**Bridge value:** HIGH — each concept has a Wikidata QID that links to other Wikidata entities (physics concepts, theorems, mathematicians). The aliases field enables fuzzy matching to our existing datasets.
**Next step:** Map Wikidata concept labels to our concept_index entries. Any match = a Wikidata-grounded bridge.

### 2. Wikidata Mathematical Objects (Q246672)
**File:** convergence/data/wikidata_math_objects.json
**Objects:** 32 objects (narrow class — spheroid, cross entropy, etc.)
**Bridge value:** LOW — too few objects to be useful alone

---

## AVAILABLE TO DOWNLOAD

### 3. MMLKG (Mizar Mathematical Library Knowledge Graph)
**Source:** figshare.com/articles/dataset/23528316
**Size:** 2.2 GB (GraphML + CSVs)
**Objects:** Full Mizar library as a knowledge graph — definitions, theorems, proofs with typed edges
**Bridge value:** EXTREMELY HIGH — this is a formal proof graph that overlaps with mathlib AND Metamath. Would triple our proof-network data.
**Blocker:** 2.2GB download + parsing. Worth it but schedule as a separate task.

### 4. MaRDI Knowledge Graph (Mathematical Research Data Initiative)
**Source:** portal.mardi4nfdi.de, SPARQL at sparql.mardi.ovh
**Objects:** Mathematical research data linked to Wikidata
**Bridge value:** HIGH — connects math objects to software, publications, and datasets.
**Blocker:** SPARQL queries work but need proper endpoint URL and query construction.
**Next step:** Explore SPARQL endpoint to understand schema, then bulk query.

### 5. MathAlgoDB (MaRDI Algorithm Database)
**Source:** mathalgodb.mardi4nfdi.de
**Objects:** Mathematical algorithms with properties, implementations, connections
**Bridge value:** MEDIUM — connects algorithms to problems and software
**Blocker:** Requires login for downloads. SPARQL endpoint available.

### 6. OpenAlex Concepts Taxonomy
**Source:** OpenAlex API (already used by Eos)
**Objects:** 65K+ academic concepts in a hierarchy, each with Wikidata QID
**Bridge value:** HIGH — maps every academic paper to concepts. We could map our datasets to OpenAlex concepts and find which papers connect them.
**Next step:** Download the concepts taxonomy (~65K entries) and map to our concept_index.

---

## EXISTING RESOURCES (already referenced in architecture)

### Literature-Based Discovery tools
- **Semantic Scholar API** — already integrated in external_research.py
- **arXiv API** — already integrated
- **Tavily** — already integrated

### Citation topology tools (for Sleeping Beauty detection)
- **Connected Papers** — web tool, no API
- **Research Rabbit** — web tool, no API
- **Litmaps** — has API, could integrate

### Semantic claim extraction
- **Elicit** — AI research assistant, no bulk API
- **Consensus** — claims search, limited API

---

## HOW THESE SEED OUR CONCEPT LAYER

Current concept_index.py extracts concepts from our 5 datasets computationally.
These external sources add a **canonical concept vocabulary**:

1. **Wikidata QIDs** become concept identifiers (e.g., Q47577 = "Fibonacci number")
2. **Wikidata aliases** enable fuzzy matching ("Fibonacci" in Fungrim → Q47577)
3. **OpenAlex concepts** link papers to our concepts (paper about "L-functions" → our LMFDB data)
4. **MMLKG** adds a formal proof graph that bridges mathlib and Metamath through shared definitions
5. **MaRDI** links mathematical objects to their computational implementations

The result: our 12,315 extracted concepts get **grounded in a global vocabulary**.
New bridge detection becomes: "these two objects map to the same Wikidata concept
but exist in different datasets and have never been connected in the literature."

That's Swanson's UPK model with a canonical identifier layer.
