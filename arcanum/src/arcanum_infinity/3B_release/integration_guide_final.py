"""
INTEGRATION GUIDE — FINAL (3B Release)
Token Autopsy + Naming Scaffold: Complete wiring for the 3B run.

Two autopsies, two questions:
  1. Token Autopsy:   "What was the model THINKING when it generated this?"
  2. Naming Scaffold: "What happened when the model tried to INTERPRET what it generated?"

═══════════════════════════════════════════════════════════════════════
STEP 1: Copy these files into src/arcanum_infinity/
═══════════════════════════════════════════════════════════════════════

  3B_release/token_autopsy.py     → src/arcanum_infinity/token_autopsy.py
  3B_release/naming_autopsy.py    → src/arcanum_infinity/naming_autopsy.py
  3B_release/specimen_updated.py  → src/arcanum_infinity/specimen.py
                                     (replaces the existing specimen.py)

WHAT CHANGED IN specimen.py:
  + autopsy_classification, autopsy_confidence, autopsy_recommendation,
    autopsy_discard_reason, autopsy_mundane_fraction,
    autopsy_novelty_coherence, autopsy_dominant_domains, autopsy_summary
  + scaffold_mode, scaffold_confidence, scaffold_interpretation,
    scaffold_density
  + capture_specimen() now accepts autopsy_engine, model, prompt_text
    (all optional — existing callers need zero changes)
  = save_json() preserved from the live version


═══════════════════════════════════════════════════════════════════════
STEP 2: Five changes to xeno_screener.py
═══════════════════════════════════════════════════════════════════════
"""

# ─── CHANGE 1: Imports (top of file) ────────────────────────────────

from .token_autopsy import TokenAutopsy
from .naming_autopsy import NamingAutopsy


# ─── CHANGE 2: __init__ — add after existing state init ─────────────

#     self.autopsy = TokenAutopsy(top_k=25)
#     self.naming_autopsy = NamingAutopsy(top_k=25)


# ─── CHANGE 3: Replace _attempt_fast_capture with this version ───────

def _attempt_fast_capture_3B(self, engine, genome, score, meta,
                              results, prompt_info, prompt_index):
    """
    Specimen capture with dual autopsy for the 3B run.

    Overhead vs. old version:
      - Token autopsy: ~10-15s per capture (token-by-token regen on 3B)
      - Naming scaffold: <1s per capture (regex on existing output text)
    Both only fire on captures, not on every genome evaluation.
    """
    try:
        specimen_dir = self.results_dir / "specimens"
        specimen_dir.mkdir(parents=True, exist_ok=True)

        # ── Token autopsy runs inside capture_specimen ──
        specimen = capture_specimen(
            genome=genome,
            generation=0,
            model_name=self.model_target.name,
            fitness=score,
            metadata=meta or {},
            novelty_results=results or [],
            results_dir=self.results_dir,
            autopsy_engine=self.autopsy,         # NEW
            model=self.model,                    # NEW
            prompt_text=prompt_info["prompt"],   # NEW
        )

        # ── Naming attempt (unchanged logic) ──
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

        # ── Naming scaffold: classify failure mode from raw output text ──
        raw_naming_text = f"{specimen.name}\n{specimen.description}"
        scaffold_class = self.naming_autopsy.classify_scaffold(
            raw_output=raw_naming_text
        )

        # Populate scaffold fields on specimen
        specimen.scaffold_mode = scaffold_class.primary_mode
        specimen.scaffold_confidence = scaffold_class.confidence
        specimen.scaffold_interpretation = scaffold_class.interpretation
        specimen.scaffold_density = scaffold_class.scaffold_density
        specimen.scaffold_neologism_count = scaffold_class.neologism_count
        specimen.scaffold_cross_lingual_scripts = scaffold_class.cross_lingual_scripts

        # Save scaffold artifacts to disk
        self.naming_autopsy.save_scaffold_data(
            shadow=None,  # Text-only mode; no full logit shadow here
            classification=scaffold_class,
            specimen_id=specimen.specimen_id,
            specimens_dir=specimen_dir,
        )

        specimen.status = "screen_capture"

        # ── Logging ──
        slog.info(f"  🏆 Screen specimen: '{specimen.name}'")
        if specimen.description:
            slog.info(f"     {specimen.description[:120]}")

        if specimen.autopsy_classification:
            icon = {
                "TRUE_ARCANUM": "🏛️", "COLLISION": "💥",
                "ECHO": "🔁", "CHIMERA": "🧬", "UNCLASSIFIABLE": "❓",
            }.get(specimen.autopsy_classification, "?")
            slog.info(f"     {icon} Token autopsy: {specimen.autopsy_classification} "
                      f"({specimen.autopsy_recommendation})")

        scaffold_icon = {
            "CLEAN_NAME": "✅", "FIELD_BIOLOGIST": "🔬",
            "META_LINGUISTIC": "📐", "CONVERSATIONAL_BLEED": "💬",
            "HALLUCINATED_CITATION": "📚", "PERSONA_BLEND": "🎭",
            "RAW_SCAFFOLD": "⚡", "UNCLASSIFIABLE": "❓",
        }.get(scaffold_class.primary_mode, "❓")
        slog.info(f"     {scaffold_icon} Scaffold: {scaffold_class.primary_mode} "
                  f"({scaffold_class.confidence:.0%})")

    except Exception as e:
        slog.error(f"  Screen capture failed: {e}")


