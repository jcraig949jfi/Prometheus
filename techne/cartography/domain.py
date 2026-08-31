"""Domain gate: keep the corpus to computational search, using an INDEPENDENT signal.

WHY THIS MODULE EXISTS -- a measured defect, not a precaution.

Cycles 000-012 compiled 97 genomes. A hand-written computational-keyword probe flagged 22 of
them (22.7%) as carrying no computational marker at all, and inspection confirmed genuine
contamination: "THE COEVOLUTION OF HUMAN HANDS AND FEET" (paleoanthropology), "Coevolution of
Supermassive Black Holes and Galaxies" (astronomy), "Metabolic Coevolution in the Bacterial
Symbiosis of Whiteflies" (entomology), "Time scale interactions and the coevolution of humans
and water" (hydrology), and a linguistics paper on lexical density pulled in by "lexicase".

One of those -- the hands-and-feet paper -- had already been written into the confound ledger
as a CONFIRMED confounded causal claim. That is the failure this gate exists to stop: the
campaign's priority lane was being populated by homonyms.

WHY NOT MORE KEYWORDS. The probe that found the contamination ALSO misfired: it flagged "The
CMA Evolution Strategy: A Tutorial" and "Non-elitist evolutionary algorithms excel in fitness
landscapes with sparse deceptive regions" as off-domain, and both are core EC. A hand-tuned
keyword list is the same lexical instrument that caused the problem, applied a second time. So
the gate uses OpenAlex's own concept assignments -- a signal produced independently of our
vocabulary, by a system with no stake in this taxonomy.

WHAT THE GATE DELIBERATELY DOES NOT DO. It does not reject a paper merely for being
biological. Bio-inspired computation, evolutionary game theory and computational biology are
legitimately in scope and legitimately carry both labels. Rejection requires an off-domain
concept AND NO in-domain concept -- so the ambiguous middle is KEPT, and kept papers carry
`domain_status` so a later pass can revisit them.
"""
from __future__ import annotations

import re
from typing import Optional

#: STRONG in-domain concepts. These name a FIELD, and a field label is hard to acquire by
#: homonym. A single one of these is sufficient to keep a work.
#:
#: The tier split exists because of a measured failure. OpenAlex tagged "THE COEVOLUTION OF
#: HUMAN HANDS AND FEET" -- a paleoanthropology paper -- with "Selection (genetic algorithm)",
#: alongside Bipedalism, Hominidae and Human evolution. A presence test over a flat in-domain
#: set accepted it on that one label, and the paper then reached the confound ledger as a
#: CONFIRMED confounded causal claim. OpenAlex's classifier has the same homonym problem our
#: lexical tagger has; treating its labels as uniformly reliable imported that problem wholesale.
STRONG_IN_DOMAIN = {
    "computer science", "artificial intelligence", "machine learning",
    "theoretical computer science", "programming language", "computer engineering",
    "software engineering", "computational science", "mathematical optimization",
    "operations research", "deep learning", "reinforcement learning",
    "artificial neural network", "computer vision", "natural language processing",
    "data mining", "distributed computing", "parallel computing", "robotics",
    "automated theorem proving", "formal verification", "program synthesis",
    "genetic programming", "evolutionary computation", "algorithm",
    "discrete mathematics", "information theory", "control theory",
}

#: WEAK in-domain concepts. Individually contaminated by homonymy across biology, ecology and
#: economics -- "selection", "coevolution", "optimization", "population" all have native
#: meanings in those fields. Present here so they still count for something, but never enough
#: on their own to overrule a pile of off-domain field labels.
WEAK_IN_DOMAIN = {
    "selection (genetic algorithm)", "genetic algorithm", "evolutionary algorithm",
    "optimization", "computation", "mathematics", "statistics", "probability",
    "combinatorics", "cybernetics", "convergence (economics)", "robustness (evolution)",
}

#: Union, kept for callers that only need membership.
IN_DOMAIN = STRONG_IN_DOMAIN | WEAK_IN_DOMAIN | {
    "computer science", "artificial intelligence", "machine learning", "algorithm",
    "theoretical computer science", "programming language", "computation", "mathematics",
    "genetic programming", "genetic algorithm", "evolutionary algorithm",
    "evolutionary computation", "optimization", "mathematical optimization",
    "computer engineering", "software engineering", "computational science",
    "artificial neural network", "deep learning", "reinforcement learning",
    "operations research", "discrete mathematics", "computer vision",
    "natural language processing", "robotics", "data mining", "combinatorics",
    "automated theorem proving", "formal verification", "program synthesis",
    "selection (genetic algorithm)", "distributed computing", "parallel computing",
    "statistics", "probability", "information theory", "control theory", "cybernetics",
}

