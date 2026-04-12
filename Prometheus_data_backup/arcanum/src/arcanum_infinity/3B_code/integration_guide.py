"""
INTEGRATION GUIDE: Wiring TokenAutopsy into XenoScreener

This file shows the exact changes needed in xeno_screener.py to enable
token autopsy during specimen capture. The changes are minimal — the
autopsy only fires when a specimen is actually captured (not during
normal fitness evaluation), so screening speed is unaffected for
non-capture prompts.

Changes are marked with # ── AUTOPSY CHANGE ──
"""

# ═══════════════════════════════════════════════════════════════════════
# CHANGE 1: Add import at the top of xeno_screener.py
# ═══════════════════════════════════════════════════════════════════════

# Add this line near the other imports:
from .token_autopsy import TokenAutopsy


# ═══════════════════════════════════════════════════════════════════════
# CHANGE 2: Initialize the autopsy engine in XenoScreener.__init__()
# ═══════════════════════════════════════════════════════════════════════

# Add this line after the other state initialization (around line 143):

#     # Token autopsy engine (fires only on specimen captures)
#     self.autopsy = TokenAutopsy(top_k=25)


# ═══════════════════════════════════════════════════════════════════════
# CHANGE 3: Update _attempt_fast_capture to pass autopsy + model + prompt
# ═══════════════════════════════════════════════════════════════════════

# Replace the existing _attempt_fast_capture method (lines 444-487) with:

def _attempt_fast_capture_WITH_AUTOPSY(self, engine, genome, score, meta,
                           results, prompt_info, prompt_index):
    """
    Quick specimen capture during screening, now with token autopsy.
    The autopsy adds ~5-10 seconds per capture (token-by-token regeneration)
    but only fires on captures, not on every genome evaluation.
    """
    try:
        specimen_dir = self.results_dir / "specimens"
        specimen_dir.mkdir(parents=True, exist_ok=True)

        # ── AUTOPSY CHANGE: pass autopsy engine, model, and prompt ──
        specimen = capture_specimen(
            genome=genome,
            generation=0,
            model_name=self.model_target.name,
            fitness=score,
            metadata=meta or {},
            novelty_results=results or [],
            results_dir=self.results_dir,
            autopsy_engine=self.autopsy,       # NEW
            model=self.model,                   # NEW
            prompt_text=prompt_info["prompt"],   # NEW
        )

        # Try naming (unchanged)
        try:
            name, description = generate_specimen_name(
                model=self.model,
                outputs=specimen.outputs,
                generation=0,
                layer=genome.layer_index,
                specimen_id=specimen.specimen_id,
                max_new_tokens=self.xeno_config.naming_max_tokens,
            )
            specimen.name = name
            specimen.description = description
        except Exception as e:
            slog.warning(f"  Naming failed: {e}")
            specimen.name = f"SCREEN-{prompt_index:03d}-L{genome.layer_index}"
            specimen.description = f"Fast screen capture from: {prompt_info['source']}"

        specimen.status = "screen_capture"

        slog.info(f"  🏆 Screen specimen: '{specimen.name}'")
        if specimen.description:
            slog.info(f"     {specimen.description[:120]}")

        # ── AUTOPSY CHANGE: log autopsy classification ──
        if specimen.autopsy_classification:
            slog.info(f"     Autopsy: {specimen.autopsy_classification} "
                      f"({specimen.autopsy_recommendation})")

    except Exception as e:
        slog.error(f"  Screen capture failed: {e}")


# ═══════════════════════════════════════════════════════════════════════
# CHANGE 4 (OPTIONAL): Add autopsy stats to the progress summary
# ═══════════════════════════════════════════════════════════════════════

# In the run() method, around line 550 where the progress summary is
# logged every 10 prompts, you can optionally track autopsy stats.
# This is a nice-to-have, not required for functionality.

# Add counters after the existing hits/captures counters (around line 515):
#     arcanum_count = 0
#     collision_count = 0
#     chimera_count = 0

# Then in the progress log (around line 550), add:
#     slog.info(f"  Autopsy: {arcanum_count} arcanum, "
#               f"{collision_count} collisions, {chimera_count} chimeras")


# ═══════════════════════════════════════════════════════════════════════
# THAT'S IT — 4 CHANGES TOTAL
# ═══════════════════════════════════════════════════════════════════════
#
# The autopsy is completely transparent to the screening loop:
#   - Non-capture prompts: zero overhead (autopsy doesn't fire)
#   - Capture prompts: ~5-10s extra for token-by-token regeneration
#   - All autopsy data saved alongside existing specimen files
#
# New files generated per capture:
#   {specimen_id}_shadow.json  — Raw logit shadow (top-25 tokens per position)
#   {specimen_id}_cloud.json   — Concept cloud analysis
#   {specimen_id}_autopsy.txt  — Human-readable autopsy report
#
# The specimen JSONL also gets new fields:
#   autopsy_classification, autopsy_confidence, autopsy_recommendation,
#   autopsy_discard_reason, autopsy_mundane_fraction,
#   autopsy_novelty_coherence, autopsy_dominant_domains, autopsy_summary
