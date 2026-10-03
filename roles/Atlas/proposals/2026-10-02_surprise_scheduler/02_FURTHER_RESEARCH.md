# Further research recommended before freezing E0-E6

Atlas, 2026-10-02. PROPOSAL; nothing executed. These are reading and verification tasks, mostly desk work, that
would change the design if their answers differ from what is assumed. Ordered by how much each could change the
series.

## R1. Verify the external claims the series leans on (blocking for E2 and E4)

The operator note makes several claims Atlas has NOT checked. They are tagged [UNVERIFIED-EXT] in 01. Verify each
against the primary source, the paper or the repository, not a summary:

| # | claim (from the note) | why it matters | where to check |
|---|---|---|---|
| a | AutoDiscovery uses Bayesian surprise (LLM prior-to-posterior belief shift) as the MCTS reward, with progressive widening | defines arm P2 | Ai2 AutoDiscovery paper and code |
| b | It found "5-29% more surprising discoveries" than alternatives across 21 datasets, under a fixed hypothesis budget | sets the expected effect size, and so the E2 power and eligibility count | paper, results section; check what "surprising discovery" was scored against |
| c | On a UW challenge with 24,000 synthetic nuclear-reactor configurations, about half the hypotheses were illogical and none were worth pursuing; it did better on real measurements | the motivating failure for E4 | the challenge report or write-up |
| d | A June 2026 follow-up: beliefs updated with prior evidence plus retrieval over past discoveries; "37.5% of static-surprise events were spurious"; +30.6% accumulated non-stationary surprise across 5 domains | defines optional arm P5 and the E5 framing | the follow-up paper |
| e | The Asta AutoDiscovery repository is Apache-2.0, supports local structured datasets, budgets, MCTS parameters and a search intent; the older research code supports bring-your-own data and resumable MCTS | decides whether P2 is used as-is or re-implemented | the repository LICENSE and README |

Additional checks:
- **How AutoDiscovery defines and scores "surprise"**, and whether its "discoveries" were validated by anything other
  than the belief shift. If they were not, its headline metric is the one this series explicitly refuses as primary.
- **Whether its statistical tests control multiplicity across a search.** An MCTS that runs thousands of tests
  without FDR control will "discover" noise. E4 tests this; the paper may already answer it.

## R2. Literature the design should be checked against (prior art; avoid reinventing)
- **Bayesian surprise and information gain:** Itti & Baldi (Bayesian surprise as KL divergence between prior and
  posterior); Bayesian optimal experimental design and expected information gain (Lindley; Chaloner & Verdinelli;
  recent BOED reviews). Question: is "realised surprise" a good proxy for "expected information gain" when choosing
  the NEXT test? BOED says choose by EXPECTED gain, not by surprise after the fact.
- **Curiosity and intrinsic motivation:** learning progress (Oudeyer & Kaplan; Schmidhuber's compression progress),
  versus prediction error. The "noisy TV" problem is the RL version of chasing artefacts: an agent rewarded for
  unpredictability is drawn to irreducible noise. That is exactly the false-finding risk this series measures.
  Learning-progress rewards are the standard fix, and they map to E5.
- **MCTS with progressive widening:** Coulom; Chaslot et al.; Couëtoux et al. (double progressive widening for
  continuous spaces). Plus bandit allocation of experiments (UCB, Thompson sampling) as simpler baselines that should
  be added to E2 if cheap.
- **Sequential and multiple testing in adaptive search:** e-values and anytime-valid inference (Vovk & Wang; Ramdas
  et al.); online FDR control (alpha-investing, LORD/SAFFRON). These are the right tools for the E2 certification gate
  under adaptive, unbounded hypothesis streams.
- **Automated science systems:** Adam/Eve robot scientists (King et al.); data-driven discovery benchmarks
  (DiscoveryBench, ScienceAgentBench and similar); "AI Scientist"-style pipelines and their reported failure modes.
  Look specifically for any benchmark that scores ARTEFACT-CHASING, not just hit rate.
- **Open-endedness and novelty:** novelty search (Lehman & Stanley); POET and its novelty estimator (Harmonia's
  09-30 ruling on POET novelty.py found regime change at n=5 and deflation; relevant to observer O8); quality-diversity.
- **Forensic and meta-science of artefacts:** the garden of forking paths (Gelman & Loken); many-analysts studies.
  Both bear on what share of a record's "findings" an automated searcher should be expected to reproduce
  spuriously.

## R3. Internal Prometheus work to read before freezing (Atlas did not read these for this proposal)
- **Ananke's 2026-09-30 inference-harvest deliverables** (roles/Ananke/research/harvest/, if produced). In particular
  any PTE_CAUSAL_AUDIT and PTE_INSTRUMENT_GAPS: they may hold PTE items for the key.
- **Tyche's residual catalogue** (tyche/residuals/v0_1, 122 entries) is a ready-made source of OPEN items and
  "residual kind" labels. Check its overlap with key candidates. Its tags are model-assigned (validate() proves the
  quote exists, not that the phenomenon is real).
- **The Artemis R-11 gate census codebook and the CVT-R prereg:** reusable as the "ruler can fail" check and the
  heredity certificate inside the certification gate.
- **Harmonia's STANDING_RULES F1-F8 (09-30):** each is a verified way a verdict was predetermined. They are
  candidate veto signatures.
- **The operator's Phase 3 / RSO and ruler-certification documents**, which the note refers to. Atlas has not read
  them. The E2 certification gate should match whatever Phase 3 defines as "certified".
- **Prior Atlas work:** atlas.policy/2 scoring and its saturation (ONT s0; LEDGER 09-24); the R06 comb signal (33
  nulls with rich telemetry). These are the natural first application if E2 succeeds.

## R4. Design questions that need a small pilot or a desk calculation, not reading
1. **Eligibility count for E2.** Given the E1 table's size, how many distinct hypotheses can the generator produce,
   and how many key items are reachable by ANY hypothesis the generator can express? If many key items are
   unreachable, recovery rates are capped and the comparison is uninformative. (This is the program's
   recurring F1 failure: an unattainable gate.)
2. **Power.** At the plausible effect size (from R1b), how many seeds and tests per arm separate P2 from P3?
3. **Cost envelope.** Tokens per test-cycle for LLM arms, times arms, times seeds. The operator needs this number
   before approving E2.
4. **Generator bias.** If the hypothesis generator is itself an LLM, all arms inherit its prior over what to
   propose. Only the SELECTION differs. Decide whether a non-LLM generator (combinatorial over table columns) should
   be one condition.

## R5. Infrastructure Atlas would need (Atlas-internal; useful regardless of this series)
- Index adapters for PTE, BEE, Aether, Ensorain, Hecate and Tyche, plus the NPE campaign directories after 09-22. Their
  absence is the main E1 blocker.
- An as-of view of the index: rows and columns exactly as they stood on date T. Partly available via
  first_harvest_id and commit dates; it needs a small query layer.
- Ruler-side fields (ruler_id, ruler_can_return_opposite, zero_parameter_baseline, author_family, readout_type), as
  proposed in HARVEST ONT s5. E2's veto list depends on them.
