"""Phase 3 requirements, OPUS-5.5 (Epimetheus). Single source of truth for REQUIREMENTS.md tables and
requirements.jsonl. Derived from first principles plus the recovered failure history, BEFORE any salvage
reading of engine source (REQUIREMENTS.md s0). Version 2: revised after the five-lens critic panel and the
architecture judge (REQUIREMENTS.md s9 lists every change).

Fields
  id         stable identifier CAT-NN (merged ids are kept with pri WITHDRAWN and a pointer)
  pri        REQUIRED | HIGH VALUE | EXPERIMENTAL | REJECTED/AVOID | WITHDRAWN
  gate       when it must exist / be satisfied:
               SLICE       built and passing before the vertical slice's X1 verdict (CMP-07)
               CORE        built and passing before the first L1 verdict of any discovery experiment
               RULE        zero-cost design rule enforced by a static check
               GATE-NULL   before any null is typed above apparatus level
               GATE-L2..L5 the verdict job refuses a claim at that level until met
               GATE-EXT    before externalisation
               GATE-C:<x>  before the first campaign of type x
  enforce    BLOCK (a named component refuses) | RULE (static check in CI) | FLAG (alarm only) | AUDIT | PROSE
  title, text, why
  motive     historical failure classes (Tityos T01..T24; Sisyphus SD1..SD15; Tantalus TD1..TD19; Ixion ID1..ID12)
  alt        alternative considered
  test       discriminating test or verification
  fake       counterfeit: a form-valid, content-false artifact the enforcement must reject (future CI fixture)
  build      build inference: 0 (design rule) | S (<5M tokens processed) | M (5-30M) | L (30-100M) | XL (>100M)
  op         inference when operated: NONE | FORK | HEAVY
"""

CATEGORIES = [
    ("SCI", "Scientific requirements"),
    ("ORG", "Organism requirements"),
    ("DEV", "Developmental requirements"),
    ("WLD", "World requirements"),
    ("PRS", "Pressure / search requirements"),
    ("MEA", "Measurement requirements (rulers, baselines, qualification)"),
    ("CAU", "Causal-analysis requirements"),
    ("TRF", "Transfer requirements"),
    ("PRV", "Provenance requirements"),
    ("REP", "Reproducibility requirements"),
    ("AGR", "Anti-prior / anti-gravity requirements"),
    ("CMP", "Compute requirements"),
    ("INF", "Inference requirements"),
    ("NRG", "Energy requirements"),
    ("HUM", "Human-attention requirements"),
    ("OUT", "Publication / output (externalization) requirements"),
]
PRIORITIES = ["REQUIRED", "HIGH VALUE", "EXPERIMENTAL", "REJECTED/AVOID", "WITHDRAWN"]
GATES_FIXED = ["SLICE", "CORE", "RULE", "GATE-NULL", "GATE-L2", "GATE-L3", "GATE-L4", "GATE-L5", "GATE-EXT", ""]
ENFORCE = ["BLOCK", "RULE", "FLAG", "AUDIT", "PROSE", ""]
BUILD = ["0", "S", "M", "L", "XL"]
OP = ["NONE", "FORK", "HEAVY"]

TAXONOMY = {
    "T01": "measurement carries its own answer", "T02": "self-verdicting", "T03": "controls that cannot fail",
    "T04": "positive control absent", "T05": "invalid null / no chance floor", "T06": "tautology",
    "T07": "construction / sampling artefacts", "T08": "baseline omitted", "T09": "selection effects",
    "T10": "statistical malpractice in gates", "T11": "post-exposure change", "T12": "unreachable design",
    "T13": "world or organism too weak", "T14": "label / proxy for property", "T15": "novelty conflation",
    "T16": "mechanism by description", "T17": "improper independence", "T18": "provenance failure",
    "T19": "status from wrong layer", "T20": "safeguards never wired", "T21": "activity read as productivity",
    "T22": "auditor commits the class", "T23": "validated != deployed configuration", "T24": "LLM measurement hazards",
    "SD1": "label-for-property", "SD2": "world-made copies", "SD3": "construction as heredity",
    "SD4": "count-fixed rulers", "SD5": "search policy read as landscape", "SD6": "selection on evaluation set",
    "SD7": "controls cannot fail / always fire", "SD8": "geometry-forced nulls", "SD9": "author-fit instruments",
    "SD10": "positive control read as signal", "SD11": "replay counted as replication", "SD12": "process state lying",
    "SD13": "post-exposure amendment", "SD14": "rules reconstructed from memory", "SD15": "monoculture of evidence",
    "TD1": "constant beats zero reference", "TD2": "tuned same-class baseline missing", "TD3": "definition restatement",
    "TD4": "controls forced by construction", "TD5": "one-shot events clear gates", "TD6": "payload label maps to answer",
    "TD7": "self-rating", "TD8": "hidden-variable sensing", "TD9": "construction artefact read as physics",
    "TD10": "shaping terms reward proxies", "TD11": "pooling hides structure", "TD12": "wrong statistical unit",
    "TD13": "capacity patching manufactures residual", "TD14": "validation set contains planted motif",
    "TD15": "format/prior/template gains as reasoning", "TD16": "transport failure as content",
    "TD17": "activity read as health", "TD18": "authored instances as exhibitions", "TD19": "name collisions",
    "ID1": "detectors without responders", "ID2": "guards that cannot fire", "ID3": "grading self-reports",
    "ID4": "label tables outlive writers", "ID5": "index coverage lag", "ID6": "class-word inflation",
    "ID7": "control-regime churn", "ID8": "reinvention instead of sharing", "ID9": "consumer invents producer interface",
    "ID10": "host handover strands services", "ID11": "credentials in tracked files", "ID12": "name reuse hides lineage",
}

R = []


def req(id, pri, gate, enforce, title, text, why, motive="", alt="", test="", fake="", build="0", op="NONE"):
    R.append(dict(id=id, cat=id.split("-")[0], pri=pri, gate=gate, enforce=enforce, title=title, text=text,
                  why=why, motive=motive, alt=alt, test=test, fake=fake, build=build, op=op))


# =============================================================================================== SCI
req("SCI-01", "REQUIRED", "SLICE", "BLOCK", "Per-claim evidence profile computed by the verdict job",
    "Every result carries a profile scored separately on Q, S (substrate expressibility), W (world demand), R (ruler "
    "validity), B (baseline discrimination), Rep (independent replication), M (mechanism by intervention), D "
    "(developmental origin) and T (transfer). The verdict job computes each axis from evidence rows; seats never score "
    "axes, and no axis is inferred from another.",
    "A single PASS/FAIL word hides which part of the apparatus produced the outcome; self-scored axes would be labels.",
    "T04 T12 T13 ID3; Tantalus 2.5-2.6; Sisyphus E1-E8", "Verdict word plus free-text caveat.",
    "Re-score 20 historical headline results; count category changes.",
    "A row whose S axis is set to Y by the submitting seat without a capacity-proof row: verdict job ignores it.", "M")
req("SCI-02", "REQUIRED", "SLICE", "BLOCK", "Mechanical claim ladder; seats write only L0",
    "Claims occupy L0..L6 (s7). Every promotion, including L0 to L1, is written only by the verdict job, which holds "
    "the only signing key (PRV-02); seats and model processes can write only L0 observation rows. Promotion criteria "
    "are executable predicates over committed, computed rows.",
    "Promotion by narrative is how attractive hallucinations became headlines.",
    "T02 T11 T22; Theseus 2,351 promotions; sigma_kernel PROMOTE without re-execution", "Prose rubric.",
    "Attempt to promote a planted false claim by every route a seat could use; all fail.",
    "An L1 row inserted directly into the store by a seat process: unsigned, ignored by every reader.", "M")
req("SCI-03", "REQUIRED", "SLICE", "BLOCK", "Typed nulls",
    "Every null names its type: substrate-expressibility, developability, world-demand, pressure, lifetime, "
    "curriculum, search-unquantified, search-bounded, ruler (incl. FAMILIAR-ONLY), statistics, budget, "
    "implementation, or phenomenon. A null is typed at the lowest tier not demonstrated; 'phenomenon' requires a null "
    "certificate (SCI-08).",
    "Most historical nulls were silent about the phenomenon because organism, world, ruler or search could not have "
    "produced a positive.", "T12 T13; TD (Ananke 30.6% physics-capped); Sisyphus E1-E8; Challenge 4f",
    "Record nulls as 'not found'.", "Reclassify historical reasoning nulls by type.",
    "A null row typed 'phenomenon' without a null-certificate id: refused.", "S")
req("SCI-04", "REQUIRED", "SLICE", "BLOCK", "Executable preregistration as an earlier commit",
    "Every experiment that can support L2 or emit a typed null is frozen as code (decision predicate, baselines, "
    "power/SESOI, attainable-verdict table, declared claim ceiling for positives and nulls) in a commit that is an "
    "ancestor of the first data commit; the runner refuses to execute against an unfrozen or modified predicate.",
    "Prose preregistration was amended after exposure; executed rules diverged from frozen rules; freezes could not "
    "be proven.", "T11 T23 SD13; E-003 C4.2; Ananke W-O; Nestor X-MAT; run_iq_null.py", "Prose prereg.",
    "Alter the predicate after freeze; runner refuses.",
    "A preregistration file committed in the same commit as its first data: runner refuses.", "M")
req("SCI-05", "REQUIRED", "SLICE", "BLOCK", "Reachability and attainability before freeze",
    "Before freeze, every verdict branch (PASS, FAIL, INDETERMINATE, and the phenomenon-level null branch) is shown "
    "reachable through the actual pipeline by constructed inputs; the outcome table partitions the outcome space; "
    "attainability ceilings created by construction (light-cone, capacity, identical random streams, parity "
    "invariants) are computed and published.",
    "Designs that could not return the outcome they reported absent were read as evidence.",
    "T12 SD8 TD4 TD9 (Bellerophon K3, Tyche H1/H6, Hecate UNFAMILIAR, IQ-NULL partition, SFE canary parity)",
    "Reviewers judge reachability.", "Automated branch-coverage run committed with the freeze.",
    "A freeze whose INDETERMINATE branch is unreachable by any constructed input: freeze refused.", "M")
req("SCI-06", "REQUIRED", "SLICE", "BLOCK", "Declared unit of replication",
    "Each experiment declares its unit of independence (lineage, founder, world instance, physics point, seed) and the "
    "verdict job computes n and SE at that unit; world families count as units for world-generality claims and never "
    "for substrate-generality claims; deterministic replay never counts as replication.",
    "Pseudo-replication and replay-as-replication inflated confidence.", "T10 SD11 TD11 TD12",
    "Count runs.", "Recompute SE at the declared unit for every verdict.",
    "A 50-row result from 6 lineages declared at row level: verdict job recomputes at lineage level.", "S")
req("SCI-07", "REQUIRED", "CORE", "BLOCK", "Anti-calibration set for kill paths",
    "Every battery or gate that can kill, demote or suppress a candidate is scored on a set of true-but-surprising "
    "known results (literature-derived and constructed) that it must not kill; its false-kill rate is published and "
    "bounded before it is used.",
    "A battery's false-kill rate is its false-negative rate; historical batteries killed true results unnoticed.",
    "Tityos E (cartography 0/4 known truths survived); PROTEUS-46 299,991-row suppression",
    "Measure false-pass rate only.", "Run each kill path on the anti-calibration set.",
    "A kill battery deployed without an anti-calibration score row: verdict job refuses its kills.", "M")
req("SCI-08", "REQUIRED", "GATE-NULL", "BLOCK", "Null certificate",
    "A phenomenon-level null is emitted only as NOT_OBSERVED(X | substrate, genome language, search, curriculum, "
    "lifetime, budget, pressure) with p_emerge below a frozen rate at the declared unit, and every element PASSING a "
    "frozen threshold: S (ORG-14), D (DEV-13, if developmental), W (WLD-02 margins exceed the ruler MDE), P (PRS-12), "
    "R (SCI-14 MDE <= SESOI; ruler not FAMILIAR-ONLY), reachability (PRS-03), lifetime (WLD-18), curriculum (WLD-08, if "
    "developmental), budget (CMP-06 curve not still rising) and bracket (SCI-13). A failed element types the null at "
    "that element. Before first use the checker refuses one constructed apparatus null per element and ADMITS a "
    "predicted genuine null (no evolved lifetime learning under P0 where P1 produces it).",
    "Without these, NO EMERGENCE is a statement about the apparatus (charter Q2); without a reachable phenomenon "
    "branch, every null stays an apparatus null forever.", "T12 T13 T04; Challenge 2e/4f; Necropolis TRUE_CORPSE",
    "Presence checklist.", "Checker qualification on constructed apparatus nulls and a predicted genuine null.",
    "A null with a needle estimate of 1e-12 against 1e6 evaluations labelled phenomenon-level: refused.", "M")
req("SCI-09", "REQUIRED", "SLICE", "BLOCK", "Declared claim ceilings (positive and null)",
    "Each experiment declares before running the highest ladder level and the strongest null type its design can "
    "support; results are capped there regardless of effect size.",
    "Designs built to probe were later cited as establishing mechanisms.", "T16; Nyx portability YES 533/549 untested",
    "Decide after results.", "Ledger check: no row exceeds its experiment's ceiling.",
    "An L3 row from an experiment declared ceiling L2: verdict job caps it.", "S")
req("SCI-10", "HIGH VALUE", "GATE-L4", "FLAG", "External validation track",
    "A small number of L3+ claims and qualified instruments are prepared as replication packages and offered to parties "
    "outside the Prometheus model family.", "Internal review is circular when one family fills every role.",
    "T17; B-prime never graded", "Internal cross-seat review.", "Count claims surviving external replication.", "", "M")
req("SCI-11", "HIGH VALUE", "CORE", "FLAG", "Prose correction propagation",
    "A lint flags committed prose that cites a retracted or demoted number (the mechanical part lives in SCI-16 and "
    "PRV-06).", "Corrections did not reach headlines.", "T18 (north_star.md; 127,000x ratio; F044)",
    "Annotate beside originals only.", "Plant a retraction; lint flags every citing document.", "", "S")
req("SCI-12", "REJECTED/AVOID", "RULE", "RULE", "Global scalar program score",
    "No single numerical 'sagacity' or 'North Star' score drives allocation automatically.",
    "A scalar target becomes the thing optimised.", "", "Composite yield index for scheduling.",
    "Static check: scheduler reads no composite score.", "", "0")
req("SCI-13", "REQUIRED", "GATE-NULL", "BLOCK", "Bracketed nulls",
    "No null in a (substrate, search, development, ruler) combination is typed phenomenon-level until that identical "
    "combination has produced a qualified positive of the same phenomenon type at an easier point on a declared "
    "difficulty axis (certificate component, horizon, composition depth, lifetime, budget, curriculum granularity, "
    "pressure level). The null is reported as a boundary between the last YES and first NO point. For every substrate "
    "the first lower bracket is X1 (evolved lifetime learning under P1 statistics and not under P0).",
    "Component proofs can all pass while their composition is broken; a located boundary is the most informative "
    "null shape.", "T12 T20", "Component-wise proofs only.",
    "Plant pipeline defects (ruler disconnected, mutation masked, prerequisites removed); each removes the lower "
    "bracket and the checker refuses phenomenon typing.",
    "A null whose bracket positive came from a different ruler version: refused (closure hash mismatch).", "S")
req("SCI-14", "REQUIRED", "GATE-NULL", "BLOCK", "Nulls as NOT_DETECTED_ABOVE(MDE) against a constructive SESOI",
    "Every experiment that can emit a null freezes a smallest effect size of interest anchored to a constructive "
    "organism (default 25% of the fixture's advantage over the best admitted baseline) and the MDE at power 0.8, "
    "computed by simulating scaled planted positives through the actual pipeline at the declared unit. A null is "
    "phenomenon-relevant only if the 90% CI excludes the SESOI; for emergence frequency, the 95% upper bound on p_emerge "
    "is below a frozen rate. Run counts (DEV-09) and independent search runs are set by this calculation.",
    "Power appeared only for positives; failure to reject was read as absence.", "T10 T12",
    "Power analysis for positives only.", "Scaled-fixture simulation recovers the frozen MDE.",
    "A null run with n below the SESOI calculation: refused phenomenon typing.", "S")
req("SCI-15", "REQUIRED", "SLICE", "BLOCK", "Ledger-derived multiplicity, consumable splits, program constants",
    "The verdict job derives the multiplicity family and count from the primary store (all preregistered experiments, "
    "arms, world families and ruler variants sharing a hypothesis key); callers never supply it. Sealed splits carry a "
    "confirmatory-read budget and retire when spent; L2 needs a one-shot confirmatory run on a never-read split. "
    "Decision thresholds come from a versioned program constants file; any deviation also reports the verdict at the "
    "defaults.", "One-experiment-at-a-time preregistration leaves a garden of forking preregistrations open.",
    "T09 T10", "Per-experiment correction with caller-supplied n.",
    "20 variants against one split with one nominal pass: fails L2.",
    "A verdict computed with n_hypotheses=3 supplied by the caller: verdict job recomputes from the ledger.", "M")