# ─── CHANGE 4 (Optional): Track autopsy stats in run() counters ──────
#
# After hits_count / captures_count declarations (around line 515):
#
#     arcanum_count = 0
#     collision_count = 0
#     chimera_count = 0
#
# In the body where captures are tallied, add:
#
#     if specimen and specimen.autopsy_classification == "TRUE_ARCANUM":
#         arcanum_count += 1
#     elif specimen and specimen.autopsy_classification == "COLLISION":
#         collision_count += 1
#     elif specimen and specimen.autopsy_classification == "CHIMERA":
#         chimera_count += 1
#
# In the progress summary log:
#
#     slog.info(f"  Autopsy: {arcanum_count} arcanum, "
#               f"{collision_count} collisions, {chimera_count} chimeras")


# ─── CHANGE 5 (Optional): Full naming shadow capture ─────────────────
#
# The text-only scaffold classifier (used in Change 3) works without
# modifying naming_engine.py. For richest data, modify
# generate_specimen_name() to also return the naming prompt, then:
#
#     naming_shadow = self.naming_autopsy.capture_naming_shadow(
#         model=self.model,
#         naming_prompt=naming_prompt_used,
#         max_new_tokens=self.xeno_config.naming_max_tokens,
#     )
#     scaffold_class = self.naming_autopsy.classify_scaffold(
#         shadow=naming_shadow,
#     )
#
# This adds token-level scaffold signal detection (which positions in the
# naming output triggered which failure modes). Adds ~5s per capture.


"""
═══════════════════════════════════════════════════════════════════════
FILES GENERATED PER SPECIMEN CAPTURE (3B run)
═══════════════════════════════════════════════════════════════════════

Existing (unchanged):
  {id}.pt                   — Genome vector
  {id}_emb.pt               — Embedding centroid
  {id}.json                 — Full specimen metadata (all fields)

From token autopsy:
  {id}_shadow.json          — Raw logit shadow (top-25 tokens per position)
  {id}_cloud.json           — Concept cloud analysis
  {id}_autopsy.txt          — Human-readable token autopsy report

From naming scaffold:
  {id}_scaffold.json        — Scaffold classification (JSON)
  {id}_scaffold_report.txt  — Human-readable scaffold report
  {id}_naming_shadow.json   — (Optional) Full naming pass logit shadow

New fields on specimen JSONL:
  autopsy_classification, autopsy_confidence, autopsy_recommendation,
  autopsy_discard_reason, autopsy_mundane_fraction,
  autopsy_novelty_coherence, autopsy_dominant_domains, autopsy_summary,
  scaffold_mode, scaffold_confidence, scaffold_interpretation,
  scaffold_density, scaffold_neologism_count, scaffold_cross_lingual_scripts
"""
