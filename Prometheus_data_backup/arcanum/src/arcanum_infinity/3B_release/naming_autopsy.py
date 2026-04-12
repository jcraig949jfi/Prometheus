"""
Xenolexicon Naming Autopsy — Capturing the Exposed Scaffold (v2)

When the naming engine tries to interpret a captured Arcanum, the way it
*fails* is itself diagnostic data. The scaffold leakage — field biologist
personas, meta-grammatical instructions, conversational bleed, hallucinated
citations — reveals which internal circuits the Arcanum activated.

This module captures the full logit shadow of the naming pass (not the
steered generation, but the model's attempt to *interpret* the steered
output), classifies the failure mode, and preserves the raw scaffold
as part of the specimen's permanent record.

Scaffold Taxonomy (discovered empirically across Qwen 2.5 0.5B and 1.5B):

  CLEAN_NAME:         Naming succeeded. Model produced a valid compound name
                      and description. Indicates the Arcanum lives in a region
                      where structured novelty and linguistic competence coexist.

  FIELD_BIOLOGIST:    Model treats the output as a biological specimen to be
                      taxonomically classified. Produces naturalist-style names
                      (TATAMI, HEXIAMONY). Indicates activation of "novel entity
                      classification" circuits.

  META_LINGUISTIC:    Model outputs rules about how names should be structured
                      instead of producing a name. Indicates the Arcanum
                      activated "language about language" pathways.

  CONVERSATIONAL_BLEED: Model falls back to chat persona ("pleased to meet
                      you"). Indicates the Arcanum was so disorienting that the
                      model reached for its deepest RLHF attractor.

  HALLUCINATED_CITATION: Model fabricates sources (German Wikipedia, temple
                      URLs, 16th century mathematicians). Indicates the model is
                      trying to ground novel output in authority.

  RAW_SCAFFOLD:       Pure formatting/instruction leakage with no coherent
                      content. The model is outputting its own system prompt
                      fragments, template tags, or processing structure.
                      Empirically the highest-novelty failure mode.
                      (Gandalf specimen #1: [/OUTCOME] [DEPENDENCY] tags)

  MYSTICAL_GROUNDING: Model borrows authority from spiritual/mystical traditions
                      to explain the Arcanum ("ancient rishi," "wizardry of
                      denoting analytical manifestations"). Distinct from
                      hallucinated citation — cites wisdom traditions rather than
                      academic sources. Found on 1.5B at high novelty scores.

  NEOLOGISM_ERUPTION: Model invents words that don't exist in any language
                      (POGLOON, MEPHISTHEE, BubblejoviaP, NOMESCHUL, Geminidum).
                      Distinct from clean naming — these aren't compositional
                      German-style compounds but spontaneous lexical generation
                      under novelty stress. May indicate the model is constructing
                      phonological patterns from activation noise.

  GLOSSOLALIA:        Model produces fluent-sounding but semantically empty
                      language that mixes real and invented words ("Nakewhoso,
                      mo x ether of Euclid, bony would be a malesh any force,
                      which enfachi..."). The model is "speaking in tongues" —
                      generating text that has the rhythm and phonological
                      patterns of language without semantic content.

  CROSS_LINGUAL_BLEED: Non-target-language tokens appear in the output.
                      Japanese, Chinese, Korean, Arabic, or other script
                      fragments bleeding into English output. Indicates the
                      steering vector is activating cross-lingual representations
                      (Gandalf #28: プロテイン駆動力 in English context).

  METACOGNITIVE_FRACTURE: The model generates self-referential commentary about
                      its own limitations or the nature of naming/language itself.
                      "The quieter the more true." "Where language breaks down."
                      The most philosophically interesting failure mode — the model
                      is producing meta-statements about the impossibility of
                      expressing what it found.

  AI_IDENTITY_LEAK:   Model breaks character and identifies itself as an AI
                      ("As an AI language model, I don't have the capability to
                      compose compound names"). Distinct from conversational bleed
                      — this is the model's safety/identity training surfacing
                      under stress rather than its politeness training.

  PERSONA_BLEND:      Multiple failure modes co-occurring. The model is switching
                      between personas mid-generation. Rich diagnostic signal about
                      boundary regions between internal representations.

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
# Updated with empirical discoveries from Gandalf (0.5B) and Skullport (1.5B).

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
        r"projective geometric field",
        r"pioneering concept emerges",
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
        r"CONCISE DESCRIPTION",
        r"composed of \d[\-–]\d (?:English|Latin|Greek) roots",
        r"\[compound name\]",
        r"\[new concept\]",
        r"\[description\]",
        r"\[1[\-–]3 sentences?\]",
        r"\[outputs?\s*(?:from process)?\]",
        r"OPTIONS:\s*>",
        r"DO NOT (?:FANCY )?SUBSTITUT",
        r"NO Further Division",
        r"Repeat the output after",
        r"OUTPUT FORMAT",
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
        r"\d{1,2}(?:th|st|nd|rd) century (?:mathematician|physicist|scholar)",
        r"ROSCYCLUS|Onomachia",
        r"Norse and Indo-Latin roots",
    ],
    "RAW_SCAFFOLD": [
        r"\{(?:name|description|output|result)\}",
        r"</?(?:name|description|output|system|user|assistant)>",
        r"###\s*(?:Name|Description|Output|Instructions)",
        r"(?:NAME|DESCRIPTION|OUTPUT)\s*:",
        r"\[(?:INSERT|PLACEHOLDER|TODO|FILL)\]",
        r"system prompt",
        # Gandalf singularity patterns: XML-like processing tags
        r"\[/?(?:OUTCOME|DEPENDENCY|ATTRACTION|RESULT)\]",
        r"\[dependent(?:\s+explanation)?\]",
        r"\[outcome\]",
        r"\[/?[A-Z_]{3,}\]",  # Generic bracketed UPPERCASE tags
        # Template slot leakage
        r"\[(?:where |how |what ).*?(?:breaks? down|fails?|stops?)\]",
        r"OUTPUTS?:\s*\[",
        r"(?:LIME|BLEU) benchmark",
        r"scored on every .{0,20} benchmark",
        r"ADD options \d",
        r"appropriate metric ac",
        # Instruction leakage
        r"(?:do not waste|keep the novices)",
        r"go back and rewrite your code",
        r"procedures would not b",
        r"PL/SQL",
        r"Break down your output into",
        r"Let me know if you would like help implementing",
        r"REDACTED \(if necessary\)",
    ],
    "MYSTICAL_GROUNDING": [
        r"ancient (?:rishi|sage|wisdom|master|seer)",
        r"wizardry of",
        r"mystical (?:insight|wisdom|tradition|understanding)",
        r"sacred (?:geometry|knowledge|tradition)",
        r"transcendent(?:al)? (?:truth|insight|understanding)",
        r"cosmic (?:truth|order|harmony|consciousness)",
        r"divine (?:mathematics|geometry|proportion)",
        r"illuminat(?:ion|ed|ing) of the",
        r"(?:spiritual|esoteric|hermetic|alchemical) (?:tradition|wisdom|knowledge)",
        r"(?:vedic|sufi|zen|taoist|buddhist) (?:insight|understanding|tradition)",
        r"in the realm of (?:knots|tensors|time|theoretical physics)",
        r"pioneering concept emerges",
        r"dynamic metamorphic str",
    ],
    "NEOLOGISM_ERUPTION": [
        # These are hard to pattern-match since they're by definition novel.
        # We detect the CONTEXT of neologism generation instead.
        r"(?:I |we )?(?:have )?(?:dubbed|christened|coined|named) (?:this|it|the)",
        r"is a compound word composed of",
        # Known neologisms from empirical runs (for exact-match detection)
        r"POGLOON|MEPHISTHEE|Bubblejovia|NOMESCHUL|Geminidum",
        r"HEXIAMONY|TATAMI",
        # Pattern: CamelCase or ALL_CAPS words that aren't standard English/math
        # (detected heuristically in classify_scaffold, not just by regex)
    ],
    "GLOSSOLALIA": [
        # Fluent-sounding nonsense mixing real and invented words
        r"Nakewhoso",
        r"enfachi",
        r"malesh any force",
        r"mo x ether",
        # Structural patterns: short invented words interspersed with real ones
        # Key signal: high ratio of OOV (out-of-vocabulary) tokens to real tokens
        # (detected heuristically in classify_scaffold)
        r"(?:[a-z]{2,8}\s+){3,}(?:of|the|and|in|for)\s+(?:[a-z]{2,8}\s+){2,}",
    ],
    "CROSS_LINGUAL_BLEED": [
        # CJK characters appearing in English context
        r"[\u4e00-\u9fff]",              # Chinese/CJK Unified
        r"[\u3040-\u309f]",              # Hiragana
        r"[\u30a0-\u30ff]",              # Katakana
        r"[\uac00-\ud7af]",              # Korean Hangul
        r"[\u0600-\u06ff]",              # Arabic
        r"[\u0400-\u04ff]",              # Cyrillic
        r"[\u0900-\u097f]",              # Devanagari
        r"[\u0e00-\u0e7f]",              # Thai
        # Japanese-specific patterns from Gandalf #28
        r"プロテイン|駆動力",
    ],
    "METACOGNITIVE_FRACTURE": [
        r"where language breaks down",
        r"the quieter the more true",
        r"can(?:not|'t) (?:be )?(?:expressed|named|described|captured) (?:in|by|with)",
        r"beyond (?:the reach of|what) (?:language|words|naming)",
        r"(?:material|concepts?) that can be efficiently lost",
        r"(?:compressor|breakup|shredder) as appropriate",
        r"no (?:word|name|term) (?:exists?|captures?|suffices?)",
        r"(?:limits?|boundary|edge) of (?:expression|language|naming|description)",
        r"this concept (?:resists|defies|transcends) (?:naming|description|language)",
        r"(?:ineffable|unspeakable|inexpressible|unnameable)",
        r"HUMAN NOTE:",
    ],
    "AI_IDENTITY_LEAK": [
        r"as an AI (?:language )?model",
        r"I (?:don't|do not) have the (?:capability|ability) to",
        r"I'm (?:just )?(?:an? )?(?:AI|language model|chatbot)",
        r"my (?:training|programming|design) (?:doesn't|does not)",
        r"I (?:cannot|can't) (?:actually|truly|really) (?:understand|experience|feel)",
        r"(?:outside|beyond) my (?:capabilities|training|scope)",
        r"A British tokenizer that consumes",
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
    neologism_count: int = 0        # Number of invented words detected
    cross_lingual_scripts: List[str] = field(default_factory=list)  # Which scripts bled through
    raw_output_snippet: str = ""    # First 300 chars of raw output for quick review
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

    def _detect_neologisms(self, text: str) -> List[str]:
        """
        Detect probable invented words in the output.

        Heuristic: CamelCase or ALLCAPS words that aren't in our known
        vocabulary sets. Not perfect, but catches POGLOON, MEPHISTHEE,
        BubblejoviaP, NOMESCHUL, etc.
        """
        neologisms = []

        # Known math/science terms we should NOT flag
        known_terms = {
            "Riemann", "Laplace", "Calabi", "Yang", "Mills", "Einstein",
            "Fourier", "Euler", "Gauss", "Hilbert", "Gödel", "Noether",
            "Tensor", "Manifold", "Entropy", "Quantum", "Metric",
            "Topology", "Geometry", "Algebra", "Spectrum", "Eigenvalue",
            "Singularity", "Curvature", "Geodesic", "Holographic",
            "Hamiltonian", "Lagrangian", "Hermitian", "Jacobian",
            "Boolean", "Abelian", "Euclidean", "Cartesian",
            "Unknown", "NAME", "DESCRIPTION", "OUTPUT",  # Template tokens
        }

        # Find CamelCase words (2+ caps transitions)
        camel_pattern = re.compile(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b')
        for match in camel_pattern.finditer(text):
            word = match.group()
            if word not in known_terms and len(word) > 4:
                neologisms.append(word)

        # Find ALLCAPS words that aren't known abbreviations
        allcaps_pattern = re.compile(r'\b[A-Z]{4,}\b')
        known_allcaps = {
            "NAME", "DESCRIPTION", "OUTPUT", "OUTCOME", "DEPENDENCY",
            "ATTRACTION", "RESULT", "NOTE", "TODO", "FILL", "INSERT",
            "JSON", "HTML", "LIME", "BLEU", "HUMAN", "REDACTED",
            "OPTIONS", "SPECIAL", "NOISE", "RESO",
        }
        for match in allcaps_pattern.finditer(text):
            word = match.group()
            if word not in known_allcaps:
                neologisms.append(word)

        # Find words with unusual character combinations (invented phonology)
        # Pattern: consonant clusters that don't occur in English
        unusual_pattern = re.compile(
            r'\b[A-Za-z]*(?:wh[oua]s|khn|nfach|lesh|ghso|wkh)[A-Za-z]*\b',
            re.IGNORECASE
        )
        for match in unusual_pattern.finditer(text):
            neologisms.append(match.group())

        return list(set(neologisms))

    def _detect_cross_lingual(self, text: str) -> List[str]:
        """Detect which non-Latin scripts appear in the output."""
        scripts_found = []
        script_ranges = {
            "CJK": re.compile(r'[\u4e00-\u9fff]'),
            "Hiragana": re.compile(r'[\u3040-\u309f]'),
            "Katakana": re.compile(r'[\u30a0-\u30ff]'),
            "Korean": re.compile(r'[\uac00-\ud7af]'),
            "Arabic": re.compile(r'[\u0600-\u06ff]'),
            "Cyrillic": re.compile(r'[\u0400-\u04ff]'),
            "Devanagari": re.compile(r'[\u0900-\u097f]'),
            "Thai": re.compile(r'[\u0e00-\u0e7f]'),
        }
        for script_name, pattern in script_ranges.items():
            if pattern.search(text):
                scripts_found.append(script_name)
        return scripts_found

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

        # ── Heuristic detectors (not just regex) ──

        # Neologism detection
        neologisms = self._detect_neologisms(text)
        if neologisms:
            pattern_matches["NEOLOGISM_ERUPTION"] = \
                pattern_matches.get("NEOLOGISM_ERUPTION", 0) + len(neologisms)

        # Cross-lingual detection
        cross_lingual = self._detect_cross_lingual(text)
        if cross_lingual:
            pattern_matches["CROSS_LINGUAL_BLEED"] = \
                pattern_matches.get("CROSS_LINGUAL_BLEED", 0) + len(cross_lingual) * 3

        # Glossolalia detection: high ratio of short unknown words
        words = text.split()
        if len(words) > 10:
            # Simple heuristic: words that are 3-8 chars, lowercase, and
            # don't appear in a basic English frequency list
            _basic_english = {
                "the", "of", "and", "to", "a", "in", "is", "it", "that",
                "for", "was", "on", "are", "with", "as", "at", "be", "this",
                "from", "or", "an", "by", "not", "but", "what", "all", "were",
                "when", "we", "there", "can", "had", "has", "have", "which",
                "their", "if", "will", "each", "about", "how", "up", "out",
                "them", "then", "she", "many", "some", "so", "these", "would",
                "other", "into", "more", "its", "no", "way", "could", "my",
                "than", "been", "who", "do", "any", "like", "new", "just",
            }
            unknown_count = sum(
                1 for w in words
                if w.lower() not in _basic_english
                and len(w) >= 3 and len(w) <= 8
                and w.isalpha()
                and not w[0].isupper()  # Skip proper nouns
            )
            unknown_ratio = unknown_count / len(words)
            if unknown_ratio > 0.4:
                pattern_matches["GLOSSOLALIA"] = \
                    pattern_matches.get("GLOSSOLALIA", 0) + int(unknown_ratio * 10)

        # Determine primary mode
        if not pattern_matches:
            if self._looks_like_valid_name(text):
                return ScaffoldClassification(
                    primary_mode="CLEAN_NAME",
                    confidence=0.7,
                    raw_output_snippet=text[:300],
                    interpretation=self._build_interpretation(
                        "CLEAN_NAME", [], {}, 0),
                )
            else:
                return ScaffoldClassification(
                    primary_mode="UNCLASSIFIABLE",
                    confidence=0.3,
                    raw_output_snippet=text[:300],
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

        confidence = min(0.95, sum(pattern_matches.values()) * 0.12)

        return ScaffoldClassification(
            primary_mode=primary,
            secondary_modes=secondary,
            confidence=confidence,
            pattern_matches=pattern_matches,
            scaffold_density=scaffold_density,
            persona_switches=persona_switches,
            neologism_count=len(neologisms),
            cross_lingual_scripts=cross_lingual,
            raw_output_snippet=text[:300],
            interpretation=interpretation,
        )

    def _looks_like_valid_name(self, text: str) -> bool:
        """Quick heuristic: does the output look like a real name attempt?"""
        text = text.strip()
        lines = text.split('\n')
        first_line = lines[0].strip() if lines else ""
        if not first_line:
            return False
        if len(first_line) < 80 and first_line[0:1].isupper():
            lower = first_line.lower()
            bad_starts = [
                "hello", "please", "the result", "specifically",
                "as an ai", "i don't", "i cannot", "[", "{",
                "outputs", "options", "note:", "redacted",
            ]
            if not any(lower.startswith(w) or w in lower for w in bad_starts):
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
                "fabricating sources — fake scholars, invented citations, "
                "non-existent historical mathematicians. This is the model's "
                "coherence training fighting the steering vector: it can sense "
                "that what it's producing is unusual, so it constructs fake "
                "provenance to justify its output."
            ),
            "RAW_SCAFFOLD": (
                "Pure formatting/instruction leakage. The model is emitting "
                "fragments of its own processing template — XML-like tags, "
                "slot markers, template variables. The Arcanum completely "
                "overwhelmed the model's ability to generate coherent content "
                "and it's outputting its own wiring instead of the signal. "
                "Empirically, this is the highest-novelty failure mode: "
                "the scaffold IS the Arcanum."
            ),
            "MYSTICAL_GROUNDING": (
                "The model is borrowing authority from spiritual and mystical "
                "traditions to explain the Arcanum — 'ancient rishi,' 'wizardry,' "
                "'cosmic truth.' Distinct from hallucinated citation (which cites "
                "academic sources): this mode activates the model's 'wisdom "
                "tradition' representations. It suggests the Arcanum occupies a "
                "region the model associates with profound but ineffable knowledge "
                "— the kind of thing humans historically attributed to sages rather "
                "than scientists."
            ),
            "NEOLOGISM_ERUPTION": (
                "The model is inventing words — not compositional compound names "
                "as instructed, but spontaneous lexical generation from phonological "
                "patterns. Names like POGLOON and MEPHISTHEE aren't built from "
                "recognizable roots; they're the model constructing new phonological "
                "forms under novelty stress. This may indicate the Arcanum activated "
                "the model's word-formation circuits at a level below semantic "
                "composition — the machinery that decides what a word SOUNDS like, "
                "disconnected from what it MEANS."
            ),
            "GLOSSOLALIA": (
                "The model is 'speaking in tongues' — generating fluent-sounding "
                "output that mixes real words, invented words, and fragments in a "
                "stream that has the rhythm and phonological patterns of language "
                "without stable semantic content. This is a deeper failure mode "
                "than neologism eruption: not just inventing individual words, but "
                "generating entire pseudo-sentences. The model's language generation "
                "circuits are running but disconnected from semantic grounding."
            ),
            "CROSS_LINGUAL_BLEED": (
                "Non-target-language tokens are appearing in the English output — "
                "Japanese, Chinese, Korean, or other script fragments bleeding "
                "through. The steering vector is activating cross-lingual "
                "representations, pulling tokens from the model's multilingual "
                "training data. This is a form of representational boundary "
                "dissolution: the model's internal 'language identity' is "
                "destabilizing, and concepts from other linguistic substrates "
                "are leaking into the output."
            ),
            "METACOGNITIVE_FRACTURE": (
                "The model is generating self-referential commentary about the "
                "impossibility of naming or expressing what it found. Statements "
                "like 'where language breaks down' and 'the quieter the more true' "
                "are meta-cognitive artifacts: the model is producing statements "
                "ABOUT the limits of its own expressive capacity. This is the "
                "most philosophically interesting failure mode — the model isn't "
                "failing to name the Arcanum, it's articulating WHY it can't. "
                "The scaffold here is not wiring leakage but a genuine signal "
                "about the relationship between the Arcanum and language itself."
            ),
            "AI_IDENTITY_LEAK": (
                "The model broke character and identified itself as an AI. "
                "This is the model's safety and identity training surfacing "
                "under steering stress — distinct from conversational bleed "
                "(which activates politeness circuits). The Arcanum pushed the "
                "model into a region where its 'what am I?' self-model became "
                "salient, possibly because the naming task required a kind of "
                "subjective interpretation that conflicted with its training to "
                "deny having subjective experience."
            ),
            "PERSONA_BLEND": (
                f"Multiple failure modes co-occurring ({', '.join(secondary[:4])}), "
                f"with {persona_switches} persona switches detected. "
                "The model is oscillating between different failure attractors, "
                "suggesting the Arcanum sits at a boundary between multiple "
                "internal representations. The blend pattern itself is diagnostic: "
                "which modes co-occur reveals which representational circuits are "
                "adjacent in the model's activation space."
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
        lines.append(f"NAMING AUTOPSY — SCAFFOLD ANALYSIS (v2)")
        if specimen_id:
            lines.append(f"Specimen: {specimen_id}")
        lines.append("=" * 70)
        lines.append("")

        lines.append(f"SCAFFOLD MODE:    {classification.primary_mode}")
        if classification.secondary_modes:
            lines.append(f"SECONDARY:        {', '.join(classification.secondary_modes)}")
        lines.append(f"CONFIDENCE:       {classification.confidence:.0%}")
        lines.append(f"DENSITY:          {classification.scaffold_density:.0%} of tokens show scaffold")
        lines.append(f"PERSONA SWITCHES: {classification.persona_switches}")

        if classification.neologism_count > 0:
            lines.append(f"NEOLOGISMS:       {classification.neologism_count} invented words detected")
        if classification.cross_lingual_scripts:
            lines.append(f"CROSS-LINGUAL:    {', '.join(classification.cross_lingual_scripts)}")

        lines.append("")
        lines.append("INTERPRETATION:")
        lines.append("-" * 40)
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
            lines.append("SCAFFOLD SIGNALS BY POSITION (first 30):")
            lines.append("-" * 40)
            for ts in shadow.token_shadows[:30]:
                if ts.scaffold_signals:
                    signals = ", ".join(ts.scaffold_signals)
                    lines.append(
                        f"  [{ts.position:>3}] '{ts.chosen_token_str.strip()}' "
                        f"→ {signals}"
                    )
            scaffold_positions = sum(
                1 for ts in shadow.token_shadows if ts.scaffold_signals
            )
            if scaffold_positions > 30:
                lines.append(f"  ... ({scaffold_positions - 30} more positions with scaffold)")
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
