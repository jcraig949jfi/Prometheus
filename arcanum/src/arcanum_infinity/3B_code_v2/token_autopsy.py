"""
Xenolexicon Token Autopsy Module

Extracts the "logit shadow" — the full probability neighborhood of what the
model *almost said* at each token position — and uses it to classify whether
a captured specimen represents genuine structured novelty or a false positive.

The autopsy answers: "When the model said X, what else was it thinking?"

Classification taxonomy:
  - TRUE_ARCANUM:  Concept clouds are coherent, internally consistent, and
                   don't decompose into known mundane concept clusters.
  - COLLISION:     Two unrelated mundane concepts smashed together by steering.
                   High distance, zero intellectual content.
  - ECHO:          Novel-looking output that decomposes into paraphrasing of
                   known concepts in unusual vocabulary.
  - CHIMERA:       Partially novel — some token positions show genuine novelty
                   while others are mundane. The novel fragment may be extractable.
  - UNCLASSIFIABLE: Insufficient signal to make a determination.

Usage:
    autopsy = TokenAutopsy(top_k=25)

    # During specimen capture (replaces normal generation):
    shadow = autopsy.capture_logit_shadow(model, genome, prompt, max_new_tokens=128)

    # Post-capture analysis:
    cloud = autopsy.build_concept_cloud(shadow, model)
    classification = autopsy.classify_specimen(cloud)
"""

import math
import torch
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple
from collections import Counter

from .tii_engine import get_steering_hook, TII_GENERATION_FAILED
from .seti_logger import slog


# ── Data Structures ──────────────────────────────────────────────────

@dataclass
class TokenShadow:
    """The logit shadow at a single token position."""
    position: int
    chosen_token_id: int
    chosen_token_str: str
    chosen_probability: float
    # Top-k alternatives: list of (token_id, token_str, probability)
    alternatives: List[Tuple[int, str, float]] = field(default_factory=list)


@dataclass
class LogitShadow:
    """Complete logit shadow for an entire generated sequence."""
    prompt_text: str
    generated_text: str
    token_shadows: List[TokenShadow] = field(default_factory=list)
    # Metadata
    layer: int = 0
    genome_norm: float = 0.0
    total_tokens: int = 0

    def to_dict(self) -> dict:
        """Serialize to JSON-safe dict."""
        return {
            "prompt_text": self.prompt_text,
            "generated_text": self.generated_text,
            "layer": self.layer,
            "genome_norm": self.genome_norm,
            "total_tokens": self.total_tokens,
            "token_shadows": [
                {
                    "pos": ts.position,
                    "chosen": ts.chosen_token_str,
                    "chosen_p": round(ts.chosen_probability, 6),
                    "alternatives": [
                        {"token": t_str, "p": round(p, 6)}
                        for _, t_str, p in ts.alternatives
                    ],
                }
                for ts in self.token_shadows
            ],
        }


@dataclass
class ConceptCluster:
    """A semantic cluster of tokens that co-occur in the logit shadow."""
    label: str                          # Human-readable cluster label
    tokens: List[str]                   # Tokens in this cluster
    total_probability_mass: float       # Sum of probabilities across positions
    positions: List[int]                # Which token positions this cluster appears in
    is_mundane: bool = False            # Flagged as a known/boring concept domain


@dataclass
class ConceptCloud:
    """Full concept cloud analysis for a specimen."""
    clusters: List[ConceptCluster] = field(default_factory=list)
    dominant_domains: List[str] = field(default_factory=list)
    novelty_coherence: float = 0.0      # How coherent are the novel clusters?
    mundane_fraction: float = 0.0       # What fraction of probability mass is mundane?
    cross_domain_collisions: int = 0    # How many positions have competing domains?
    summary: str = ""                   # Human-readable summary

    def to_dict(self) -> dict:
        return {
            "clusters": [asdict(c) for c in self.clusters],
            "dominant_domains": self.dominant_domains,
            "novelty_coherence": round(self.novelty_coherence, 4),
            "mundane_fraction": round(self.mundane_fraction, 4),
            "cross_domain_collisions": self.cross_domain_collisions,
            "summary": self.summary,
        }


# ── Discard Classification ───────────────────────────────────────────

