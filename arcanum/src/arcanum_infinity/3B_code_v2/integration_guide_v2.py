"""
INTEGRATION GUIDE v2: Token Autopsy + Naming Autopsy

Two autopsies, two questions:
  1. Token Autopsy:  "What was the model THINKING when it generated this?"
  2. Naming Autopsy: "What happened when the model tried to INTERPRET what it generated?"

Both fire only during specimen capture. Zero overhead on non-capture evaluations.

═══════════════════════════════════════════════════════════════════════
FILES TO ADD TO YOUR CODEBASE:
═══════════════════════════════════════════════════════════════════════

  token_autopsy.py    → The steered generation logit shadow + concept cloud
  naming_autopsy.py   → The naming pass scaffold capture + failure taxonomy
  specimen_updated.py → Updated specimen.py with all new fields (replaces old one)

═══════════════════════════════════════════════════════════════════════
CHANGES TO xeno_screener.py:
═══════════════════════════════════════════════════════════════════════
"""

# ─── CHANGE 1: Imports (top of file) ────────────────────────────────
# Add these two lines near the other imports:

from .token_autopsy import TokenAutopsy
from .naming_autopsy import NamingAutopsy


# ─── CHANGE 2: Init (in __init__, around line 143) ──────────────────
# Add these two lines after the other state initialization:

#     self.autopsy = TokenAutopsy(top_k=25)
#     self.naming_autopsy = NamingAutopsy(top_k=25)


# ─── CHANGE 3: Replace _attempt_fast_capture (lines 444-487) ────────
# The new version runs both autopsies during specimen capture:

def _attempt_fast_capture_V2(self, engine, genome, score, meta,
                              results, prompt_info, prompt_index):
    """
    Specimen capture with dual autopsy:
    1. Token autopsy on the steered generation (what was it thinking?)
    2. Naming autopsy on the naming pass (what happened when it tried to interpret?)
    """
    try:
        specimen_dir = self.results_dir / "specimens"
        specimen_dir.mkdir(parents=True, exist_ok=True)

        # ── Capture specimen WITH token autopsy ──
        specimen = capture_specimen(
            genome=genome,
            generation=0,
            model_name=self.model_target.name,
            fitness=score,
            metadata=meta or {},
            novelty_results=results or [],
            results_dir=self.results_dir,
            autopsy_engine=self.autopsy,        # Token autopsy
            model=self.model,
            prompt_text=prompt_info["prompt"],
        )

        # ── Naming attempt (unchanged logic) ──
        naming_prompt_used = ""
        raw_naming_output = ""
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

        # ── Naming autopsy: capture the scaffold ──
        #
        # NOTE: To get the full logit shadow of the naming pass, you need
        # to reconstruct the naming prompt. If generate_specimen_name
        # doesn't expose the prompt it used, you can either:
        #   (a) Modify naming_engine.py to return the prompt text, or
        #   (b) Use the text-only scaffold classifier on whatever raw
        #       output you can capture.
        #
        # Option (b) works without any changes to naming_engine.py:
        # Just classify the raw name + description text.
        raw_naming_text = f"{specimen.name}\n{specimen.description}"
        scaffold_class = self.naming_autopsy.classify_scaffold(
            raw_output=raw_naming_text
        )

        # Store scaffold classification on the specimen
        specimen.scaffold_mode = scaffold_class.primary_mode
        specimen.scaffold_confidence = scaffold_class.confidence
        specimen.scaffold_interpretation = scaffold_class.interpretation
        specimen.scaffold_density = scaffold_class.scaffold_density

        # Save scaffold data to disk
        self.naming_autopsy.save_scaffold_data(
            shadow=None,  # No full shadow in text-only mode
            classification=scaffold_class,
            specimen_id=specimen.specimen_id,
            specimens_dir=specimen_dir,
        )

        specimen.status = "screen_capture"

        # ── Logging ──
        slog.info(f"  🏆 Screen specimen: '{specimen.name}'")
        if specimen.description:
            slog.info(f"     {specimen.description[:120]}")

        # Token autopsy result
        if specimen.autopsy_classification:
            icon = {
                "TRUE_ARCANUM": "🏛️", "COLLISION": "💥",
                "ECHO": "🔁", "CHIMERA": "🧬", "UNCLASSIFIABLE": "❓",
            }.get(specimen.autopsy_classification, "?")
            slog.info(f"     {icon} Token autopsy: {specimen.autopsy_classification} "
                      f"({specimen.autopsy_recommendation})")

        # Scaffold result
        scaffold_icon = {
            "CLEAN_NAME": "✅", "FIELD_BIOLOGIST": "🔬",
            "META_LINGUISTIC": "📐", "CONVERSATIONAL_BLEED": "💬",
            "HALLUCINATED_CITATION": "📚", "PERSONA_BLEND": "🎭",
            "RAW_SCAFFOLD": "⚡",
        }.get(scaffold_class.primary_mode, "❓")
        slog.info(f"     {scaffold_icon} Scaffold: {scaffold_class.primary_mode}")

    except Exception as e:
        slog.error(f"  Screen capture failed: {e}")


