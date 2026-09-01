"""Adversarial audit of the mechanism vocabulary. Repairs the second required item.

WHY EMPIRICAL AND NOT BY INSPECTION. At cycle 042 I audited the vocabulary by reading it and
qualified seven bare terms (LIM-012). Reading catches the words a reader already suspects. This
audit instead MEASURES each surface form against papers the domain gate has already judged, so
a term is convicted by what it actually matched, not by whether it looks dangerous to me.

THE TEST. For every surface form of every mechanism, count how often it fires on:

    IN-SCOPE   papers the domain gate counted as in-domain
    OUT-SCOPE  papers the gate REJECTED, plus papers it could not place
               (AMBIGUOUS_KEPT / UNKNOWN_KEPT), plus the recorded rejection titles

A form whose firings are mostly out-of-scope is contaminating regardless of how technical it
looks. Precision here is a LOWER BOUND on the term's real precision -- out-of-scope papers are
only the ones our own retrieval happened to pull -- so a term that looks bad on this measure is
bad, while a term that looks clean has merely not been caught yet.
"""
from __future__ import annotations

import json
import re
from typing import Optional

from . import domain, store, taxonomy


def _blob(g: dict, cap: int = 800) -> str:
    parts = [g.get("title") or ""]
    for s in (g.get("evidence_spans") or []):
        if s.get("scope") == "abstract":
            parts.append((s.get("text") or "")[:cap])
    return " ".join(parts)


def populations() -> tuple:
    """(in_scope_texts, out_scope_texts). Rejected sources contribute their titles."""
    ins, outs = [], []
    for g in store.current("genomes").values():
        if g.get("duplicate_of"):
            continue
        t = _blob(g)
        if domain.counts_as_in_domain(g.get("domain_status") or ""):
            ins.append(t)
        else:
            outs.append(t)
    for r in store.read("rejected"):
        if r.get("title"):
            outs.append(r["title"])
    return ins, outs


def audit(min_fires: int = 3) -> dict:
    ins, outs = populations()
    rows = []
    for mech, forms in sorted(taxonomy.MECHANISMS.items()):
        for form in forms:
            pat = re.compile(r"\b" + re.escape(form) + r"\b", re.I)
            a = sum(1 for t in ins if pat.search(t))
            b = sum(1 for t in outs if pat.search(t))
            total = a + b
            rows.append({
                "mechanism": mech, "surface_form": form,
                "in_scope_fires": a, "out_scope_fires": b, "total_fires": total,
                "precision": (a / total) if total else None,
                "words": len(form.split()),
            })
    fired = [r for r in rows if r["total_fires"] >= min_fires]
    contaminating = sorted([r for r in fired if (r["precision"] or 1.0) < 0.5],
                           key=lambda r: (r["precision"], -r["total_fires"]))
    silent = [r for r in rows if r["total_fires"] == 0]
    return {
        "n_in_scope": len(ins), "n_out_scope": len(outs),
        "n_surface_forms": len(rows),
        "min_fires_threshold": min_fires,
        "forms_that_fired": len(fired),
        "forms_never_fired": len(silent),
        "CONTAMINATING": contaminating,
        "all_rows": rows,
        "interpretation": (
            "precision here is a LOWER BOUND: out-of-scope papers are only those our own "
            "retrieval happened to pull. A form that looks bad IS bad; a form that looks clean "
            "has merely not been caught yet. Forms that never fired are not exonerated either "
            "-- they are untested."),
    }


def report(a: dict) -> str:
    L = []
    L.append("VOCABULARY CONTAMINATION AUDIT")
    L.append("  in-scope texts %d | out-of-scope texts %d | surface forms %d"
             % (a["n_in_scope"], a["n_out_scope"], a["n_surface_forms"]))
    L.append("  forms that fired >= %d times: %d | never fired: %d"
             % (a["min_fires_threshold"], a["forms_that_fired"], a["forms_never_fired"]))
    L.append("")
    L.append("  CONTAMINATING (precision < 0.5 among forms that fired):")
    if not a["CONTAMINATING"]:
        L.append("    none")
    for r in a["CONTAMINATING"]:
        L.append("    %-24s %-28s in %2d / out %2d  prec %.2f"
                 % (r["mechanism"], repr(r["surface_form"])[:28],
                    r["in_scope_fires"], r["out_scope_fires"], r["precision"]))
    return "\n".join(L)


def main() -> int:
    a = audit()
    print(report(a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
