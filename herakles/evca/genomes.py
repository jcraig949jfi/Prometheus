"""The six recovered EvCA genomes, embedded, with their provenance.

WHY EMBEDDED RATHER THAN LOADED. The library must not read a file at import
or at call time, so the hex strings live here as constants. That creates a
drift risk: the constants could diverge from the specimen record. The risk is
answered by a test, `test_embedded_genomes_match_the_specimen`, which loads
`herakles/specimens/spec-evca-density/derived/evolved_rule_tables.json` and
asserts every field below still matches. Drift becomes a failing test rather
than a silent disagreement between two sources of truth.

PROVENANCE CLASS: RECOVERED_SPECIMEN. These are the original genomes,
produced by the original investigators between 1993 and 1995 and preserved
only as printed hexadecimal in published tables. The bytes were reassembled
from those tables on 2026-09-03 by the Herakles seat. Nothing was inferred or
filled in.

THE PUBLISHED NUMBERS ARE NOT ACCEPTANCE CRITERIA. `published_P` is what the
sources printed. Whether this implementation reproduces it is a separate
QUALIFICATION question with its own conventions, sampling and uncertainty
rule, handled in the C1-e report. Nothing here should be read as a tolerance.

TWO RECOVERY HAZARDS, RECORDED BECAUSE BOTH PRODUCE PLAUSIBLE WRONG DATA:
  1. Row pairing. `pdftotext -layout` mis-pairs continuation rows, moving each
     rule's second hex row onto the following rule's line. The result is
     syntactically valid and scores near zero. Deliberately mis-pairing par's
     first row with exp's second yields a rule scoring about 0.010.
  2. Ligature map. `evca-review.pdf` has a broken Computer Modern ligature
     map; one extracted glyph is really the two characters "ff".

Execution was the only trustworthy transcription check. `maj` and `GKL` are
derivable from their definitions and served as the calibration for the other
four.
"""
from __future__ import annotations

from typing import Dict, List

#: name -> record. `hex` is the pinned 32-digit encoding; `published_P` maps
#: lattice size to the figure printed in the source; `confidence` is the
#: recovery seat's own grade, not an independent one.
GENOMES: Dict[str, Dict[str, object]] = {
    "maj": {
        "hex": "000101170117177f0117177f177f7fff",
        "kind": "hand-designed (simple majority)",
        "published_P": {149: 0.000, 599: 0.000, 999: 0.000},
        "source": "EvCA review Table 1",
        "confidence": "certain",
        "note": "Derivable from first principles (output 1 iff popcount >= 4) "
                "and matches the printed hex in all 32 digits. A calibration "
                "anchor for the bit-order convention.",
    },
    "exp": {
        "hex": "0505408305c90101200b0efb94c7cff7",
        "kind": "GA-evolved, block-expanding strategy",
        "published_P": {149: 0.652, 599: 0.515, 999: 0.503},
        "source": "EvCA review Table 1; also EvEmComp Table 1",
        "confidence": "high",
        "note": "Recovery measured about 0.664 at N=149, roughly 2.5 "
                "measurement standard errors from the printed 0.652. The "
                "suspected cause is a max-relaxation-steps convention "
                "difference. Unresolved; a named suspect for C1-e.",
    },
    "par": {
        "hex": "0504058705000f77037755837bffb77f",
        "kind": "GA-evolved, particle-based strategy",
        "published_P": {149: 0.769, 599: 0.725, 999: 0.714},
        "source": "EvCA review Table 1; also EvEmComp Table 1",
        "confidence": "certain",
        "note": "Recovery measured within one standard error of the printed "
                "figure.",
    },
    "particle1": {
        "hex": "1000022441170231155f57dd734bffff",
        "kind": "GA-evolved, particle-based strategy, different run",
        "published_P": {149: 0.742, 599: 0.718, 999: 0.701},
        "source": "EvEmComp Table 1 ONLY. In neither the review nor PPSN III.",
        "confidence": "high",
        "note": "Single-source. The printed string appears as eight groups of "
                "eight characters and was reassembled to 32 hex digits.",
    },
    "particle2": {
        "hex": "031001001fa00013331f9fff5975ffff",
        "kind": "GA-evolved, particle-based strategy, different run",
        "published_P": {149: 0.755, 599: 0.696, 999: 0.670},
        "source": "EvEmComp Table 1 ONLY. In neither the review nor PPSN III.",
        "confidence": "high",
        "note": "Single-source.",
    },
    "GKL": {
        "hex": "005f005f005f005f005fff5f005fff5f",
        "kind": "hand-designed (Gacs-Kurdyumov-Levin)",
        "published_P": {149: 0.816, 599: 0.766, 999: 0.757},
        "source": "EvEmComp Table 1",
        "confidence": "certain",
        "note": "Derivable from its definition and matches the printed hex in "
                "all 32 digits. The second calibration anchor.",
    },
}

#: Stable order for reporting and for golden fixtures.
NAMES: List[str] = ["maj", "exp", "par", "particle1", "particle2", "GKL"]

#: The specimen record these constants must agree with.
SPECIMEN_JSON = ("herakles/specimens/spec-evca-density/derived/"
                 "evolved_rule_tables.json")


def rule_hex(name: str) -> str:
    if name not in GENOMES:
        raise KeyError("unknown genome %r; known: %s"
                       % (name, ", ".join(NAMES)))
    return str(GENOMES[name]["hex"])