#: Concepts that put a work outside it, ABSENT any in-domain concept.
OFF_DOMAIN = {
    "biology", "ecology", "evolutionary biology", "medicine", "genetics", "botany",
    "zoology", "microbiology", "immunology", "virology", "paleontology", "anthropology",
    "astronomy", "astrophysics", "physics of galaxies", "geology", "hydrology",
    "geography", "political science", "sociology", "psychology", "linguistics",
    "economics", "law", "history", "philosophy", "chemistry", "materials science",
    "agronomy", "veterinary medicine", "oncology", "psychiatry", "nursing",
    "environmental science", "meteorology", "oceanography", "archaeology",
    "human evolution", "hominidae", "coevolution", "herbivore", "bipedalism",
}

#: Fallback only, for records with no concept labels at all. Weaker than the concept gate and
#: marked as such on the record -- a fallback that pretends to the same authority as the
#: primary signal is how a known-weak instrument gets quoted as a strong one.
_COMPUTATIONAL_FALLBACK = re.compile(
    r"\b(algorithm|comput\w+|optimi[sz]\w+|program\w*|neural network|machine learning|"
    r"heuristic|benchmark|software|source code|solver|synthesis|genetic algorithm|"
    r"evolutionary (?:algorithm|computation|strategy|strategies)|fitness function|"
    r"search space|gradient|classifier|dataset|artificial intelligence)\b", re.I)

#: --- SIGNAL 2: VENUE -------------------------------------------------------------------
#:
#: Added after the concept gate was caught failing in BOTH directions on measured cases:
#:   FALSE ACCEPT -- "THE COEVOLUTION OF HUMAN HANDS AND FEET" (paleoanthropology) carried
#:                   OpenAlex's "Selection (genetic algorithm)".
#:   FALSE REJECT -- "Deceptiveness and neutrality: the ND family of fitness landscapes", a
#:                   genuine evolutionary-computation paper, was labelled Economics, Political
#:                   science, Sociology, Advertising and Law and economics -- almost certainly
#:                   because "neutrality" and "deceptiveness" are political-science words.
#:
#: One unreliable signal cannot be repaired by tuning it; it has to be outvoted. Venue is close
#: to independent of both the concept classifier and our own vocabulary: a paper in IEEE
#: Transactions on Evolutionary Computation is in scope whatever any classifier says, and a
#: paper in Molecular Ecology is not. Coverage is 73% of the current corpus, so venue ABSTAINS
#: rather than voting when absent.
COMPUTATIONAL_VENUE = re.compile(
    r"(evolutionary computation|genetic and evolutionary computation|gecco|"
    r"congress on evolutionary computation|cec|parallel problem solving|ppsn|"
    r"foundations of genetic algorithms|foga|artificial life|alife|"
    r"genetic programming|eurogp|"
    r"ieee transactions|acm transactions|acm|ieee|springer|"
    r"neural information processing|neurips|nips|"
    r"international conference on machine learning|icml|iclr|aaai|ijcai|"
    r"journal of machine learning research|jmlr|"
    r"machine learning|artificial intelligence|computer science|computing|computation|"
    r"software engineering|programming language|pldi|popl|oopsla|icse|"
    r"automated reasoning|theorem proving|formal methods|"
    r"arxiv|corr)", re.I)

NON_COMPUTATIONAL_VENUE = re.compile(
    r"(molecular ecology|molecular biology|systematic biology|journal of ecology|"
    r"ecology letters|american naturalist|evolution(?!ary comput)|heredity|genetics|"
    r"proceedings of the royal society|plos (?:biology|medicine|genetics)|"
    r"nature (?:genetics|medicine|ecology|climate)|cell|lancet|"
    r"bioinformatics|briefings in bioinformatics|nucleic acids|"
    r"american economic review|journal of finance|academy of management|"
    r"political science|sociolog\w+|linguistic\w*|astrophysical|astronomy|"
    r"geolog\w+|hydrolog\w+|climate|atmospheric|oceanograph\w+|"
    r"immunolog\w+|virolog\w+|oncolog\w+|psychiatr\w+|medicine)", re.I)


