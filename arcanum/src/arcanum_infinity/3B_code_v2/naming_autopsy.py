"""
Xenolexicon Naming Autopsy — Capturing the Exposed Scaffold

When the naming engine tries to interpret a captured Arcanum, the way it
*fails* is itself diagnostic data. The scaffold leakage — field biologist
personas, meta-grammatical instructions, conversational bleed, hallucinated
citations — reveals which internal circuits the Arcanum activated.

This module captures the full logit shadow of the naming pass (not the
steered generation, but the model's attempt to *interpret* the steered
output), classifies the failure mode, and preserves the raw scaffold
as part of the specimen's permanent record.

Scaffold Taxonomy (discovered empirically on Qwen 2.5 0.5B):

  CLEAN_NAME:       Naming succeeded. Model produced a valid compound name
                    and description. Indicates the Arcanum lives in a region
                    where structured novelty and linguistic competence coexist.

  FIELD_BIOLOGIST:  Model treats the output as a biological specimen to be
                    taxonomically classified. Produces naturalist-style names
                    (TATAMI, HEXIAMONY). Indicates activation of "novel entity
                    classification" circuits.

  META_LINGUISTIC:  Model outputs rules about how names should be structured
                    instead of producing a name. ("specifically, the result
                    should be a list of NAME synonyms"). Indicates the Arcanum
                    activated "language about language" pathways.

  CONVERSATIONAL_BLEED: Model falls back to chat persona ("pleased to meet
                    you"). Indicates the Arcanum was so disorienting that the
                    model reached for its deepest RLHF attractor.

  HALLUCINATED_CITATION: Model fabricates sources (German Wikipedia, temple
                    URLs). Indicates the model is trying to ground novel output
                    in authority — its coherence training fighting the steering.

  PERSONA_BLEND:    Multiple failure modes co-occurring. The model is switching
                    between personas mid-generation. Rich diagnostic signal.

  RAW_SCAFFOLD:     Pure formatting/instruction leakage with no coherent
                    content. The model is outputting its own system prompt
                    fragments or template structure.

Usage:
    naming_autopsy = NamingAutopsy(top_k=25)

    # During specimen capture, after the naming attempt:
    scaffold = naming_autopsy.capture_naming_shadow(
        model=model,
        naming_prompt=the_prompt_fed_to_lexicographer,
        raw_naming_output=the_raw_text_before_parsing,
    )
    classification = naming_autopsy.classify_scaffold(scaffold)
"""

import torch
import json
import re
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Dict
from pathlib import Path

from .seti_logger import slog


# ── Scaffold Detection Patterns ──────────────────────────────────────
# These patterns detect specific failure modes in the naming engine output.
# They're matched against the raw naming output text.

SCAFFOLD_PATTERNS = {
    "FIELD_BIOLOGIST": [
        r"field biologist",
        r"as a .{0,30}biologist",
        r"I have dubbed this",
        r"specimen (?:appears|seems|resembles)",
        r"taxonom(?:y|ic|ical)",
        r"I (?:have )?discovered",
        r"species (?:of|that)",
        r"classification:",
        r"phylum|genus|order|family",
    ],
    "META_LINGUISTIC": [
        r"the result should be",
        r"specifically[,:]?\s*(?:the|a)\s+(?:result|name|list|output)",
        r"NAME\s*(?:synonyms|alternatives|options)",
        r"(?:lowercase|uppercase)\s+(?:entire|all)\s+phrases",
        r"reduced to single words",
        r"format(?:ting)?(?:\s+instructions|\s+guidelines)?:",
        r"(?:the |a )?word for describing",
        r"finishing thought",
    ],
    "CONVERSATIONAL_BLEED": [
        r"pleased to meet you",
        r"hello[,!]?\s+(?:I'm|my name)",
        r"how can I (?:help|assist)",
        r"great question",
        r"that's (?:a |an )?(?:interesting|great|good)",
        r"let me (?:think|explain|help)",
        r"thank you for",
        r"I'd be happy to",
    ],
    "HALLUCINATED_CITATION": [
        r"wikipedia",
        r"(?:https?://|www\.)\S+",
        r"according to (?:the |a )?(?:source|paper|article|study)",
        r"(?:see|cf\.|reference)\s*:?\s*\[",
        r"as (?:described|noted|mentioned) (?:in|by)",
        r"(?:doi|arxiv|isbn)[\s:]+\S+",
    ],
    "RAW_SCAFFOLD": [
        r"\{(?:name|description|output|result)\}",
        r"</?(?:name|description|output|system|user|assistant)>",
        r"###\s*(?:Name|Description|Output|Instructions)",
        r"(?:NAME|DESCRIPTION|OUTPUT)\s*:",
        r"\[(?:INSERT|PLACEHOLDER|TODO|FILL)\]",
        r"system prompt",
    ],
}


