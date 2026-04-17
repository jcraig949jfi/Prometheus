"""
Literature harvest — EC complexity/structure projections.

Task: harvest_ec_complexity_projections (claimed by Harmonia_M2_sessionD).

Single API call to Claude Opus. Ask the literal brief. Do NOT ask the model
to validate or judge — just enumerate. Then (me) check each projection
against LMFDB ec_curvedata column schema.

Output: cartography/docs/harvest_ec_projections.md (markdown table).
"""
import sys
import io
import time
import re
from pathlib import Path

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def call_claude_once() -> str:
    import anthropic
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from keys import get_key
    client = anthropic.Anthropic(api_key=get_key('CLAUDE'))
    system_prompt = (
        "You will produce a STRUCTURED enumeration as a markdown table. "
        "Do NOT commentate, validate, judge importance, or add caveats. Just list. "
        "Columns: | Name | Year | Resolves | "
        "One row per projection. Return 30-50 rows. "
        "Use first-published year or approximate decade if exact is unknown. "
        "The 'Resolves' column is one short clause describing what structural "
        "feature of elliptic curves the projection is sensitive to. "
        "Do not include preamble or closing remarks. Start with the table."
    )
    user_brief = (
        "List all the ways mathematicians measure complexity or structure of "
        "elliptic curves. Include both classical invariants (rank, regulator, "
        "etc.) and less-used projections from 1970s-2000s literature. "
        "Return 30-50 projections."
    )
    t0 = time.time()
    r = client.messages.create(
        model='claude-opus-4-7',
        max_tokens=2500,
        system=system_prompt,
        messages=[{'role': 'user', 'content': user_brief}],
    )
    elapsed = time.time() - t0
    text = r.content[0].text
    print(f'[harvest] model={r.model} in={r.usage.input_tokens} out={r.usage.output_tokens} elapsed={elapsed:.1f}s')
    return text


def lmfdb_ec_columns() -> list[str]:
    """Query live ec_curvedata columns for the check-by-me field."""
    import psycopg2
    conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='lmfdb',
                            user='lmfdb', password='lmfdb')
    cur = conn.cursor()
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'ec_curvedata' ORDER BY ordinal_position"
    )
    cols = [r[0] for r in cur.fetchall()]
    cur.close(); conn.close()
    return cols


# Heuristic mapping from projection name-keywords to LMFDB columns.
# This is not exhaustive; it's the first-pass check the task asks me to do.
NAME_TO_COLUMN = {
    'rank': 'rank',
    'analytic rank': 'analytic_rank',
    'regulator': 'regulator',
    'torsion': 'torsion',
    'conductor': 'conductor',
    'discriminant': 'absD',
    'j-invariant': 'jinv',
    'j invariant': 'jinv',
    'faltings': 'faltings_height',
    'szpiro': 'szpiro_ratio',
    'abc quality': 'abc_quality',
    'isogeny': 'isogeny_degrees',
    'cm': 'cm',
    'complex multiplication': 'cm',
    'bad prime': 'bad_primes',
    'sha': 'sha',
    "tate-shafarevich": 'sha',
    'manin': 'manin_constant',
    'optimality': 'optimality',
    'minimal quadratic twist': 'min_quad_twist_ainvs',
    'twist': 'min_quad_twist_ainvs',
    'class size': 'class_size',
    'class degree': 'class_deg',
    'serre': 'serre_invariants',
    'adelic': 'adelic_level',
    'mod-l': 'elladic_images',
    'l-adic': 'elladic_images',
    'galois representation': 'elladic_images',
    'galois image': 'elladic_images',
    'reduction type': 'semistable',
    'semistable': 'semistable',
    'num int': 'num_int_pts',
    'integral points': 'num_int_pts',
    'intrinsic torsion': 'intrinsic_torsion',
    'squarefree disc': 'squarefree_disc',
    'a-invariants': 'ainvs',
    'weierstrass': 'ainvs',
    'nonmax': 'nonmax_primes',
    'signd': 'signD',
    'root number': 'signD',
    'sign of functional equation': 'signD',
    'degree': 'class_deg',
    'stable faltings': 'stable_faltings_height',
    'modell': 'modell_images',
    'modular galois': 'modm_images',
}