req("SCI-16", "REQUIRED", "CORE", "BLOCK", "Dependency-driven mechanical demotion; challenge suspension",
    "Verdict rows store the hashes of all dependencies (ruler qualification, world certificate, plant set, statistics "
    "version, baseline-ladder version, preregistration). Revoking any dependency triggers re-evaluation and demotion of "
    "every dependent row to the level its surviving evidence supports. A registered challenge from any party suspends "
    "externalisation and further promotion (never archive status) until the Reality layer resolves it, with a "
    "per-challenger rate limit.", "Promotion was mechanical, demotion was not; detectors had no responders.",
    "T18 ID1", "Flag citing prose only.", "Revoke a ruler qualification; dependent L3 rows demote in one cycle.",
    "An L3 row still citing a revoked qualification hash after a cycle: alarm and freeze.", "M")
req("SCI-17", "REQUIRED", "RULE", "RULE", "Vocabulary lock on defined terms",
    "Terms defined in s3 (reasoning, abstraction, metacognition, constructing cognition, transferable or recursive "
    "sagacity, reasoning/developmental primitive, deliberation) appear about a claim in any committed artifact, ledger "
    "description or digest only when the matching predicate is TRUE in the verdict job for that claim id; a CI lint "
    "enforces it.", "Hallucinations survive at the naming layer.", "T14 T16 TD15",
    "Style guidance.", "Lint on a planted digest.",
    "A digest calling an L3 hub structure 'working memory': lint fails.", "S")
req("SCI-18", "REQUIRED", "GATE-L2", "BLOCK", "Per-family and per-cell reporting",
    "Effects are reported per world family and per generator-parameter cell; an effect claimed across families needs "
    "sign consistency in >= 2/3 of families and a heterogeneity test; a pooled-only effect is capped at L1; the "
    "admission rule and generator distribution are attached as the sampling frame.",
    "Pooling hid opposite-signed offsets and degenerate families.", "T07 TD11 (Cosmos offsets cancelled)",
    "Pooled effects.", "Planted cancelling families detected.",
    "A pooled L2 effect carried by one family: capped at L1.", "S")

# =============================================================================================== ORG
req("ORG-01", "REQUIRED", "SLICE", "BLOCK", "Persistent writable state (within-episode and cross-episode)",
    "Organisms have writable internal state persisting across steps (within-episode) and across episodes within a "
    "lifetime, declared separately. Capacity is demonstrated by a constructive organism reaching the ruler's "
    "qualification competence in the hardest admitted family; the state budget offered to search is >= 4x the state "
    "that organism uses.", "Hidden-state inference, retention and reuse are impossible without it; sizing at the "
    "minimal controller size guarantees S-failure for non-minimal evolved solutions.",
    "Tantalus 4.1; Ares one-bit worlds; Ananke i.i.d. targets", "Episode-reset or world-held memory.",
    "Constructive organism carries state across the certified horizon.",
    "A campaign whose state budget is below 4x the fixture's: launch refused.", "M")
req("ORG-02", "REQUIRED", "CORE", "BLOCK", "Selectable access to stored state (capacity, not a named primitive)",
    "Some organism in the substrate can store k items and retrieve the one cued by the world, with k swept; whether "
    "access is address-based, content-based, or developmentally constructed is a substrate property, not a mandated "
    "primitive.", "Binding and reuse need selectable access; mandating a particular addressing primitive would "
    "foreclose substrates where addressability must itself be constructed.", "Tantalus F (binding absent)",
    "Mandated address and content ports.", "Constructive organism for keyed recall.",
    "A substrate admitted with no keyed-recall capacity proof: admission refused.", "M")
req("ORG-03", "REQUIRED", "SLICE", "BLOCK", "Conditional control / dynamic routing",
    "Which internal operations execute can depend on internal state; shown by a constructive organism selecting among "
    "sub-procedures by a hidden cue.", "Composition needs state-dependent selection.",
    "Ananke straight-line programs; Ensorain fixed policies", "Straight-line programs.", "Capacity proof.",
    "Admission without the proof: refused.", "S")
req("ORG-04", "REQUIRED", "SLICE", "BLOCK", "Structural plasticity during lifetime",
    "Organisms can create, delete, copy and modify internal structure (not only values) during their lifetime as a "
    "consequence of their own activity and experience.", "Construction of cognition is unobservable otherwise.",
    "Aphrodite immutable improver; Ensorain fixed policy", "Parameter-only plasticity.",
    "Lattice switch: structural development off arm (ORG-20).",
    "A substrate whose 'structural' writes are confined to a fixed-size table: admission flags it.", "M")
req("ORG-05", "REQUIRED", "CORE", "BLOCK", "Internal steps decoupled from action (metered)",
    "Organisms can execute metered internal steps that emit no action; worlds allow but never require variable "
    "deliberation time. The compute-competence curve is an outcome descriptor (MEA-07), not a definition of cognition.",
    "Without it internal simulation cannot exist; making it a definitional criterion would exclude amortised and "
    "parallel cognition.", "", "One internal step per tick.", "Lattice switch: internal ticks off arm.",
    "A substrate where internal steps are free: admission flags missing metering.", "S")
req("ORG-06", "REQUIRED", "SLICE", "BLOCK", "Modifiable modification machinery (lattice switch)",
    "In the primary substrate, the lifetime update rules are represented in state the organism's own activity can "
    "change, so plasticity of plasticity is physically possible; it is a declared lattice switch whose effect is "
    "measured by matched single-switch arms on one code path. Its capacity proof (planted order-1, order-2, order-3 "
    "and maturation-clock organisms classified by DEV-14) is required before the first recursive-sagacity campaign.",
    "Recursive sagacity is unobservable when the improver is immutable code.",
    "Aphrodite (improver never changes); Ananke M3 one-time SETRULE bootstrap", "Fixed rule, evolvable hyperparameters.",
    "Switch-off arm loses the order-3 fixture's acceleration.",
    "An 'order-3' fixture whose acceleration survives the switch-off: capacity proof refused.", "M")
req("ORG-07", "REQUIRED", "SLICE", "BLOCK", "Resource accounting in the physics",
    "The physics reports structure held and internal steps executed per organism per tick; costs (if any) are a "
    "declared pressure (PRS-06), not part of the organism affordances.",
    "Costs and compression rulers need counts; counting is an instrument, cost is a pressure.",
    "Sisyphus E7", "Implicit costs.", "Counts reproduce under replay.", "", "S")
req("ORG-08", "REQUIRED", "SLICE", "BLOCK", "Instrument affordances, provenance shadow from day one",
    "Deterministic execution from keyed seeds; full-state snapshot/restore (bit-identical); substructure ids stable "
    "under rewrite; a material provenance shadow on every element (genome, rewrite event, transplant, model-authored "
    "edit); step-level trace on demand; intervention hooks for every carrier class listed by ORG-19.",
    "Mechanism claims need intervention; heredity and descent claims need material provenance, which was added "
    "late or never.", "T16 SD1 SD3; Ares W4", "Black-box organisms analysed by reading.",
    "Snapshot/restore bit-identity; transplanted known subroutine reproduces behaviour; shadow survives copy.",
    "A transplant whose provenance shadow is reset to 'genome': shadow audit fails.", "L")
req("ORG-09", "HIGH VALUE", "CORE", "FLAG", "Physical multiple timescales",
    "State with different persistence (evolvable decay/consolidation constants) is a physics option and a lattice axis.",
    "Lets pressure decide timescale use without named memory systems.", "Challenge 2", "Single timescale.",
    "Ablate timescale diversity on long-horizon families.", "", "S")
req("ORG-10", "HIGH VALUE", "CORE", "FLAG", "Invocable stored structure",
    "A stored structure can be executed or applied from more than one internal context.",
    "Reuse is a precondition for abstraction to pay.", "Crius workspace; 'invocation without content'",
    "Reuse only by copying.", "Shared-ablation detects one structure serving several tasks.", "", "S")
req("ORG-11", "HIGH VALUE", "CORE", "FLAG", "Neutral genotype-phenotype redundancy",
    "The genotype-to-phenotype map has neutral networks and the declared search can traverse them.",
    "Neutral paths were the recurring route to otherwise unreachable mechanisms.", "SD5; PROTEUS-46; Crius R-07",
    "Strict-improvement acceptance.", "Neutral fraction and connectivity to fixtures measured.", "", "S")
req("ORG-12", "EXPERIMENTAL", "GATE-C:social", "PROSE", "Inter-organism communication",
    "Channels with source identity available.", "Needed for social pressure; large search dimension.",
    "Ananke (no sender identity)", "None.", "After single-organism qualification.", "", "M")
req("ORG-13", "EXPERIMENTAL", "GATE-C:selfref", "PROSE", "Self-reference",
    "The organism can read parts of its own structure as data.", "Possibly needed for self-modification; invites "
    "trivial self-copying basins.", "SD2", "None.", "Arm comparison.", "", "S")
req("ORG-14", "REQUIRED", "GATE-NULL", "BLOCK", "Constructive capacity proofs by any recorded procedure",
    "For each (affordance, phenomenon class, substrate) triple a preregistered experiment depends on, a constructive "
    "organism obtained by a recorded procedure (hand construction, compilation from a reference program, "
    "verifier-guided synthesis, privileged optimisation with full world access, exhaustive or random search on a small "
    "instance) that exhibits the phenomenon and gains from it is committed before that experiment's first data commit. "
    "Proofs gate interpretation of nulls and launch of null-seeking campaigns; a reality-validated positive is its own "
    "existence proof. The false-capacity rate of each procedure against independently authored tests is reported.",
    "Without a constructive existence proof a null cannot distinguish impossible from not found; requiring hand "
    "construction would select substrates for human programmability.", "Challenge 1a S axis; T13",
    "Hand-built only; or argue from the instruction set.", "Fixture runs in CI; failure blocks the experiment.",
    "A 'capacity proof' that passes only on training instances: refused (sealed-instance evaluation).", "L")
req("ORG-15", "REQUIRED", "GATE-NULL", "BLOCK", "Expressible / developable / reachable / findable",
    "For each target record separately: expressible (ORG-14), developable (DEV-13), reachable (a path of stated "
    "length and fitness profile exists AND the declared acceptance rule and operators can traverse it, PRS-03), "
    "findable (declared search within budget, with rate). A null is typed at the lowest tier not demonstrated. "
    "Absence of expressibility is established only by proof (state or information bound, closure enumeration).",
    "Conflating the tiers turned search failures into substrate verdicts.",
    "Ergon/D-5 split; Tyche parity-3; Ananke XOR plant .850 never found; Ensorain E0 representable but not learnable",
    "Findable only.", "Each tier has its fixture or estimator.",
    "A null typed 'expressibility' on search evidence alone: refused.", "S")
req("ORG-16", "REJECTED/AVOID", "RULE", "RULE", "Named cognitive modules as built-ins",
    "No substrate ships with working-memory buffers, attention modules, hypothesis slots, confidence outputs, "
    "planners, world-model modules or labelled abstraction operators as primitives.",
    "They encode the familiar ontology and make discovery a restatement.", "TD3; Hecate familiarity by construction",
    "Provide familiar modules and search their wiring.", "Static audit of the primitive list at admission.",
    "A primitive named 'attend' or 'confidence': admission lint fails.", "0")
req("ORG-17", "REJECTED/AVOID", "RULE", "BLOCK", "World- or author-supplied competence",
    "Organisms whose competence is supplied by hand-coded policies, hand-written solvers, fixed classifiers or "
    "world-supplied operations are not used for claims about organism capability; the verdict job refuses claims "
    "whose capability survives ablation of the supplied component.",
    "The measured capability then belongs to the author.", "Tantalus 2.5; Apollo solvers; SD2",
    "Allow with caveats.", "Ablate the supplied component.", "", "S")
req("ORG-18", "REJECTED/AVOID", "RULE", "RULE", "Gradient descent through a fixed architecture as the primary substrate",
    "Backprop-trained fixed architectures are reference controls only.",
    "They fix the architecture the program wants constructed.", "", "Transformer as main organism.",
    "Static: primary substrate admission checklist.", "", "0")
req("ORG-19", "REQUIRED", "CORE", "BLOCK", "Substrate closure audit",
    "At admission, list every channel through which information can persist or route (structure, registers/state, "
    "timing/phase, organism-written world state, initialisation values, execution order, arbitration, resource "
    "levels, random streams) and supply an intervention operator for each channel class.",
    "Mechanisms carried by unlisted channels (zero-register dependence, write-back, timing) were invisible or misread.",
    "SD (zero-register dependence; write-back physics); Ananke bit held in flight", "List structural classes only.",
    "Planted organisms per channel are localised; an unlisted-channel organism fails the audit.",
    "A substrate whose random stream is shared across arms but unlisted: audit fails.", "M")
req("ORG-20", "REQUIRED", "SLICE", "BLOCK", "Physics-ablation lattice on one code path",
    "Every affordance of the primary substrate is a single switch or capacity knob on one bit-identical code path "
    "guarded by regression hashes (structural development, modifiable modification, invocation, timescale diversity, "
    "selectable access, internal ticks, self-reference as an arm). Each switch used by a preregistered experiment "
    "carries an affordance-necessity proof: a constructive organism that loses its target capability when only that "
    "switch is off. Arms differ only by switches and keyed random streams.",
    "The cleanest causal geometry in the record was single switches on a bit-identical path; developmental controls, "
    "plasticity-of-plasticity contrasts and construction tests are all single-factor contrasts inside one physics.",
    "Aether G1 lesion laws; SFE canary identical-stream null (SD8)", "Separate kernels per variant.",
    "Regression hashes identical across switch settings on switch-irrelevant runs.",
    "A switch implemented as a separate code branch with its own RNG consumption: regression hash gate fails.", "L")
req("ORG-21", "REQUIRED", "GATE-L3", "BLOCK", "Encoding axis",
    "The primary physics is available in >= 2 genotype encodings (direct and developmental/indirect); any claim "
    "attributed to physics rather than encoding must hold under both.",
    "Many historical physics effects were encoding effects (1-byte aliases moved acquisition 1/64 -> 39/64).",
    "sis-b implication 9", "One encoding.", "Claim re-run under the second encoding.",
    "A physics claim supported under one encoding only: capped at L2.", "M")

# =============================================================================================== DEV
req("DEV-01", "REQUIRED", "SLICE", "BLOCK", "Development separate from evolution",
    "Two declared timescales: search acts on genomes (including developmental rules); development acts on state "
    "within a lifetime through experience; each can be switched off independently (lattice).",
    "Search need only find a rule that bootstraps better machinery; untestable if fused.", "Challenge 4a",
    "Direct evolution of mature organisms.", "Frozen-development arm vs developing arm.", "", "S")
req("DEV-02", "REQUIRED", "SLICE", "BLOCK", "Claim-indexed developmental control table",
    "'Curriculum produced it' needs same-compute direct exposure plus shuffled order; 'development carries it' needs "
    "the retention-boundary frozen control (snapshot restored at every episode boundary) and, where the substrate has "
    "parameters, a parameter-only arm; savings or transfer needs the equal-compute irrelevant-experience twin; "
    "contingency claims need yoked replay (the organism fed the recorded stream of a comparison organism or teacher); "
    "every claim needs constant/lookup baselines per rung. Arms are lattice switches with keyed random streams.",
    "Otherwise 'the curriculum produced it' is indistinguishable from 'more compute produced it'.",
    "Challenge 4g; BEE ON vs YOKED", "Five arms for every claim.", "Verdict job checks the table per claim type.",
    "A savings claim without the irrelevant-experience twin: refused.", "S")
req("DEV-03", "REQUIRED", "CORE", "BLOCK", "Snapshot now, analyse later",
    "Developmental runs store full-state snapshots at a declared cadence and at detected change points within a "
    "declared storage cap; localisation, retention, reuse, savings, transplant and cross-run comparison are computed "
    "from snapshots on demand, only for runs whose ceiling is >= L3.",
    "The trajectory is the measured object, but the full battery at every transition multiplies cost.",
    "Challenge 4d", "Full battery per transition.", "Random snapshots restore bit-identically and continue identically.",
    "A snapshot that restores but diverges on continuation: run invalidated.", "M")
req("DEV-04", "REQUIRED", "SLICE", "BLOCK", "Capacity vs realisation by retention boundary; DC as reaction norm",
    "Realised competence R(o_t, T) is measured from snapshot o_t on sealed instances with every state change "
    "discarded at episode end (within-episode adaptation counted and its curve reported). Development is any change "
    "that survives the retention boundary. Developmental capacity is a reaction norm: competence distribution over N "
    "runs under a curriculum panel (standard, shuffled, direct, impoverished) at budgets spanning >= 1.5 decades ending "
    ">= 3x beyond the saturation budget of a reference precompiled genome; 'capacity exceeds realisation' needs "
    "crossing evidence.", "Freezing by mechanism deletes working memory in substrates where memory and development "
    "share a mechanism; single-budget DC ranks precompiled genomes above developing ones.",
    "Challenge 4e", "Score only; single budget.", "Two-assay protocol; planted precompiled vs developing organisms "
    "cross.", "A DC claim from one budget point: refused.", "M")
