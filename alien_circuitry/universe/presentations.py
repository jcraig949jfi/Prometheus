"""Presentations for Universe A.  Each relator direction is its own named rule.

U-A1  ABELIAN   <x, y | xy = yx>      calibration universe.  Diagnostic truth (withheld from compressors):
                                       the exponent vector (#x - #X, #y - #Y) is invariant under every action.
U-A2  BRAID_B3  <x, y | xyx = yxy>    test universe.  Known mathematics (Garside normal form) is NOT encoded anywhere.

The abelian presentation lists all four commutation variants because, without an introduce rule, the graph
cannot derive  xY = Yx  from  xy = yx  by conjugation; each variant must be a primitive action to make the
operational relation match the intended calibration structure.  This is a design choice, documented here.

PC2 (cloned actions) is a plumbing control: `with_clones` appends an exact duplicate of every relator rule under
a different name.  The clone is behaviourally identical by construction; the control checks that pipelines merge it.
"""
from .directed_rewriting import Rule, cancel_rules

PRESENTATIONS = {
    # name: (relations, both_directions)
    "ABELIAN": ([("xy", "yx"), ("xY", "Yx"), ("Xy", "yX"), ("XY", "YX")], True),
    "BRAID_B3": ([("xyx", "yxy"), ("XYX", "YXY")], True),
    # U-A3 CANDIDATE (diagnostic only, not adopted): the braid relation applied in ONE direction.  With cancel this is a
    # terminating, NON-confluent rewriting system; traps then arise from committing to the wrong normal form
    # (critical-pair divergence), not from targeting a non-normal-form word.
    "BRAID_B3_ONEWAY": ([("xyx", "yxy"), ("XYX", "YXY")], False),
    # U-A3 ONE-WAY BRAID (lookahead gate, 2026-09-12): exactly the relator xyx -> yxy, one way, plus cancel.
    # Terminating by the measure (len, #x) in lexicographic order: cancel lowers len; the relator keeps len and
    # replaces two x and one y by one x and two y, so #x drops by one.  Termination is intrinsic, not cap-induced.
    # Non-confluent: 'xyxX' -> 'xy' (cancel) or -> 'yxyX' (relator), and 'yxyX' is terminal.
    "U_A3_ONEWAY_BRAID": ([("xyx", "yxy")], False),
    # PC1 CANDIDATES for the gate (measured, not adopted): one-way commutation.
    # ONEWAY_ABELIAN_ALL4 moves every y-letter left past every x-letter; expected confluent (no divergence).
    # ONEWAY_ABELIAN_XY has only xy -> yx; expected non-confluent ('xyY' -> 'x' or -> 'yxY' terminal).
    "ONEWAY_ABELIAN_ALL4": ([("xy", "yx"), ("xY", "Yx"), ("Xy", "yX"), ("XY", "YX")], False),
    "ONEWAY_ABELIAN_XY": ([("xy", "yx")], False),
}


def rules_for(name: str, with_clones: bool = False) -> list[Rule]:
    rels, both = PRESENTATIONS[name]
    rules = cancel_rules()
    for i, (l, r) in enumerate(rels):
        rules.append(Rule(f"rel{i}[{l}->{r}]", "relator", l, r))
        if both:
            rules.append(Rule(f"rel{i}[{r}->{l}]", "relator", r, l))
    if with_clones:
        for i, (l, r) in enumerate(rels):
            rules.append(Rule(f"clone{i}[{l}->{r}]", "relator_clone", l, r))
            if both:
                rules.append(Rule(f"clone{i}[{r}->{l}]", "relator_clone", r, l))
    return rules


def is_cancel_free(word: str) -> bool:
    return all(word[i] != ALPHABET_INV[word[i + 1]] for i in range(len(word) - 1))


def is_normal_form(word: str, name: str) -> bool:
    """No legal action applies (cancel-free and no relator LHS present)."""
    if not is_cancel_free(word):
        return False
    rels, both = PRESENTATIONS[name]
    for l, r in rels:
        if l in word or (both and r in word):
            return False
    return True


ALPHABET_INV = {"x": "X", "X": "x", "y": "Y", "Y": "y"}


def exponent_vector(word: str) -> tuple[int, int]:
    """Diagnostic coordinate for U-A1.  Never to be exposed to a compressor."""
    return (word.count("x") - word.count("X"), word.count("y") - word.count("Y"))
