"""Deterministic adjudicators. These are the ONLY functions permitted to write CONFIRMED.

THE DIVISION OF LABOUR THIS MODULE ENFORCES:

    an LLM (or a regex, or a heuristic) may PROPOSE
    only a deterministic function over STORED EVIDENCE may ADJUDICATE

Every predicate here takes evidence spans that are already persisted, applies an explicit rule,
and returns (verdict, reason). The reason string names the rule and quotes what triggered it,
so a reader who distrusts us can re-run the rule against the same stored text and get the same
answer. None of these functions may fetch anything, and none may call a model.

HONEST LIMITS, STATED UP FRONT. These predicates operate mostly on ABSTRACTS, because that is
what open metadata gives us for most papers. An abstract is a marketing surface: it states
results and rarely states ablations, so `mechanism_isolated` will UNDER-fire badly. That is the
right direction to be wrong -- a false CONFIRMED on mechanism isolation would corrupt the
campaign's priority lane, whereas a miss merely leaves a claim at PROPOSED where a human or a
full-text pass can revisit it. The under-firing rate is itself reported, not hidden.
"""
from __future__ import annotations

import re
from typing import Optional

# --- lexical instruments -------------------------------------------------------------------
# Each is a deliberately narrow surface pattern. Narrow beats clever here: a pattern that fires
# often is a pattern whose CONFIRMED verdicts mean nothing.

CAUSAL_CONNECTIVE = re.compile(
    r"\b(because|due to|owing to|attributable to|caused by|as a result of|"
    r"this is explained by|we attribute (?:this|the|these)|stems from|driven by)\b", re.I)

COMPARATIVE = re.compile(
    r"\b(outperform\w*|better than|improve\w*\s+(?:over|upon|on)|superior to|"
    r"exceed\w*|higher than|lower than|reduc\w+\s+(?:by|the)|"
    r"compared (?:to|with)|versus|baseline)\b", re.I)

ABLATION = re.compile(
    r"\b(ablat\w+|we remove\w*|without the|holding .{0,30} (?:fixed|constant)|"
    r"controlled for|all else equal|ceteris paribus|isolat\w+ the|"
    r"with and without|lesion\w*|knockout|counterfactual\w*)\b", re.I)

MATCHED_BUDGET = re.compile(
    r"\b(same (?:number of )?(?:evaluations|budget|compute|samples)|"
    r"equal (?:budget|compute|evaluations)|matched (?:budget|compute|for compute)|"
    r"under (?:the same|identical) budget|iso-?(?:flop|compute|budget))\b", re.I)

#: Treatment dimensions that, if named alongside a causal claim about a DIFFERENT dimension,
#: mean the comparison moved more than one thing at once.
TREATMENT_DIMENSIONS = {
    "representation": re.compile(r"\b(representation|encoding|genotype|architecture|dsl|"
                                 r"grammar|program space)\b", re.I),
    "search_budget": re.compile(r"\b(budget|generations|iterations|evaluations|"
                                r"function evaluations|steps|epochs)\b", re.I),
    "population": re.compile(r"\b(population size|batch size|number of (?:individuals|agents))\b",
                             re.I),
    "data": re.compile(r"\b(training (?:data|set)|dataset|corpus|more data|data augmentation)\b",
                       re.I),
    "compute": re.compile(r"\b(compute|gpu|tpu|flops|wall[- ]?clock|hardware|parallel\w*)\b", re.I),
    "objective": re.compile(r"\b(objective|fitness function|reward|loss function|metric)\b", re.I),
    "selection": re.compile(r"\b(selection|tournament|lexicase|elitis\w+|archive)\b", re.I),
}

#: Cost-migration signatures. The campaign's deepest question is not "did the method win" but
#: "did it remove the bottleneck or relocate it", and these are the relocations worth naming.
COST_MIGRATION = {
    "C_exec -> C_eval": (re.compile(r"\b(cheaper|faster|fewer)\s+\w{0,12}\s*(execution|rollout)",
                                    re.I),
                         re.compile(r"\b(more|additional|increased)\s+\w{0,12}\s*"
                                    r"(evaluations?|simulations?|episodes?)\b", re.I)),
    "C_eval -> C_search": (re.compile(r"\b(fewer|cheaper)\s+\w{0,12}\s*evaluations?\b", re.I),
                           re.compile(r"\b(larger|longer|more)\s+\w{0,12}\s*"
                                      r"(search|population|generations?)\b", re.I)),
    "C_search -> human_ontology": (re.compile(r"\b(faster|fewer|efficient)\s+\w{0,12}\s*search\b",
                                              re.I),
                                   re.compile(r"\b(hand[- ]?(?:designed|crafted|chosen|tuned)|"
                                              r"expert[- ]?(?:defined|designed)|domain knowledge|"
                                              r"prior knowledge|we define the)\b", re.I)),
    "search -> training_data": (re.compile(r"\b(pretrain\w*|fine[- ]?tun\w*|foundation model|"
                                           r"language model)\b", re.I),
                                re.compile(r"\b(large[- ]?scale|billions? of|web[- ]?scale|"
                                           r"internet[- ]?scale)\b", re.I)),
}


