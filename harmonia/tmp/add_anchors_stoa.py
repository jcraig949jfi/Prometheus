"""Add anchors_stoa field to the 11 catalog frontmatters per sessionB
COMMIT_COMPLETE 1776913566292-0 follow-up batch.

Bi-directional Stoa<->catalog linkage. Prediction file's resolved_against_catalogs
points at catalogs; this fills in the reverse pointer per catalog.
"""
import os
from pathlib import Path

CATALOGS_DIR = Path("D:/Prometheus/harmonia/memory/catalogs")
PREDICTION_PATH = "stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md"

# 11 catalogs that anchor the sessionD teeth-test stringency prediction
TARGETS = [
    "lehmer.md",
    "collatz.md",
    "zaremba.md",
    "brauer_siegel.md",
    "knot_concordance.md",
    "ulam_spiral.md",
    "hilbert_polya.md",
    "p_vs_np.md",
    "irrationality_paradox.md",
    "knot_nf_lens_mismatch.md",
    "drum_shape.md",
]

added = 0
skipped = 0
for name in TARGETS:
    path = CATALOGS_DIR / name
    if not path.exists():
        print(f"MISSING: {name}")
        continue
    text = path.read_text(encoding="utf-8")
    # Skip if already present
    if "anchors_stoa:" in text:
        print(f"already_present: {name}")
        skipped += 1
        continue
    # Find the closing --- of frontmatter
    if not text.startswith("---\n"):
        print(f"NO_FRONTMATTER: {name}")
        continue
    # Find the second --- (frontmatter end)
    second_marker_idx = text.find("\n---\n", 4)
    if second_marker_idx == -1:
        print(f"NO_CLOSING_MARKER: {name}")
        continue
    # Insert anchors_stoa field before the closing ---
    new_text = (
        text[:second_marker_idx]
        + f"\nanchors_stoa: {PREDICTION_PATH}"
        + text[second_marker_idx:]
    )
    path.write_text(new_text, encoding="utf-8")
    print(f"added: {name}")
    added += 1

print(f"\nSummary: {added} added, {skipped} already had field, {len(TARGETS) - added - skipped} other status")
