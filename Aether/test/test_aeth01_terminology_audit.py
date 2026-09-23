"""Active-AGE computational terminology audit (nomenclature hygiene).

Fails when unallowlisted biology-metaphor residue appears on the active
Aether surface. Historical reviews, frozen wire ids, and ordinary
engineering senses remain allowed. See COMPUTATIONAL_TERMINOLOGY.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

AETHER = Path(__file__).resolve().parents[1]
AETH01 = AETHER / "AETH-01"

# Path segments / exact files treated as historical or migration docs.
HISTORICAL_NAME_RES = (
    re.compile(r"(?i)ASTRA_"),
    re.compile(r"(?i)REPAIR_LEDGER"),
    re.compile(r"(?i)REVIEW_PACKET"),
    re.compile(r"(?i)AETH-00"),
    re.compile(r"(?i)INDEPENDENT_CLOSURE_REVIEW"),
    re.compile(r"(?i)notes[/\\]"),
    re.compile(r"(?i)COMPUTATIONAL_TERMINOLOGY"),
    re.compile(r"(?i)TERMINOLOGY_REFACTOR"),
    re.compile(r"(?i)test_aeth01_terminology_audit"),
)

ACTIVE_SUFFIXES = {".py", ".md", ".json", ".sh", ".yml", ".yaml", ".toml", ".txt"}

# Deprecated metaphors (word-ish). Matches are later filter-classified.
DEPRECATED = [
    ("HEREDITY_VARIATION", re.compile(r"\bHEREDITY_VARIATION\b")),
    ("organism_id", re.compile(r"\borganism_id\b", re.I)),
    ("organism", re.compile(r"\borganisms?\b", re.I)),
    ("heredity", re.compile(r"\bheredity\b", re.I)),
    ("heritable", re.compile(r"\bheritables?\b", re.I)),
    ("genome", re.compile(r"\bgenomes?\b", re.I)),
    ("reproduction", re.compile(r"\breproductions?\b", re.I)),
    ("reproductive", re.compile(r"\breproductives?\b", re.I)),
    ("offspring", re.compile(r"\boffsprings?\b", re.I)),
    ("lineage", re.compile(r"\blineages?\b", re.I)),
    ("population", re.compile(r"\bpopulations?\b", re.I)),
    ("mutation", re.compile(r"\bmutations?\b", re.I)),
    ("mutated", re.compile(r"\bmutated\b", re.I)),
    ("dormant", re.compile(r"\bdormant\b", re.I)),
    ("survival", re.compile(r"\bsurvivals?\b", re.I)),
    ("survive", re.compile(r"\bsurvive[sd]?\b", re.I)),
    ("fitness", re.compile(r"\bfitness\b", re.I)),
    ("outcompete", re.compile(r"\boutcompet(?:e|es|ed|ing)\b", re.I)),
    ("ecology", re.compile(r"\becolog(?:y|ical)\b", re.I)),
    ("metabolic", re.compile(r"\bmetabolics?\b", re.I)),
    ("parasite", re.compile(r"\bparasites?\b|\bparasitism\b", re.I)),
    ("copier", re.compile(r"\bcopiers?\b", re.I)),
    ("self-copying", re.compile(r"\bself[-_]copying\b", re.I)),
    ("specimen", re.compile(r"\bspecimens?\b", re.I)),
    ("kill_gate", re.compile(r"\bkill[_\s-]?gates?\b", re.I)),
    ("cell", re.compile(r"\bcells?\b", re.I)),
]

# Whole-line allow patterns (engineering / frozen / explicit legacy).
LINE_ALLOW = [
    re.compile(r"SIGKILL|lifecycle|parent (?:directory|process)|process (?:death|lifetime)", re.I),
    re.compile(r"\bmut_numer\b|\bMUT_NUMER\b"),
    re.compile(r"\bcell_starved\b|\bmutation_applied\b"),
    re.compile(r"legacy (?:serialized|name|term|terminology|identifier|path|title)", re.I),
    re.compile(r"historical (?:legacy|metaphor|term|terminology|document|name|path)", re.I),
    re.compile(r"deprecated historical metaphor|compatibility alias|frozen in `aeth01", re.I),
    re.compile(r"HEREDITY_REQUIREMENTS\.md|KILL_GATES_01\.md"),
    re.compile(r"TRANSMITTED_VARIATION|falsification gate|rejection gate|lattice site", re.I),
    re.compile(r"biological metaphors? found in historical", re.I),
    # Preferred neutral phrases that contain a deprecated stem.
    re.compile(r"\bstate copiers?\b", re.I),
    re.compile(r"frozen ladder alias:\s*`?HEREDITY_VARIATION`?", re.I),
]


def _is_historical(path: Path) -> bool:
    rel = path.relative_to(AETHER).as_posix()
    return any(rx.search(rel) for rx in HISTORICAL_NAME_RES)


def _active_files():
    skip_parts = {"__pycache__", ".git"}
    for path in AETHER.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in ACTIVE_SUFFIXES:
            continue
        if any(part in skip_parts for part in path.parts):
            continue
        if path.name.startswith(".") and "preserve" in path.name:
            continue
        if _is_historical(path):
            continue
        yield path


def _classify(term: str, line: str) -> str | None:
    """Return allow reason or None if the hit is a violation."""
    if any(rx.search(line) for rx in LINE_ALLOW):
        return "line-allow"
    # Frozen tier id is allowed when paired with canonical alias mention nearby
    # or used as an explicit equality/compat token in code.
    if term == "HEREDITY_VARIATION":
        if "TRANSMITTED_VARIATION" in line or "CLAIM_TIERS" in line or "alias" in line.lower():
            return "frozen-tier-alias"
        if re.search(r'["\']HEREDITY_VARIATION["\']', line):
            return "frozen-tier-literal"
    if term in {"mutation", "mutated"} and re.search(r"\bmut_numer\b|\bMUT_NUMER\b|Mu\b|bit.?perturb", line):
        return "mu-domain-context"
    if term == "cell" and re.search(r"lattice site|site/|sites?\b|grid cell|for cell in", line, re.I):
        # still prefer site; allow tight code loops during migration notes only if "site" also present
        if re.search(r"\bsites?\b", line, re.I):
            return "site-preferred-with-cell"
    if term == "survive" and re.search(r"process|pod|watchdog|retry|test", line, re.I):
        return "engineering-survive"
    if term == "heredity" and "HEREDITY_REQUIREMENTS" in line:
        return "path-citation"
    if term == "kill_gate" and "KILL_GATES_01" in line:
        return "path-citation"
    return None


def _scan():
    violations = []
    allowed = []
    for path in _active_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(AETHER).as_posix()
        for i, line in enumerate(text.splitlines(), 1):
            for term, rx in DEPRECATED:
                if not rx.search(line):
                    continue
                reason = _classify(term, line)
                rec = {"path": rel, "line": i, "term": term, "text": line.strip()[:160], "reason": reason}
                if reason:
                    allowed.append(rec)
                else:
                    violations.append(rec)
    return violations, allowed


def test_active_age_surface_has_no_unallowlisted_metaphors():
    violations, _allowed = _scan()
    if not violations:
        return
    sample = "\n".join(
        f"{v['path']}:{v['line']}: [{v['term']}] {v['text']}" for v in violations[:40]
    )
    pytest.fail(
        f"{len(violations)} unallowlisted deprecated-metaphor hit(s) on active AGE surface.\n"
        f"See AETH-01/COMPUTATIONAL_TERMINOLOGY.md.\n{sample}"
    )


def test_terminology_contract_exists_and_states_agent_prompt():
    text = (AETH01 / "COMPUTATIONAL_TERMINOLOGY.md").read_text(encoding="utf-8")
    assert "AGE models byte-valued computational sites" in text
    assert "TRANSMITTED_VARIATION" in text
    assert "MUT_NUMER" in text
    assert "aeth01.v1" in text


def test_audit_reports_path_line_term_and_allow_reason_shape():
    _violations, allowed = _scan()
    # Contract file itself is historical-skipped; frozen ids elsewhere should yield allows.
    assert isinstance(allowed, list)
    for rec in allowed[:5]:
        assert {"path", "line", "term", "text", "reason"} <= set(rec)
