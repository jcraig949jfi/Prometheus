"""
Research Memory — Tracks tested hypotheses to prevent duplication.
===================================================================
Maintains a persistent file of hypothesis fingerprints (normalized text)
with their outcomes. New hypotheses are checked against this memory
before being accepted.

Also detects tautologies: hypotheses where all referenced datasets
are about the same mathematical domain (not cross-domain).

Storage: convergence/data/research_memory.jsonl (append-only)
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

CONVERGENCE = Path(__file__).resolve().parents[2] / "convergence"
MEMORY_FILE = CONVERGENCE / "data" / "research_memory.jsonl"

# Cache loaded at module level
_memory_cache: dict = {}  # fingerprint → {status, count, last_seen}


def _fingerprint(hypothesis: str) -> str:
    """Normalize hypothesis text to a fingerprint for dedup comparison.

    Strips numbers, normalizes whitespace, lowercases, removes filler words.
    Two hypotheses that differ only in specific numbers or phrasing
    should produce the same fingerprint.
    """
    h = hypothesis.lower().strip()
    # Remove specific numbers (conductors, crossing numbers, etc.)
    h = re.sub(r'\b\d+\.?\d*\b', 'N', h)
    # Remove filler
    for word in ["the", "a", "an", "is", "are", "of", "in", "to", "for", "and",
                 "or", "that", "this", "with", "from", "by", "at", "on", "as",
                 "more", "less", "than", "significantly", "statistically",
                 "positively", "negatively", "higher", "lower"]:
        h = re.sub(rf'\b{word}\b', '', h)
    # Collapse whitespace
    h = re.sub(r'\s+', ' ', h).strip()
    # Take first 100 chars as fingerprint
    return h[:100]


def _load_memory():
    """Load research memory from disk into cache."""
    global _memory_cache
    if _memory_cache:
        return
    if not MEMORY_FILE.exists():
        return
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                fp = entry.get("fingerprint", "")
                if fp:
                    _memory_cache[fp] = {
                        "status": entry.get("status", "unknown"),
                        "count": entry.get("count", 1),
                        "last_seen": entry.get("last_seen", ""),
                        "hypothesis": entry.get("hypothesis", ""),
                    }
            except json.JSONDecodeError:
                pass


def record(hypothesis: str, status: str):
    """Record a hypothesis and its outcome in memory."""
    _load_memory()
    fp = _fingerprint(hypothesis)
    CONVERGENCE.joinpath("data").mkdir(parents=True, exist_ok=True)

    if fp in _memory_cache:
        _memory_cache[fp]["count"] += 1
        _memory_cache[fp]["status"] = status
        _memory_cache[fp]["last_seen"] = datetime.now().isoformat()
    else:
        _memory_cache[fp] = {
            "status": status,
            "count": 1,
            "last_seen": datetime.now().isoformat(),
            "hypothesis": hypothesis[:200],
        }

    # Append to file
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "fingerprint": fp,
            "hypothesis": hypothesis[:200],
            "status": status,
            "count": _memory_cache[fp]["count"],
            "last_seen": datetime.now().isoformat(),
        }) + "\n")


def is_duplicate(hypothesis: str) -> tuple[bool, str]:
    """Check if a hypothesis has already been tested.

    Returns (is_dup, reason).
    A hypothesis is duplicate if its fingerprint matches a previously
    tested hypothesis that was either falsified or tested 3+ times.
    """
    _load_memory()
    fp = _fingerprint(hypothesis)

    if fp in _memory_cache:
        entry = _memory_cache[fp]
        count = entry["count"]
        status = entry["status"]

        if status == "falsified" and count >= 3:
            return True, f"Previously falsified {count}x: {entry.get('hypothesis', '')[:80]}"
        if count >= 5:
            return True, f"Tested {count}x already (status={status}): {entry.get('hypothesis', '')[:80]}"

    return False, ""


def is_tautology(hypothesis: str, searches: list[dict]) -> tuple[bool, str]:
    """Check if a hypothesis is a same-domain tautology.

    A tautology is when all searches reference the same mathematical domain.
    "mathlib L-series imports correlate with Fungrim L-series formulas" is not
    a cross-domain discovery — both are about L-series.

    Rules:
    - If all search_types are from the same dataset → tautology
    - If the hypothesis only references one mathematical TOPIC despite
      using multiple datasets → soft tautology (warn but allow)
    """
    if not searches:
        return False, ""

    # Check: are all searches from the same dataset?
    datasets = set()
    for s in searches:
        st = s.get("search_type", "")
        if st.startswith("oeis"): datasets.add("oeis")
        elif st.startswith("lmfdb"): datasets.add("lmfdb")
        elif st.startswith("knots"): datasets.add("knots")
        elif st.startswith("fungrim"): datasets.add("fungrim")
        elif st.startswith("antedb"): datasets.add("antedb")
        elif st.startswith("mathlib"): datasets.add("mathlib")
        elif st.startswith("metamath"): datasets.add("metamath")
        elif st.startswith("materials"): datasets.add("materials")
        elif st.startswith("nf_") or st.startswith("number_field"): datasets.add("number_fields")
        elif st.startswith("isogeny"): datasets.add("isogenies")
        elif st.startswith("local_field"): datasets.add("local_fields")
        elif st.startswith("spacegroup"): datasets.add("spacegroups")
        elif st.startswith("polytop"): datasets.add("polytopes")
        elif st.startswith("pibase"): datasets.add("pibase")
        elif st.startswith("mmlkg"): datasets.add("mmlkg")

    if len(datasets) <= 1:
        return True, f"Single-dataset hypothesis (only {datasets}). Not cross-domain."

    # Check: is the hypothesis about one topic using two databases that cover it?
    # e.g., "Fungrim zeta formulas correlate with mathlib zeta imports"
    hl = hypothesis.lower()
    topic_keywords = {
        "zeta": ["zeta", "riemann", "l-function", "l-series", "lseries"],
        "prime": ["prime", "primality", "sieve"],
        "elliptic": ["elliptic curve", "modular form", "conductor"],
        "knot": ["knot", "crossing", "jones", "alexander"],
    }

    topics_mentioned = set()
    for topic, keywords in topic_keywords.items():
        if any(kw in hl for kw in keywords):
            topics_mentioned.add(topic)

    if len(topics_mentioned) == 1 and len(datasets) == 2:
        topic = list(topics_mentioned)[0]
        # Two databases, one topic — likely tautological
        # But only if both databases naturally contain this topic
        tautology_pairs = {
            "zeta": {frozenset({"fungrim", "mathlib"}), frozenset({"fungrim", "metamath"}),
                     frozenset({"mathlib", "metamath"}), frozenset({"antedb", "mathlib"}),
                     frozenset({"antedb", "metamath"})},
            "prime": {frozenset({"metamath", "mathlib"}), frozenset({"oeis", "metamath"})},
            "elliptic": {frozenset({"lmfdb", "mathlib"})},
        }
        if topic in tautology_pairs and frozenset(datasets) in tautology_pairs[topic]:
            return True, f"Same-topic tautology: both {datasets} cover '{topic}'"

    return False, ""


def summary() -> dict:
    """Summary of research memory."""
    _load_memory()
    statuses = {}
    total_tests = 0
    for entry in _memory_cache.values():
        s = entry["status"]
        statuses[s] = statuses.get(s, 0) + 1
        total_tests += entry["count"]
    return {
        "unique_hypotheses": len(_memory_cache),
        "total_tests": total_tests,
        "by_status": statuses,
    }


if __name__ == "__main__":
    s = summary()
    print(f"Research Memory: {s['unique_hypotheses']} unique, {s['total_tests']} total tests")
    print(f"By status: {s['by_status']}")