req("DEV-05", "REQUIRED", "GATE-L4", "BLOCK", "Construction test",
    "A construction claim requires: (i) experience-specificity (experience explains more structural variance than "
    "developmental noise; structure from experience A carries C_A not C_B); (ii) capability carried by developed "
    "structure (ablation with sham); (iii) construction advantage: at matched experience and compute the strongest "
    "available value-only learner on a pre-grown generic structure of the developed organism's final size fails to "
    "reach C, and is shown able to reach a planted parametrically reachable target (the control can succeed); (iv) "
    "optional proof that no value setting of the birth structure expresses C. The substrate declares at admission its "
    "form/value partitions (>= 2); (iii) must hold under each. Where no partition is meaningful, construction is "
    "claimed from (i)+(ii) and the record says (iii) was not applicable.",
    "Growth in birth size is not construction; a weak re-optimiser rewards absence of a strong control.",
    "", "Topology-necessity by weak re-optimisation.", "Planted constructive vs parametric organisms.",
    "A construction claim whose value-only control never reached its planted reachable target: refused.", "M")
req("DEV-06", "REQUIRED", "SLICE", "BLOCK", "Grading outside the organism's reach",
    "Curriculum graders, answer keys and world internals are inaccessible to the organism except through declared "
    "observations; enforced by the differential all-channel leak audit (WLD-07).",
    "A curriculum that leaks its answers teaches only reading.", "T01 TD6 (R6 truth in probe; Icarus R5)",
    "Code review.", "Planted leaky curriculum flagged.", "", "S")
req("DEV-07", "HIGH VALUE", "CORE", "FLAG", "Idle periods",
    "Worlds include periods with no input and no reward in which organisms may run metered internal steps.",
    "Lets consolidation emerge without naming it.", "", "Named consolidation phase.",
    "Idle vs no-idle on retention and savings.", "", "S")
req("DEV-08", "REQUIRED", "GATE-L4", "BLOCK", "Transition claims need change-point evidence (form is an outcome)",
    "Any claim asserting a developmental transition or stage requires change-point rejection of a smooth-learning "
    "null with a coinciding diff on a carrier shown (by ablation) to carry the new capability. Whether construction "
    "was step-like or gradual is otherwise reported as an outcome, never a promotion criterion.",
    "Stage-like development is a hypothesis; making it a promotion criterion would exclude gradual construction.",
    "", "Read stages off curves.", "Planted step vs smooth trajectories under neutral churn.",
    "A 'stage' claim whose coinciding diff touches only neutral structure: refused.", "S")
req("DEV-09", "REQUIRED", "CORE", "BLOCK", "Distributional capacity for capacity claims",
    "Capacity claims are estimated over N independent developmental runs per genome, N from SCI-14; inside search, "
    "single developmental runs per evaluation are allowed with k >= 3 re-evaluations of elites before archiving.",
    "Development is stochastic; but N runs per fitness evaluation would shrink search reach N-fold.",
    "T09 (winner's curse)", "One run per genome; or N per evaluation.", "Variance decomposition genome vs run.",
    "A capacity claim from one run: refused.", "S")
req("DEV-10", "HIGH VALUE", "GATE-L4", "FLAG", "Re-development after damage",
    "Secondary capacity measure against damage-elsewhere and naive-development controls.",
    "Separates capacity to construct from possession of a construct.", "", "None.", "Planted organisms.", "", "S")
req("DEV-11", "REJECTED/AVOID", "RULE", "RULE", "Curricula that teach the mechanism",
    "No shaping rewards on internal states, no hand-specified intermediate structures, no rewards for producing named "
    "representations; the preregistration linter rejects reward terms that read organism internals.",
    "Shaping the mechanism makes its emergence a restatement.", "TD10", "Shaping toward expected structures.",
    "Linter on a planted internal-reading reward term.", "", "0")
req("DEV-12", "EXPERIMENTAL", "GATE-C:transmission", "PROSE", "Transmission of developed structure",
    "Non-genetic inheritance as an arm.", "Possible accelerant; confounds credit if always on.", "", "Always on/never.",
    "Arm comparison after qualification.", "", "S")
req("DEV-13", "REQUIRED", "GATE-NULL", "BLOCK", "Developmental capacity proof (developable tier)",
    "For each developmental target, commit a genome g* in the genome language the search operates on (decodable and "
    "mutable under the declared operators) that, from the standard birth state under curriculum C within lifetime L, "
    "develops the capability in >= q of N runs, before any developmental null in that substrate is interpreted. If no "
    "g* can be built, developmental nulls are typed 'developability not shown'.",
    "A static capacity proof never shows that any developmental program in the genome language can build the "
    "capability within one lifetime: the missing middle of Challenge 4.", "Ensorain E0; Aphrodite; Challenge 4b/4f",
    "Static proofs only.", "g* with plasticity disabled must fail; decode-mutate-redecode membership check.",
    "A g* that only works with a hand-inserted mature structure at birth: refused (birth-state check).", "L")
req("DEV-14", "REQUIRED", "GATE-C:RS", "BLOCK", "Write-provenance order instrument",
    "Every lifetime write is tagged with its writer set (trace plus intervention confirmation); developed structure "
    "receives a write order (0 birth; k+1 when written with an order-k writer). The instrument supports reversion of "
    "all structure at or above an order and donor-history dose-response transplants; it is qualified on planted "
    "order-1, order-2 (library as proposal prior), order-3 (self-modified builder) and maturation-clock organisms.",
    "Recursive sagacity must be separated from fixed-rule-plus-library learning-to-learn and from maturation clocks; "
    "transplant semantics alone assume the split they try to define.", "Aphrodite library-as-data; Ananke SETRULE",
    "Machinery/content by transplant labels.", "Four planted organisms classified correctly.",
    "A maturation-clock organism classified order-3: instrument refused.", "L")

# =============================================================================================== WLD
req("WLD-01", "REQUIRED", "SLICE", "BLOCK", "Cognitive depth certificate (bound-typed)",
    "Every admitted family carries certificate components reported as (value, bound type exact|upper|lower, method, "
    "policy language, compute). CORE minimum: gap_react (exact over stochastic memoryless policies where |O| permits); "
    "gap_lookup on held-out instances after canonicalisation by the family's symmetries; d_horizon; d_mem as a bracket "
    "(lower bound by fooling-set / reward-relevant automaton minimisation for deterministic hidden-state families or "
    "causal-state reconstruction for designed processes; upper bound by an explicit controller) at >= 3 performance "
    "levels including the ruler's qualification competence. Further components (d_comp relative to a declared policy "
    "language; d_hyp; d_voi; d_ns; d_think; adaptive gap and payback; d_unfam; policy multiplicity) are REQUIRED for "
    "families hosting claims about them. Robustness across generator variants becomes REQUIRED once experiment X2 "
    "passes.", "World size is not cognitive depth; reference policies give only upper bounds while admission needs "
    "lower bounds.", "Tantalus 4.2; SD E1; T13", "Grid size as depth.", "Certificates predict which baselines fail (X2).",
    "A certificate reporting d_mem from a reference controller labelled 'exact': validator refuses.", "L")
req("WLD-02", "REQUIRED", "SLICE", "BLOCK", "Admission baselines and solvability witness",
    "A family is admitted only if the constant policy, best memoryless policy, canonicalised seen-episode lookup on "
    "held-out instances and the acquisition-matched finite-state learners (MEA-07) fail by margins exceeding the ruler "
    "MDE, and solvability is shown by an exact optimum, a reference policy, a privileged-search existence witness, or "
    "an achievability bound (recorded which).", "Otherwise the world does not demand the phenomenon.",
    "T08 TD1-TD2; Challenge 2c", "Admit and add baselines later.", "Admission run committed with the certificate.",
    "A family admitted with a margin smaller than the ruler's MDE: refused.", "M")
req("WLD-03", "REQUIRED", "SLICE", "BLOCK", "Families, sealed and quotient-disjoint splits",
    "Worlds come from family generators; held-out instances (disjoint under the family symmetry quotient) and held-out "
    "families are stored encrypted or as sealed generator seeds, decrypted only inside the evaluation job; search and "
    "development jobs hold no key; selection never sees them.",
    "Evaluation on the training distribution certifies memorisation; champion selection on held-out data inflated "
    "everything downstream.", "T09 SD6 TD14 (Ares D1)", "Fixed world list; discipline.",
    "Search-job key audit; planted symmetric-image split flagged.",
    "A held-out instance that is a rotation of a training instance: generator validator refuses.", "M")
req("WLD-04", "REQUIRED", "SLICE", "BLOCK", "Exact or bounded solvability for the qualification tier",
    "Families used to qualify rulers and certify depth are exactly solvable or provably bounded; solver output is "
    "cross-checked by a slow reference solver written from the spec by a different author.",
    "Known-answer worlds are the cheapest positive controls.", "Ludus tension", "Open-ended worlds only.",
    "Two solvers agree on all qualification instances.", "", "L")
req("WLD-05", "REQUIRED", "CORE", "BLOCK", "Independent authorship of evaluation worlds (computed class)",
    "Evaluation families are authored at computed independence class >= I1 (REP-06) relative to the substrate and "
    "ruler authors in year one; families supporting L3+ need >= I2, and L5 needs I3 or I4.",
    "Single-author worlds, organisms and rulers share blind spots.", "T17 SD9 (Cosmos six families one author)",
    "Same seat writes worlds and organisms.", "Independence class computed from access logs.",
    "A family declared 'independent' whose author read the substrate repo: classed I0, refused for L3.", "M")
req("WLD-06", "HIGH VALUE", "CORE", "FLAG", "Depth dimensions as generator parameters",
    "Generators expose partial observability, hidden state, delay, irreversibility, costly observation, misleading "
    "evidence, nonstationarity, compositional grammar, surface-varied recurrence and regime shifts as parameters with "
    "measured certificate effect.", "Lets depth be swept and linked to what develops.", "", "One-off worlds.",
    "Sweeps move certificate components monotonically.", "", "M")
req("WLD-07", "REQUIRED", "SLICE", "BLOCK", "Differential all-channel leak audit",
    "For every family, pairs of world states that differ only in the hidden variable or answer are run through every "
    "channel the organism can read (observations, reward timing, termination, legal-action set/order/count, metabolic "
    "charges, RNG consumption, step budget, error paths), plus a cheap learner with full access to all channels; a "
    "planted leak on each channel must be detected.",
    "The most recurrent false-positive generator was the measurement carrying its answer; side channels were never "
    "tested.", "T01 TD6; Icarus R5", "Observation-stream check only.", "Planted leak per channel detected.",
    "A family whose episode length depends on the hidden answer: audit fails.", "M")
req("WLD-08", "REQUIRED", "GATE-NULL", "BLOCK", "Verified curriculum prerequisite structure",
    "A curriculum used for a developmental claim or null is admitted only if (a) the DEV-13 genome acquires rung n+1 "
    "with censoring-aware savings >= a declared margin after rung n vs naive; (b) a reference learner shows the same "
    "ordering effect; (c) each rung's acquisition fits the lifetime (WLD-18); (d) an organism ignoring rung-n "
    "structure fails rung n by the admission margin.", "Otherwise a developmental null cannot be told from a "
    "curriculum with no usable prerequisite structure.", "Challenge 4c/4f; Vivarium H1/H0 zero shared abstractions",
    "Assume ordering helps.", "Savings measured.", "A curriculum whose rungs are ignorable: refused.", "M")
req("WLD-09", "REQUIRED", "RULE", "BLOCK", "World physics cannot supply the target capability",
    "Operations that implement the phenomenon under study (copying, memory, inference) are not provided by the world "
    "unless the experiment is about using them; claims must survive ablation of any world helper.",
    "Worlds that supplied copying made 'spontaneous replication' a world property.", "SD2 (splice, hidden world copies)",
    "Allow world helpers.", "Helper ablation.", "", "S")
req("WLD-10", "HIGH VALUE", "GATE-C:epistemic", "FLAG", "Epistemic world dimension",
    "Families with unreliable sources of learnable reliability, misleading first evidence, costly verification, "
    "competing explanations and reward for revision, with exact Bayes-optimal references.",
    "Needed to ask whether critical-thought mechanisms can emerge.", "", "None.",
    "Bayes-optimal >> naive-first-evidence.", "", "M")
req("WLD-11", "EXPERIMENTAL", "GATE-C:social", "PROSE", "Social, adversarial and cooperative worlds",
    "Multi-organism families (including one yoked-ecology arm once the vertical slice passes).",
    "Rich pressure source; confounds single-organism questions.", "", "Start multi-agent.", "Deferred.", "", "M")
req("WLD-12", "EXPERIMENTAL", "GATE-C:tools", "PROSE", "Tool construction",
    "Organisms build persistent world artifacts that change their later capabilities.", "Large search cost.",
    "", "None.", "Arm after month 6.", "", "M")
req("WLD-13", "REJECTED/AVOID", "RULE", "RULE", "Size as admission; shallow worlds for reasoning claims",
    "Worlds are never admitted on scale; worlds certified at most one-bit latch or lookup do not host reasoning claims.",
    "Scale demonstrations were mistaken for depth.", "Aether 16384^2; Ares; SD E1", "Bigger worlds.", "Static.", "", "0")
req("WLD-14", "REQUIRED", "RULE", "BLOCK", "Physics never consults the ruler",
    "World and organism physics never read ruler outputs, lineage labels, verdicts or measurement state; rulers observe "
    "physics through a read-only tap; any measurement-to-physics feedback is a declared, separately qualified "
    "mechanism.", "When physics assigns lineage by resemblance at birth, the measurement manufactures the phenomenon.",
    "SD1 (Archaeon 26 -> 0; BEE glineage by resemblance; label G 93 vs content 0)", "Convenience coupling.",
    "Static import check; planted coupling detected.", "A physics module importing a ruler module: CI fails.", "S")
req("WLD-15", "HIGH VALUE", "GATE-C:open-demand", "FLAG", "Open-demand tier and d_unfam",
    "Admit families where every baseline and every familiar reference policy fails but solvability is shown by an exact "
    "optimum, a privileged-search witness or an achievability bound; certificate component d_unfam = optimum (or "
    "witness) minus best familiar reference.", "Worlds admitted only when familiar reasoning solves them select for "
    "familiar reasoning.", "anti-gravity critique", "Reference-policy admission only.",
    "Coverage report: families with d_unfam > 0 with planted witness succeeding.", "", "M")
req("WLD-16", "REQUIRED", "GATE-C:epistemic", "BLOCK", "Own-reliability dissociation",
    "Epistemic families include manipulations of the organism's own processing reliability (internal-step truncation, "
    "injected internal noise) that leave observations and the ideal-observer posterior unchanged; a first-order Bayes "
    "policy without self-monitoring is a mandatory baseline.",
    "Without it, a first-order Bayes-optimal policy satisfies the metacognition definition.",
    "comparative-cognition associative confound", "Decodable calibration only.",
    "Planted self-monitoring organism shifts abstention under truncation; first-order Bayes does not.",
    "A metacognition claim without the dissociation arm: refused.", "M")
req("WLD-17", "REQUIRED", "GATE-L2", "BLOCK", "Certificate and admission tools cross-checked on sealed known-answer worlds",
    "Before any family supports L2+, at least two independently authored certificate/admission tools (one at I2+ or "
    "procedural) are scored on a sealed set of known-answer worlds that includes closed-form-solvable, "
    "lookup-solvable-on-held-out, one-shot-latch-solvable and leaky worlds; the union-vs-best miss rate is reported.",
    "A central world forge creates correlated blind spots (a gate admitted Nim although a closed-form rule is optimal).",
    "Ludus GATE-W1; WTP-03 G5 admitted 0 spectral/sparse/random", "One certificate tool.",
    "Miss rates on the sealed set.", "A Nim-like family admitted as deep by both tools: alarm.", "M")
req("WLD-18", "REQUIRED", "GATE-NULL", "BLOCK", "Lifetime vs acquisition time; adaptive gap and payback",
    "Families used for pressure or developmental claims report V_fix (best policy fixed at birth), V_adapt(L) "
    "(Bayes-adaptive optimum over lifetime L), Delta = V_adapt - V_fix, identification time tau_id, payback ratio "
    "L/tau_id, and the needle size of the innate solution under the declared operators; a lifetime is admitted for a "
    "developmental claim only if L >= 3 x the DEV-13 genome's 90th-percentile acquisition time.",
    "A developmental null in a lifetime shorter than the best developer's acquisition time is the newborn-in-graduate-"
    "school result in time.", "Ensorain FR-081 (0/181 lifetimes in the region of interest)", "Declared lifetimes.",
    "X1 lifetime sweep reproduces the predicted innate-to-learned switch.",
    "A developmental null with L below threshold: typed 'lifetime'.", "M")
req("WLD-19", "REQUIRED", "GATE-C:reasoning", "BLOCK", "Deliberation certificate d_think",
    "Families hosting reasoning or deliberation claims report d_think: the log ratio of the smallest per-decision "
    "reactive circuit (or lookup) to the smallest iterative controller reaching x% of optimal, exact for small "
    "families and bounded otherwise.", "Any iterative computation can be unrolled; the benefit of thinking exists only "
    "as a time-space trade-off the certificate must compute.", "", "Compute-competence curve alone.",
    "On a map-in-observation maze family, d_think predicts which planted organisms show anytime gains.", "", "M")