def _venue_vote(venue: Optional[str]) -> tuple:
    """+1 in-domain, -1 off-domain, 0 abstain. Abstention is the default and is not a failure:
    27% of the corpus has no venue at all, and a signal that guesses when it does not know is
    worse than one that stays silent."""
    if not venue:
        return 0, "venue absent (abstains)"
    v = str(venue)
    # Order matters: "Molecular Biology and Evolution" contains neither computational token,
    # but a venue like "IEEE ... Bioinformatics" would match both; off-domain wins there
    # because the subject matter, not the publisher, is what places a paper.
    if NON_COMPUTATIONAL_VENUE.search(v):
        return -1, "non-computational venue: " + v[:60]
    if COMPUTATIONAL_VENUE.search(v):
        return 1, "computational venue: " + v[:60]
    return 0, "venue unrecognised (abstains): " + v[:60]


def _concept_vote(concepts: Optional[list]) -> tuple:
    cl = {str(c).strip().lower() for c in (concepts or []) if c}
    if not cl:
        return 0, "no concept labels (abstains)"
    strong = sorted(cl & STRONG_IN_DOMAIN)
    weak = sorted(cl & WEAK_IN_DOMAIN)
    off = sorted(cl & OFF_DOMAIN)
    if strong:
        return 1, "strong in-domain concept(s) " + repr(strong[:3])
    if len(off) >= OFF_DOMAIN_MAJORITY:
        return -1, str(len(off)) + " off-domain field label(s) " + repr(off[:3]) + ", none strong"
    if off:
        return -1, "off-domain concept " + repr(off[:2]) + ", none strong"
    if weak:
        return 0, "weak in-domain only " + repr(weak[:3]) + " (abstains)"
    return 0, "concepts present but unrecognised (abstains)"


def _lexical_vote(text: str) -> tuple:
    if not text:
        return 0, "no text (abstains)"
    m = _COMPUTATIONAL_FALLBACK.search(text)
    if m:
        return 1, "computational term in text: " + repr(m.group(0))
    return -1, "no computational term in title or abstract"


DOMAIN_STATUS = ("IN_DOMAIN_CONCEPT", "IN_DOMAIN_FALLBACK", "AMBIGUOUS_KEPT",
                 "OFF_DOMAIN_REJECTED", "UNKNOWN_KEPT")


#: How many off-domain FIELD labels outweigh weak-only in-domain evidence. Two is the smallest
#: number that cannot be produced by a single mis-assignment, and the paleoanthropology case
#: carried five.
OFF_DOMAIN_MAJORITY = 2


def classify(concepts: Optional[list], text: str = "", venue: Optional[str] = None) -> tuple:
    """Three independent signals vote. Return (status, reason).

    Signals: OpenAlex concepts, publication venue, and lexical computational markers. Each
    returns +1 / -1 / 0 (abstain). The work is rejected only when the sum is <= -2, i.e. at
    least two signals actively say off-domain and none says otherwise strongly enough.

    WHY A VOTE. The concept gate was caught failing in both directions on real cases -- it
    admitted a paleoanthropology paper via "Selection (genetic algorithm)" and expelled a
    genuine fitness-landscape paper as political science. A single unreliable classifier cannot
    be fixed by tuning its thresholds; it has to be outvoted by signals that fail differently.
    Venue and lexical markers fail differently from concepts and from each other.

    ABSTENTION IS FIRST-CLASS. 27% of the corpus has no venue and some records have no
    concepts. A signal that guesses when it lacks evidence would reintroduce exactly the
    false confidence this design exists to remove.
    """
    cv, cr = _concept_vote(concepts)
    vv, vr = _venue_vote(venue)
    lv, lr = _lexical_vote(text)
    total = cv + vv + lv
    detail = ("concepts=" + str(cv) + " (" + cr + "); venue=" + str(vv) + " (" + vr
              + "); lexical=" + str(lv) + " (" + lr + "); sum=" + str(total))

    if total <= -2:
        return "OFF_DOMAIN_REJECTED", "two or more signals say off-domain | " + detail
    if total >= 2:
        return "IN_DOMAIN_CONCEPT", "two or more signals say in-domain | " + detail
    if total == 1:
        return "IN_DOMAIN_FALLBACK", "net in-domain on one signal | " + detail
    if total == -1:
        return "AMBIGUOUS_KEPT", "net off-domain by one signal -- KEPT for review | " + detail
    return "UNKNOWN_KEPT", "signals cancel or all abstain -- kept, not counted | " + detail


def is_rejected(status: str) -> bool:
    return status == "OFF_DOMAIN_REJECTED"


def counts_as_in_domain(status: str) -> bool:
    """Which statuses may be counted as corpus in a report. AMBIGUOUS_KEPT and UNKNOWN_KEPT
    are held but NOT counted, so headline corpus numbers cannot be inflated by records the
    gate could not actually place."""
    return status in ("IN_DOMAIN_CONCEPT", "IN_DOMAIN_FALLBACK")