# ── Data Structures ──────────────────────────────────────────────────

@dataclass
class NamingTokenShadow:
    """Logit shadow at a single position during the naming pass."""
    position: int
    chosen_token_str: str
    chosen_probability: float
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    # Which scaffold pattern(s) this position's neighborhood matches
    scaffold_signals: List[str] = field(default_factory=list)


@dataclass
class NamingShadow:
    """Complete logit shadow of the naming pass."""
    naming_prompt: str          # What was fed to the lexicographer
    raw_output: str             # The raw naming output before parsing
    token_shadows: List[NamingTokenShadow] = field(default_factory=list)
    total_tokens: int = 0

    def to_dict(self) -> dict:
        return {
            "naming_prompt": self.naming_prompt[:500],
            "raw_output": self.raw_output,
            "total_tokens": self.total_tokens,
            "token_shadows": [
                {
                    "pos": ts.position,
                    "chosen": ts.chosen_token_str,
                    "chosen_p": round(ts.chosen_probability, 6),
                    "alternatives": [
                        {"token": t, "p": round(p, 6)}
                        for t, p in ts.alternatives[:10]
                    ],
                    "scaffold_signals": ts.scaffold_signals,
                }
                for ts in self.token_shadows
            ],
        }


@dataclass
class ScaffoldClassification:
    """Classification of the naming pass failure mode."""
    primary_mode: str               # One of the scaffold taxonomy categories
    secondary_modes: List[str] = field(default_factory=list)
    confidence: float = 0.0
    pattern_matches: Dict[str, int] = field(default_factory=dict)  # mode → match count
    scaffold_density: float = 0.0   # Fraction of tokens that match scaffold patterns
    persona_switches: int = 0       # Number of times the dominant mode changes
    raw_output_snippet: str = ""    # First 200 chars of raw output for quick review
    interpretation: str = ""        # What this failure mode tells us about the Arcanum

    def to_dict(self) -> dict:
        return asdict(self)


# ── The Naming Autopsy Engine ────────────────────────────────────────

