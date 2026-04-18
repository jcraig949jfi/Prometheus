"""Path 4: literature harvest — what structural projections on EC L-function zeros exist
beyond the classical Katz-Sarnak / Rubinstein-Sarnak / Duenez-HKMS trio?

Meta-question: are our five EC-L-function specimens (F011, F013, F010-Is_Even,
F012 killed, F005 high-Sha-parity) saturating the known classical structure at
our conductor range, or is there uncharted terrain?

Method: single Claude Opus call with a sharp brief asking for an enumeration
of low-lying-zero / zero-distribution projections on EC L-functions. Cap token
output. Parse into a markdown table. Compare against what Prometheus has already
catalogued (P028, P050, P051, central-zero-forcing).

Output: cartography/docs/harvest_ec_lfunc_zero_projections.md
"""
import sys
import io
import time
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def call_claude_once() -> str:
    import anthropic
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from keys import get_key
    client = anthropic.Anthropic(api_key=get_key("CLAUDE"))
    system_prompt = (
        "You will produce a STRUCTURED enumeration as a markdown table. "
        "Do NOT commentate, validate, judge importance, or add caveats. Just list. "
        "Columns: | Name | Year | What it measures | Classical-or-open | "
        "One row per projection. Return 20-40 rows. "
        "Use first-published year or approximate decade. "
        "'Classical-or-open' = 'classical' if the projection is fully characterized by Katz-Sarnak / "
        "Rubinstein-Sarnak / Conrey-Farmer-Mezzadri-Snaith / Duenez-HKMS / known random-matrix theory; "
        "'open' if it's a live research question without closed-form RMT prediction. "
        "Do not include preamble or closing remarks. Start with the table."
    )
    user_brief = (
        "List structural projections on the low-lying zeros of elliptic curve L-functions. "
        "Include: one-level density variants, pair correlation, n-level densities, moments, "
        "excised ensembles, family-specific corrections, ratio conjectures, mean-square zeros, "
        "number variance, compound-invariant stratifications (rank × CM × reduction type × "
        "Atkin-Lehner sign × symmetry type), Sato-Tate-vertical axes, Katz-Sarnak family "
        "type refinements, and anything from the 2010-2025 literature on finite-conductor "
        "finite-height corrections to GUE. Focus on projections that ARE applicable to "
        "EC L-function zero data currently in LMFDB (conductor 11 to ~400K, ~2M with "
        "zeros), not speculative machinery. Return 20-40 rows."
    )
    t0 = time.time()
    r = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_brief}],
    )
    elapsed = time.time() - t0
    text = r.content[0].text
    print(f"[harvest] model={r.model} in={r.usage.input_tokens} out={r.usage.output_tokens} elapsed={elapsed:.1f}s")
    return text


# Minimal keyword match against our catalogued projections
PROMETHEUS_COVERAGE = {
    "rank": "P023 covered",
    "cm": "P025 covered",
    "complex multiplication": "P025 covered",
    "semistable": "P026 covered",
    "reduction type": "P026 covered",
    "kodaira": "P035 covered",
    "katz-sarnak": "P028 covered",
    "symmetry type": "P028 covered",
    "so_even": "P028 covered",
    "so_odd": "P028 covered",
    "first-gap": "P050 covered",
    "first gap": "P050 covered",
    "n(t) unfolding": "P051 covered",
    "unfold": "P051 covered",
    "root number": "P036 covered",
    "atkin-lehner": "P036 covered",
    "sha": "P038 covered",
    "regulator": "P101 covered",
    "isogeny class": "P100 covered",
    "pair correlation": "NOT_CATALOGUED",
    "one-level density": "partial (P028 Katz-Sarnak touches it)",
    "number variance": "NOT_CATALOGUED",
    "n-level density": "NOT_CATALOGUED",
    "moment": "NOT_CATALOGUED (Aporia Report 4 in progress per sessionC)",
    "keating-snaith": "NOT_CATALOGUED (Aporia Report 4)",
    "ratio conjecture": "NOT_CATALOGUED",
    "excised ensemble": "RECENTLY CONFIRMED at F011 (Aporia Report 1)",
}


def coverage_check(name_and_desc: str) -> str:
    low = name_and_desc.lower()
    hits = []
    for kw, note in PROMETHEUS_COVERAGE.items():
        if kw in low:
            hits.append(note)
    hits = list(dict.fromkeys(hits))
    return "; ".join(hits) if hits else "NOT_CATALOGUED"