def _spans_text(spans: list) -> str:
    """Concatenate stored evidence. Only what was persisted is visible to a predicate."""
    parts = []
    for s in spans or []:
        t = s.get("text") if isinstance(s, dict) else getattr(s, "text", None)
        if t:
            parts.append(t)
    return "\n".join(parts)


def _quote(pattern: re.Pattern, text: str, width: int = 90) -> Optional[str]:
    m = pattern.search(text)
    if not m:
        return None
    a = max(0, m.start() - width // 2)
    return "..." + text[a:m.end() + width // 2].replace("\n", " ") + "..."


# --- P1: CLAIM_PRESENT -----------------------------------------------------------------------

def claim_present(spans: list) -> tuple:
    """The stored text asserts a comparative result.

    This is the weakest of the three predicates and the only one that abstracts support well.
    CONFIRMED means the words are there -- nothing about whether they are true.
    """
    text = _spans_text(spans)
    if not text:
        return "BLOCKED", "no stored evidence spans"
    q = _quote(COMPARATIVE, text)
    if q:
        return "CONFIRMED", "P1 comparative assertion found: " + q
    return "REFUTED", "P1 no comparative assertion in stored evidence"


# --- P2: CLAIM_SUPPORTED ---------------------------------------------------------------------

def claim_supported(spans: list) -> tuple:
    """A comparison against a named alternative appears in the stored evidence.

    Requires BOTH a comparative assertion and an explicit comparator (a baseline, a prior
    method, or a versus construction). "Our method achieves 94%" is CLAIM_PRESENT and is NOT
    CLAIM_SUPPORTED: a number with nothing to compare it to supports no comparative claim.
    """
    text = _spans_text(spans)
    if not text:
        return "BLOCKED", "no stored evidence spans"
    comp = _quote(COMPARATIVE, text)
    if not comp:
        return "REFUTED", "P2 no comparative assertion"
    has_comparator = re.search(r"\b(baseline|state[- ]of[- ]the[- ]art|sota|prior work|"
                               r"compared (?:to|with)|versus|vs\.?|than)\b", text, re.I)
    if not has_comparator:
        return "REFUTED", "P2 comparative language present but no named comparator"
    return "CONFIRMED", "P2 comparison against a named alternative: " + comp


# --- P3: MECHANISM_ISOLATED ------------------------------------------------------------------

def mechanism_isolated(spans: list, mechanism: Optional[str] = None) -> tuple:
    """The evidence reports varying ONE mechanism with the rest held fixed.

    Requires ablation/control language AND, ideally, a matched-budget statement. This predicate
    UNDER-FIRES on abstracts by design: abstracts advertise results, not controls. A REFUTED
    here means "the stored evidence does not show isolation", which for an abstract usually
    means "we cannot see the methods section" -- and that is exactly why the verdict is
    reported alongside the evidence scope rather than as a fact about the paper.
    """
    text = _spans_text(spans)
    if not text:
        return "BLOCKED", "no stored evidence spans"
    abl = _quote(ABLATION, text)
    if not abl:
        return "REFUTED", "P3 no ablation/control language in stored evidence"
    budget = _quote(MATCHED_BUDGET, text)
    if mechanism:
        near = re.search(re.escape(mechanism.replace("_", " ")), text, re.I)
        if not near:
            return "REFUTED", ("P3 ablation language present but the attributed mechanism "
                               + repr(mechanism) + " is not named in the same evidence")
    reason = "P3 ablation/control language: " + abl
    if budget:
        reason += " | matched budget: " + budget
    return "CONFIRMED", reason


# --- P4: CONFOUNDED_MECHANISM_CLAIM ----------------------------------------------------------

def confounded_mechanism_claim(spans: list) -> tuple:
    """A causal attribution where other treatment dimensions also moved and no control is shown.

    The signature: a causal connective, plus two or more distinct treatment dimensions named,
    plus NO ablation language. That is the shape of "X improves things because Y" written over
    an experiment in which Y was not the only change.

    Returns (verdict, reason, co_varying). A PROPOSED-level flag would be cheap; this is
    CONFIRMED only when all three conditions hold over the stored text, so the campaign's
    priority lane is populated by a rule rather than by an impression.
    """
    text = _spans_text(spans)
    if not text:
        return "BLOCKED", "no stored evidence spans", []
    causal = _quote(CAUSAL_CONNECTIVE, text)
    if not causal:
        return "REFUTED", "P4 no causal attribution language", []
    dims = [name for name, pat in TREATMENT_DIMENSIONS.items() if pat.search(text)]
    if len(dims) < 2:
        return "REFUTED", ("P4 causal claim present but fewer than two treatment dimensions "
                           "named (" + repr(dims) + ")"), dims
    if ABLATION.search(text):
        return "REFUTED", ("P4 causal claim with multiple dimensions BUT ablation language "
                           "present -- not confounded on this evidence"), dims
    return ("CONFIRMED",
            "P4 causal attribution + " + str(len(dims)) + " co-varying dimensions "
            + repr(dims) + " + no ablation language | " + causal,
            dims)


# --- P5: COST_MIGRATION ----------------------------------------------------------------------

def cost_migration(spans: list) -> tuple:
    """Did the paper remove a bottleneck, or move it somewhere less visible?

    Fires when a saving on one axis co-occurs with a cost on another. Deliberately conservative:
    both halves must be present in the stored text. Returns (verdict, reason, migrations).
    """
    text = _spans_text(spans)
    if not text:
        return "BLOCKED", "no stored evidence spans", []
    found = []
    reasons = []
    for label, (saving, cost) in COST_MIGRATION.items():
        s, c = saving.search(text), cost.search(text)
        if s and c:
            found.append(label)
            reasons.append(label + " [" + s.group(0) + " / " + c.group(0) + "]")
    if not found:
        return "REFUTED", "P5 no paired saving/cost signature", []
    return "CONFIRMED", "P5 " + "; ".join(reasons), found


# --- P6: PERSISTENT_COVERAGE_HOLE ------------------------------------------------------------

MIN_FORMULATIONS = 4
MIN_SOURCES = 3


def hole_is_persistent(attempts: list) -> tuple:
    """Promote a coverage hole only after independent retrieval genuinely failed.

    Requires at least MIN_FORMULATIONS distinct query formulations across at least MIN_SOURCES
    distinct indexes, ALL returning zero relevant results. Four rephrasings against one index is
    one search wearing four hats, which is why sources are counted separately from formulations.

    A CONFIRMED verdict still means only: "no matching experiment was found under this
    protocol." It does not mean nobody tried it. That sentence is carried on the record itself
    so it cannot be dropped by a summariser downstream.
    """
    if not attempts:
        return "BLOCKED", "no retrieval attempts recorded -- absence is unauditable"
    forms = {a.get("formulation") for a in attempts if a.get("formulation")}
    srcs = {a.get("source") for a in attempts if a.get("source")}
    relevant = sum(int(a.get("n_relevant", 0)) for a in attempts)
    if relevant > 0:
        return "REFUTED", ("P6 retrieval found " + str(relevant)
                           + " relevant result(s) -- the cell is occupied")
    if len(forms) < MIN_FORMULATIONS:
        return "BLOCKED", ("P6 only " + str(len(forms)) + " distinct formulations (need "
                           + str(MIN_FORMULATIONS) + ")")
    if len(srcs) < MIN_SOURCES:
        return "BLOCKED", ("P6 only " + str(len(srcs)) + " distinct sources (need "
                           + str(MIN_SOURCES) + ") -- rephrasings against one index are "
                           "not independent")
    return ("CONFIRMED",
            "P6 " + str(len(forms)) + " formulations across " + str(len(srcs))
            + " independent indexes, 0 relevant. MEANS: no matching experiment found under "
              "this retrieval protocol. Does NOT mean nobody has tried it.")


#: Registry so the cycle loop and the report can enumerate what actually adjudicates, and so a
#: reader can see at a glance that the list is short and every entry is mechanical.
PREDICATES = {
    "P1_claim_present": claim_present,
    "P2_claim_supported": claim_supported,
    "P3_mechanism_isolated": mechanism_isolated,
    "P4_confounded_mechanism_claim": confounded_mechanism_claim,
    "P5_cost_migration": cost_migration,
    "P6_hole_is_persistent": hole_is_persistent,
}