# ═══════════════════════════════════════════════════════════════════════
# CHANGE 4: Add scaffold fields to Specimen dataclass
# ═══════════════════════════════════════════════════════════════════════
#
# In specimen_updated.py, add these fields after the autopsy fields:
#
#     # ── Naming Scaffold (NEW) ─────────────────────────────────────
#     scaffold_mode: str = ""             # CLEAN_NAME | FIELD_BIOLOGIST | etc.
#     scaffold_confidence: float = -1.0
#     scaffold_interpretation: str = ""
#     scaffold_density: float = -1.0
#
# (These are already compatible — just add them to the dataclass.)


# ═══════════════════════════════════════════════════════════════════════
# OPTIONAL BUT RECOMMENDED: Full naming shadow capture
# ═══════════════════════════════════════════════════════════════════════
#
# The text-only scaffold classifier (used above) works without modifying
# naming_engine.py. But for the richest data, you'd want to:
#
# 1. Modify generate_specimen_name() to ALSO return the naming prompt
#    it constructed (just return it as a third value).
#
# 2. Then in _attempt_fast_capture, after naming:
#
#     naming_shadow = self.naming_autopsy.capture_naming_shadow(
#         model=self.model,
#         naming_prompt=naming_prompt_used,
#         max_new_tokens=self.xeno_config.naming_max_tokens,
#     )
#     scaffold_class = self.naming_autopsy.classify_scaffold(
#         shadow=naming_shadow
#     )
#
# This gives you token-level scaffold signal detection (which positions
# in the naming output triggered which failure modes) and the full
# probability neighborhood of the naming pass.


# ═══════════════════════════════════════════════════════════════════════
# NEW FILES PER SPECIMEN CAPTURE:
# ═══════════════════════════════════════════════════════════════════════
#
# Existing (unchanged):
#   {id}.pt              — Genome vector
#   {id}_emb.pt          — Embedding centroid
#
# From token autopsy:
#   {id}_shadow.json     — Raw logit shadow (top-25 per position)
#   {id}_cloud.json      — Concept cloud analysis
#   {id}_autopsy.txt     — Human-readable token autopsy report
#
# From naming autopsy:
#   {id}_scaffold.json   — Scaffold classification
#   {id}_scaffold_report.txt — Human-readable scaffold report
#   {id}_naming_shadow.json  — (Optional) Full naming pass logit shadow
#
# On the specimen JSONL, new fields:
#   autopsy_classification, autopsy_confidence, autopsy_recommendation,
#   autopsy_discard_reason, autopsy_mundane_fraction,
#   autopsy_novelty_coherence, autopsy_dominant_domains, autopsy_summary,
#   scaffold_mode, scaffold_confidence, scaffold_interpretation,
#   scaffold_density