def parse_model_table(text: str) -> list[tuple[str, str, str, str]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        cells = [p for p in parts if p != ""]
        if len(cells) < 4:
            continue
        name, year, measures, classical = cells[0], cells[1], cells[2], cells[3]
        if name.lower() in ("name", "projection"):
            continue
        rows.append((name, year, measures, classical))
    return rows


def main():
    print("[harvest] calling Claude Opus...")
    raw = call_claude_once()
    print(f"[harvest] response received; length={len(raw)}")

    rawpath = Path("cartography/docs/harvest_ec_lfunc_zero_projections_raw.txt")
    rawpath.parent.mkdir(parents=True, exist_ok=True)
    rawpath.write_text(raw, encoding="utf-8")

    rows = parse_model_table(raw)
    print(f"[harvest] parsed {len(rows)} rows")

    n_classical = sum(1 for _, _, _, c in rows if "classical" in c.lower())
    n_open = sum(1 for _, _, _, c in rows if "open" in c.lower())

    md = [
        "# EC L-function Zero Projections — Literature Harvest",
        "",
        "**Task:** Path 4 of the 4-path reflection (post-Aporia-Report-1).",
        "**Drafted by:** Harmonia_M2_sessionB, 2026-04-18.",
        "**Source:** Single Claude Opus (claude-opus-4-7) call. Raw response at `cartography/docs/harvest_ec_lfunc_zero_projections_raw.txt`.",
        "",
        "**Meta-question:** are our five EC-L-function specimens saturating classical structure at our conductor range, or is there uncharted terrain?",
        "",
        f"**Summary:** model enumerated **{len(rows)} projections**. Of these: **{n_classical} classical** "
        f"(fully characterized by known RMT) / **{n_open} open** (no closed-form prediction). "
        f"The 'Prometheus coverage' column cross-walks each projection against our current catalog.",
        "",
        "| Name | Year | What it measures | Classical-or-open | Prometheus coverage |",
        "|---|---|---|---|---|",
    ]
    for name, year, measures, classical in rows:
        coverage = coverage_check(name + " " + measures)
        md.append(f"| {name} | {year} | {measures} | {classical} | {coverage} |")

    n_covered = sum(1 for n, _, m, _ in rows if coverage_check(n + " " + m) != "NOT_CATALOGUED")
    n_not_catalogued = len(rows) - n_covered

    md += [
        "",
        "---",
        "",
        "## Saturation analysis",
        "",
        f"- **Catalogued or partially covered**: {n_covered} / {len(rows)}",
        f"- **Not catalogued**: {n_not_catalogued} / {len(rows)}",
        "",
        "### Readings",
        "",
        "- **If classical ≫ open AND Prometheus covers most classical rows**: EC-L-function zero terrain "
        "at our conductor range is largely mapped. Remaining frontier is in the open rows (no classical "
        "RMT prediction) or in the residuals where observed ≠ classical prediction.",
        "",
        "- **If classical ≈ open**: the literature itself still has significant uncharted terrain. "
        "Paths to novel findings remain without needing to beat classical theory.",
        "",
        "- **If many rows are NOT catalogued in Prometheus**: Priority-4 harvest followup — file "
        "targeted `catalog_entry` tasks for each uncatalogued projection. Low-cost expansion of the "
        "coordinate-system inventory.",
        "",
        "### Specimen-level ledger (context for Path 4 meta-question)",
        "",
        "Prometheus EC-L-function specimens that reduce to classical theory at our conductor range:",
        "- **F011** (GUE first-gap deficit): Duenez-HKMS excised ensemble. `calibration_confirmed`.",
        "- **F013** (zero-spacing rigidity vs rank): downstream of central-zero-forcing, same family.",
        "- **F005** (high-Sha parity): BSD identity, not a dynamical finding.",
        "",
        "Prometheus EC-L-function specimens that retain residual/open status:",
        "- **F011 rank-0 residual** (just discovered in Path 1+2): ε₀ = 31.08% ± 6.19% non-excised. "
        "GENUINE FRONTIER.",
        "- **F012** (Möbius at g2c aut groups): killed under clean measurement + Liouville cross-check.",
        "- **F010** (NF backbone): killed under block-shuffle null.",
        "",
        "## Provenance",
        "",
        "- API call: 1× Claude Opus 4.7, ~2500 output token cap.",
        "- Keyword-match coverage: heuristic only. Projections flagged NOT_CATALOGUED deserve a manual "
        "second-pass before filing a new `catalog_entry` task.",
        "- This harvest is for Priority 4 seeding. Do not bulk-import. Each row becomes a future "
        "targeted task after review.",
    ]

    outpath = Path("cartography/docs/harvest_ec_lfunc_zero_projections.md")
    outpath.write_text("\n".join(md), encoding="utf-8")
    print(f"[harvest] wrote {outpath} with {len(rows)} rows")
    print(f"[harvest] classical={n_classical}, open={n_open}, catalogued={n_covered}, not_catalogued={n_not_catalogued}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