req("WLD-20", "REQUIRED", "GATE-L5", "BLOCK", "Policy-multiplicity certificate for convergence claims",
    "Convergence or transfer-by-convergence claims count only on families with >= 2 functionally distinct near-optimal "
    "policies, so convergence is not implied by the optimum.", "Narrow optima force convergence.",
    "ecology critique", "Any family.", "Certificate shows distinct witnesses.", "", "S")
req("WLD-21", "REQUIRED", "CORE", "BLOCK", "Known-answer verification of externally sourced worlds and results",
    "Any world, rule set or result reconstructed from an external source (games, literature) is verified against that "
    "source with known-answer tests before use; reconstruction from memory is refused.",
    "Rules reconstructed from memory reversed a headline (86%).", "SD14 (Ludus Martian Dice)", "Trust recall.",
    "Known-answer test per reconstructed world.", "A world spec citing no source and no known-answer test: refused.", "S")

# =============================================================================================== PRS
req("PRS-01", "REQUIRED", "GATE-C:pressure", "BLOCK", "Pressure ladder with computed conditions",
    "Pressures are declared, certified variables: P0 static environment (development is waste at equilibrium on a "
    "smooth landscape); P1 per-lifetime variation with adaptive gap Delta >= delta and payback ratio >= rho_min "
    "(WLD-18), predicting an innate-adaptive program when the smallest adaptive controller fits the genome budget and "
    "slow-state plasticity otherwise; a separate ruggedness axis (needle size of the innate solution) predicting "
    "transient Baldwinian plasticity even at Delta = 0; P2 shared latent structure across a sequence of environments in "
    "a long lifetime; P3 within-lifetime shifts of the useful learning bias; P3b open-ended bias growth (PRS-14); P4 "
    "ecological interaction. A level is in force only when its pressure certificate (PRS-12) passes.",
    "Development pays only under specific statistics; the original P1 condition compared the wrong quantities and its "
    "cited known positive (Hinton-Nowlan) was a static-needle effect.", "Challenge 2; critic dev-lens",
    "Scalar fitness on a fixed world.", "X1a variability x reliability sweep; X1b static needle (transient learning "
    "then assimilation).", "A 'P1' campaign whose Delta was never computed: refused.", "M")
req("PRS-02", "REQUIRED", "SLICE", "BLOCK", "Search policy declared; plurality before typing nulls",
    "Acceptance rule, optimiser and budget are always declared; at least two policies (one random sampling at the same "
    "budget) are required before a null is typed above apparatus level.",
    "Greedy tie-rejecting walks manufactured cliffs.", "SD5; PROTEUS-46", "One policy.",
    "Same target under several policies.", "A null typed 'search-bounded' with one policy: refused.", "S")
req("PRS-03", "REQUIRED", "GATE-NULL", "BLOCK", "Reachability estimator",
    "Every negative search result carries a reachability estimate from a frozen estimator: (a) rediscovery-from-"
    "distance curve p_hit(k) from genomes k = 1, 2, 4, 8, ... operator steps from >= 5 independently authored planted "
    "solutions of the target phenotype class, with exact binomial CIs; (b) d0, the operator distance from the initial "
    "distribution to the nearest planted solution; (c) the fitness profile of the best known path against the "
    "acceptance rule; (d) random-sampling hit rate of the phenotype class at plant length. 'Search could have reached' "
    "only if lower-bound p_hit at k >= d0 times independent runs >= 3 expected hits; otherwise 'search-bounded' with the "
    "budget multiple needed.", "Zero hits bounds nothing; one exact plant genotype misjudges reach.",
    "PROTEUS-46; Crius 47-edit mechanism; Ananke FLIP/XOR; Tyche parity-3; DENOVO-01", "Report budget only.",
    "Estimator recovers known p_hit on planted landscapes.", "A 'could have reached' null with 0.4 expected hits: refused.",
    "M")
req("PRS-04", "REQUIRED", "SLICE", "BLOCK", "No selection on sealed evaluation data",
    "Selection, champion choice and hyperparameter choice never touch sealed instances (enforced by WLD-03 keys).",
    "Champion selection on held-out data inflated every downstream number.", "T09 SD6", "Discipline.",
    "Key audit.", "", "0")
req("PRS-05", "HIGH VALUE", "CORE", "FLAG", "Multi-objective, lexicase and QD selection with stable descriptors",
    "Selection over vectors with archives keyed on behavioural and intervention signatures computed over >= k "
    "re-evaluation seeds (a cell admitted only if stable); a strict noise-free tie-break counterfactual arm.",
    "Scalar fitness collapses stepping stones; noise-filled archives preserve noise as diversity.", "Tyche v2",
    "Scalar fitness.", "Archive coverage and later transfer.", "", "S")
req("PRS-06", "REQUIRED", "RULE", "RULE", "Metabolic cost is a declared pressure with ramps and a zero-cost arm",
    "Costs on structure and steps (if used) are a declared pressure with ramp schedules; every cost sweep includes a "
    "zero-cost arm; cost units never equal the abstraction ruler's description language.",
    "Full costs from generation 0 killed footholds; cost in the ruler's units makes 'abstraction emerged' guaranteed.",
    "Sisyphus E7; anti-gravity critique", "Fixed costs.", "Prereg linter checks arms and units.", "", "0")
req("PRS-07", "REQUIRED", "GATE-C:pressure", "BLOCK", "Between- and within-lifetime change rates as swept axes",
    "Environmental change rates between generations and within lifetimes are swept variables in pressure campaigns.",
    "They define the P0/P1/P3 boundaries.", "", "Static or i.i.d. worlds.", "Sweep in X1a.", "", "S")
req("PRS-08", "HIGH VALUE", "CORE", "FLAG", "Optimiser plurality",
    "Beyond PRS-02, non-evolutionary optimisers (novelty search; gradient meta-learning for reference learners) are "
    "declared arms where they test a substrate-vs-search question.", "Separates search from substrate effects.", "",
    "Evolution only.", "Arm comparison.", "", "S")
req("PRS-09", "HIGH VALUE", "CORE", "FLAG", "Recombination as a declared factor",
    "Crossover on/off as an arm.", "Recombination crossed valleys in one representation and was harmful in others.",
    "Sisyphus C7", "Always on.", "Arm comparison.", "", "S")
req("PRS-10", "EXPERIMENTAL", "GATE-C:coevolution", "PROSE", "World-organism coevolution",
    "Open-ended coevolution of generators and organisms; adaptive family selection logged as a selection channel.",
    "Rich curricula; uninterpretable before certificates.", "WTP-03 G5", "Start with coevolution.", "After X2.", "", "M")
req("PRS-11", "REJECTED/AVOID", "RULE", "RULE", "Shaping bonuses on proxies",
    "No fitness terms paying for proxies of the target; the prereg linter requires each fitness term to be declared and "
    "justified against the target.", "Proxies get optimised instead.", "TD10 (Ananke contrast bonus)",
    "Bonuses to speed search.", "Linter.", "", "0")
req("PRS-12", "REQUIRED", "GATE-NULL", "BLOCK", "Pressure certificate under the actual selection regime",
    "Before a search null is interpreted, the capability fixtures (ORG-14, DEV-13) and the best incapable baselines are "
    "scored under the exact selection regime (fitness function, every cost-ramp point, lifetime, episodes per "
    "evaluation, population size); P1 baselines include the best fixed detect-and-dispatch genome within the genome "
    "size limit, P2 the best flat learner, P3 the best fixed-rule learner. The capable organism must win with "
    "N_e*s >= 10 at every ramp point and a paired advantage exceeding per-evaluation noise.",
    "A world can demand memory in competence terms while selection cannot see it.", "", "Declared pressure levels.",
    "Planted pressure failures (cost above benefit; task off reproductive path; N_e*s < 1) fail the certificate.",
    "A null under a regime where the fixture loses to the incapable baseline: typed 'pressure'.", "M")
req("PRS-13", "REQUIRED", "SLICE", "BLOCK", "Concentration floor",
    "No arm launches below the budget at which the planted-target p_hit(k) curve gives >= 3 expected hits; if the "
    "envelope cannot fund N arms at that budget, fewer arms are funded.",
    "Splitting budgets guaranteed search-limited nulls, the commonest historical null type.",
    "Ananke 96x36; Crius (8+24)x300; 'budgets were uniformly small'", "Fund every arm a little.",
    "Launch gate reads the curve.", "An arm launched at 0.5 expected hits: launch refused.", "S")
req("PRS-14", "EXPERIMENTAL", "GATE-C:RS", "PROSE", "P3b open-ended bias-growth regime",
    "An environment sequence whose useful learning biases compose earlier biases at growing depth, certified so that "
    "any fixed meta-rule of declared size falls behind after h* families; recursive-sagacity nulls are phenomenon-level "
    "only under a regime whose certificate predicts recursion.", "P3 as stated predicts order-2 meta-plasticity, which "
    "the recursive-sagacity definition calls ordinary learning-to-learn; no rung predicted the headline phenomenon.",
    "", "P3 only.", "Fixed-meta and library organisms plateau after h*; planted order-3 continues.", "", "M")

# =============================================================================================== MEA
req("MEA-01", "REQUIRED", "SLICE", "BLOCK", "Instrument qualification layer",
    "A ruler emits verdict-bearing rows only after a committed qualification dossier shows: definition in atomic "
    "variables; attainable verdict set; planted-positive sensitivity curve across effect sizes on the actual pipeline "
    "(authored AND procedurally generated plants, reported separately; a ruler whose generated/authored sensitivity "
    "ratio is below a preregistered fraction is FAMILIAR-ONLY and cannot support phenomenon-level nulls); "
    "matched-negative false-positive rate; cheapest-cheat battery; neutral-variation and dilution invariance; failure "
    "regimes; an input manifest forbidding condition labels, lineage/generator ids and seeds, with bit-identical "
    "output under label permutation and a content-stripped metadata classifier at chance. The qualification hash "
    "covers the transitive closure of the measurement pipeline (ruler, preprocessing, renderer, world adapter, "
    "configuration, statistics version) and is recomputed at verdict time.",
    "Only 30 of 146 historical instruments showed they could output the class they ruled on; executed controls caught "
    "defects in a day while reading-based audits took months; validated configurations differed from deployed ones.",
    "T03 T04 T05 T23 SD1 SD3 SD4 SD9 SD12; Tityos 2.1", "Qualification by review.",
    "Verdict job refuses rows from unqualified or closure-mismatched rulers.",
    "A verdict produced with a changed renderer under an unchanged ruler hash: refused.", "L")
req("MEA-02", "REQUIRED", "SLICE", "BLOCK", "Sealed plants at computed independence class",
    "Plant sets are authored at computed independence class >= I1 relative to the ruler author in year one (>= I2 for "
    "rulers supporting L3+), sealed from ruler authors, and include a procedurally generated class (functional "
    "organisms found by exhaustive or random search over small organisms, never inspected or named by ruler authors "
    "before qualification).", "Detectors read exactly the tell their own generators planted; model-authored plants are "
    "inside the model's ontology.", "T01 T17 SD9", "Ruler author writes plants.",
    "Seal and access logs per plant set.", "A plant set whose author read the ruler code: classed I0, refused.", "L")
req("MEA-03", "REQUIRED", "SLICE", "BLOCK", "Automatic baseline ladder with chance floor",
    "Every headline is compared automatically against constant, marginal, canonicalised lookup, same-class tuned batch "
    "estimator, the label's definition as a zero-parameter rule, one-shot latch, payload-label reader, "
    "shuffled-input/shuffled-label (format/prior/template) control, random-genome, frozen-development and yoked-replay "
    "organisms where applicable; the chance floor on the same population and denominator is published beside the "
    "number; a missing rung blocks the verdict.", "The cheap baseline arrived after the data again and again, and won.",
    "T05 T08 TD1 TD2 TD3 TD5 TD15; Ensorain N6; Cosmos definition rung; Ergon one-liner; Nemesis constant",
    "Baselines chosen per experiment.", "Ladder present in frozen design.",
    "A headline whose constant rung was computed on a different denominator: refused.", "M")
req("MEA-04", "REQUIRED", "RULE", "RULE", "Chance floor template",
    "Report templates cannot render a headline without its chance floor (enforcement of MEA-03 at the reporting layer).",
    "25 of 37 tier-1 scorers published none.", "T05 (NEM-14)", "Effect only.", "Template check.", "", "0")
req("MEA-05", "REQUIRED", "SLICE", "BLOCK", "Controls wired to abort; cheats from the sealed set",
    "Control outcomes are evaluated in the verdict code path and abort or withdraw the verdict on failure; every cheat "
    "control must have fired on cheats from the sealed plant set, including the cheapest non-degenerate multi-step "
    "cheat and a symmetry-preserving cheat, under the same closure hash as the verdict. Code checkers that gate claims "
    "are mutation-tested in CI.", "Controls that could not fail certified everything.",
    "T03 T20 SD7 TD4 ID2; Nemesis rule", "Controls reported alongside.", "Break a control; verdict aborts.",
    "A cheat control whose fire record is from an older pipeline version: refused.", "M")
req("MEA-06", "REQUIRED", "SLICE", "BLOCK", "Row-level measurement metadata",
    "Every verdict-bearing row records ruler and closure hash, denominator, exclusions, unit, world-family hash and "
    "runtime-reported model identity where any model touched the row.",
    "Unrecorded judge identity and steering fields made effects unrecoverable.", "T18 T24", "Reports only.",
    "Schema validation in the verdict job.", "A row missing its denominator: refused.", "S")
req("MEA-07", "REQUIRED", "CORE", "BLOCK", "Assays separating memorisation, lookup, FSM tricks, reactivity and structure",
    "The ruler stack includes held-out-structure evaluation; acquisition-matched finite-state baselines (best "
    "controllers produced by >= 2 generic FSC/PSR learners, e.g. state merging and EM-trained HMMs, from the same "
    "experience and feedback budget; the existence of an equivalent FSC is never evidence against a mechanism); "
    "representation-scrambling transfer; shared-ablation reuse; savings; and a deliberation signature (competence keeps "
    "rising with internal steps beyond the measured settling time, exceeds a latency-matched reactive baseline and the "
    "same organism with recurrent edges cut, and is concentrated on high-d_think or high-d_hyp decisions). AMORTISED "
    "(certificate demands met, flat curve) is a typed outcome.",
    "'Best bounded FSC' is either unbeatable or universal absorption; latency produces rising curves in reactive "
    "pipelines.", "TD5; Hecate universal-formalism absorption", "Accuracy only; existence-of-FSC baseline.",
    "Each assay qualified on planted organisms of each class.",
    "A deep reactive pipeline labelled deliberative: settling control refuses.", "L")
req("MEA-08", "REQUIRED", "GATE-L3", "BLOCK", "Auditor calibration",
    "A human or model audit may not gate any claim until calibrated on sealed planted defects with its false-negative "
    "rate published; code checkers are covered by MEA-05 mutation testing.",
    "No auditor was measured; auditors committed the classes they audit.", "T22", "Trust audits.",
    "Planted-defect campaign per gating auditor.", "", "M")
req("MEA-09", "REQUIRED", "SLICE", "BLOCK", "Execution state is not scientific outcome",
    "Completion, exit codes and harness PASS are separate fields from scientific outcome and never map to POSITIVE.",
    "Index layers turned 'completed' into POSITIVE.", "T19 T21 ID6 TD17", "One status field.",
    "Schema separation.", "A 'completed' run counted as positive: schema refuses.", "S")
req("MEA-10", "REQUIRED", "GATE-L5", "BLOCK", "Cross-variant and cross-substrate ruler qualification",
    "Rulers for cross-variant claims are qualified on >= 2 lattice variants, both encodings and >= 1 reference learner; "
    "rulers feeding L5 predicates are qualified on a second substrate.",
    "Cross-substrate transfer was tested for 2 of 146 instruments.", "Tityos 2.1", "Per-variant qualification.",
    "Dossier coverage check.", "", "M")
req("MEA-11", "REQUIRED", "SLICE", "BLOCK", "Known-answer-tested statistics library",
    "One shared statistics library with known-answer tests is the only route for verdict statistics.",
    "Gate libraries were anti-conservative; estimators differed between null and observed.", "T10 TD12",
    "Per-seat statistics.", "Known-answer suite in CI.", "A verdict computed outside the library: refused.", "M")
req("MEA-12", "REJECTED/AVOID", "SLICE", "BLOCK", "LLM judges in the kill or promote path",
    "No model judgement decides survival, promotion, novelty or ruler outcome; enforced by the row-class filter (PRV-07).",
    "LLM judges were prompt-steerable, uncalibrated, same-family and familiarity-bound.", "T14 T15 T24",
    "Calibrated LLM judges.", "Row-class filter.", "", "0")
req("MEA-13", "REJECTED/AVOID", "SLICE", "BLOCK", "Scoring self-reports",
    "No measurement reads a generator's description or rating of its output; enforced by PRV-07.",
    "Self-report counted as novelty.", "T02 T14 TD7 ID3", "Calibrated self-report.", "Row-class filter.", "", "0")
