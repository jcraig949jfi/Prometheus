"""
Scorer for Nous hypothesis engine responses.

Parses LLM responses and extracts structured ratings.
"""

import re
import logging

log = logging.getLogger("nous")

# Normalize unicode dashes (U+2010, U+2011, U+2012, U+2013, U+2014, U+2015)
# to ASCII hyphen-minus before matching
_DASH_RE = re.compile(r"[\u2010\u2011\u2012\u2013\u2014\u2015]")


def _normalize(text: str) -> str:
    """Replace unicode dashes with ASCII hyphens for consistent matching."""
    return _DASH_RE.sub("-", text)


def parse_ratings(text: str) -> dict:
    """
    Extract reasoning, metacognition, hypothesis_generation, and implementability
    ratings from response text.
    Returns dict with ratings (1-10) or None for each if not found.
    """
    ratings = {
        "reasoning": None,
        "metacognition": None,
        "hypothesis_generation": None,
        "implementability": None,
    }

    norm = _normalize(text)

    # Pattern families (applied in priority order):
    #
    # Format A: "Reasoning Improvement: 7/10"  or  "Reasoning: 7/10"
    # Format B: "- Reasoning improvement: **8** - explanation"
    # Format C: "Reasoning improvement: **8/10**"
    # Format D: "Reasoning: 8"  (bare number after colon)
    # Format E: "*   **Reasoning Improvement: 7/10**."
    patterns = [
        # key-label, regex -> group(1) is the digit
        ("reasoning", [
            r"reasoning\s*(?:improvement)?\s*[:=]\s*\**\s*(\d+)\s*(?:/\s*10)?\s*\**",
        ]),
        ("metacognition", [
            r"metacognition\s*(?:improvement)?\s*[:=]\s*\**\s*(\d+)\s*(?:/\s*10)?\s*\**",
        ]),
        ("hypothesis_generation", [
            r"hypothesis\s*(?:generation)?\s*[:=]\s*\**\s*(\d+)\s*(?:/\s*10)?\s*\**",
        ]),
        ("implementability", [
            r"implementability\s*[:=]\s*\**\s*(\d+)\s*(?:/\s*10)?\s*\**",
            r"implement(?:ation)?\s*(?:feasibility|potential|score)?\s*[:=]\s*\**\s*(\d+)\s*(?:/\s*10)?\s*\**",
        ]),
    ]

    for key, pattern_list in patterns:
        for pattern in pattern_list:
            match = re.search(pattern, norm, re.IGNORECASE)
            if match:
                val = int(match.group(1))
                if 1 <= val <= 10:
                    ratings[key] = val
                    break

    # Fallback A: look for a line with bold number after a keyword
    # e.g., "- Reasoning improvement: **8** - explanation"
    for key, keywords in [
        ("reasoning", ["reasoning"]),
        ("metacognition", ["metacognition", "metacognitive"]),
        ("hypothesis_generation", ["hypothesis"]),
        ("implementability", ["implementab", "implementation feasib"]),
    ]:
        if ratings[key] is not None:
            continue
        for kw in keywords:
            bold_match = re.search(
                rf"{kw}[^:]*:\s*\**\s*(\d+)\s*\**",
                norm, re.IGNORECASE,
            )
            if bold_match:
                val = int(bold_match.group(1))
                if 1 <= val <= 10:
                    ratings[key] = val
                    break

    # Fallback B: look for three or four numbers in sequence near end
    # e.g., "8, 7, 9" or "8/10, 7/10, 9/10"
    n_missing = sum(1 for v in ratings.values() if v is None)
    if n_missing >= 3:
        # Try four-number pattern first (with implementability)
        block4 = re.search(
            r"(\d+)\s*/?\s*10?\s*[,;]\s*(\d+)\s*/?\s*10?\s*[,;]\s*"
            r"(\d+)\s*/?\s*10?\s*[,;]\s*(\d+)",
            norm[-600:],
        )
        if block4:
            vals = [int(block4.group(i)) for i in (1, 2, 3, 4)]
            if all(1 <= v <= 10 for v in vals):
                keys = ["reasoning", "metacognition", "hypothesis_generation", "implementability"]
                for k, v in zip(keys, vals):
                    if ratings[k] is None:
                        ratings[k] = v

        # Try three-number pattern
        if sum(1 for v in ratings.values() if v is None) >= 3:
            block3 = re.search(
                r"(\d+)\s*/?\s*10?\s*[,;]\s*(\d+)\s*/?\s*10?\s*[,;]\s*(\d+)",
                norm[-500:],
            )
            if block3:
                vals = [int(block3.group(i)) for i in (1, 2, 3)]
                if all(1 <= v <= 10 for v in vals):
                    keys = ["reasoning", "metacognition", "hypothesis_generation"]
                    for k, v in zip(keys, vals):
                        if ratings[k] is None:
                            ratings[k] = v

    return ratings


def assess_novelty(text: str) -> str:
    """Determine if the model considers the combination novel, existing, or unclear."""
    lower = _normalize(text).lower()

    existing_signals = [
        "already a known", "maps to existing", "already exists",
        "well-established", "well established", "this is essentially",
        "closely related to", "already been explored", "existing field",
        "existing technique", "not novel", "already known",
        "not entirely novel", "not wholly novel",
    ]
    novel_signals = [
        "novel", "new combination", "hasn't been explored",
        "not yet been", "unique intersection", "genuinely new",
        "no existing", "unexplored", "original", "not been combined",
        "first to combine", "no known prior",
    ]
    unproductive_signals = [
        "unproductive", "not fertile", "forced", "superficial",
        "doesn't yield", "no meaningful", "tenuous", "contrived",
    ]

    if any(s in lower for s in unproductive_signals):
        return "unproductive"

    novel_count = sum(1 for s in novel_signals if s in lower)
    existing_count = sum(1 for s in existing_signals if s in lower)

    if novel_count > existing_count:
        return "novel"
    elif existing_count > novel_count:
        return "existing"
    return "unclear"


def score_response(text: str) -> dict:
    """
    Full scoring of a single LLM response.

    Returns:
        dict with ratings, novelty, is_unproductive, composite_score, high_potential
    """
    ratings = parse_ratings(text)
    novelty = assess_novelty(text)

    # Composite uses the three core ratings (not implementability)
    core_keys = ["reasoning", "metacognition", "hypothesis_generation"]
    valid_core = [ratings[k] for k in core_keys if ratings[k] is not None]

    if valid_core:
        composite = sum(valid_core) / len(valid_core)
    else:
        composite = 0.0
        log.warning("No ratings could be parsed from response")

    high_potential = (
        len(valid_core) == 3
        and all(v >= 7 for v in valid_core)
    )

    return {
        "ratings": ratings,
        "novelty": novelty,
        "is_unproductive": novelty == "unproductive",
        "composite_score": round(composite, 2),
        "high_potential": high_potential,
    }
