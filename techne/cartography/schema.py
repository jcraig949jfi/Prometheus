"""Storage and provenance schema for the Techne 48-hour research cartography campaign.

THE ONE DESIGN COMMITMENT EVERYTHING ELSE FOLLOWS FROM:

    "paper says X" and "X is true" are different records, and the schema must make it
    impossible to write the second when you only observed the first.

So EvidenceType, SupportRelation and AdjudicationStatus are separate enumerated fields on
every Claim, and the three predicates

    CLAIM_PRESENT       the text asserts it
    CLAIM_SUPPORTED     an experiment in the paper bears on it
    MECHANISM_ISOLATED  the experiment varied that mechanism and held the rest fixed

are stored independently. A paper reporting "Method A beats baseline B, because diversity
increased" gives CLAIM_PRESENT and (usually) CLAIM_SUPPORTED for the performance result, and
gives NOTHING for the diversity attribution unless an ablation isolated it. That third column
is where the campaign's priority lane lives.

MISSING VALUES STAY MISSING. Every budget, metric and descriptor defaults to None, and None
means "not stated in the evidence we hold", never zero and never a guess. A vector completed
by imputation would silently convert an absence of reporting into a measurement.

LLM ROLE. Anything an LLM produced -- a translation, a classification, a synonym, a candidate
gap -- is written with adjudication=PROPOSED and carries `proposed_by`. Only a deterministic
predicate over stored evidence may write CONFIRMED. Nothing in this module can promote a record
on its own; promotion requires the deterministic checks in `predicates.py`.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from typing import Any, Optional

SCHEMA_VERSION = "cartography-0.1"


# --- controlled vocabularies -------------------------------------------------------------
# Enumerations are plain tuples of strings, validated on write. A free-text field here would
# become an unauditable taxonomy within a day.

EVIDENCE_TYPE = (
    "AUTHOR_CLAIM",                  # the paper asserts it
    "DIRECT_OBSERVATION",            # a number/table/figure we actually read
    "DERIVED_INTERPRETATION",        # our reading of what the evidence implies
    "REPLICATION",                   # an independent reproduction
    "CONTRADICTION",                 # evidence against
    "UNSUPPORTED_CAUSAL_ATTRIBUTION",  # cause asserted, not isolated
    "UNKNOWN",
)

ADJUDICATION = (
    "PROPOSED",      # an LLM or heuristic suggested it; NOT adjudicated
    "CONFIRMED",     # a deterministic predicate over stored evidence passed
    "REFUTED",       # a deterministic predicate over stored evidence failed
    "BLOCKED",       # could not be adjudicated; reason recorded
)

CLAIM_PREDICATE = (
    "CLAIM_PRESENT",
    "CLAIM_SUPPORTED",
    "MECHANISM_ISOLATED",
)

#: Gen-0 bottleneck taxonomy. HYPOTHESES, not sacred -- see taxonomy.py for the mutation rules
#: and the frozen tests a mutation must beat.
BOTTLENECK = ("B1_REPRESENTATION", "B2_CREDIT_SEARCH", "B3_TELEOLOGY_EVAL", "B_UNASSIGNED")

FAILURE_MODE = (
    "premature_convergence", "semantic_nonlocality", "syntax_breakage",
    "representation_ceiling", "compute_explosion", "evaluation_explosion",
    "credit_failure", "flat_landscape", "deceptive_landscape", "generalization_failure",
    "brittleness", "archive_descriptor_failure", "ontology_leakage", "scaling_failure",
    "reproduction_failure", "benchmark_overfitting", "baseline_mismatch",
    "causal_confound", "hidden_compute_shift", "hidden_data_shift",
)

GAP_STATUS = (
    "COVERAGE_HOLE_CANDIDATE",   # an empty QD cell. NOT a discovery.
    "PERSISTENT_COVERAGE_HOLE",  # survived N independent retrieval formulations
    "KILLED_BY_RETRIEVAL",       # adversarial search found occupying work
    "KILLED_AS_ILL_TYPED",       # the cell is not a coherent experiment
)


def _check(value: Optional[str], allowed: tuple, field: str) -> Optional[str]:
    if value is None:
        return None
    if value not in allowed:
        raise ValueError("invalid " + field + ": " + repr(value)
                         + "; allowed: " + repr(list(allowed)))
    return value


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def digest(obj: Any) -> str:
    """Stable content hash, used for artifact identity and for pre-reveal freezing in the
    historical backtest -- where the whole point is that a prediction cannot be edited after
    the future is revealed."""
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# --- records -----------------------------------------------------------------------------

@dataclasses.dataclass
class EvidenceSpan:
    """A literal piece of retrieved text plus where it came from.

    `text` must be VERBATIM from the source. If we only have an abstract, that is what is
    stored and `scope` says so -- an extraction from an abstract must never be recorded as if
    the full experimental section had been read.
    """
    source_id: str
    scope: str                 # "title" | "abstract" | "fulltext" | "metadata" | "repo"
    text: str
    url: Optional[str] = None
    retrieved_at: str = dataclasses.field(default_factory=now_iso)

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ResearchGenome:
    """One paper/artifact compiled into operational coordinates.

    Nearly every field is Optional and defaults to None. That is the point: a genome with six
    populated fields is an honest genome, and a genome with sixty populated fields where forty
    were inferred is a fabrication with good posture.
    """
    research_genome_id: str
    source_id: str
    title: str
    year: Optional[int] = None
    authors: list = dataclasses.field(default_factory=list)
    venue: Optional[str] = None
    source_url: Optional[str] = None
    doi: Optional[str] = None

    # graph edges (ids, not objects -- the graph is reconstructed at read time)
    citation_edges: list = dataclasses.field(default_factory=list)
    cited_by_count: Optional[int] = None
    code_edges: list = dataclasses.field(default_factory=list)
    dataset_edges: list = dataclasses.field(default_factory=list)

    # operational coordinates -- all Optional, all evidence-backed or absent
    problem_statement: Optional[str] = None
    claimed_boundary: Optional[str] = None
    representation: Optional[str] = None
    phenotype_definition: Optional[str] = None
    variation_operator: Optional[str] = None
    search_operator: Optional[str] = None
    selection_operator: Optional[str] = None
    credit_assignment: Optional[str] = None
    archive_operator: Optional[str] = None
    evaluation_operator: Optional[str] = None
    environment: Optional[str] = None
    task_distribution: Optional[str] = None

    baselines: list = dataclasses.field(default_factory=list)
    ablations: list = dataclasses.field(default_factory=list)
    metrics: list = dataclasses.field(default_factory=list)

    # budgets -- None means NOT STATED. Never impute.
    compute_budget: Optional[str] = None
    evaluation_budget: Optional[str] = None
    search_budget: Optional[str] = None
    population_budget: Optional[str] = None
    parameter_budget: Optional[str] = None
    wallclock: Optional[str] = None
    hardware: Optional[str] = None

    claimed_mechanism: list = dataclasses.field(default_factory=list)
    claimed_result: list = dataclasses.field(default_factory=list)
    stated_limitations: list = dataclasses.field(default_factory=list)
    observed_failures: list = dataclasses.field(default_factory=list)

    code_available: Optional[bool] = None
    code_location: Optional[str] = None
    executable_status: Optional[str] = None
    data_available: Optional[bool] = None
    reproduction_status: Optional[str] = None

    open_access: Optional[bool] = None
    fulltext_available: bool = False
    #: False for title-only records. These are ADMITTED to the archive because a cell they
    #: occupy is genuinely occupied, but NO claim predicate may run on them: a title cannot
    #: support CLAIM_PRESENT, CLAIM_SUPPORTED or MECHANISM_ISOLATED.
    abstract_available: bool = False

    #: Independent subject labels from the index (OpenAlex concepts), kept verbatim. These
    #: drive the domain gate precisely BECAUSE they are not produced by our vocabulary.
    concepts: list = dataclasses.field(default_factory=list)
    #: The index's own document type (article / review / book-chapter / ...). Load-bearing for
    #: P4: a review cannot host a confounded experiment because it runs none.
    work_type: Optional[str] = None
    domain_status: Optional[str] = None
    domain_reason: Optional[str] = None

    # QD descriptors
    bottleneck: str = "B_UNASSIGNED"
    descriptors: dict = dataclasses.field(default_factory=dict)

    evidence_spans: list = dataclasses.field(default_factory=list)
    extraction_confidence: dict = dataclasses.field(default_factory=dict)
    techne_translation: Optional[str] = None
    candidate_falsifications: list = dataclasses.field(default_factory=list)
    unresolved_questions: list = dataclasses.field(default_factory=list)

    discovered_in_cycle: Optional[int] = None
    provenance: dict = dataclasses.field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self):
        _check(self.bottleneck, BOTTLENECK, "bottleneck")

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Claim:
    """One assertion, with its predicate level and adjudication kept apart.

    `predicate` says WHAT KIND of statement this row is (present / supported / isolated).
    `adjudication` says whether a deterministic check has run. A row with
    predicate=MECHANISM_ISOLATED and adjudication=PROPOSED is a hypothesis about the paper,
    not a finding about the world, and the reporting layer must never count it as the latter.
    """
    claim_id: str
    research_genome_id: str
    text: str
    predicate: str
    evidence_type: str
    adjudication: str = "PROPOSED"
    evidence_spans: list = dataclasses.field(default_factory=list)
    supports: list = dataclasses.field(default_factory=list)
    contradicts: list = dataclasses.field(default_factory=list)
    extraction_confidence: Optional[float] = None
    adjudicated_by: Optional[str] = None      # name of the deterministic predicate that ran
    adjudication_reason: Optional[str] = None
    proposed_by: Optional[str] = None         # "llm" | "regex:<name>" | "human"
    source_location: Optional[str] = None
    cycle: Optional[int] = None
    created_at: str = dataclasses.field(default_factory=now_iso)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self):
        _check(self.predicate, CLAIM_PREDICATE, "predicate")
        _check(self.evidence_type, EVIDENCE_TYPE, "evidence_type")
        _check(self.adjudication, ADJUDICATION, "adjudication")

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class RetrievalAttempt:
    """One query actually issued, with its result count. This is what makes an absence claim
    auditable: a coverage hole is only as strong as the searches that failed to fill it, and
    those searches must be inspectable by someone who does not trust us."""
    query: str
    source: str                      # "openalex" | "crossref" | "arxiv" | "dblp"
    formulation: str                 # which independent formulation this is
    n_results: int
    n_relevant: int = 0
    top_ids: list = dataclasses.field(default_factory=list)
    issued_at: str = dataclasses.field(default_factory=now_iso)
    url: Optional[str] = None

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class CoverageHole:
    """An empty QD cell. NOT a discovery, and the type name is deliberately not 'Gap'.

    `status` starts at COVERAGE_HOLE_CANDIDATE and can only reach PERSISTENT_COVERAGE_HOLE by
    surviving N independent retrieval formulations, all of which are stored in
    `retrieval_attempts`. Even then it means only "no matching experiment found under this
    protocol" -- which is a statement about our retrieval, not about humanity.
    """
    hole_id: str
    coordinates: dict                # the QD cell: descriptor -> value
    status: str = "COVERAGE_HOLE_CANDIDATE"
    retrieval_attempts: list = dataclasses.field(default_factory=list)
    n_formulations: int = 0
    nearest_prior_work: list = dataclasses.field(default_factory=list)
    why_nearest_does_not_fill: Optional[str] = None
    killed_by: Optional[str] = None
    cheapest_falsification: Optional[str] = None
    confidence_in_absence: Optional[str] = None   # deliberately a word, not a number
    #: The archive's classification health WHEN THIS HOLE WAS PROPOSED. Load-bearing: an empty
    #: cell in an archive where 96.7% of papers could not be placed is a statement about the
    #: tagger, not about the literature. Measured 2026-08-31 at cycle 020: 3.3% of
    #: abstract-bearing genomes were fully classified and 49% carried zero mechanism tags.
    #: Without this field a hole count reads as a gap count, which is the campaign's single
    #: most dangerous misreading.
    archive_classification_rate: Optional[float] = None
    archive_size_at_proposal: Optional[int] = None
    cycle: Optional[int] = None
    created_at: str = dataclasses.field(default_factory=now_iso)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self):
        _check(self.status, GAP_STATUS, "status")

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ConfoundedClaim:
    """A causal attribution where the attributed mechanism was not the only thing that moved.

    This is the campaign's priority lane. `co_varying` lists the OTHER treatment differences
    found in the same comparison; a non-empty list with a causal claim attached is the
    signature of CONFOUNDED_MECHANISM_CLAIM. `cost_migration` records the stronger pattern:
    the bottleneck was not removed, it was relocated.
    """
    confound_id: str
    research_genome_id: str
    claimed_mechanism: str
    co_varying: list = dataclasses.field(default_factory=list)
    cost_migration: Optional[str] = None     # e.g. "C_exec -> C_eval"
    evidence_spans: list = dataclasses.field(default_factory=list)
    adjudication: str = "PROPOSED"
    adjudicated_by: Optional[str] = None
    cycle: Optional[int] = None
    created_at: str = dataclasses.field(default_factory=now_iso)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self):
        _check(self.adjudication, ADJUDICATION, "adjudication")

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class CycleRecord:
    """The durable fossil of one 30-minute cycle. Written whether the cycle succeeded, found
    nothing, or was blocked -- a cycle that produced nothing and says so is a data point about
    the frontier; a cycle that produced nothing and wrote nothing is a hole in the record."""
    cycle: int
    started_at: str
    ended_at: Optional[str] = None
    frontier_kind: Optional[str] = None
    frontier_target: Optional[str] = None
    searches: list = dataclasses.field(default_factory=list)
    sources_new: int = 0
    sources_rejected: int = 0
    genomes_created: int = 0
    claims_created: int = 0
    claims_adjudicated: int = 0
    holes_proposed: int = 0
    holes_killed: int = 0
    confounds_found: int = 0
    experiments_proposed: int = 0
    taxonomy_changes_proposed: int = 0
    failures: list = dataclasses.field(default_factory=list)
    blockers: list = dataclasses.field(default_factory=list)
    notes: list = dataclasses.field(default_factory=list)
    artifact_digest: Optional[str] = None
    status: str = "OK"               # OK | NULL | BLOCKED | INVALID
    schema_version: str = SCHEMA_VERSION

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)