req("MEA-14", "REQUIRED", "SLICE", "BLOCK", "Acquisition-cost protocol",
    "Acquisition cost is a vector (feedback bits, environment transitions, internal steps including idle steps, "
    "metabolic cost) to first frozen-evaluation crossing of eps on sealed instances, on a checkpoint grid with spacing "
    "< 10% of the fastest reference median, reported as full curves at >= 3 eps levels (one reached by the naive "
    "organism in >= 50% of runs) with censoring-aware survival estimators and a threshold-free learning-curve-area "
    "difference; comparisons at matched other components or as Pareto frontiers; every savings claim has a yoked-replay "
    "arm.", "Scalar feedback counts let exploration efficiency, internal brute force and censoring pass as sagacity.",
    "critic dev-lens", "Scalar A(o,T,eps).", "Planted passive learner, explorer, internal enumerator and censored naive "
    "are separated; the scalar metric misranks them.", "A TS computed with censored naive runs set to the budget: refused.",
    "M")
req("MEA-15", "REQUIRED", "CORE", "BLOCK", "Decoder qualification",
    "Any decoder used as evidence is an MEA-01 ruler that must beat the same decoder on the raw input stream, on "
    "untrained, random-structure and structure-permuted organisms of equal size, and on label-permuted data, at declared "
    "probe capacity on held-out instances; a decoded variable supports a claim only with an interchange intervention.",
    "Expressive decoders recover input-difficulty features from any input-driven state.", "TD8", "Raw probing.",
    "Planted input-only proxy fails; planted internal carrier passes.", "", "M")
req("MEA-16", "REQUIRED", "CORE", "BLOCK", "Qualification battery for every operational definition",
    "Each s3 definition is an executable predicate qualified, before it labels any result, on committed planted "
    "organisms: at least one satisfying the definition and the cheapest organisms satisfying each clause without the "
    "property (compositional library, maturation clock, shared hub, deep reactive pipeline, first-order Bayes agent, "
    "painter for heredity, latch for memory); false-accept and false-reject rates are published.",
    "Definitions are rulers; the package condemned unqualified rulers.", "T04 T12 SD3 TD5", "Definitions as prose.",
    "Every planted non-target rejected and target accepted.", "A definition used to label a result before its battery ran: "
    "verdict job refuses.", "L")
req("MEA-17", "REQUIRED", "GATE-L2", "BLOCK", "Standing blind canaries with dead-man switch",
    "A sealed injector (>= I1 in year one; I3/I4 when available) continuously introduces planted false claims, at least "
    "one per covered failure class, into the live stream; catch rate and time to catch are published per class; if no "
    "canary has been injected and caught within the declared window, promotion above L2 freezes.",
    "One-time tests drift; detectors without responders went unanswered for days.", "T20 ID1 ID2",
    "One-time ladder test.", "Disable a gate in staging: canary escapes, alarm fires, freeze engages.", "", "M")
req("MEA-18", "REQUIRED", "GATE-C:open-ended", "BLOCK", "Qualification of open-endedness, novelty and complexity metrics",
    "Any such metric must qualify against garbage, static, noise, drift, extremal-maximiser and neutral-shadow arms "
    "before it may steer search or emit verdicts.", "An open-endedness score ranked garbage above living rollouts.",
    "T04 (ASAL CLIP); TECHNE-107", "Use published metrics as is.", "Qualification arms.", "", "S")

# =============================================================================================== CAU
req("CAU-01", "REQUIRED", "CORE", "BLOCK", "Ablations that do not force silence",
    "Ablation replaces a carrier's contribution with matched alternatives (resampling from other runs; mean or noise "
    "matched), qualified on planted mechanisms.", "Silence-forcing ablations were unfalsifiable.",
    "T03 (c1_hostile_adjudication; audit_primitives chk)", "Zero ablation.", "Qualification on plants.",
    "A zero ablation labelled matched: qualification refuses.", "M")
req("CAU-02", "REQUIRED", "GATE-L3", "BLOCK", "Transplant semantics",
    "Every transplant declares coordinate frame, dangling-pointer rule (null / host-corresponding / carried, all run "
    "where pointers exist), host-distance ladder (age-matched twin, other lineage, naive birth host, foreign-world "
    "host), arms (with, without, ablated-after-incorporation, size- and statistics-matched sham drawn from another "
    "lineage's developed structure, content-randomised sham), and reports persistence, execution and competence "
    "separately.", "Transplant outcomes belong to (donor, host, interface); shams sometimes beat donors.",
    "T16; Aphrodite Tier 3C shams 16/16; Archaeon 39/39 persist 0/39 competent", "Transplant without shams.",
    "Planted transferable vs non-transferable structures.", "", "M")
req("CAU-03", "REQUIRED", "GATE-L3", "BLOCK", "Graded interventions as fractions",
    "Mechanism claims include dose-response; doses and damage are fractions of structure (scattered Bernoulli(f)); "
    "rulers are dilution-neutral under organism-size change.", "Count-fixed rulers manufactured length effects.",
    "SD4 (4/7 CW01 claims vanished under Bernoulli(f))", "Fixed-count lesions.", "Planted mechanisms monotone.", "", "S")
req("CAU-04", "REQUIRED", "GATE-L3", "BLOCK", "Interchange interventions",
    "Swap a candidate carrier's state between runs differing only in the latent variable named by a certificate "
    "component and test whether behaviour follows; an alternative route to L3 and required at L4.",
    "The only test tying a localised carrier to the variable a certificate names.", "Ananke carrier swaps",
    "Ablation only.", "Planted carriers.", "", "M")
req("CAU-05", "REQUIRED", "GATE-L3", "BLOCK", "Whole-closure lesion coverage",
    "Lesion families cover every carrier class listed by ORG-19, including output-side structure.",
    "Lesions blind to a third of a circuit.", "T13 (Ares W4)", "Obvious parts.", "Coverage report per family.", "", "S")
req("CAU-06", "REQUIRED", "GATE-L3", "BLOCK", "Blind automated localisation",
    "Mechanisms are localised by automated search over carriers with interventions, blind to interpretive labels; "
    "reading source proposes, never establishes.", "546 of 549 mechanism labels rested on reading.", "T16",
    "Dissection by reading.", "Recovers planted mechanisms blind.", "", "L")
req("CAU-07", "HIGH VALUE", "GATE-L4", "FLAG", "Divergent-mechanism runs on minimal cores",
    "Independent histories reaching the same capability are compared on minimal causal cores; divergence must exceed "
    "the null distribution of divergence among independent runs of a planted same-mechanism organism under neutral "
    "drift.", "Neutral drift makes same-mechanism runs look divergent.", "Challenge 4d", "Raw structural comparison.",
    "Planted divergent vs drift-only organisms.", "", "M")
req("CAU-08", "HIGH VALUE", "GATE-L3", "FLAG", "Scale-appropriate operators",
    "Observables and intervention operators at more than one organisational scale.", "Mesoscale mechanisms.",
    "Challenge 2a", "Instruction level only.", "Planted circuit-level mechanisms recovered.", "", "M")
req("CAU-09", "REQUIRED", "GATE-L3", "BLOCK", "Carrier-agnostic intervention",
    "A carrier is any intervenable variable class (structure, transient state, timing/phase, organism-written world "
    "state, resource level, execution order, population statistic). L3 is met EITHER by structural ablation plus "
    "transplant with shams OR by state/trajectory interchange plus graded dose-response on the carrier, with blind "
    "localisation in both. CONTEXT-BOUND CARRIER (interchange succeeds within hosts, naive-host transplant fails) is a "
    "typed mechanism outcome.", "Rulers that certify only addressable, transplantable substructures smuggle "
    "modularity back in and misfile distributed or dynamical carriers.", "Ananke bit in flight; Ares output self-loop",
    "Structural ablation only.", "Planted organisms with structural, transient, timing and world-state carriers each "
    "reach L3 by some route and none by a sham route.", "", "M")
req("CAU-10", "REQUIRED", "CORE", "BLOCK", "Automated minimisation to a causal core",
    "Every candidate passing L1 is reduced by ablation-based minimisation over carriers to a minimal core preserving the "
    "capability within tolerance; unclassifiability, panel input, divergence, transition diffs and novelty distance are "
    "computed only on minimal cores in canonical form.", "Opacity and size correlate with 'unexplainable'; neutral "
    "padding rewards junk.", "anti-gravity critique", "Interpret raw organisms.",
    "Padded known mechanism minimises to the reference core and scores FAMILIAR.", "", "M")

# =============================================================================================== TRF
req("TRF-01", "REQUIRED", "CORE", "BLOCK", "Transfer as acquisition-cost reduction",
    "Transfer is the censoring-aware acquisition-curve contrast (MEA-14) between the developed organism and the age- "
    "and compute-matched irrelevant-experience twin (primary), decomposed against naive-at-birth (maturation), a "
    "temporally shuffled-history twin, a capacity-matched random-content twin and yoked replay (TRF-06).",
    "Reusable cognition shows as cheaper learning; each control removes a different confound.", "",
    "Zero-shot accuracy.", "Planted transferable vs non-transferable structure.", "", "M")
req("TRF-02", "REQUIRED", "GATE-L4", "BLOCK", "Two-sided novelty certificate and transfer ceiling",
    "T_new is admitted only if surface learners (lookup, nearest-neighbour, marginal/n-gram on development families) "
    "show savings < delta_s AND a structure-oracle learner shows savings > delta_o; TS is normalised by A(naive) - "
    "A(B_C), with B_C the Bayes learner given the true family prior.",
    "A one-sided check admits interpolation and lets 'shares nothing' pass, making TS = 0 uninterpretable.",
    "TD14", "Cheap-learner check only.", "Certificate admits a shared-latent T_new and rejects T_null and T_leak.", "", "M")
req("TRF-03", "REQUIRED", "GATE-L4", "BLOCK", "Representation-scrambling transfer",
    "Observations of a known family are re-encoded by a bijection class acting on joint observations; reuse is shown "
    "by interchange between original and re-encoded episodes sharing the latent state.",
    "Separates surface-bound from structure-bound competence without assuming an encoder/core split.", "",
    "None.", "Planted surface-bound vs structure-bound organisms.", "", "S")
req("TRF-04", "REQUIRED", "GATE-L5", "BLOCK", "Transfer to independently authored worlds",
    "Transfer tests for L5 include families authored at >= I2 relative to the training families.",
    "Shared-author families share regularities.", "T17", "Same-author.", "Authorship class check.", "", "M")
req("TRF-05", "REQUIRED", "GATE-L5", "BLOCK", "Cross-substrate functional convergence",
    "A mechanism claimed transferable is found, by function and intervention signature, in a second substrate, on "
    "families with a policy-multiplicity certificate (WLD-20).", "The strongest evidence a mechanism belongs to the "
    "problem.", "SD15", "Single substrate.", "Signature matching qualified on planted pairs.", "", "L")
req("TRF-06", "REQUIRED", "CORE", "BLOCK", "Capacity-matched controls",
    "TS, savings, recursive-sagacity and transplant claims must exceed a capacity-matched naive host (equal structure "
    "count, topology statistics, metabolic budget, inert content) and a structure-permuted twin.",
    "Growing organisms give hosts free capacity; cheaper acquisition can come from capacity.", "TD13",
    "Compute-matched controls only.", "Planted extra-inert-capacity organism shows zero TS.", "", "S")

# =============================================================================================== PRV
req("PRV-01", "REQUIRED", "SLICE", "BLOCK", "Content addressing over canonical bytes; unique identifiers",
    "Artifacts are content-addressed over canonical bytes (LF-normalised = git blob for text); host-byte hashes are "
    "rejected; identifiers are unique and name collisions are refused at registration.",
    "CRLF host hashes recurred; identity collisions ('F33' x4; two Theseus tenants) hid lineage.",
    "T18 TD19 ID12", "Hash files as found.", "LF and CRLF copies hash equal; duplicate id refused.", "", "S")
req("PRV-02", "REQUIRED", "SLICE", "BLOCK", "Mechanical verdict authority (signed batch job)",
    "Only the verdict job, which holds the only signing key, can produce verdict and promotion rows; every reader "
    "ignores unsigned rows; generation, interpretation and model processes have no write path to verdict or archive "
    "status. The verdict job is a deterministic batch step, not a standing service.",
    "Generators verdicted their own records; synthetic verdicts were written by SQL.", "T02 TD7",
    "Role discipline; standing verdict service.", "Attempted writes from a generator process fail.",
    "A verdict row signed with a test key: readers ignore it.", "M")
req("PRV-03", "REQUIRED", "SLICE", "BLOCK", "Append-only ledger with prediction before observation",
    "Experiments, predictions, segment manifests and verdicts live in an append-only hash-chained ledger; per-tick data "
    "lives in content-addressed segment files whose hashes are in the ledger.",
    "Makes post-exposure change visible mechanically.", "T11", "Git history only; per-evaluation ledger rows.",
    "Chain verification.", "", "M")
req("PRV-04", "REQUIRED", "SLICE", "BLOCK", "No untracked inputs; clean-tree receipts",
    "Every artifact consumed by a verdict is tracked or content-addressed with custody; receipts pin code hash and a "
    "clean tree or the hash of the applied diff; gitignored, stashed or host-local inputs block the verdict.",
    "Gitignored outputs, stashes and host-local ledgers were consumed and lost.", "T18; Ixion E", "Best effort.",
    "Dependency check.", "A verdict citing a file under a gitignored path: refused.", "S")
req("PRV-05", "WITHDRAWN", "", "", "Clean-tree receipts (merged into PRV-04)", "Merged into PRV-04.", "Resource critique "
    "merge.", "", "", "", "", "0")
req("PRV-06", "REQUIRED", "CORE", "BLOCK", "One primary store; derived views rebuilt",
    "One authoritative store records every experiment attempted and its outcome; indexes, wikis and dashboards are "
    "derived views rebuilt from it with rebuild-equality checks.", "Four overlapping stores disagreed; indexes lagged "
    "by days.", "ID5; Ixion G1", "Peer stores.", "Rebuild-equality check.", "", "M")
req("PRV-07", "REQUIRED", "SLICE", "BLOCK", "Row-level reliability class as a predicate filter",
    "Rows carry their origin class (computed, parsed from machine ledgers, model-authored, human-authored); verdict "
    "predicates accept only computed or parsed rows.", "This filter is the mechanical backing for MEA-12 and MEA-13.",
    "Ixion E; T14 ID3", "Method field only.", "A model-authored row fed to a predicate is ignored.", "", "S")
req("PRV-08", "REQUIRED", "SLICE", "BLOCK", "Negative evidence is never lost",
    "Timeouts, crashes, refusals and empty outputs are typed outcomes, never absence or content.",
    "Lost negative evidence created false negatives; transport failures were rendered as content.", "TD16; Tityos D",
    "Drop failed runs.", "Fault injection.", "", "S")
req("PRV-09", "REQUIRED", "RULE", "RULE", "Producers declare outputs",
    "Producers declare where they write; consumers never guess.", "A consumer guessing its producer ran 354 dead ticks.",
    "ID9 (Atalanta; D-28)", "Convention.", "Interface registry check.", "", "0")
req("PRV-10", "REQUIRED", "CORE", "BLOCK", "Fixture and plant ancestry tags",
    "Hand-built fixtures, plants and model-authored edits carry provenance tags through the material shadow (ORG-08); "
    "lineages descending from them are flagged and cannot support emergence, discovery or developmental-origin claims.",
    "Positive controls and authored instances were read as signals.", "SD10 TD18", "Trust lineage records.",
    "A planted fixture-derived lineage is flagged.", "", "S")
req("PRV-11", "REQUIRED", "RULE", "RULE", "No credentials in tracked files",
    "A secrets scanner runs in CI and pre-commit; tracked credentials block the commit.", "Credentials sat in tracked "
    "files.", "ID11", "Manual hygiene.", "Planted test secret blocked.", "", "0")

# =============================================================================================== REP
req("REP-01", "REQUIRED", "SLICE", "BLOCK", "Deterministic replay",
    "CPU runs replay bit-identically from (code hash, family hash, keyed seeds, configuration); GPU-trained reference "
    "learners replay within a declared tolerance with deterministic flags where available.",
    "Replay is the precondition of audit (not replication).", "", "Best effort.", "Sampled replay test.", "", "S")
req("REP-02", "REQUIRED", "GATE-L3", "BLOCK", "Independent reimplementation before L3",
    "Before L3, the ruler(s) and the substrate kernel a claim rests on are reimplemented at computed class >= I2 and "
    "agree on a frozen differential-test corpus; a slow same-family reference interpreter, differentially tested, is "
    "CORE from the start.", "Ports were counted as independent confirmation.", "T17 T22 SD15", "Ports.",
    "Differential tests.", "A 'reimplementation' sharing imports with the original: classed I1, refused.", "L")
req("REP-03", "REQUIRED", "GATE-L3", "BLOCK", "Cross-host fresh-seed replication",
    "Cross-host replay runs in CI (CORE); cross-host replication with fresh seeds is required at L3.",
    "Host defects shaped results.", "T09", "Single host.", "Receipts from two hosts.", "", "S")
