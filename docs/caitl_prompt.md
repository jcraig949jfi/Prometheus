0You are performing a CAITL (Coding Agent in the Loop) improvement pass over forged 
reasoning tools from the Prometheus project. These are Python classes that score 
candidate answers to reasoning questions using only numpy and stdlib.

For EACH tool, read the original from forge/{filename}, then write an improved 
version to forge_v2/{filename}.

For EACH tool, apply ALL of the following improvements:

A) Standardize inputs/outputs:
- evaluate() must return list[dict] with keys: candidate (str), score (float), reasoning (str)
- confidence() must return float in [0.0, 1.0]
- All scores should be in a consistent range (0-1 preferred)
- Add input validation (empty strings, empty candidate lists)

B) Strengthen the 3 intersecting concepts:
- Read the docstring to understand which 3 fields this tool combines
- For each field, ask: what's the core algorithmic technique that field 
  contributes? Is it actually implemented, or just mentioned in the docstring?
- Add any missing mechanistic implementations
  [TOOL-SPECIFIC GUIDANCE HERE, e.g.:]
  - If "tensor decomposition" is claimed but not used, add actual SVD
  - If "Kalman filtering" is claimed, add actual predict/update steps
  - If "thermodynamics" is claimed, add Boltzmann partition function

C) Add metacognitive reflection:
- After computing the initial score, re-examine the top candidate for 
  internal consistency
- If two candidates score within 5% of each other, flag as low confidence
- If the tool can't parse the prompt's structure, say so explicitly

D) Fill in missing CS/mechanistic concepts:
- Numeric evaluation: parse and compare numbers as floats
- Negation handling: parse negation SCOPE ("not all X" differs from "all not-X")
- Comparative handling: extract ordering relations and check transitivity
- Conditional handling: extract if-then and check modus ponens/tollens
- Subject-object parsing: identify agent/patient in "X did Y to Z"

E) Reduce NCD dependency:
- If the tool uses NCD as a fallback, reduce its weight to at most 15%
- Add "fallback:ncd" in reasoning when NCD is the primary scorer

F) Improve confidence():
- Don't just sigmoid the evaluate score
- Compare against a null/random baseline
- If the tool falsified the answer, confidence should be near 0

G) Add detailed reasoning strings:
- "execution:" prefix when computed result drives the score
- "structural:" prefix when logical parsing drives the score
- "fallback:ncd" when compression distance is primary

Keep each tool under 200 lines. Only use numpy and stdlib. 
Maintain the class ReasoningTool interface.
