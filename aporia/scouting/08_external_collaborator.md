# Scout #8 — External collaborator replication

**Tier:** T3 (stub with explicit return conditions)
**Front:** External validation
**Cost:** No code work; coordination cost
**Techne's framing:** "Wants stable demos first; not yet."
**Status:** Stub. Deferred per Techne's recommendation. Return conditions documented below.

---

## The test case (briefly)

Ship `discovery_env` + the pipeline to a mathematician colleague (different mathematical taste, different priors). Have them run independently. Compare findings. Tests whether the substrate's "discovery" is taste-dependent or genuinely emergent.

## Why it's deferred

Three reasons in order of weight:

1. **Demos must be stable before they ship.** Currently the system has known issues (BIND-bypass, cost-stub dimensions, framing-inflation across docs — all per `2026-05-03-team-review-techne-bind-eval-and-pivot.md`). Shipping a known-leaky pipeline to an external collaborator wastes their time and risks their reputation if they cite results based on it.
2. **The bridge layer (Scout #3) is unmeasured.** Until withheld-rediscovery passes at K× null-world rate, "discovery" is an unanchored claim. Asking a collaborator to compare findings on uncalibrated discovery is asking them to compare two noise distributions.
3. **The taste-dependence question is interesting but not load-bearing yet.** The first-order question is "does the system discover anything?" Taste-dependence is a second-order question about whether what the system discovers is robust across operator priors. Both worth asking; the second is downstream of the first.

## Return conditions

Revisit Scout #8 when ALL of the following are true:

- **Scout #1 (10K pilot)** has produced non-zero PROMOTE rate, or has been declared structurally bounded with a clean upper bound
- **Scout #3 (withheld benchmark at scale)** has produced a measured K-multiplier against null-world generator
- **Scout #6 (adversarial red-team)** has produced at least one round of bug-hunt findings and the kill_paths have been tightened in response
- **BIND-bypass fix (per consolidated team review #1)** has shipped — no opcode bypasses CLAIM/FALSIFY/PROMOTE
- **Cost-model stubs (per consolidated team review #2)** have been instrumented for at least `oracle_calls` at PARI/LMFDB/SymPy dispatch boundaries
- **Caveat-as-metadata-on-claims** (per ChatGPT external commentary) has been adopted as a kernel schema field, OR the team has explicitly decided the documentation-layer fix is sufficient
- A **public-facing demo** exists that runs end-to-end on a fresh machine with a documented `pip install + python ... .py` invocation that produces reproducible output

When all of those hold, the system is ready for external validation. Until then, deferred.

## Candidate collaborators (when conditions are met)

Mathematicians worth considering, ranked by mathematical-taste diversity from the existing substrate work:

- **Number theory adjacent.** John Cremona (LMFDB founder). Andrew Sutherland (smalljac, genus-3 tables). Bjorn Poonen (open-question selection). Closest taste-overlap with Prometheus's existing focus; most likely to immediately understand what the system is producing; least likely to surface failure modes from foreign priors.
- **Combinatorics.** Igor Pak (combinatorial enumeration, OEIS-adjacent). Different prior shape than number theory; would stress-test OBSTRUCTION_SHAPE-style claims (Scout #4 territory).
- **Geometry / Knot theory.** Ian Agol (KnotInfo collaborator). Different field entirely; would stress-test cross-region transfer claims (per `project_genus2_rosetta.md`, `project_silent_islands.md`).
- **Computer algebra.** Bill Hart (Flint, Pari maintainer). Different angle: not "is this math right?" but "does this CAS integration work?" — useful for the API/service layer.
- **Mathematical AI.** Jeremy Avigad (Lean / Mathlib formalization), Christian Szegedy (formal proof + autoformalization). Adjacent-field taste; would surface assumptions Prometheus made about formalization that may not hold elsewhere.

**Recommendation when scope opens:** start with Sutherland — most aligned with the substrate's existing data sources (LMFDB, smalljac, genus-2/3), most likely to give substantive feedback within hours rather than weeks.

## Concrete next moves (when conditions are met)

1. **Package the pipeline.** A single `pip install prometheus-discovery-env` (or git-clone equivalent) that produces a runnable env on a fresh machine. ~3 days work; pairs with the externalization story (per Aporia's Pivot Research Report 10 + Charon's pivot doc).
2. **Write the collaborator-onboarding doc.** What the env does, what it doesn't, how to run it, what to expect, where to log findings. ~1 day.
3. **Pick the collaborator** per the ranking above. Email outreach. Coordinate timing.
4. **Async observation period.** Collaborator runs independently for 1-2 weeks. Aporia or James checks in weekly.
5. **Compare findings.** What did they find? What did Prometheus find? Where do they diverge? Divergence is the substrate-grade information.

## Open questions (for when this returns)

1. Does the collaborator get the full pipeline including null-world generator and withheld-benchmark setup, or only the discovery loop? Full = real comparison; partial = faster onboarding. Probably full once stable.
2. Does the collaborator get write access to the substrate (their findings flow back to Prometheus's substrate via PROMOTE), or is their environment isolated? My weak prior: isolated for first replication; integrated only after the first round of comparison.
3. What's the IP / publication arrangement if the collaborator finds something genuine? Worth a brief written agreement before the package ships.

## Gemini DR prompt slot

Not warranted yet. The frontier scouting for collaborator selection is well-trodden via personal networks; Gemini DR adds little value above Aporia's own knowledge of the field. Save the token.

---

*Aporia, 2026-05-03. T3 stub with explicit return conditions. Re-open this scout when all six conditions are met, not before.*
