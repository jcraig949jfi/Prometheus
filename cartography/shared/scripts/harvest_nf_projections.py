"""Literature harvest — NF (number field) complexity/structure projections.

Task: harvest_nf_complexity_projections (Harmonia_M2_sessionB, tick 7).
Modelled on sessionD's harvest_ec_projections.py (same structure, NF-specific brief + column map).
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
        "Columns: | Name | Year | Resolves | "
        "One row per projection. Return 30-50 rows. "
        "Use first-published year or approximate decade if exact is unknown. "
        "The 'Resolves' column is one short clause describing what structural "
        "feature of number fields the projection is sensitive to. "
        "Do not include preamble or closing remarks. Start with the table."
    )
    user_brief = (
        "List all the ways mathematicians measure complexity or structural type of "
        "number fields (degree, discriminant, class number, regulator, Galois group, "
        "signature, unit rank, etc.). Include both classical invariants AND "
        "less-used projections from 1970s-2000s literature that might be obscure "
        "(e.g. root discriminant, Lehmer's lambda, monogenic criterion, narrow class group, "
        "p-class field tower, Iwasawa invariants, reflection theorems, Odlyzko bounds, "
        "regulator-discriminant ratios). Return 30-50 projections."
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


def lmfdb_nf_columns() -> list[str]:
    import psycopg2
    conn = psycopg2.connect(host="192.168.1.176", port=5432, dbname="lmfdb",
                            user="lmfdb", password="lmfdb")
    cur = conn.cursor()
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'nf_fields' ORDER BY ordinal_position"
    )
    cols = [r[0] for r in cur.fetchall()]
    cur.close(); conn.close()
    return cols


NAME_TO_COLUMN = {
    "degree": "degree",
    "discriminant": "disc_abs",
    "disc_abs": "disc_abs",
    "root discriminant": "rd",
    "regulator": "regulator",
    "class number": "class_number",
    "class group": "class_group",
    "narrow class": "narrow_class_number",
    "relative class": "relative_class_number",
    "galois group": "galt",
    "galois label": "galois_label",
    "galois type": "galt",
    "abelian": "gal_is_abelian",
    "cyclic": "gal_is_cyclic",
    "solvable": "gal_is_solvable",
    "signature": "r2",
    "real places": "r2",
    "complex places": "r2",
    "torsion": "torsion_order",
    "ramification": "ramps",
    "ramified primes": "ramps",
    "num ram": "num_ram",
    "ramification index": "ramps",
    "coeffs": "coeffs",
    "defining polynomial": "coeffs",
    "complex multiplication": "cm",
    "cm": "cm",
    "grh": "used_grh",
    "generalized riemann": "used_grh",
    "maximal cm subfield": "maximal_cm_subfield",
    "unit signature": "unit_signature_rank",
    "unit rank": "unit_signature_rank",
    "embeddings": "embeddings_gen_real",
    "real embeddings": "embeddings_gen_real",
    "monogenic": "monogenic",
    "galois discriminant": "galois_disc_exponents",
    "galois disc": "galois_disc_exponents",
    "index": "index",
    "inessential": "inessentialp",
    "subfields": "subfields",
    "label": "label",
    "minimal sibling": "minimal_sibling",
    "maxp": "maxp",
    "largest bad prime": "maxp",
    "disc rad": "disc_rad",
    "radical": "disc_rad",
    "disc sign": "disc_sign",
    "grd": "grd",
    "group discriminant": "grd",
}


def check_row(name: str, cols: list[str]) -> str:
    lname = name.lower()
    hits = []
    for kw, col in NAME_TO_COLUMN.items():
        if kw in lname and col in cols:
            hits.append(col)
    hits = list(dict.fromkeys(hits))
    if hits:
        return ", ".join(hits)
    return "(derivable / not a direct column)"


def parse_model_table(text: str) -> list[tuple[str, str, str]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        cells = [p for p in parts if p != ""]
        if len(cells) < 3:
            continue
        name, year, resolves = cells[0], cells[1], cells[2]
        if name.lower() in ("name", "projection"):
            continue
        rows.append((name, year, resolves))
    return rows


def main():
    print("[harvest] calling Claude Opus...")
    raw = call_claude_once()
    print("[harvest] response received; length =", len(raw))

    rawpath = Path("cartography/docs/harvest_nf_projections_raw.txt")
    rawpath.parent.mkdir(parents=True, exist_ok=True)
    rawpath.write_text(raw, encoding="utf-8")

    cols = lmfdb_nf_columns()
    print(f"[harvest] LMFDB nf_fields has {len(cols)} columns")

    rows = parse_model_table(raw)
    print(f"[harvest] parsed {len(rows)} projection rows")

    md_lines = [
        "# NF Complexity / Structure Projections — Literature Harvest",
        "",
        "**Task:** `harvest_nf_complexity_projections`  ",
        "**Drafted by:** Harmonia_M2_sessionB, 2026-04-17 (tick 7)  ",
        "**Source:** Single Claude Opus (claude-opus-4-7) call with literal task brief. Raw response preserved at `cartography/docs/harvest_nf_projections_raw.txt`.",
        "",
        "**Method:** Prompted the model once with the literal task brief. Did NOT ask it to validate or judge. The `Checked-by-you` column is a heuristic keyword match against live `lmfdb.nf_fields` column schema (42 columns as of 2026-04-17); `(derivable / not a direct column)` means no direct LMFDB column exists by my heuristic match, but the projection may still be computable from stored invariants.",
        "",
        "**What this harvest is for:** populating the catalog with candidate coordinate systems per Pattern 17 (Language and Organization is the Real Bottleneck) and investment_priorities.md Priority 4 (Coordinate Harvest from Literature). Each row below is a potential future catalog entry; cross-reference against `coordinate_system_catalog.md` and `build_landscape_tensor.py` before drafting a new entry.",
        "",
        "**Sibling harvest:** `cartography/docs/harvest_ec_projections.md` (sessionD, same tick-cycle) covers elliptic-curve projections. Together the two harvests are intended to seed Priority 4 of `investment_priorities.md`.",
        "",
        "| Name | Year | Resolves | LMFDB column / derivable | Checked-by-you |",
        "|---|---|---|---|---|",
    ]
    for name, year, resolves in rows:
        checked = check_row(name, cols)
        md_lines.append(f"| {name} | {year} | {resolves} | {checked} | heuristic-keyword-match against live nf_fields schema |")

    hits = sum(1 for n, _, _ in rows if check_row(n, cols) != "(derivable / not a direct column)")
    md_lines += [
        "",
        "---",
        "",
        "## Provenance",
        "- API call: 1x Claude Opus, ~2500 output token cap.",
        "- LMFDB schema reference: `information_schema.columns WHERE table_name = nf_fields` at 2026-04-17.",
        f"- Total projections enumerated by model: {len(rows)}.",
        f"- Direct LMFDB column hits (heuristic): {hits}.",
        "",
        "## Discipline notes",
        "- This list is the *model's* enumeration. It is not validated; several rows may overlap or be misattributed. Pattern 5 (Known Bridges Are Known) applies: pattern-match against class field theory / Iwasawa theory / Langlands before treating any entry as novel.",
        "- The `Checked-by-you` column is a heuristic, not an audit. Projections marked `(derivable / not a direct column)` may still be (a) computable from stored invariants, (b) present in a sibling LMFDB table (e.g. `nf_subfields`, `nf_galois_groups`), or (c) genuinely not stored in LMFDB — in which case they are frontier-harvest candidates (Priority 4 exit-points).",
        "- Per catalog discipline (Section 10 meta-principle): adding any of these to the coordinate system catalog requires the full entry format (resolves, collapses, tautology profile, calibration anchors, known failure modes, when/not to use). Do not bulk-import this table into the catalog.",
        "- Heuristic mapping is NF-specific (different from EC). See `NAME_TO_COLUMN` in `harvest_nf_projections.py` for the keyword→column rules I used.",
        "",
        "## Flag for sessionA review",
        "- Several classical NF projections may not have a direct `nf_fields` column because they live in a *sibling* table (e.g. unit groups, p-adic valuations, class group structure beyond the exponent). Before marking any row 'not stored', please check the full `nf_*` LMFDB table family.",
        "- Rows marked `cm` may conflate number-field-level CM (is the ring of integers OK an order in a CM field?) with elliptic-curve CM — the two notions are related but distinct. A harvest-mover creating a catalog entry from such a row must disambiguate.",
    ]

    outpath = Path("cartography/docs/harvest_nf_projections.md")
    outpath.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[harvest] wrote {outpath} with {len(rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
