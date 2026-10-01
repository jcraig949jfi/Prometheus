"""Label-vs-content divergence check.

Incidents: C9-D14 (on the pair tape an organism keeps its id while its bytes are replaced;
identity to its birth genome 0.97 -> 0.00 with no lineage event); X-ATOMIC-RANDOM /
X-CONTENT ("anc0 share 0.99-1.0" while founder bytes are 13-25%); U-I6 / ADV2 D6 (label 256/256
while >= 0.9-founder-like sites fall to 0); Harmonia F8 "a descent label is not descent".

Input: population members as (label_is_founder_lineage: bool, genome: bytes) and the founder
genome. Content is scored per member as positional identity to the founder over the founder's
length (optionally an alternative content score). Chance identity for random bytes is 1/256.

Verdicts
    LABEL_EXCEEDS_CONTENT  label share - content share > gap  (the label is not carrying the
                           material; claims must be scoped to "lineage", not "content")
    OK                     label and content shares agree within gap
    NOT_VERIFIED           empty population / empty founder
Returned details include the chance baseline so "content above chance" is visible.
"""
from typing import Callable, Iterable, Optional, Tuple

from . import CheckResult, OK, NOT_VERIFIED

NAME = "label_vs_content"
CHANCE = 1 / 256


def positional_identity(founder: bytes, genome: bytes) -> float:
    n = len(founder)
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if i < len(genome) and genome[i] == founder[i]) / n


def check_label_vs_content(members: Iterable[Tuple[bool, bytes]], founder: bytes,
                           content_threshold: float = 0.5, gap: float = 0.25,
                           content_fn: Optional[Callable[[bytes, bytes], float]] = None) -> CheckResult:
    members = list(members)
    if not members or not founder:
        return CheckResult(NAME, NOT_VERIFIED, "empty population or founder")
    content_fn = content_fn or positional_identity
    scores = [content_fn(founder, g) for _, g in members]
    label_share = sum(1 for lab, _ in members if lab) / len(members)
    content_share = sum(1 for s in scores if s >= content_threshold) / len(members)
    mean_founder_bytes = sum(scores) / len(scores)
    details = {"label_share": label_share, "content_share": content_share,
               "mean_founder_byte_share": mean_founder_bytes, "chance_byte_share": CHANCE,
               "content_threshold": content_threshold, "n": len(members)}
    if label_share - content_share > gap:
        return CheckResult(NAME, "LABEL_EXCEEDS_CONTENT",
                           "label share %.2f vs content share %.2f (mean founder bytes %.3f): "
                           "descent is in the label, not the material"
                           % (label_share, content_share, mean_founder_bytes), details)
    return CheckResult(NAME, OK, "label and content shares agree", details)