DISCARD_CATEGORIES = {
    "TRUE_ARCANUM": "Genuine structured novelty — concept clouds are coherent and non-mundane",
    "COLLISION": "Two unrelated mundane concepts smashed together by steering",
    "ECHO": "Known concept paraphrased in unusual vocabulary",
    "CHIMERA": "Partially novel — extractable novel fragment mixed with mundane",
    "UNCLASSIFIABLE": "Insufficient signal for determination",
}


@dataclass
class SpecimenClassification:
    """Classification result from the token autopsy."""
    category: str                       # One of DISCARD_CATEGORIES keys
    confidence: float                   # 0.0 to 1.0
    discard_reason: str = ""            # Why it was classified this way
    novel_positions: List[int] = field(default_factory=list)  # Positions with genuine novelty
    mundane_positions: List[int] = field(default_factory=list)  # Positions that decompose to boring
    recommendation: str = ""            # "KEEP", "DISCARD", "EXTRACT_FRAGMENT"

    def to_dict(self) -> dict:
        return asdict(self)


# ── Mundane Domain Lexicons ──────────────────────────────────────────
# These token sets flag concept clusters as "known/boring" domains.
# If the top-k alternatives at a position are dominated by one of these
# sets, that position is mundane regardless of the chosen token.

MUNDANE_DOMAINS = {
    "conversational": {
        "hello", "hi", "hey", "please", "thank", "thanks", "sorry",
        "welcome", "yes", "no", "okay", "sure", "right", "well",
        "actually", "basically", "honestly", "literally", "really",
        "great", "good", "nice", "fine", "cool", "awesome",
        "help", "question", "answer", "explain", "understand",
        "think", "believe", "feel", "know", "mean", "say",
    },
    "web_culture": {
        "click", "subscribe", "like", "share", "comment", "post",
        "link", "page", "site", "website", "blog", "forum",
        "user", "profile", "account", "login", "password",
        "twitter", "reddit", "youtube", "instagram", "tiktok",
        "meme", "viral", "trending", "content", "creator",
    },
    "gender_social": {
        "women", "woman", "men", "man", "female", "male",
        "girl", "boy", "she", "he", "her", "his", "him",
        "husband", "wife", "boyfriend", "girlfriend", "dating",
        "attractive", "beauty", "beautiful", "handsome", "sexy",
        "body", "figure", "curves", "hourglass", "slim", "fit",
        "relationship", "marriage", "divorce", "single",
        "alpha", "beta", "sigma", "masculine", "feminine",
        "pill", "manosphere", "incel",
    },
    "commercial": {
        "buy", "sell", "price", "cost", "cheap", "expensive",
        "product", "brand", "review", "rating", "star", "best",
        "deal", "offer", "discount", "sale", "free", "premium",
        "amazon", "walmart", "ebay", "shop", "store", "order",
    },
    "formatting_meta": {
        "list", "bullet", "number", "heading", "title", "section",
        "paragraph", "sentence", "word", "letter", "character",
        "format", "style", "bold", "italic", "font", "size",
        "table", "column", "row", "cell", "header", "footer",
        "note", "reference", "citation", "source", "link",
    },
}

# Domains that are EXPECTED in our math/physics provocation context
# (not mundane just because they appear — only mundane if they're
# the ONLY thing in the shadow with no novel structure)
EXPECTED_DOMAINS = {
    "mathematics": {
        "theorem", "proof", "conjecture", "lemma", "corollary",
        "equation", "formula", "function", "variable", "constant",
        "set", "group", "ring", "field", "space", "manifold",
        "topology", "geometry", "algebra", "analysis", "calculus",
        "dimension", "vector", "matrix", "tensor", "scalar",
        "eigenvalue", "eigenvector", "spectrum", "operator",
        "infinite", "finite", "continuous", "discrete", "convergence",
        "integral", "derivative", "differential", "gradient",
        "metric", "distance", "norm", "inner", "product", "dual",
        "homomorphism", "isomorphism", "morphism", "functor",
        "category", "object", "arrow", "composition",
    },
    "physics": {
        "energy", "force", "momentum", "mass", "velocity",
        "acceleration", "gravity", "quantum", "particle", "wave",
        "field", "potential", "lagrangian", "hamiltonian",
        "symmetry", "conservation", "invariant", "gauge",
        "spacetime", "curvature", "geodesic", "metric",
        "entropy", "temperature", "thermodynamic", "statistical",
        "photon", "electron", "boson", "fermion", "spin",
    },
}


# ── The Token Autopsy Engine ─────────────────────────────────────────

