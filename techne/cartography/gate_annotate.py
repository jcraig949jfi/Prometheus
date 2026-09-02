"""Blind annotation harness for the measurement qualification gate.

    python -m techne.cartography.gate_annotate --show 1 14      # print evidence, no tagger output
    python -m techne.cartography.gate_annotate --score          # score labels once recorded

BLINDNESS. `--show` prints title, stratum and targeted method/evaluation passages and NOTHING
from taxonomy.py. The frozen classifications exist in gate_freeze_2026-09-02.json and are not
read here. That protects the first pass from anchoring on the instrument being tested.

THE LIMIT THAT CANNOT BE ENGINEERED AWAY. The annotator is the same model that built the
tagger, and it has already seen aggregate outputs from Experiments 2 and 3 in prior turns --
that 12 of 54 reached three axes, for instance. That exposure cannot be undone. The labels are
therefore REFERENCE LABELS, never ground truth, and the independence statement in the packet
says so without softening.

THE FIVE STATUSES, applied per paper per coordinate:

    VALUE              one frozen ontology value is justified by the text
    MULTI_VALUE        two or more are independently justified; forcing one destroys
                       information
    ONTOLOGY_MISSING   a competent reader can name the mechanism, and no frozen value
                       faithfully represents it
    EVIDENCE_AMBIGUOUS even full text does not justify a unique assignment
    OUT_OF_SCOPE       the paper should not have been admitted at all

The distinction between ONTOLOGY_MISSING and EVIDENCE_AMBIGUOUS is the one the whole gate turns
on: the first convicts the ontology, the second exonerates it. They must not be conflated, and
a judgment that cannot cite a passage is EVIDENCE_AMBIGUOUS by default.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

CARTO = pathlib.Path(__file__).resolve().parent
SAMPLE = CARTO / "exp2_fulltext_sample.json"
LABELS = CARTO / "gate_reference_labels.json"

#: Where the answer to each coordinate normally lives in a paper.
PROBES = {
    "representation": re.compile(
        r"(?:we (?:represent|encode|evolve|search over|optimi[sz]e)|representation is|"
        r"each (?:individual|candidate|solution|program) is|genotype|encoded as|"
        r"search space (?:of|is)|our (?:programs|circuits|networks))[^.]{0,220}\.", re.I),
    "selection": re.compile(
        r"(?:we (?:select|choose|rank|update|train)|selection|parent selection|"
        r"we use .{0,30}(?:gradient|descent|search|solver)|fitness is used|"
        r"tournament|elitis|archive|acquisition)[^.]{0,220}\.", re.I),
    "evaluation": re.compile(
        r"(?:we evaluate|evaluated on|benchmark|test (?:set|suite|cases)|"
        r"objective (?:function|is)|reward|we measure|success is|ground truth|"
        r"verifier|specification)[^.]{0,220}\.", re.I),
}


def load() -> list:
    return json.loads(SAMPLE.read_text(encoding="utf-8"))["papers"]


def evidence(p: dict, per_probe: int = 2, width: int = 240) -> dict:
    """Targeted passages, so a judgment can cite something rather than impressionise."""
    ft = p.get("fulltext") or ""
    out = {}
    for name, pat in PROBES.items():
        hits = []
        for m in pat.finditer(ft):
            s = re.sub(r"\s+", " ", m.group(0)).strip()
            if 40 < len(s) < width and s not in hits:
                hits.append(s)
            if len(hits) >= per_probe:
                break
        out[name] = hits
    return out


def _safe(s: str) -> str:
    """Console here is cp1252; papers contain Greek and math glyphs. Print ASCII-safe rather
    than crashing an annotation pass on a Delta."""
    return s.encode("ascii", "replace").decode("ascii")


def show(lo: int, hi: int) -> None:
    ps = load()
    for i, p in enumerate(ps[lo - 1:hi], start=lo):
        print("=" * 78)
        print(_safe("[%02d] %s" % (i, (p.get("title") or "")[:70])))
        print(_safe("     stratum=%s  arxiv=%s  fulltext=%d chars"
                        % (p["stratum"], p["arxiv_id"], len(p.get("fulltext") or ""))))
        ab = re.sub(r"\s+", " ", p.get("abstract") or "")
        print(_safe("     ABSTRACT: " + ab[:420]))
        ev = evidence(p)
        for k in ("representation", "selection", "evaluation"):
            for s in ev[k]:
                print(_safe("     [%s] %s" % (k[:4].upper(), s[:200])))


def score() -> dict:
    """Compare reference labels against the FROZEN tagger output, per axis."""
    import collections
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    frozen = json.loads((CARTO / "gate_freeze_2026-09-02.json").read_text(encoding="utf-8"))
    auto = frozen["derived"]["current_classifications_54"]
    axes = ("bottleneck", "representation_family", "selection_family", "evaluation_regime")

    per_axis = {}
    for ax in axes:
        cm = collections.Counter()
        support = tp = fp = fn = abst = 0
        adjudicable = 0
        for aid, rec in labels["labels"].items():
            g = rec[ax]
            a = auto.get(aid, {}).get(ax, "unknown")
            a_abstains = a in ("unknown", "B_UNASSIGNED")
            if g["status"] == "OUT_OF_SCOPE":
                continue
            adjudicable += 1
            if g["status"] in ("ONTOLOGY_MISSING", "EVIDENCE_AMBIGUOUS"):
                # the tagger cannot be right or wrong here; count separately
                cm[(g["status"], "ABSTAIN" if a_abstains else "ASSERTED")] += 1
                continue
            support += 1
            gold = set(g.get("values") or ([g["value"]] if g.get("value") else []))
            if a_abstains:
                abst += 1
                fn += 1
                cm[("|".join(sorted(gold)), "ABSTAIN")] += 1
            elif a in gold:
                tp += 1
                cm[("|".join(sorted(gold)), a)] += 1
            else:
                fp += 1
                fn += 1
                cm[("|".join(sorted(gold)), a)] += 1
        prec = tp / (tp + fp) if (tp + fp) else None
        rec_ = tp / (tp + fn) if (tp + fn) else None
        f1 = (2 * prec * rec_ / (prec + rec_)) if (prec and rec_) else None
        per_axis[ax] = {"adjudicable": adjudicable, "scorable_support": support,
                        "exact_match": tp, "accuracy": (tp / support) if support else None,
                        "precision": prec, "recall": rec_, "f1": f1,
                        "abstentions": abst,
                        "abstention_rate": (abst / support) if support else None,
                        "false_positives": fp, "false_negatives": fn,
                        "confusion": {str(k): v for k, v in cm.most_common()}}
    return {"per_axis": per_axis}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", nargs=2, type=int, metavar=("LO", "HI"))
    ap.add_argument("--score", action="store_true")
    a = ap.parse_args()
    if a.show:
        show(a.show[0], a.show[1])
    elif a.score:
        print(json.dumps(score(), indent=2)[:4000])
    else:
        ps = load()
        print("%d papers. --show LO HI to print blind evidence." % len(ps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