req("REP-04", "REQUIRED", "GATE-L4", "BLOCK", "Cross-family re-derivation",
    "Analyses supporting L4+ and every externalisation are re-derived at class I3 (another model family or a human) "
    "from frozen rows.", "Correlated blind spots of one family are the main independence failure.", "T17 SD15",
    "Same family.", "Agreement record with computed class.", "", "M", "FORK")
req("REP-05", "REQUIRED", "GATE-EXT", "BLOCK", "One-command reproduction packages",
    "Every externalised result ships as a package reproducing it on a clean machine.", "Externally inspectable work.",
    "", "Docs only.", "Clean-machine test.", "", "M")
req("REP-06", "REQUIRED", "CORE", "BLOCK", "Computed independence classes",
    "Independence classes are computed, never declared: I0 same session; I1 same family with any shared brief, code or "
    "rows; I2 same family, spec-only brief, no read access to the claimant's code, rows, journals or narrative (sandbox "
    "logs) and disjoint import graph apart from the statistics library; I3 different model family (runtime-reported) or "
    "a human; I4 procedural, counted only when the generator's author is I2+ and its grammar commit precedes the "
    "substrate and ruler commits.", "Independence was a field the author filled in.", "T17 SD9 SD15",
    "Declared independence.", "Counterfeit same-family reimplementation with read access is classed I1.", "", "M")
req("REP-07", "REQUIRED", "SLICE", "BLOCK", "Keyed random streams",
    "Every arm, world instance and organism draws from independently keyed random streams; designs in which arms share "
    "streams or initial populations must declare it and pass SCI-05's attainability check.",
    "Identical RNG and populations across worlds made a null geometric.", "SD8 (SFE canary)", "One global seed.",
    "Runner configuration validator.", "Two arms sharing a stream undeclared: launch refused.", "S")

# =============================================================================================== AGR
req("AGR-01", "REQUIRED", "CORE", "BLOCK", "Three-layer authority in code",
    "Generation proposes; Reality (worlds, development, interventions, qualified rulers, verdict job) decides survival; "
    "Interpretation (models, humans, prior-art search) proposes experiments and descriptions and can never delete, "
    "demote or exclude a candidate (enforced by PRV-02 and PRV-07).", "The dangerous loop is generate-recognise-admit.",
    "T02 T14 T15; Challenge 3c", "Model-mediated gates.", "Interpretation has no write path to status.", "", "S")
req("AGR-02", "REQUIRED", "GATE-L2", "BLOCK", "Unclassifiable is preserved (with guard, on minimal cores)",
    "A candidate passing behavioural and causal gates is preserved; its investigative priority rises when calibrated "
    "classification fails, weighted inversely by its minimal core's description length relative to the familiarity "
    "reference minimum; any core matching a reference mechanism is FAMILIAR whatever a panel says; unclassifiability is "
    "never evidence and never applies before the gates.", "Familiarity-bound instruments could only say 'familiar'; "
    "without the guard, opacity is rewarded.", "T15; Challenge 3a/3b", "Discard unclassifiable.",
    "Planted unfamiliar-but-real mechanism survives; padded familiar mechanism does not gain priority.", "", "S")
req("AGR-03", "REJECTED/AVOID", "RULE", "RULE", "A fixed compute-share quota as the anti-gravity mechanism",
    "No fixed percentage quota on model-originated variation is used as evidence of anti-gravity; it bounds neither "
    "survivor share nor the prior carried by authored grammars and operators (replaced by AGR-14, AGR-15, AGR-04).",
    "Unenforceable and aimed at the smallest channel.", "anti-gravity and resource critiques", "70% quota.", "n/a",
    "", "0")
req("AGR-04", "REQUIRED", "CORE", "BLOCK", "Material-descent gravity meter (counting)",
    "Model origin is tracked per genome element by the material shadow through recombination, duplication and "
    "mutation; the survivor share by material descent is reported per ladder level. Familiarity measurement happens "
    "only inside the generation-source campaign under a fixed token cap.", "Per-edit labels are laundered by "
    "recombination; familiarity tracking by panel is recurring inference.", "", "Per-edit labels.",
    "Planted model-seeded material tracked through recombination.", "", "S")
req("AGR-05", "EXPERIMENTAL", "GATE-C:panel", "PROSE", "Calibrated multi-model disagreement instrument",
    "Panels of several model families describe minimal cores of reality-validated phenomena, calibrated on generated "
    "(unfamiliar) and padded familiar plants; patterns are priority signals, never verdicts.",
    "Its unfamiliar class has no non-model source until generated plants and minimal cores exist.", "T17",
    "Majority vote.", "Calibration run.", "", "M", "FORK")
req("AGR-06", "REQUIRED", "RULE", "RULE", "Alienness is an outcome, never a fitness term",
    "Distance from prior art or the familiarity reference is computed after validation and never used as selection "
    "pressure; a static check audits fitness functions.", "Selecting for strangeness is a Goodhart target.",
    "Challenge 3e", "Novelty bonus by familiarity.", "Static audit.", "", "0")
req("AGR-07", "REQUIRED", "GATE-L5", "BLOCK", "Substrate dissimilarity on measured triggers",
    "Year one requires one primary substrate whose physics does not map onto standard neural modules, its lattice and "
    "encodings, one familiar reference learner (AGR-08) and a minimal probe kernel (<= ~1.5k lines, authored at class "
    ">= I2, preferably I3) for substrate-variance tests. A second full substrate, authored at >= I2 and run on the same "
    "anchor families, is commissioned at the first of: a claim reaching L4; a target class shown unreachable or "
    "needle-inflated > 100x in the primary substrate; the physics-span check blind to planted substrate quirks; the "
    "probe kernel's X1 threshold outside the primary's within-kernel span. It is REQUIRED before any L5 claim or any "
    "null generalised beyond its substrate; dissimilarity is measured (ruler plant-profile disagreement, emulation "
    "overhead, operator-semantics overlap), not asserted.", "One substrate is one prior; but several bespoke kernels "
    "from one author family split budget and multiply build cost without an instrument for convergence.",
    "SD15; Sisyphus s1; resource and judge rulings", "Three substrates from the start.",
    "Desk audit of nulls (X0) and port-cost receipt decide; triggers logged.", "", "L")
req("AGR-08", "REQUIRED", "SLICE", "BLOCK", "Familiar architectures as controls",
    "Every campaign family has >= 1 familiar reference learner trainable on CPU (evolved plastic RNN or small GRU "
    "meta-learner) on the same certified worlds and budgets; an in-context transformer reference is required only where "
    "an L2+ claim compares an unfamiliar organism with familiar architectures.",
    "'Unfamiliar' and 'better' are only measurable against a familiar control; three references saturate one GPU.",
    "", "Exclude familiar architectures; or three references everywhere.", "Reference arm present.", "", "M")
req("AGR-09", "REQUIRED", "GATE-L3", "BLOCK", "Prior-art check after validation with measured recall and precision",
    "Every L3+ claim undergoes a logged prior-art search (literature and code) whose recall on planted known mechanisms "
    "and precision on decoys are measured; novelty claims cite corpus, recall and precision.",
    "Literature caught classes no internal seat caught; absence of search was read as novelty.",
    "T15; F011; F043; Artemis W08", "Doctrine discouraging literature comparison.", "Recall/precision tests.", "", "M",
    "FORK")
req("AGR-10", "HIGH VALUE", "CORE", "FLAG", "Mechanical novelty archive", "Novelty archives keyed on stable "
    "behavioural and intervention signatures computed by code.", "Keeps diversity pressure outside learned priors.",
    "", "LLM novelty scoring.", "Archive coverage.", "", "S")
req("AGR-11", "REJECTED/AVOID", "RULE", "RULE", "Model familiarity as selection",
    "No candidate is selected for or against because a model judges it familiar.", "Encodes the corpus.", "T15",
    "Familiarity filter.", "Static.", "", "0")
req("AGR-12", "REQUIRED", "GATE-L3", "BLOCK", "Executable familiarity reference with reachability",
    "Familiarity is computed by code against a versioned library of executable reference mechanisms per family at "
    "matched resources: X is FAMILIAR-k if a reference with description length <= k reproduces X's held-out behaviour "
    "and intervention signature within tolerance. Before first use a sealed generated mechanism must score UNFAMILIAR "
    "and a disguised known mechanism FAMILIAR.", "Matching descriptions always finds a match; model judgement measures "
    "familiarity to the model.", "T15 (Hecate C6 universal absorption)", "Text matching; model judgement.",
    "Reachability fixture in CI.", "", "L")
req("AGR-13", "REQUIRED", "CORE", "BLOCK", "Mechanical follow-up allocation",
    "Every L1 candidate automatically receives the standard battery (minimisation, ablation/interchange, transplant, "
    "scrambling, held-out families) from a reserved compute share; candidates no model-proposed experiment targets are "
    "served first; holds are logged Interpretation actions that expire.", "Preservation without follow-up is deletion "
    "by starvation.", "T20", "Interpretation proposes follow-ups.", "Planted unclassifiable candidate reaches L3 with "
    "no model-proposed experiment.", "", "M")
req("AGR-14", "REQUIRED", "CORE", "BLOCK", "Model-free reference arm",
    "Every campaign family that uses any model-authored founders, edits, repairs or grammar extensions includes an arm "
    "with none at matched evaluation budget; claims above L2 reproduce there or are tagged MODEL-ASSISTED (or "
    "MODEL-SEEDED when the localised core is model-originated) and capped at L3.", "Makes the LLM contribution "
    "measurable and stops the corpus recognising itself.", "Icarus pattern; T24", "Quota.", "Ledger records "
    "reproduction per claim.", "", "S")
req("AGR-15", "REQUIRED", "GATE-L3", "BLOCK", "Grammar and operator gravity",
    "Each mechanism claimed at L3+ is re-searched under >= 2 independently authored primitive bases, one procedurally "
    "generated (random basis of the same expressive class), reporting minimised description length in each; a "
    "mechanism short only in the authored basis is tagged GRAMMAR-BORNE. Every variation operator, model operators "
    "included, publishes its unselected variation kernel.", "The prior enters through authored grammars, primitive sets "
    "and mutation kernels, not only through per-edit proposals.", "Tyche, Theseus, Aphrodite chemistries",
    "Meter LLM edits only.", "Planted grammar-borne vs basis-independent mechanisms.", "", "M")
req("AGR-16", "REQUIRED", "GATE-C:llm-variation", "BLOCK", "Information isolation of model operators",
    "A model operator receives only genome text, fitness of bounded precision and a frozen hashed prompt; never world or "
    "grader source, task descriptions beyond the prompt, sealed data, fixtures, plants or per-case failure objects; "
    "contexts are hashed into the ledger; prompt revisions are confounds; a planted-solution canary must be refused.",
    "The model operator is an information channel from world to genome.", "Icarus R5 (prompt rewritten to state the "
    "rule)", "Trust prompts.", "Planted cheat operator detected.", "", "S", "FORK")
req("AGR-17", "HIGH VALUE", "GATE-L2", "FLAG", "Author-dependence meter",
    "For each L2+ claim, record whether the demanding world was authored or endogenous.", "Authored worlds smuggle the "
    "designer's ontology.", "ecology critique", "None.", "Field present.", "", "0")

# =============================================================================================== CMP
req("CMP-01", "REQUIRED", "SLICE", "BLOCK", "Throughput from needle estimates; fast kernel vs slow reference",
    "Each substrate entering a campaign has a measured throughput and a fast kernel differentially tested against a "
    "slow reference interpreter; the throughput target derives from CMP-05/PRS-13, not a universal number.",
    "Search budgets must be compared with needle sizes.", "", "Universal 10^7 target.", "Differential tests.", "", "L")
req("CMP-02", "REQUIRED", "SLICE", "BLOCK", "Declared budgets and compute receipts",
    "Each experiment declares CPU, GPU, memory, storage and wall budgets; receipts record actual use and nominal energy.",
    "No cost record exists in the program.", "Ixion s7", "None.", "Receipt schema.", "", "S")
req("CMP-03", "HIGH VALUE", "CORE", "FLAG", "Justified GPU use", "GPU only where a kernel gains from it.",
    "GPU and electricity are scarce.", "", "GPU by default.", "Benchmark justification.", "", "0")
req("CMP-04", "REQUIRED", "SLICE", "BLOCK", "One job runner",
    "Long runs execute under one job runner, idempotent by input content hash; leases and fencing only where writers "
    "contend.", "Eight coexisting queue mechanisms.", "ID8", "Per-seat queues.", "Inventory check.", "", "M")
req("CMP-05", "REQUIRED", "SLICE", "BLOCK", "Feasibility check before campaign",
    "Before launch, throughput x budget is compared with the reachability estimate; campaigns that cannot plausibly "
    "reach a planted target are not launched (PRS-13).", "Budget-capped nulls.", "SD E3", "Launch and see.",
    "Launch gate.", "", "S")
req("CMP-06", "REQUIRED", "GATE-NULL", "BLOCK", "Budget curves in two currencies",
    "Every arm comparison is reported as competence-vs-budget curves at >= 4 budgets spanning >= 1.5 decades in two "
    "currencies (organism steps including lifetimes; genome evaluations), one primary declared at freeze; a "
    "comparative null holds only over the measured range and only where the treatment's top-budget slope CI includes "
    "zero, otherwise typed 'budget'.", "Single-point comparisons miss crossing curves and confound currency.", "",
    "One matched point.", "X1 curves reproduce the known ordering; a constructed crossing is reported as a crossing.",
    "", "S")
req("CMP-07", "REQUIRED", "SLICE", "BLOCK", "Vertical slice and known-positive gate before breadth",
    "No second substrate, second world grammar, GATE-L3 machinery or open-ended campaign is built until a vertical "
    "slice (one substrate x one certified family x one qualified ruler x one preregistered experiment, end to end "
    "through ledger and verdict job) reproduces a known positive (X1) at L1 with its matched negative; if the slice "
    "fails within its token budget, a typed diagnosis names the failed layer before further build.",
    "Layers built to spec that never carried an experiment were the most expensive historical failure.",
    "Vivarium; Ludus foundry; Worlds Kernel; Campaign 6", "Breadth first.", "Build plan shows no breadth item before "
    "the slice's L1 row.", "", "S")
req("CMP-08", "REQUIRED", "RULE", "RULE", "No orphan services",
    "No standing service unless it self-checks, restarts without a model session or operator, and writes a typed "
    "failure record within an hour; batch jobs with signed outputs are preferred.", "Services died with nobody "
    "responding.", "ID1 ID10", "Standing services.", "Fault injection.", "", "S")

# =============================================================================================== INF
req("INF-01", "REQUIRED", "SLICE", "BLOCK", "Inference only at declared epistemic forks",
    "Model inference is used only at listed forks: hypothesis and world-grammar framing, preregistration drafting "
    "(then linted by code), cross-family review of frozen designs, interpretation of anomalies that passed reality "
    "gates, code authoring inside budgeted work items (INF-06), and the budgeted generation-source campaign.",
    "Tokens are scarce; most model use was administrative restatement.", "Ixion s4 s7 B", "Agentic loops everywhere.",
    "Token ledger by fork class.", "", "S", "FORK")
req("INF-02", "REQUIRED", "SLICE", "BLOCK", "Token accounting including agentic sessions",
    "All model use, including interactive and agentic coding sessions, is accounted: per-session input, cache-read and "
    "output tokens and runtime-reported model id, harvested deterministically from session logs and joined to commits "
    "by session trailer and to work items; unattributed sessions are reported as such.",
    "No mechanism records inference cost; a one-client choke point cannot see coding sessions.", "Ixion s7",
    "Self-reported costs.", "Ledger totals match provider usage within 10%.", "", "S")
req("INF-03", "REQUIRED", "RULE", "RULE", "Derived status; no model-written status",
    "Status, heartbeats and dashboards are computed from receipts, ledgers and git; no clock-driven model-written "
    "status.", "86 heartbeats in 25 h restated receipts.", "Ixion B; T21 ID4 TD17", "Model heartbeats.",
    "Status generator is deterministic.", "", "S")
req("INF-04", "HIGH VALUE", "CORE", "FLAG", "Deterministic anomaly triage",
    "Statistical rules and qualified rulers triage anomalies before any model sees them.", "Response was model-mediated "
    "and slow.", "Ixion s7", "Models screen raw output.", "Triage replay.", "", "S")
req("INF-05", "REJECTED/AVOID", "RULE", "RULE", "Models in the execution path",
    "No model call inside a run's tick loop, evaluation, ruler or scheduler.", "Determinism, cost, independence.",
    "Archaeon charter", "LLM-in-the-loop evaluation.", "Static check on runner imports.", "", "0")