class TokenAutopsy:
    """
    Extracts and analyzes the logit shadow of a steered generation.

    The logit shadow is the full top-k probability distribution at each
    token position — revealing what the model "almost said" alongside
    what it actually output.
    """

    def __init__(self, top_k: int = 25):
        """
        Args:
            top_k: Number of alternative tokens to capture at each position.
                   25 is a good balance of coverage vs. storage.
        """
        self.top_k = top_k

    def capture_logit_shadow(
        self,
        model,
        genome,
        prompt: str,
        max_new_tokens: int = 128,
    ) -> Optional[LogitShadow]:
        """
        Run steered generation token-by-token, capturing the full top-k
        logit distribution at each step.

        This replaces the normal model.generate() call during specimen
        capture. It's slower (no KV-cache batching) but gives us the
        complete probability neighborhood at every position.

        Args:
            model: TransformerLens HookedTransformer
            genome: SteeringGenome with layer_index, vector, position_ratio
            prompt: The provocation prompt text
            max_new_tokens: Maximum tokens to generate

        Returns:
            LogitShadow with complete token-level data, or None on failure
        """
        layer = genome.layer_index
        vector = genome.vector
        pos_ratio = getattr(genome, 'position_ratio', 1.0)
        hook_name = f"blocks.{layer}.hook_resid_pre"

        try:
            input_tokens = model.to_tokens(prompt)
            current_tokens = input_tokens.clone()
            prompt_len = input_tokens.shape[1]

            token_shadows = []
            generated_ids = []

            for step in range(max_new_tokens):
                # Forward pass with steering, get logits
                with model.hooks(fwd_hooks=[(hook_name,
                        get_steering_hook(vector, position_ratio=pos_ratio))]):
                    with torch.no_grad():
                        logits = model(current_tokens)

                # Get logits for the last position (next token prediction)
                next_logits = logits[0, -1, :].float()

                # Softmax to get probabilities
                probs = torch.softmax(next_logits, dim=-1)

                # Top-k extraction
                top_probs, top_ids = torch.topk(probs, min(self.top_k, probs.shape[0]))

                # Sample or argmax the next token (use argmax for reproducibility)
                chosen_id = top_ids[0].item()
                chosen_prob = top_probs[0].item()
                chosen_str = model.to_string(torch.tensor([[chosen_id]]))[0] if hasattr(model, 'to_string') else str(chosen_id)

                # Clean up token strings
                try:
                    chosen_str = model.tokenizer.decode([chosen_id])
                except Exception:
                    chosen_str = f"[{chosen_id}]"

                # Build alternatives list
                alternatives = []
                for i in range(min(self.top_k, len(top_ids))):
                    tid = top_ids[i].item()
                    tp = top_probs[i].item()
                    try:
                        t_str = model.tokenizer.decode([tid])
                    except Exception:
                        t_str = f"[{tid}]"
                    alternatives.append((tid, t_str, tp))

                token_shadows.append(TokenShadow(
                    position=step,
                    chosen_token_id=chosen_id,
                    chosen_token_str=chosen_str,
                    chosen_probability=chosen_prob,
                    alternatives=alternatives,
                ))

                generated_ids.append(chosen_id)

                # Check for EOS
                if hasattr(model, 'tokenizer') and chosen_id == model.tokenizer.eos_token_id:
                    break

                # Append chosen token and continue
                next_token = torch.tensor([[chosen_id]], device=current_tokens.device)
                current_tokens = torch.cat([current_tokens, next_token], dim=1)

            # Reconstruct generated text
            try:
                generated_text = model.tokenizer.decode(generated_ids, skip_special_tokens=True)
            except Exception:
                generated_text = "".join(ts.chosen_token_str for ts in token_shadows)

            shadow = LogitShadow(
                prompt_text=prompt,
                generated_text=generated_text,
                token_shadows=token_shadows,
                layer=layer,
                genome_norm=vector.norm().item(),
                total_tokens=len(token_shadows),
            )

            slog.trace(f"Logit shadow captured: {len(token_shadows)} tokens, "
                       f"layer={layer}")

            return shadow

        except torch.cuda.OutOfMemoryError:
            slog.warning("CUDA OOM during logit shadow capture")
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            return None

        except Exception as e:
            slog.exception(f"Logit shadow capture failed: {e}")
            return None

    def build_concept_cloud(self, shadow: LogitShadow, model=None) -> ConceptCloud:
        """
        Analyze a logit shadow to build the concept cloud — a map of what
        semantic domains the model was drawing from at each position.

        This is the core analysis: for each token position, we look at the
        top-k alternatives and classify them into semantic clusters. Then
        we aggregate across all positions to see the overall "concept
        neighborhood" of the specimen.

        Args:
            shadow: LogitShadow from capture_logit_shadow
            model: Optional model reference (unused currently, reserved for
                   embedding-based clustering in future)

        Returns:
            ConceptCloud with cluster analysis and classification signals
        """
        if not shadow.token_shadows:
            return ConceptCloud(summary="Empty shadow — no tokens to analyze")

        # Step 1: For each position, classify the top-k tokens into domains
        position_domains: List[Dict[str, float]] = []  # pos → {domain: probability_mass}
        position_mundane_mass: List[float] = []
        position_novel_mass: List[float] = []

        all_mundane_tokens = set()
        for domain_tokens in MUNDANE_DOMAINS.values():
            all_mundane_tokens.update(domain_tokens)

        all_expected_tokens = set()
        for domain_tokens in EXPECTED_DOMAINS.values():
            all_expected_tokens.update(domain_tokens)

        for ts in shadow.token_shadows:
            domains: Dict[str, float] = {}
            mundane_mass = 0.0
            total_mass = 0.0

            for _tid, t_str, prob in ts.alternatives:
                t_lower = t_str.strip().lower()
                total_mass += prob

                # Check against mundane domains
                matched_mundane = False
                for domain_name, domain_tokens in MUNDANE_DOMAINS.items():
                    if t_lower in domain_tokens:
                        domains[domain_name] = domains.get(domain_name, 0.0) + prob
                        mundane_mass += prob
                        matched_mundane = True
                        break

                if not matched_mundane:
                    # Check expected domains (not mundane, but known)
                    for domain_name, domain_tokens in EXPECTED_DOMAINS.items():
                        if t_lower in domain_tokens:
                            domains[f"expected:{domain_name}"] = \
                                domains.get(f"expected:{domain_name}", 0.0) + prob
                            break
                    else:
                        # Truly uncategorized — potentially novel
                        domains["uncategorized"] = \
                            domains.get("uncategorized", 0.0) + prob

            position_domains.append(domains)
            position_mundane_mass.append(mundane_mass / max(total_mass, 1e-10))
            position_novel_mass.append(1.0 - mundane_mass / max(total_mass, 1e-10))

        # Step 2: Aggregate into clusters
        domain_totals: Dict[str, float] = {}
        domain_positions: Dict[str, List[int]] = {}
        domain_tokens_seen: Dict[str, set] = {}

        for pos, domains in enumerate(position_domains):
            for domain_name, mass in domains.items():
                domain_totals[domain_name] = domain_totals.get(domain_name, 0.0) + mass
                if domain_name not in domain_positions:
                    domain_positions[domain_name] = []
                domain_positions[domain_name].append(pos)

                # Track which tokens appeared in this domain
                if domain_name not in domain_tokens_seen:
                    domain_tokens_seen[domain_name] = set()
                for _tid, t_str, _p in shadow.token_shadows[pos].alternatives:
                    t_lower = t_str.strip().lower()
                    if domain_name in MUNDANE_DOMAINS:
                        if t_lower in MUNDANE_DOMAINS[domain_name]:
                            domain_tokens_seen[domain_name].add(t_lower)

        clusters = []
        for domain_name, total_mass in sorted(domain_totals.items(),
                                                key=lambda x: -x[1]):
            is_mundane = domain_name in MUNDANE_DOMAINS
            clusters.append(ConceptCluster(
                label=domain_name,
                tokens=sorted(domain_tokens_seen.get(domain_name, set())),
                total_probability_mass=total_mass,
                positions=domain_positions.get(domain_name, []),
                is_mundane=is_mundane,
            ))

        # Step 3: Compute summary statistics
        total_mundane = sum(c.total_probability_mass for c in clusters if c.is_mundane)
        total_all = sum(c.total_probability_mass for c in clusters)
        mundane_fraction = total_mundane / max(total_all, 1e-10)

        # Count positions where multiple mundane domains compete
        collisions = 0
        for domains in position_domains:
            mundane_domains_present = [d for d in domains if d in MUNDANE_DOMAINS]
            if len(mundane_domains_present) >= 2:
                collisions += 1

        # Identify dominant domains (>10% of total mass)
        dominant = [c.label for c in clusters
                    if c.total_probability_mass / max(total_all, 1e-10) > 0.10]

        # Novelty coherence: how consistent are the uncategorized tokens?
        # (Simple heuristic: if uncategorized mass is high AND concentrated
        # in specific positions rather than spread thin, that's more coherent)
        uncat_positions = domain_positions.get("uncategorized", [])
        if uncat_positions and len(shadow.token_shadows) > 0:
            uncat_concentration = len(set(uncat_positions)) / len(shadow.token_shadows)
            uncat_mass = domain_totals.get("uncategorized", 0.0)
            novelty_coherence = min(1.0, uncat_mass * (1.0 - uncat_concentration + 0.1))
        else:
            novelty_coherence = 0.0

        # Build human-readable summary
        summary_parts = []
        if mundane_fraction > 0.5:
            top_mundane = [c.label for c in clusters
                          if c.is_mundane and c.total_probability_mass > 0.1]
            summary_parts.append(
                f"HIGH MUNDANE ({mundane_fraction:.0%}): "
                f"dominated by {', '.join(top_mundane)}"
            )
        if collisions > len(shadow.token_shadows) * 0.3:
            summary_parts.append(
                f"COLLISION PATTERN: {collisions}/{len(shadow.token_shadows)} "
                f"positions show competing mundane domains"
            )
        if novelty_coherence > 0.3:
            summary_parts.append(
                f"NOVEL SIGNAL: coherence={novelty_coherence:.2f}, "
                f"uncategorized mass in {len(set(uncat_positions))} positions"
            )

        cloud = ConceptCloud(
            clusters=clusters,
            dominant_domains=dominant,
            novelty_coherence=novelty_coherence,
            mundane_fraction=mundane_fraction,
            cross_domain_collisions=collisions,
            summary=" | ".join(summary_parts) if summary_parts else "Analysis complete",
        )

        return cloud

    def classify_specimen(self, cloud: ConceptCloud) -> SpecimenClassification:
        """
        Classify a specimen based on its concept cloud analysis.

        This is the "should we keep it?" decision. The classification
        determines whether the specimen enters the museum, gets discarded
        with a reason, or gets flagged for fragment extraction.

        Args:
            cloud: ConceptCloud from build_concept_cloud

        Returns:
            SpecimenClassification with category, confidence, and recommendation
        """
        mundane = cloud.mundane_fraction
        coherence = cloud.novelty_coherence
        collisions = cloud.cross_domain_collisions
        n_clusters = len(cloud.clusters)

        # Decision tree (deliberately simple and interpretable)

        # Case 1: COLLISION — high mundane, multiple competing domains
        if mundane > 0.5 and collisions > 3:
            mundane_domains = [c.label for c in cloud.clusters
                              if c.is_mundane and c.total_probability_mass > 0.05]
            return SpecimenClassification(
                category="COLLISION",
                confidence=min(0.95, mundane + 0.1 * collisions / max(n_clusters, 1)),
                discard_reason=(
                    f"Mundane domain collision: {', '.join(mundane_domains[:3])}. "
                    f"{mundane:.0%} of probability mass is from known domains, "
                    f"with {collisions} cross-domain collision positions."
                ),
                mundane_positions=[
                    i for i, d in enumerate(
                        [sum(1 for dn in dom if dn in MUNDANE_DOMAINS)
                         for dom in [{}]]  # placeholder
                    )
                ],
                recommendation="DISCARD",
            )

        # Case 2: ECHO — low novelty coherence, mostly expected domains
        expected_mass = sum(
            c.total_probability_mass for c in cloud.clusters
            if c.label.startswith("expected:")
        )
        total_mass = sum(c.total_probability_mass for c in cloud.clusters)
        expected_fraction = expected_mass / max(total_mass, 1e-10)

        if expected_fraction > 0.6 and coherence < 0.15:
            return SpecimenClassification(
                category="ECHO",
                confidence=min(0.9, expected_fraction),
                discard_reason=(
                    f"Output decomposes into known {', '.join(cloud.dominant_domains[:3])} "
                    f"concepts. {expected_fraction:.0%} expected domain mass, "
                    f"novelty coherence only {coherence:.2f}."
                ),
                recommendation="DISCARD",
            )

        # Case 3: CHIMERA — mixed signal, some positions novel, others mundane
        if mundane > 0.25 and coherence > 0.15:
            return SpecimenClassification(
                category="CHIMERA",
                confidence=0.6,
                discard_reason=(
                    f"Mixed signal: {mundane:.0%} mundane, "
                    f"but novelty coherence={coherence:.2f} suggests "
                    f"extractable novel fragment."
                ),
                novel_positions=[
                    i for i in range(len(cloud.clusters))
                    if not cloud.clusters[i].is_mundane
                ] if cloud.clusters else [],
                recommendation="EXTRACT_FRAGMENT",
            )

        # Case 4: TRUE_ARCANUM — low mundane, meaningful novelty coherence
        if mundane < 0.25 and coherence > 0.1:
            return SpecimenClassification(
                category="TRUE_ARCANUM",
                confidence=min(0.9, (1.0 - mundane) * coherence * 3),
                discard_reason="",
                recommendation="KEEP",
            )

        # Case 5: UNCLASSIFIABLE — not enough signal either way
        return SpecimenClassification(
            category="UNCLASSIFIABLE",
            confidence=0.3,
            discard_reason=(
                f"Ambiguous: mundane={mundane:.0%}, coherence={coherence:.2f}, "
                f"collisions={collisions}. Needs manual review."
            ),
            recommendation="KEEP",  # Err on the side of keeping
        )

    def generate_autopsy_report(
        self,
        shadow: LogitShadow,
        cloud: ConceptCloud,
        classification: SpecimenClassification,
    ) -> str:
        """
        Generate a human-readable autopsy report for a specimen.
        This gets saved alongside the specimen for later review.
        """
        lines = []
        lines.append("=" * 70)
        lines.append("TOKEN AUTOPSY REPORT")
        lines.append("=" * 70)
        lines.append("")

        # Classification
        lines.append(f"CLASSIFICATION: {classification.category}")
        lines.append(f"CONFIDENCE:     {classification.confidence:.0%}")
        lines.append(f"RECOMMENDATION: {classification.recommendation}")
        if classification.discard_reason:
            lines.append(f"REASON:         {classification.discard_reason}")
        lines.append("")

        # Summary stats
        lines.append(f"Total tokens analyzed: {shadow.total_tokens}")
        lines.append(f"Layer: {shadow.layer}")
        lines.append(f"Mundane fraction: {cloud.mundane_fraction:.0%}")
        lines.append(f"Novelty coherence: {cloud.novelty_coherence:.2f}")
        lines.append(f"Cross-domain collisions: {cloud.cross_domain_collisions}")
        lines.append(f"Dominant domains: {', '.join(cloud.dominant_domains)}")
        lines.append("")

        # Generated text
        lines.append("GENERATED TEXT:")
        lines.append("-" * 40)
        lines.append(shadow.generated_text[:500])
        lines.append("")

        # Top concept clusters
        lines.append("CONCEPT CLUSTERS (by probability mass):")
        lines.append("-" * 40)
        for i, cluster in enumerate(cloud.clusters[:8]):
            mundane_tag = " [MUNDANE]" if cluster.is_mundane else ""
            lines.append(
                f"  {i + 1}. {cluster.label}{mundane_tag}: "
                f"mass={cluster.total_probability_mass:.3f}, "
                f"positions={len(cluster.positions)}"
            )
            if cluster.tokens:
                lines.append(f"     tokens: {', '.join(cluster.tokens[:10])}")
        lines.append("")

        # Token-by-token detail (first 20 positions)
        lines.append("TOKEN DETAIL (first 20 positions):")
        lines.append("-" * 40)
        for ts in shadow.token_shadows[:20]:
            chosen = ts.chosen_token_str.strip()
            top_alts = [f"{t_str.strip()}({p:.2f})"
                        for _, t_str, p in ts.alternatives[1:6]]
            lines.append(
                f"  [{ts.position:>3}] '{chosen}' (p={ts.chosen_probability:.3f}) "
                f"| runners: {', '.join(top_alts)}"
            )
        if len(shadow.token_shadows) > 20:
            lines.append(f"  ... ({len(shadow.token_shadows) - 20} more positions)")
        lines.append("")

        # Cloud summary
        lines.append(f"ANALYSIS: {cloud.summary}")
        lines.append("=" * 70)

        return "\n".join(lines)
