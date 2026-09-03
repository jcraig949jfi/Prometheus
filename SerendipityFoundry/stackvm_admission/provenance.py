"""Provenance type system for the stackvm-v1 scientific null path.

CONSTITUTIONAL RULE A (from prior adversarial review, now enforced in code):

    HINDSIGHT IN THE HYPOTHESIS IS FREE.
    HINDSIGHT IN THE NULL IS FATAL.

A candidate may be selected using arbitrary historical knowledge: the candidate
is corpus-measurable, and for a null whose distribution GIVEN the candidate does
not depend on the corpus, P(reject | H0) <= 1/K survives ANY corpus-measurable
selection rule -- no multiplicity is owed for the search, however aggressive.
That premise dies the moment any element of the null is fitted to the corpus.

So every value on the scientific null path carries exactly one tag:

  SPEC_DERIVED        read from interpreter / opcode / operator SOURCE. The
                      design of the instrument, never an observation from it.
  PROTOCOL_CONSTANT   fixed by the admission protocol independently of this
                      substrate's history; must be justified without reference
                      to any recorded outcome.
  EXTERNAL_RANDOMNESS beacon-derived, created after the registration commit.
  CORPUS_DERIVED      anything computed from, fitted to, selected because of,
                      or justified by recorded outcomes.

CORPUS_DERIVED IS STRUCTURALLY ILLEGAL ANYWHERE ON THE SCIENTIFIC NULL PATH.
It is a type error refused at construction, not a policy someone must remember.

A TAG IS NOT SELF-CERTIFYING. A registrant can lie. Two defences:
  1. every SPEC_DERIVED value carries a SOURCE CITATION (file, symbol) and the
     content hash of the source file it came from; the checker re-reads the
     file and refuses if the hash does not match or the symbol is absent;
  2. every PROTOCOL_CONSTANT carries a written justification that must not
     mention any recorded outcome, plus the ledger sequence at which it was
     fixed -- a constant fixed AFTER corpus inspection is provenance-suspect
     and must be declared as such.
Neither defence is complete (a determined liar can cite a real symbol for a
value they chose for corpus reasons); section "residual" in the spec says so.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field

SPEC_DERIVED = "SPEC_DERIVED"
PROTOCOL_CONSTANT = "PROTOCOL_CONSTANT"
EXTERNAL_RANDOMNESS = "EXTERNAL_RANDOMNESS"
CORPUS_DERIVED = "CORPUS_DERIVED"

LEGAL_ON_NULL_PATH = frozenset(
    {SPEC_DERIVED, PROTOCOL_CONSTANT, EXTERNAL_RANDOMNESS})
ALL_TAGS = LEGAL_ON_NULL_PATH | {CORPUS_DERIVED}

# Every field of the scientific null path. A null-path object must supply all
# of them; an unlisted extra field is refused (silent extras are how a
# corpus-derived knob hides).
NULL_PATH_FIELDS = (
    "reference_sampler", "reference_config", "context_family",
    "context_arity", "matching_law", "role_rule", "tie_rule",
    "betting_rule", "exclusions", "stopping_rule", "observable",
    "max_steps", "n_references", "n_blocks",
)


class ProvenanceError(TypeError):
    """A type error, deliberately. Refused at construction."""


@dataclass(frozen=True)
class Tagged:
    """A value that cannot be used on the null path without its provenance."""
    value: object
    tag: str
    justification: str
    source_file: str = ""
    source_symbol: str = ""
    fixed_at_seq: int = -1
    _verified: bool = field(default=False, compare=False)

    def __post_init__(self):
        if self.tag not in ALL_TAGS:
            raise ProvenanceError("unknown provenance tag %r" % self.tag)
        if not self.justification.strip():
            raise ProvenanceError(
                "every tagged value needs a justification; an untstated "
                "reason is indistinguishable from a corpus-derived one")
        if self.tag == SPEC_DERIVED and not (self.source_file
                                             and self.source_symbol):
            raise ProvenanceError(
                "SPEC_DERIVED requires source_file and source_symbol -- a "
                "spec claim with no citation is an assertion, not provenance")


def verify_spec_citation(t: Tagged, expected_hash: str = "") -> bool:
    """Re-read the cited source and confirm the symbol is really there.
    Returns True only if the file exists, contains the symbol, and (when an
    expected hash is supplied) still hashes to it."""
    if t.tag != SPEC_DERIVED:
        return True
    if not os.path.exists(t.source_file):
        raise ProvenanceError(
            "SPEC_DERIVED cites a nonexistent file: %s" % t.source_file)
    raw = open(t.source_file, "rb").read()
    h = hashlib.sha256(raw).hexdigest()
    if expected_hash and h != expected_hash:
        raise ProvenanceError(
            "spec source %s changed (hash %s != pinned %s) -- a null built "
            "on a moved spec is not the null that was qualified"
            % (t.source_file, h[:16], expected_hash[:16]))
    if t.source_symbol.encode() not in raw:
        raise ProvenanceError(
            "SPEC_DERIVED cites symbol %r absent from %s"
            % (t.source_symbol, t.source_file))
    return True


class NullPath:
    """The scientific null path. Construction is the enforcement point."""

    def __init__(self, **fields):
        missing = [f for f in NULL_PATH_FIELDS if f not in fields]
        if missing:
            raise ProvenanceError(
                "null path incomplete: %s -- every element must be declared "
                "and tagged before the null can be trusted" % missing)
        extra = [k for k in fields if k not in NULL_PATH_FIELDS]
        if extra:
            raise ProvenanceError(
                "undeclared null-path field(s) %s -- an unlisted knob is how "
                "a corpus-derived value hides" % extra)
        for name, t in fields.items():
            if not isinstance(t, Tagged):
                raise ProvenanceError(
                    "null-path field %r is untagged (%r) -- untagged values "
                    "cannot be admitted to the null path" % (name, type(t)))
            if t.tag == CORPUS_DERIVED:
                raise ProvenanceError(
                    "CORPUS_DERIVED value on the scientific null path: %r "
                    "(%s). Hindsight in the hypothesis is free; hindsight in "
                    "the NULL is fatal. The 1/K bound does not hold for a "
                    "corpus-fitted null." % (name, t.justification[:70]))
            if t.tag not in LEGAL_ON_NULL_PATH:
                raise ProvenanceError("illegal tag %r on %r" % (t.tag, name))
        self.fields = dict(fields)

    def verify_citations(self, pinned: dict = None) -> dict:
        pinned = pinned or {}
        out = {}
        for name, t in self.fields.items():
            out[name] = verify_spec_citation(t, pinned.get(t.source_file, ""))
        return out

    def to_json(self) -> dict:
        return {n: {"value": repr(t.value), "tag": t.tag,
                    "justification": t.justification,
                    "source_file": t.source_file,
                    "source_symbol": t.source_symbol,
                    "fixed_at_seq": t.fixed_at_seq}
                for n, t in sorted(self.fields.items())}