req("INF-06", "REQUIRED", "SLICE", "BLOCK", "Build inference budget, build ledger, stop rule",
    "Every build work item declares an executable acceptance test and a token budget before its first session; a "
    "deterministic build ledger records tokens (by model id), sessions, cap- or limit-terminated sessions (typed), "
    "commits, accepted LOC and tests; a weekly report gives tokens per accepted LOC, rework ratio, boot overhead and "
    "review-to-build ratio; an item is flagged at 1.0x budget and stopped at 1.5x pending re-plan; at most three build "
    "sessions run at once.", "The build, not operation, is where year-one inference goes; overruns get paid for by "
    "cutting controls.", "record of token-limited runs marked INCOMPLETE", "Unbudgeted code authoring.",
    "Planted over-budget item stopped at 1.5x.", "", "S")
req("INF-07", "HIGH VALUE", "CORE", "FLAG", "Deterministic boot packet",
    "Agentic sessions start from a generated packet <= 20k tokens (work item, acceptance test, interfaces, open "
    "decisions).", "Boot and coordination overhead dominated session cost.", "Ixion s4", "Read prose state files.",
    "Boot overhead < 15% of session tokens.", "", "S")

# =============================================================================================== NRG
req("NRG-01", "HIGH VALUE", "CORE", "FLAG", "Energy estimate per run",
    "Receipts carry wall-time x nominal per-host watts; calibrated measurement where counters exist.",
    "Electricity matters but is second-order at MVP scale.", "", "None.", "Spot calibration.", "", "0")
req("NRG-02", "REQUIRED", "SLICE", "BLOCK", "Quarterly envelope over all scarce resources",
    "The program runs inside a declared quarterly envelope over tokens (build and operate, by model family), operator "
    "minutes, core-hours, GPU-hours (local and rented) and kWh; the weekly digest reports burn; an overrun > 25% on any "
    "line blocks new work items on that line until re-planned in the decisions register.",
    "Tokens and operator minutes are the binding constraints.", "", "Energy-only envelope.", "Envelope report.", "",
    "S")

# =============================================================================================== HUM
req("HUM-01", "REQUIRED", "CORE", "BLOCK", "Bounded operator decisions",
    "The operator approves budget envelopes, substrate admission against the published mechanical checklist (with "
    "sunset rules), and externalisation; the operator may acknowledge but not block a mechanically satisfied "
    "promotion (holds are logged Interpretation actions that expire).", "A human gate at the top of the ladder is a "
    "corpus-trained familiarity filter and an attention sink.", "Ixion s4", "Operator in every loop.",
    "Count operator touches.", "", "0")
req("HUM-02", "REQUIRED", "RULE", "RULE", "Minimum dwell between control-regime changes; one decisions register",
    "Changes to the control model have a minimum dwell and are recorded in a single decisions register.",
    "Five regimes in six days.", "ID7", "Change at will.", "Register check.", "", "0")
req("HUM-03", "REQUIRED", "RULE", "RULE", "Operator is not the relay",
    "Cross-model reviews and cross-seat messages are executed by code, not pasted by the operator.",
    "Relay load scaled with fleet size.", "Ixion s4", "ASCII relay.", "Relay count.", "", "S")
req("HUM-04", "REQUIRED", "SLICE", "BLOCK", "Operator attention budget; scheduled sessions",
    "Routine operator time <= 90 minutes per week in year one, measured from prompt timestamps and the register; build "
    "sessions are launched by a scheduler from a prioritised queue with per-session caps and done criteria; work "
    "needing operator action outside HUM-01 classes is logged as a design defect.", "Agentic build work otherwise "
    "eats operator hours or stalls.", "Ixion s4 (~9 prompts/day)", "Ad hoc sessions.", "Weekly digest.", "", "S")

# =============================================================================================== OUT
req("OUT-01", "REQUIRED", "GATE-EXT", "BLOCK", "Externalisation criteria",
    "Externalised artifacts are limited to claims at L3+ with I3 re-derivation (REP-04), qualified instruments with "
    "dossiers, certified world suites with baseline ladders, and interpretable nulls with null certificates, each as a "
    "reproduction package; challenged claims are suspended (SCI-16).", "Genuine work should end in inspectable form "
    "without promoting hallucinations.", "T18", "Externalise interesting observations.", "Checklist gate in the "
    "release job.", "", "S")
req("OUT-02", "HIGH VALUE", "GATE-EXT", "FLAG", "Certified world suite and baseline ladder as a public benchmark",
    "Release the certified families, certificates and baseline ladders.", "Useful regardless of organism success.",
    "", "None.", "Package test.", "", "M")
req("OUT-03", "HIGH VALUE", "GATE-EXT", "FLAG", "Negative results with apparatus profile",
    "Interpretable nulls written up with null certificates.", "A calibrated null is a result.", "", "Positives only.",
    "Profile completeness.", "", "S")
req("OUT-04", "EXPERIMENTAL", "GATE-EXT", "PROSE", "Interactive observatory", "Browsable trajectories, mechanisms, "
    "interventions.", "Secondary to evidence.", "", "None.", "Deferred.", "", "M")
req("OUT-05", "REJECTED/AVOID", "GATE-EXT", "BLOCK", "Externalising L0-L2 positives as findings",
    "The release job refuses claims below L3.", "Attractive hallucinations must not become external claims.", "T18",
    "Early announcement.", "Release job check.", "", "0")


COVERAGE = {
    "T01": ["WLD-07", "DEV-06", "MEA-02", "MEA-03", "WLD-14"], "T02": ["PRV-02", "SCI-02", "MEA-13"],
    "T03": ["MEA-05", "CAU-01", "SCI-05"], "T04": ["MEA-01", "MEA-02", "ORG-14", "MEA-16"],
    "T05": ["MEA-03", "MEA-11", "MEA-01"], "T06": ["MEA-03", "MEA-16"], "T07": ["WLD-03", "SCI-18", "MEA-03"],
    "T08": ["MEA-03", "WLD-02"], "T09": ["WLD-03", "SCI-15", "DEV-09"], "T10": ["MEA-11", "SCI-06", "SCI-15", "SCI-14"],
    "T11": ["SCI-04", "PRV-03"], "T12": ["SCI-05", "SCI-08", "SCI-13"], "T13": ["WLD-01", "WLD-02", "ORG-14", "SCI-03"],
    "T14": ["PRV-07", "MEA-07", "SCI-17"], "T15": ["AGR-09", "AGR-12", "AGR-06"], "T16": ["CAU-06", "CAU-09", "SCI-09"],
    "T17": ["REP-06", "REP-02", "REP-04", "MEA-02", "WLD-05"], "T18": ["PRV-01", "PRV-04", "SCI-16", "MEA-06"],
    "T19": ["MEA-09"], "T20": ["MEA-05", "MEA-17", "SCI-13"], "T21": ["INF-03", "MEA-09"],
    "T22": ["MEA-08", "REP-02", "REP-04"], "T23": ["MEA-01", "SCI-04"], "T24": ["PRV-07", "INF-05", "MEA-06", "AGR-14"],
    "SD1": ["WLD-14", "MEA-01", "ORG-08"], "SD2": ["WLD-09"], "SD3": ["MEA-16", "ORG-08"], "SD4": ["CAU-03", "MEA-01"],
    "SD5": ["PRS-02", "PRS-03"], "SD6": ["WLD-03", "PRS-04"], "SD7": ["MEA-05"], "SD8": ["REP-07", "SCI-05"],
    "SD9": ["REP-06", "MEA-02", "WLD-05"], "SD10": ["PRV-10"], "SD11": ["SCI-06", "REP-03"],
    "SD12": ["MEA-01", "MEA-09", "INF-03"], "SD13": ["SCI-04"], "SD14": ["WLD-21"], "SD15": ["REP-06", "REP-04"],
    "TD1": ["MEA-03"], "TD2": ["MEA-03"], "TD3": ["MEA-03", "MEA-16"], "TD4": ["MEA-05", "SCI-05"],
    "TD5": ["MEA-07", "MEA-16"], "TD6": ["WLD-07"], "TD7": ["PRV-02", "MEA-13"], "TD8": ["MEA-15"],
    "TD9": ["SCI-05"], "TD10": ["PRS-11", "PRS-12"], "TD11": ["SCI-18", "SCI-06"], "TD12": ["SCI-06", "MEA-11"],
    "TD13": ["TRF-06"], "TD14": ["TRF-02", "WLD-03"], "TD15": ["MEA-03", "SCI-17"], "TD16": ["PRV-08"],
    "TD17": ["INF-03", "MEA-09"], "TD18": ["PRV-10"], "TD19": ["PRV-01"],
    "ID1": ["SCI-16", "MEA-17"], "ID2": ["MEA-05"], "ID3": ["PRV-07", "MEA-13"], "ID4": ["INF-03"], "ID5": ["PRV-06"],
    "ID6": ["MEA-09"], "ID7": ["HUM-02"], "ID8": ["CMP-04"], "ID9": ["PRV-09"], "ID10": ["CMP-08"], "ID11": ["PRV-11"],
    "ID12": ["PRV-01"],
}


# =====================================================================================================================
# POST-FREEZE AMENDMENTS (final review workflow wf_335d0a49-a24, 2026-10-01). The frozen v2 definitions above are kept
# verbatim; each amendment below records what changed and why. None of these amendments was motivated by salvage
# findings: they answer charter-compliance, internal-consistency and hostile-scientific-review findings.
# =====================================================================================================================

GATES_FIXED.append("GATE-NOVELTY")
_BY = {r["id"]: r for r in R}


def amend(aid, rid, reason, **fields):
    r = _BY[rid]
    r.setdefault("amendments", []).append("%s: %s" % (aid, reason))
    r.update(fields)


# --- gating: shrink SLICE to what X1a needs (review: SLICE contradicted the 30-day plan) ----------------------------
amend("A01", "ORG-06", "re-gated to CORE; the slice needs only the lifetime-modification switch (DEV-01)", gate="CORE")
amend("A02", "ORG-20", "re-gated to CORE; the slice uses only the X1 switches (lifetime modification, internal ticks)",
      gate="CORE")
amend("A03", "AGR-08", "re-gated to CORE; X1a's reference arm is part of the slice plan but not a slice gate",
      gate="CORE")
amend("A04", "WLD-04", "slice scope: F1 exact dynamic programme; the different-author slow solver is CORE",
      text=_BY["WLD-04"]["text"] + " In the slice, F1's exact dynamic programme suffices; the different-author slow "
      "solver is required at CORE.",
      fake="A qualification-tier family whose 'exact' solver is an unbounded heuristic search: certificate validator "
      "refuses the exact bound type.")
amend("A05", "WLD-07", "slice scope: F1 channels only; all families at CORE",
      text=_BY["WLD-07"]["text"] + " In the slice the audit covers F1; every admitted family is covered at CORE.")
amend("A06", "MEA-02", "slice scope: authored plants at I1 plus random genomes; procedurally generated class at CORE",
      text=_BY["MEA-02"]["text"] + " In the slice, authored plants at I1 plus random genomes suffice for the "
      "acquisition-curve dossier; the procedurally generated class is required at CORE.")
amend("A07", "MEA-03", "slice ladder for the known-positive replication; FSC-learner rungs at CORE",
      text=_BY["MEA-03"]["text"] + " For the slice's known-positive replication (X1a) the ladder is constant, best "
      "fixed policy, best detect-and-dispatch genome and random genome; the acquisition-matched FSC rungs are required "
      "at CORE.")
amend("A08", "SCI-02", "L1-slice waiver and L4 split",
      text=_BY["SCI-02"]["text"] + " An L1-slice verdict (known-positive replications in the vertical slice) waives the "
      "CAU-10 minimisation and AGR-13 follow-up clauses of L1. L4 is split into L4r (reasoning primitive) and L4d "
      "(developmental primitive), REQUIREMENTS.md s7.")

# --- nulls, brackets, vocabulary ----------------------------------------------------------------------------------
amend("A09", "SCI-03", "charter s3 categories kept distinct: provenance type added; phenomenon split; UNBRACKETED added",
      text=_BY["SCI-03"]["text"] + " Added types: provenance (custody, lineage-label or untracked-input defect); "
      "UNBRACKETED (no lower bracket exists, SCI-13). 'Phenomenon' is split into hypothesis-refuted (a preregistered "
      "directional prediction contradicted under a null certificate) and true-negative (absent within certified "
      "bounds, no directional prediction).")
amend("A10", "SCI-13", "bracket types defined so novel phenomena can receive a null; otherwise UNBRACKETED",
      text="No null in a (substrate, search, development, ruler) combination is typed phenomenon-level unless a lower "
      "bracket exists of one of two types: (a) an evolved or developed positive of the same phenomenon type at the "
      "ADJACENT easier point of a declared difficulty axis, produced by the identical combination; or (b) a "
      "rediscovery-from-distance positive: a planted genome of the same phenomenon type placed at operator distance "
      "k >= d0/2 from the initial distribution and recovered by the identical search, development and ruler in >= 3 "
      "of N runs. X1 brackets only lifetime-learning phenomena. Without a bracket the null is typed UNBRACKETED. The "
      "null is reported as a boundary between the last YES and the first NO point.")
amend("A11", "SCI-08", "regime certificate added as an element for recursive-sagacity nulls",
      text=_BY["SCI-08"]["text"] + " For recursive-sagacity nulls the regime certificate (PRS-14) is an additional "
      "element.")
amend("A12", "SCI-17", "lint list extended to the charter's s24 terms",
      text=_BY["SCI-17"]["text"] + " The lint list also includes emergence, cognition, sagacity, self-improvement and "
      "self-monitoring.")
amend("A13", "PRS-14", "made REQUIRED for any recursive-sagacity null (it is a SCI-08 element)", pri="REQUIRED",
      enforce="BLOCK", fake="A recursive-sagacity null obtained under a P3 regime with no P3b certificate: refused "
      "phenomenon typing.")

# --- recursive sagacity: executor-set rule (review: order propagated through library-as-prior) ---------------------
amend("A14", "DEV-14", "order rule changed to executor sets; R6 executor-vs-content transplant; battery extended",
      text="Every lifetime write is tagged with its EXECUTOR set: the minimal set of instructions or nodes whose "
      "execution performed the write (ablating a member changes or prevents the write while operands are held fixed). "
      "Structures consulted only as operands, templates or proposal priors do not propagate order. A developed "
      "structure has order k+1 when the highest-order member of its executor set has order k. The instrument supports "
      "reversion of all structure at or above an order, donor-depth dose-response transplants, and R6 "
      "executor-versus-content transplants (host A: donor order >= 2 executors with birth content; host B: birth "
      "executors with donor content). It is qualified on planted organisms that must classify correctly: order 1; "
      "order 2 (library as proposal prior); order 3 (self-modified builder); a maturation clock; a fixed builder with a "
      "compositional library of composition depth >= 5 (must classify <= order 2); the gradient meta-learned recurrent "
      "reference with persistent activations (must classify <= order 2); and a saturation null in which random genomes "
      "and P1/P2-evolved genomes have < 5% of developed structure tagged order >= 3, otherwise recursion is "
      "RECURSION_UNTESTABLE in that substrate.",
      fake="A deep-library organism (fixed builder, composition depth 6) tagged order 3: instrument refused.")
amend("A15", "DEV-05", "value-only control frozen in the preregistration instead of 'strongest available'",
      text=_BY["DEV-05"]["text"].replace("the strongest available value-only learner",
                                         "the value-only learner class and budget named in the experiment's freeze"))

# --- pressures, assays, worlds ------------------------------------------------------------------------------------
amend("A16", "PRS-01", "genome-budget axis G added; competition and cooperation explicitly deferred to P4/E9",
      text=_BY["PRS-01"]["text"] + " Axis G: genome budget swept relative to the description length of the minimal "
      "solution; a developmental program is predicted when the solution exceeds the budget. Competition and "
      "cooperation are deferred to P4 (E9) because they confound single-organism developmental attribution until the "
      "instruments are qualified.")
amend("A17", "PRS-07", "catastrophic shift added as a distinct axis",
      text=_BY["PRS-07"]["text"] + " Rare, large regime shifts (catastrophic shift) are a separate axis from the change "
      "rate.")
amend("A18", "MEA-07", "incidental recurrence vs genuine reuse assay added",
      text=_BY["MEA-07"]["text"] + " Incidental recurrence (similar canonical cores built separately, convergently or "
      "by SPAWN copy) is separated from reuse (one core invoked from several contexts) by shared ablation and material "
      "copy lineage, with both classes planted in MEA-16.")
amend("A19", "WLD-01", "minimal sufficient policy stated per family; depth-proxy prior art",
      text=_BY["WLD-01"]["text"] + " Each family also states its minimal sufficient policy in the declared policy "
      "language with its analytic size (for example identify-then-exploit with log2(#mappings) bits; the causal-state "
      "count; a k-slot keyed store of k*log2|V| bits). d_think is a logical-depth-style quantity (Bennett 1988); "
      "excess entropy (Crutchfield and Feldman 2003) is among the proxies the certificate must beat (X2).")

# --- independence and anti-gravity --------------------------------------------------------------------------------
amend("A20", "REP-04", "I3 re-execution from raw receipts and source, including a code read",
      text="Analyses supporting L4r/L4d and every externalisation are re-executed by an I3 party (another model "
      "family or a human) from raw receipts and source, including a code read of the kernel, the ruler(s) and the "
      "world generator, not only re-derived from frozen rows.")