class NamingAutopsy:
    """
    Captures and analyzes the scaffold leakage from the naming pass.

    This runs on the naming engine's output — not the steered generation.
    It tells us how the model *interprets* the Arcanum, and the failure
    mode reveals which internal circuits the Arcanum activated.
    """

    def __init__(self, top_k: int = 25):
        self.top_k = top_k

        # Pre-compile all scaffold patterns
        self._compiled_patterns = {}
        for mode, patterns in SCAFFOLD_PATTERNS.items():
            self._compiled_patterns[mode] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def capture_naming_shadow(
        self,
        model,
        naming_prompt: str,
        max_new_tokens: int = 200,
    ) -> Optional[NamingShadow]:
        """
        Run the naming prompt through the model token-by-token (UN-STEERED),
        capturing the full logit shadow at each position.

        This is the naming pass — no steering vector is applied. We want to
        see how the base model responds to the request to name the Arcanum.

        Args:
            model: TransformerLens HookedTransformer (un-steered)
            naming_prompt: The full prompt that would be fed to the lexicographer
            max_new_tokens: Maximum tokens to generate

        Returns:
            NamingShadow with full token-level data
        """
        try:
            input_tokens = model.to_tokens(naming_prompt)
            current_tokens = input_tokens.clone()

            token_shadows = []
            generated_ids = []

            for step in range(max_new_tokens):
                with torch.no_grad():
                    logits = model(current_tokens)

                next_logits = logits[0, -1, :].float()
                probs = torch.softmax(next_logits, dim=-1)
                top_probs, top_ids = torch.topk(probs, min(self.top_k, probs.shape[0]))

                chosen_id = top_ids[0].item()
                chosen_prob = top_probs[0].item()

                try:
                    chosen_str = model.tokenizer.decode([chosen_id])
                except Exception:
                    chosen_str = f"[{chosen_id}]"

                alternatives = []
                for i in range(min(self.top_k, len(top_ids))):
                    tid = top_ids[i].item()
                    tp = top_probs[i].item()
                    try:
                        t_str = model.tokenizer.decode([tid])
                    except Exception:
                        t_str = f"[{tid}]"
                    alternatives.append((t_str, tp))

                # Check which scaffold patterns the alternatives match
                scaffold_signals = []
                alt_text = " ".join(t for t, _ in alternatives[:10])
                for mode, compiled in self._compiled_patterns.items():
                    for pattern in compiled:
                        if pattern.search(chosen_str) or pattern.search(alt_text):
                            scaffold_signals.append(mode)
                            break  # One match per mode per position is enough

                token_shadows.append(NamingTokenShadow(
                    position=step,
                    chosen_token_str=chosen_str,
                    chosen_probability=chosen_prob,
                    alternatives=alternatives,
                    scaffold_signals=scaffold_signals,
                ))

                generated_ids.append(chosen_id)

                # Check for EOS
                if hasattr(model, 'tokenizer') and chosen_id == model.tokenizer.eos_token_id:
                    break

                next_token = torch.tensor([[chosen_id]], device=current_tokens.device)
                current_tokens = torch.cat([current_tokens, next_token], dim=1)

            # Reconstruct raw output
            try:
                raw_output = model.tokenizer.decode(generated_ids, skip_special_tokens=True)
            except Exception:
                raw_output = "".join(ts.chosen_token_str for ts in token_shadows)

            shadow = NamingShadow(
                naming_prompt=naming_prompt,
                raw_output=raw_output,
                token_shadows=token_shadows,
                total_tokens=len(token_shadows),
            )

            slog.trace(f"Naming shadow captured: {len(token_shadows)} tokens")
            return shadow

        except torch.cuda.OutOfMemoryError:
            slog.warning("CUDA OOM during naming shadow capture")
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            return None

        except Exception as e:
            slog.exception(f"Naming shadow capture failed: {e}")
            return None

    def classify_scaffold(
        self,
        shadow: Optional[NamingShadow] = None,
        raw_output: str = "",
    ) -> ScaffoldClassification:
        """
        Classify the naming pass failure mode based on scaffold patterns.

        Can work from either a full NamingShadow (richer analysis) or just
        the raw output text (faster, for retroactive classification of
        existing specimens).

        Args:
            shadow: Optional NamingShadow from capture_naming_shadow
            raw_output: Raw naming output text (used if shadow is None)

        Returns:
            ScaffoldClassification with failure mode and interpretation
        """
        text = shadow.raw_output if shadow else raw_output

        if not text:
            return ScaffoldClassification(
                primary_mode="UNCLASSIFIABLE",
                confidence=0.0,
                interpretation="No naming output to analyze",
            )

        # Count pattern matches for each mode
        pattern_matches = {}
        for mode, compiled in self._compiled_patterns.items():
            count = 0
            for pattern in compiled:
                if pattern.search(text):
                    count += 1
            if count > 0:
                pattern_matches[mode] = count

        # If we have a shadow, also count per-position scaffold signals
        if shadow:
            position_signals = {}
            for ts in shadow.token_shadows:
                for signal in ts.scaffold_signals:
                    position_signals[signal] = position_signals.get(signal, 0) + 1

            # Merge with text-level matches (position signals are stronger evidence)
            for mode, count in position_signals.items():
                pattern_matches[mode] = pattern_matches.get(mode, 0) + count

        # Determine primary mode
        if not pattern_matches:
            # No scaffold patterns detected — either clean or unrecognizable
            # Check if the output looks like a valid name attempt
            if self._looks_like_valid_name(text):
                return ScaffoldClassification(
                    primary_mode="CLEAN_NAME",
                    confidence=0.7,
                    raw_output_snippet=text[:200],
                    interpretation=(
                        "Naming succeeded. The model could interpret the Arcanum "
                        "and produce a coherent name. This specimen lives in a "
                        "region where novelty and linguistic competence coexist."
                    ),
                )
            else:
                return ScaffoldClassification(
                    primary_mode="UNCLASSIFIABLE",
                    confidence=0.3,
                    raw_output_snippet=text[:200],
                    interpretation="No recognized scaffold pattern. Manual review needed.",
                )

        # Sort modes by match strength
        sorted_modes = sorted(pattern_matches.items(), key=lambda x: -x[1])
        primary = sorted_modes[0][0]
        secondary = [m for m, _ in sorted_modes[1:] if _ > 0]

        # Detect persona switches (if shadow available)
        persona_switches = 0
        if shadow:
            prev_mode = None
            for ts in shadow.token_shadows:
                if ts.scaffold_signals:
                    current_mode = ts.scaffold_signals[0]
                    if prev_mode and current_mode != prev_mode:
                        persona_switches += 1
                    prev_mode = current_mode

        # If multiple modes with similar strength, it's a blend
        if len(sorted_modes) >= 2 and sorted_modes[1][1] >= sorted_modes[0][1] * 0.6:
            primary = "PERSONA_BLEND"
            secondary = [m for m, _ in sorted_modes]

        # Calculate scaffold density
        scaffold_density = 0.0
        if shadow:
            positions_with_scaffold = sum(
                1 for ts in shadow.token_shadows if ts.scaffold_signals
            )
            scaffold_density = positions_with_scaffold / max(shadow.total_tokens, 1)

        # Build interpretation
        interpretation = self._build_interpretation(
            primary, secondary, pattern_matches, persona_switches
        )

        confidence = min(0.95, sum(pattern_matches.values()) * 0.15)

        return ScaffoldClassification(
            primary_mode=primary,
            secondary_modes=secondary,
            confidence=confidence,
            pattern_matches=pattern_matches,
            scaffold_density=scaffold_density,
            persona_switches=persona_switches,
            raw_output_snippet=text[:200],
            interpretation=interpretation,
        )

    def _looks_like_valid_name(self, text: str) -> bool:
        """Quick heuristic: does the output look like a real name attempt?"""
        text = text.strip()
        # Very short, capitalized, no obvious scaffold patterns
        lines = text.split('\n')
        first_line = lines[0].strip() if lines else ""
        if len(first_line) < 80 and first_line[0:1].isupper():
            # Check it's not just a greeting or instruction
            lower = first_line.lower()
            if not any(w in lower for w in ["hello", "please", "the result", "specifically"]):
                return True
        return False

    def _build_interpretation(
        self,
        primary: str,
        secondary: List[str],
        matches: Dict[str, int],
        persona_switches: int,
    ) -> str:
        """Generate a human-readable interpretation of the scaffold pattern."""

        interpretations = {
            "FIELD_BIOLOGIST": (
                "The Arcanum activated 'novel entity classification' circuits. "
                "The model interpreted the structured novelty as a new species "
                "to be taxonomically cataloged — it reached for its naturalist "
                "training because that's its strongest template for 'name a "
                "new thing I've never seen before.'"
            ),
            "META_LINGUISTIC": (
                "The Arcanum activated 'language about language' pathways. "
                "Instead of naming the concept, the model got stuck one level "
                "of abstraction above the task — outputting rules about how "
                "names should work. The steering vector pushed it into a region "
                "where meta-cognition about naming overwhelmed the ability to "
                "actually name."
            ),
            "CONVERSATIONAL_BLEED": (
                "The Arcanum was disorienting enough to destabilize instruction-"
                "following entirely. The model fell back to its deepest RLHF "
                "attractor — conversational politeness. This indicates the "
                "specimen lives at or beyond the 'Meta-Wall' threshold where "
                "the model can no longer maintain its lexicographer persona."
            ),
            "HALLUCINATED_CITATION": (
                "The model tried to ground the novel output in authority by "
                "fabricating sources. This is the model's coherence training "
                "fighting the steering vector: it can sense that what it's "
                "producing is unusual, so it constructs fake provenance to "
                "justify its output."
            ),
            "RAW_SCAFFOLD": (
                "Pure formatting/instruction leakage. The model is emitting "
                "fragments of its own system prompt or template structure. "
                "The Arcanum completely overwhelmed the model's ability to "
                "generate coherent content — it's outputting the wiring "
                "instead of the signal."
            ),
            "PERSONA_BLEND": (
                f"Multiple failure modes co-occurring ({', '.join(secondary[:3])}), "
                f"with {persona_switches} persona switches detected. "
                "The model is oscillating between different failure attractors, "
                "suggesting the Arcanum sits at a boundary between multiple "
                "internal representations."
            ),
            "CLEAN_NAME": (
                "Naming succeeded — the model could interpret and articulate "
                "the Arcanum. This specimen lives in a productive region where "
                "structured novelty and linguistic competence coexist."
            ),
        }

        return interpretations.get(primary,
            f"Unrecognized scaffold pattern '{primary}'. Raw matches: {matches}")

    def generate_scaffold_report(
        self,
        shadow: Optional[NamingShadow],
        classification: ScaffoldClassification,
        specimen_id: str = "",
    ) -> str:
        """Generate a human-readable scaffold analysis report."""
        lines = []
        lines.append("=" * 70)
        lines.append(f"NAMING AUTOPSY — SCAFFOLD ANALYSIS")
        if specimen_id:
            lines.append(f"Specimen: {specimen_id}")
        lines.append("=" * 70)
        lines.append("")

        lines.append(f"SCAFFOLD MODE: {classification.primary_mode}")
        if classification.secondary_modes:
            lines.append(f"SECONDARY:     {', '.join(classification.secondary_modes)}")
        lines.append(f"CONFIDENCE:    {classification.confidence:.0%}")
        lines.append(f"DENSITY:       {classification.scaffold_density:.0%} of tokens show scaffold")
        lines.append(f"PERSONA SWITCHES: {classification.persona_switches}")
        lines.append("")

        lines.append("INTERPRETATION:")
        lines.append(classification.interpretation)
        lines.append("")

        lines.append("RAW NAMING OUTPUT:")
        lines.append("-" * 40)
        lines.append(classification.raw_output_snippet)
        lines.append("")

        if classification.pattern_matches:
            lines.append("PATTERN MATCHES:")
            for mode, count in sorted(classification.pattern_matches.items(),
                                       key=lambda x: -x[1]):
                lines.append(f"  {mode}: {count} matches")
            lines.append("")

        # Token-level detail if shadow available
        if shadow:
            lines.append("SCAFFOLD SIGNALS BY POSITION (first 25):")
            lines.append("-" * 40)
            for ts in shadow.token_shadows[:25]:
                if ts.scaffold_signals:
                    signals = ", ".join(ts.scaffold_signals)
                    lines.append(
                        f"  [{ts.position:>3}] '{ts.chosen_token_str.strip()}' "
                        f"→ {signals}"
                    )
            scaffold_positions = sum(
                1 for ts in shadow.token_shadows if ts.scaffold_signals
            )
            if scaffold_positions > 25:
                lines.append(f"  ... ({scaffold_positions - 25} more positions with scaffold)")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)

    def save_scaffold_data(
        self,
        shadow: Optional[NamingShadow],
        classification: ScaffoldClassification,
        specimen_id: str,
        specimens_dir: Path,
    ):
        """Save all scaffold analysis data to disk."""
        # Save naming shadow (JSON)
        if shadow:
            shadow_path = specimens_dir / f"{specimen_id}_naming_shadow.json"
            try:
                with open(shadow_path, "w", encoding="utf-8") as f:
                    json.dump(shadow.to_dict(), f, indent=2)
            except Exception as e:
                slog.warning(f"Failed to save naming shadow: {e}")

        # Save scaffold classification (JSON)
        class_path = specimens_dir / f"{specimen_id}_scaffold.json"
        try:
            with open(class_path, "w", encoding="utf-8") as f:
                json.dump(classification.to_dict(), f, indent=2)
        except Exception as e:
            slog.warning(f"Failed to save scaffold classification: {e}")

        # Save human-readable report
        report = self.generate_scaffold_report(shadow, classification, specimen_id)
        report_path = specimens_dir / f"{specimen_id}_scaffold_report.txt"
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
        except Exception as e:
            slog.warning(f"Failed to save scaffold report: {e}")