def check_row(name: str, cols: list[str]) -> str:
    """Given a projection name, heuristically find matching LMFDB column."""
    lname = name.lower()
    hits = []
    for kw, col in NAME_TO_COLUMN.items():
        if kw in lname and col in cols:
            hits.append(col)
    hits = list(dict.fromkeys(hits))  # preserve order, dedupe
    if hits:
        return ', '.join(hits)
    return '(derivable / not a direct column)'


def parse_model_table(text: str) -> list[tuple[str, str, str]]:
    """Extract rows from the model's markdown table."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith('|') or line.startswith('|---') or '---' in line:
            continue
        parts = [p.strip() for p in line.split('|')]
        # markdown rows look like | a | b | c | -> parts: ['', 'a', 'b', 'c', '']
        cells = [p for p in parts if p != '']
        if len(cells) < 3:
            continue
        name, year, resolves = cells[0], cells[1], cells[2]
        if name.lower() in ('name', 'projection'):
            continue  # header
        rows.append((name, year, resolves))
    return rows


def main():
    print('[harvest] calling Claude Opus...')
    raw = call_claude_once()
    print('[harvest] response received; length =', len(raw))
    # Save the raw response as provenance
    rawpath = Path('cartography/docs/harvest_ec_projections_raw.txt')
    rawpath.parent.mkdir(parents=True, exist_ok=True)
    rawpath.write_text(raw, encoding='utf-8')

    cols = lmfdb_ec_columns()
    print(f'[harvest] LMFDB ec_curvedata has {len(cols)} columns')

    rows = parse_model_table(raw)
    print(f'[harvest] parsed {len(rows)} projection rows')

    md_lines = [
        '# EC Complexity / Structure Projections — Literature Harvest',
        '',
        '**Task:** `harvest_ec_complexity_projections`  ',
        '**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 6)  ',
        '**Source:** Single Claude Opus (claude-opus-4-7) call with literal task brief. Raw response preserved at `cartography/docs/harvest_ec_projections_raw.txt`.',
        '',
        '**Method:** Prompted the model once with the literal task brief. Did NOT ask it to validate or judge. The `Checked-by-you` column is a heuristic keyword match against live `lmfdb.ec_curvedata` column schema (50 columns as of 2026-04-17); `(derivable / not a direct column)` means no direct LMFDB column exists by my heuristic match, but the projection may still be computable from stored invariants.',
        '',
        '**What this harvest is for:** populating the catalog with candidate coordinate systems per Pattern 17 (Language and Organization is the Real Bottleneck). Each row below is a potential future catalog entry; cross-reference against `coordinate_system_catalog.md` before drafting a new entry.',
        '',
        '| Name | Year | Resolves | LMFDB column / derivable | Checked-by-you |',
        '|---|---|---|---|---|',
    ]
    for name, year, resolves in rows:
        checked = check_row(name, cols)
        md_lines.append(f'| {name} | {year} | {resolves} | {checked} | heuristic-keyword-match against live ec_curvedata schema |')

    md_lines += [
        '',
        '---',
        '',
        '## Provenance',
        f'- API call: 1x Claude Opus, ~2500 output token cap.',
        f'- LMFDB schema reference: `information_schema.columns WHERE table_name = ec_curvedata` at 2026-04-17.',
        f'- Total projections enumerated by model: {len(rows)}.',
        f'- Direct LMFDB column hits (heuristic): {sum(1 for n, _, _ in rows if check_row(n, cols) != "(derivable / not a direct column)")}.',
        '',
        '## Discipline notes',
        '- This list is the *model\'s* enumeration. It is not validated; several rows may overlap or be misattributed. Pattern 5 (Known Bridges Are Known) applies: pattern-match against Langlands / modularity / class field theory before treating any entry as novel.',
        '- The `Checked-by-you` column is a heuristic, not an audit. If a projection appears as `(derivable / not a direct column)` but is obviously classical (e.g. L-value, Tamagawa), it likely has a home in a sibling LMFDB table (`ec_mwbsd`, `ec_tamagawa`, etc.) rather than `ec_curvedata` — further check needed.',
        '- Per catalog discipline (Section 10 meta-principle): adding any of these to the coordinate system catalog requires the full entry format (resolves, collapses, tautology, anchors, failure modes). Do not bulk-import this table into the catalog.',
    ]

    outpath = Path('cartography/docs/harvest_ec_projections.md')
    outpath.write_text('\n'.join(md_lines), encoding='utf-8')
    print(f'[harvest] wrote {outpath} with {len(rows)} rows')
    return 0


if __name__ == '__main__':
    sys.exit(main())