amend("A21", "AGR-07", "probe kernel authorship at I3 required", text=_BY["AGR-07"]["text"].replace(
    "authored at class >= I2, preferably I3", "authored at class I3 (another model family or a human)"))
amend("A22", "AGR-14", "renamed operator-model-free arm; scope of what it controls stated",
      title="Operator-model-free reference arm",
      text=_BY["AGR-14"]["text"] + " This arm removes only the model-operator channel: substrate, primitive basis A0, "
      "worlds and rulers are model-authored in every arm; only AGR-15/AGR-18 generated bases, the probe kernel and a "
      "second substrate probe that prior.")
for _rid in ("AGR-09", "AGR-12", "AGR-15"):
    amend("A23", _rid, "moved from GATE-L3 to GATE-NOVELTY: required for unfamiliarity claims and externalisation, "
          "not for mechanism status", gate="GATE-NOVELTY")

# --- counterfeits for SLICE requirements and for failure classes that lacked one -------------------------------------
_FAKES = {
    "ORG-07": "A run whose receipt reports structure counts that differ between replays: replay check fails.",
    "DEV-01": "A 'development off' arm that still executes REWRITE instructions: switch audit fails.",
    "DEV-06": "A curriculum grader object reachable from organism memory: leak audit fails.",
    "PRS-04": "A champion chosen by a job that read a sealed key: key-access log refuses the verdict.",
    "MEA-12": "A verdict row whose decisive field came from a model call: row-class filter ignores it.",
    "MEA-13": "A generator's self-rating field fed to a ruler: row-class filter ignores it.",
    "PRV-01": "Two artifacts with LF and CRLF bytes registered under different hashes, or a duplicate id: "
              "registration refused.",
    "PRV-03": "A ledger with a prediction row appended after its observation row: chain verifier fails.",
    "PRV-06": "A dashboard number that differs from a rebuild of the primary store: rebuild-equality check fails.",
    "PRV-07": "A model-authored row labelled 'computed': the writer process contradicts the label; the row is ignored.",
    "PRV-08": "A crashed run recorded as zero output: outcome schema refuses the missing failure type.",
    "PRV-09": "A consumer reading a path its producer never declared: interface registry check fails.",
    "PRV-10": "An emergence claim whose localised core descends from a plant: ancestry tag refuses the claim.",
    "PRV-11": "A test secret committed in a tracked file: pre-commit scanner blocks the commit.",
    "REP-01": "A run whose replay differs at bit level on CPU: replay test fails.",
    "REP-06": "A reimplementation declared I2 whose sandbox log shows a read of the claimant's rows: classed I1.",
    "CMP-01": "A fast kernel that diverges from the slow reference on a generated corpus case: differential test fails.",
    "CMP-02": "A receipt without CPU-seconds or nominal energy: receipt schema refuses it.",
    "CMP-04": "Two identical-input jobs both executed (idempotency failure): runner refuses the second.",
    "CMP-05": "A campaign launched whose throughput x budget is below the reachability estimate: launch refused.",
    "CMP-07": "A second-substrate work item opened before the slice's L1-slice verdict: build plan check refuses it.",
    "CMP-08": "A standing service killed without producing a typed failure record within an hour: fault test fails.",
    "INF-01": "A model call from a code path tagged with no declared fork: client refuses the call.",
    "INF-02": "A coding session whose tokens are absent from the build ledger: reconciliation flags it unattributed.",
    "INF-03": "A status line whose value is not reproducible from receipts: status generator check fails.",
    "INF-06": "A work item at 1.6x its token budget still running: stop rule fires.",
    "NRG-02": "A new work item opened on a resource line already 30% over envelope: blocked.",
    "HUM-02": "A control-regime change recorded less than the minimum dwell after the previous one: register check "
              "fails.",
    "HUM-04": "A week with operator time above 90 minutes and no defect logged: digest flags the breach.",
    "WLD-09": "A world that supplies a copy operation to organisms in a heredity experiment: helper-ablation check "
              "fails.",
    "MEA-15": "A decoder that reads input difficulty as 'own error' with no beat over the raw-input decoder: "
              "qualification refuses it.",
    "TRF-06": "A TS claim whose advantage disappears against the capacity-matched naive host: refused.",
    "AGR-12": "A familiarity reference that scores a sealed generated mechanism FAMILIAR: reachability fixture fails.",
}
for _rid, _f in _FAKES.items():
    if not _BY[_rid]["fake"]:
        amend("A24", _rid, "counterfeit fixture added (review: SLICE requirements and covered classes lacked one)",
              fake=_f)

# --- new requirements ------------------------------------------------------------------------------------------------
req("NRG-03", "REQUIRED", "SLICE", "BLOCK", "Dollar cost per receipt",
    "A versioned price table in the program constants file holds per-model-id input, output, cache-write and "
    "cache-read token rates, the rented GPU-hour rate, the electricity tariff per kWh and optional hardware "
    "amortisation per core-hour. Receipts and the build ledger compute USD = sum(tokens by class x rate) + GPU-hours x "
    "rate + kWh x tariff (+ amortisation), reconciled monthly against provider invoices to within 10%.",
    "The charter asks for dollar cost; money is the common unit for trading tokens, compute and energy.",
    "Ixion s7 (no cost record exists)", "Token counts only.", "Monthly reconciliation against invoices.",
    "A receipt whose USD field is quoted rather than computed from the price table: receipt schema refuses it.", "S")
req("DEV-15", "REQUIRED", "CORE", "RULE", "Credit assignment is organism-constructed",
    "The physics supplies no global error or gradient signal; the world supplies only declared reward or observation. "
    "Any credit-assignment carrier must be evolved or developed; it is localised by interchange on eligibility-like "
    "state, and a planted fixed-rule credit assigner is part of the MEA-16 battery. Architectural reorganisation is "
    "defined as a change of macro-scale organisation (module or strongly-connected-component partition under CAU-08 "
    "operators) coinciding with a capability change, distinct from local structural writes.",
    "Credit assignment is one of the charter's developmental distinctions; supplying it in the physics would install "
    "the mechanism under study.", "", "Backprop-like signals in the physics.",
    "Static check: no physics module computes an error term from the world's reward.",
    "A physics release exposing a per-node error signal derived from reward: static check fails.", "S")
req("DEV-16", "HIGH VALUE", "GATE-L4", "FLAG", "Reachability expansion",
    "A developmental stage creates a new reachable stage when a family censored (unacquired within the lifetime) in "
    ">= q of N naive runs has a finite censoring-aware acquisition cost after another family is acquired, and "
    "retention-boundary reversion of the carrier built for it makes the family censored again; the count of families "
    "acquirable below budget is reported against age.",
    "The charter asks how developmental stages create new reachable stages.", "Challenge 4c", "Not measured.",
    "Planted prerequisite organisms show expansion; reversion removes it.", "", "S")
req("REP-08", "REQUIRED", "CORE", "BLOCK", "Cross-family audit and sealed counterfeits before the day-60 gate",
    "Before the day-60 gate, an I3 party (a budgeted non-Claude model through code, or a human) reads and audits the "
    "verdict job and the acquisition-curve ruler source and authors at least 20 sealed counterfeits that the gate "
    "authors never see; E0's success criterion is the catch rate on these held-out counterfeits, not on "
    "requirement-derived fixtures.", "Requirement authors, gate authors and counterfeit authors from one family teach "
    "to the test.", "T17 T22; hostile review", "Same-family counterfeits only.", "Catch rate on the held-out set.",
    "An E0 pass reported on requirement-derived fixtures only: day-60 gate refuses it.", "M", "FORK")
req("AGR-18", "REQUIRED", "CORE", "BLOCK", "Search-mass reservation outside the authored basis",
    "In every discovery campaign family a preregistered share of search evaluations (default >= 30%) runs under "
    "procedurally generated primitive bases A1..An and, once certified, at least one open-demand family (WLD-15) "
    "receives a preregistered share; realised shares are reported in the quarterly yield vector. This is an "
    "allocation, not evidence of anti-gravity (contrast the rejected AGR-03).",
    "Without it, discovery search runs only in the authored basis, a familiar computing ontology.",
    "charter s23; review", "No reservation; L3-only re-search.", "Realised-share report per campaign.",
    "A discovery campaign launched with 0% generated-basis evaluations: launch refused.", "S")
req("MEA-19", "REQUIRED", "CORE", "BLOCK", "Compression-regime qualification battery",
    "Before 'compression' or 'transferable sagacity' is used about a result, the TS ruler must rank four planted "
    "organisms correctly: stored solutions (saves only on canonicalised seen instances; TS = 0 on structurally novel "
    "families), patterns (saves environment transitions to identify latent state, not policy feedback), strategies "
    "(saves policy acquisition within developed families, not on two-sided-certified novel families) and principles "
    "(saves on certified novel families).", "The charter's 1,000 solutions / 100 patterns / 20 strategies / 5 "
    "principles comparison must be measurable, not asserted.", "charter s6", "Assert the ordering.",
    "TS ranks the four planted organisms in order.",
    "A stored-solutions organism credited with TS > 0 on a certified novel family: ruler refused.", "M")
req("SCI-19", "REQUIRED", "GATE-L2", "BLOCK", "Adversarial survival at L2",
    "An L2 claim survives a budgeted explanation attempt by a party at independence class >= I2 given only the frozen "
    "rows and the preregistration; the attempt's alternative explanations are tested and recorded.",
    "Maps the charter's 'adversarial survival' stage onto the ladder.", "T22; charter s17", "None.",
    "Planted false L2 claims are explained away; genuine ones survive.",
    "An L2 promotion with no recorded explanation attempt: verdict job refuses it.", "S")

COVERAGE["T13"].append("DEV-15")
COVERAGE["T15"] = ["AGR-12", "AGR-09", "AGR-06"]
COVERAGE["T17"].append("REP-08")

# --- vocabulary: remove the undefined near-synonym the SCI-17 lint now forbids (final review, A12 follow-up) --------
amend("A25", "WLD-16", "'self-monitoring' replaced by 'own-reliability tracking' (s3 metacognition predicate)",
      text=_BY["WLD-16"]["text"].replace("policy without self-monitoring", "policy without own-reliability tracking"),
      test=_BY["WLD-16"]["test"].replace("Planted self-monitoring organism",
                                         "Planted own-reliability-tracking organism (metacognition clauses i-iii TRUE)"))

# --- verification pass after the final review (workflow wf_1b94ed0a-e44) ------------------------------------------
_BY = {r["id"]: r for r in R}  # include the requirements added after the first amendment block
amend("A26", "WLD-02", "slice scope: F1 admitted on the S1 baseline subset; the FSC learners are required at CORE",
      text=_BY["WLD-02"]["text"] + " In the slice, F1 is admitted on the S1 baseline subset (constant, best fixed "
      "policy, best detect-and-dispatch genome, random genome) with exact Delta and rho; the acquisition-matched FSC "
      "learners are required at CORE.")
amend("A27", "MEA-02", "slice independence rule stated (computed classes are CORE)",
      text=_BY["MEA-02"]["text"] + " In the slice, I1 is determined from the logged authorship record (the plant "
      "author is a different session from the ruler author, with a shared brief and no read access to the ruler "
      "code); computed classes (REP-06) are required at CORE.")
amend("A28", "CMP-07", "L1-slice wording in text and test",
      text=_BY["CMP-07"]["text"].replace("at L1 with its matched negative", "at L1-slice with its matched negative"),
      test=_BY["CMP-07"]["test"].replace("the slice's L1 row", "the slice's L1-slice verdict"))
amend("A29", "NRG-02", "USD line added to the envelope",
      text=_BY["NRG-02"]["text"].replace("GPU-hours (local and rented) and kWh;",
                                         "GPU-hours (local and rented), kWh and USD computed from the NRG-03 price "
                                         "table;"))
amend("A30", "WLD-15", "made REQUIRED and blocking so the AGR-18 open-demand share cannot be avoided",
      pri="REQUIRED", enforce="BLOCK",
      fake="An S4 discovery campaign family launched with no certified open-demand family receiving a preregistered "
      "share: launch refused (AGR-18).")
amend("A31", "AGR-18", "open-demand share mandatory from S4",
      text=_BY["AGR-18"]["text"].replace(
          "and, once certified, at least one open-demand family (WLD-15) receives a preregistered share;",
          "and, from S4 (month 4), at least one certified open-demand family (WLD-15) receives a preregistered share;"))
amend("A32", "MEA-01", "'why' corrected: an attainable verdict set is not detectability",
      why=_BY["MEA-01"]["why"].replace("showed they could output the class they ruled on",
                                       "had demonstrated detectability (planted positive recovered, matched negative "
                                       "rejected)"))
amend("A33", "WLD-01", "X2 test restated against the best proxy",
      test="Certificates predict the held-out performance of learners not used in any certificate computation better "
      "than the best proxy (state count, observation entropy rate, excess entropy, optimal-policy description length) "
      "by a preregistered margin (X2).")
amend("A34", "DEV-14", "order-2 plant made consistent with the executor rule",
      text=_BY["DEV-14"]["text"].replace(
          "order 1; order 2 (library as proposal prior); order 3 (self-modified builder)",
          "order 1, including a library used only as a proposal prior (consulted structure does not propagate order); "
          "order 2 (a developed update rule that executes later writes); order 3 (a self-modified builder)"),
      test="Planted organisms classified correctly, including the deep-library, meta-learned-RNN and saturation-null "
      "plants.")
amend("A35", "AGR-07", "trigger keyed to L4r; X0 no longer named as deciding the substrate question",
      text=_BY["AGR-07"]["text"].replace("a claim reaching L4;", "a claim reaching L4r;"),
      test="X0b (with a reachable portfolio branch), X10/X10b, X11 and the port-cost receipt decide; X0 is "
      "non-discriminating for substrate count; triggers logged.")
GATES_FIXED[GATES_FIXED.index("GATE-L4")] = "GATE-L4r"
GATES_FIXED.insert(GATES_FIXED.index("GATE-L4r") + 1, "GATE-L4d")
for _rid, _g in (("DEV-05", "GATE-L4d"), ("DEV-08", "GATE-L4d"), ("DEV-10", "GATE-L4d"), ("DEV-16", "GATE-L4d"),
                 ("SCI-10", "GATE-L4r"), ("CAU-07", "GATE-L4r"), ("TRF-02", "GATE-L4r"), ("TRF-03", "GATE-L4r"),
                 ("REP-04", "GATE-L4r")):
    amend("A36", _rid, "GATE-L4 split into GATE-L4r and GATE-L4d (L4d-only machinery is not a precondition of L4r)",
          gate=_g)

# --- S1 work items: every SLICE requirement is built by exactly one item; budgets in M tokens processed -----------
S1_BUDGET_CAP_M = 80  # 40% of the upper 90-day build envelope (RSE_ARCHITECTURE.md s7)
S1_WORK_ITEMS = [
    ("W1", "R0 runner: deterministic execution, keyed streams, snapshot/restore, receipts (CPU, energy, tokens, USD), "
     "one job runner", 10, ["PRV-01", "PRV-04", "REP-01", "REP-07", "CMP-02", "CMP-04", "MEA-09"]),
    ("W2", "Ledger, signed verdict job, row-class filter, claim ladder to L1-slice, typed nulls, preregistration as "
     "an earlier commit, ledger-derived multiplicity", 12,
     ["SCI-01", "SCI-02", "SCI-03", "SCI-04", "SCI-06", "SCI-09", "SCI-15", "PRV-02", "PRV-03", "PRV-07", "PRV-08",
      "MEA-12"]),
    ("W3", "DGM kernel v0 (X1 instructions) with slow reference interpreter and differential tests, provenance "
     "shadow, stable ids, resource accounting, the two X1 lattice switches", 14,
     ["ORG-01", "ORG-03", "ORG-04", "ORG-07", "ORG-08", "DEV-01", "DEV-04", "CMP-01"]),
    ("W4", "F1 family: generator, exact Delta/rho and exact dynamic programme, sealed splits, slice leak audit, "
     "admission on the S1 baseline subset", 6, ["WLD-01", "WLD-02", "WLD-03", "WLD-04", "WLD-07", "DEV-06"]),
    ("W5", "Acquisition-curve ruler and dossier (authored plants plus random genomes), known-answer statistics "
     "subset, controls wired to abort, row metadata", 8,
     ["SCI-05", "MEA-01", "MEA-02", "MEA-05", "MEA-06", "MEA-11", "MEA-13", "MEA-14"]),
    ("W6", "Evolutionary engine v0 (declared policy, concentration floor, feasibility check), S1 baseline subset, "
     "developmental control table for X1a", 5, ["PRS-02", "PRS-04", "PRS-13", "CMP-05", "MEA-03", "DEV-02"]),
    ("W7", "CPU reference learner (evolved plastic recurrent network) for the X1a reference arm", 3, []),
    ("W8", "Build and token ledger, versioned price table, quarterly envelope, operator digest, inference-fork "
     "registry, slice-first build-plan check", 4,
     ["INF-01", "INF-02", "INF-06", "NRG-02", "NRG-03", "HUM-04", "CMP-07"]),
    ("W9", "Counterfeit fixture suite for the SLICE requirements (CI)", 2, []),
]
