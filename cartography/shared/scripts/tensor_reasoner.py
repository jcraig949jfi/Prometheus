"""
Tensor Reasoner — LLM-powered reasoning about cross-domain intersections.
=========================================================================
Connects the GPU dissection tensor (86K objects x 145 dims, 11 strategy
groups) to math-capable LLMs for reasoning about WHY two objects from
different domains are close in signature space.

Architecture:
  1. IntersectionFormatter — builds structured prompts from tensor results
  2. TensorReasoner — two-tier inference (local ollama -> cloud NemoClaw)
  3. Integration — loads MAP-Elites/GA results and runs reasoning pipeline

Two-tier model hierarchy:
  Local:  ollama at localhost:11434 (Qwen3-8B / DeepSeek-R1-Distill-7B)
  Cloud:  NVIDIA NemoClaw API (Qwen 3.5 397B) — OpenAI-compatible format

Both tiers are optional. If neither is available, prompts are saved for
manual review.

Usage:
    from tensor_reasoner import TensorReasoner, IntersectionFormatter
    reasoner = TensorReasoner()
    result = reasoner.reason_about_intersection(obj_a, obj_b, 0.42, ["mod_p", "padic"])

    # Or from saved intersection files:
    report = reasoner.analyze_explorer_results("path/to/results.json")
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import ssl
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# keys.py does not have an NVIDIA entry — NVIDIA_API_KEY is loaded from env
# vars directly (matching the skopos.py pattern).
try:
    from keys import get_key
except ImportError:
    def get_key(name):
        raise ValueError(f"keys.py not found; cannot load key '{name}'")


# ============================================================
# Constants
# ============================================================

OLLAMA_BASE = "http://localhost:11434"
NVIDIA_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "qwen/qwen3.5-397b-a17b"
LOCAL_MODELS = ["qwen3:8b", "deepseek-r1:7b"]

# Strategy group metadata — human-readable descriptions for the prompt
STRATEGY_GROUP_INFO = {
    "complex":   "Complex plane evaluation (unit circle magnitudes of polynomials)",
    "mod_p":     "Modular arithmetic fingerprints (residue class coverage mod small primes)",
    "spectral":  "Spectral decomposition (FFT power spectrum of coefficient sequences)",
    "padic":     "p-adic valuations (prime factorization depth of key integers)",
    "symmetry":  "Symmetry group encoding (Sato-Tate group classification)",
    "galois":    "Galois group hash (transitive group degree and index)",
    "zeta":      "Zeta-like arithmetic density (divisibility fractions by small primes)",
    "disc_cond": "Discriminant/conductor signature (log magnitude, sign, divisor count)",
    "operadic":  "Operadic structure (formula type and module encoding)",
    "entropy":   "Information-theoretic (Shannon entropy, compression features)",
    "attractor": "Attractor dynamics (Lyapunov exponent, autocorrelation of sequences)",
}

# Known cross-domain bridge context (brief, for prompt injection)
KNOWN_BRIDGES = {
    ("EC", "NF"): "Elliptic curves over Q have associated number fields via their endomorphism rings and mod-p representations. Conductor and discriminant share factorization structure.",
    ("EC", "knot"): "Knot determinants and EC conductors can share p-adic factorization patterns. Alexander polynomials evaluated on roots of unity resemble L-function special values.",
    ("EC", "OEIS"): "EC a_p traces appear in many OEIS sequences (e.g., A006571 for 11a1). Rank distributions and torsion orders have known OEIS entries.",
    ("EC", "genus2"): "Genus-2 Jacobians factor into EC products in special cases. Conductors share prime factorization when genus-2 is isogenous to a product of ECs.",
    ("EC", "fungrim"): "Fungrim contains identities for L-functions, modular forms, and special values that relate to EC invariants via modularity theorem.",
    ("knot", "NF"): "Knot invariants (Alexander polynomial, determinant) can encode number-theoretic information. Knot groups have representations into GL(n, Z/p).",
    ("knot", "OEIS"): "Knot determinants, crossing numbers, and polynomial evaluations at roots of unity are catalogued in OEIS.",
    ("knot", "genus2"): "Seifert surfaces of knots can have genus 2. Knot polynomials evaluated at special points connect to Jacobian invariants.",
    ("NF", "OEIS"): "Class numbers, discriminants, regulators of number fields appear in OEIS. Dedekind zeta special values connect to OEIS sequences.",
    ("NF", "genus2"): "Genus-2 curves have associated number fields via their endomorphism algebras. Conductor factorization patterns may overlap.",
    ("NF", "fungrim"): "Fungrim contains identities for Dedekind zeta functions, class number formulas, and Dirichlet L-functions relevant to NFs.",
    ("OEIS", "genus2"): "Genus-2 conductor sequences, point counts over finite fields, and Euler factor coefficients may appear in OEIS.",
    ("OEIS", "fungrim"): "Fungrim formulas define generating functions and recurrences that produce OEIS sequences.",
    ("genus2", "fungrim"): "Fungrim contains modular form identities relevant to genus-2 Siegel modular forms and paramodular forms.",
}

# Verdicts
VERDICTS = ["KNOWN_THEOREM", "NOVEL_BRIDGE", "ARTIFACT", "UNCLEAR"]

# Confidence threshold for local->cloud escalation
LOCAL_CONFIDENCE_THRESHOLD = 0.7


# ============================================================
# IntersectionFormatter
# ============================================================

class IntersectionFormatter:
    """Formats intersection data into structured prompts for LLM reasoning.

    Takes a pair of mathematical objects from the dissection tensor and
    builds a prompt with all relevant context for classification.
    """

    def __init__(self, dissection_tensor=None):
        """
        Args:
            dissection_tensor: optional DissectionTensor instance for
                looking up raw object data and computing per-group distances.
                If None, works from pre-extracted dicts.
        """
        self.dt = dissection_tensor

    def _get_object(self, obj_id: str) -> Optional[dict]:
        """Look up a MathObject in the tensor by ID."""
        if self.dt is None:
            return None
        for obj in self.dt.objects:
            if obj.obj_id == obj_id:
                return {
                    "obj_id": obj.obj_id,
                    "domain": obj.domain,
                    "label": obj.label,
                    "signatures": {k: v.tolist() if hasattr(v, 'tolist') else v
                                   for k, v in obj.signatures.items()},
                    "raw": obj.raw,
                }
        return None

    def _per_group_distances(self, obj_a_id: str, obj_b_id: str) -> dict:
        """Compute distance between two objects per strategy group.

        Returns {group_name: distance} where distance is NaN if the
        group has no shared dimensions.
        """
        if self.dt is None or self.dt.tensor is None:
            return {}

        # Find indices
        idx_a = idx_b = None
        for i, label in enumerate(self.dt.labels):
            if label == obj_a_id:
                idx_a = i
            elif label == obj_b_id:
                idx_b = i
            if idx_a is not None and idx_b is not None:
                break

        if idx_a is None or idx_b is None:
            return {}

        import torch
        distances = {}
        for group_name, strat_list in self.dt.STRATEGY_GROUPS.items():
            dims = []
            for s in strat_list:
                if s in self.dt._strategy_slices:
                    start, end = self.dt._strategy_slices[s]
                    dims.extend(range(start, end))
            if not dims:
                continue
            cols = torch.tensor(dims, device=self.dt.tensor.device)
            va = self.dt.tensor[idx_a, cols]
            vb = self.dt.tensor[idx_b, cols]
            ma = self.dt.mask[idx_a, cols]
            mb = self.dt.mask[idx_b, cols]
            shared = ma & mb
            n_shared = shared.float().sum().item()
            if n_shared < 1:
                distances[group_name] = float('nan')
            else:
                diff = ((va - vb) ** 2) * shared.float()
                distances[group_name] = float((diff.sum() / n_shared).sqrt().item())
        return distances

    def _get_bridge_context(self, domain_a: str, domain_b: str) -> str:
        """Get known bridge context for a domain pair."""
        key = tuple(sorted([domain_a, domain_b]))
        return KNOWN_BRIDGES.get(key, "No specific cross-domain bridge context available.")

    def format_prompt(self, obj_a: dict, obj_b: dict, distance: float,
                      contributing_groups: list[str] = None,
                      per_group_dists: dict = None) -> str:
        """Build the full reasoning prompt.

        Args:
            obj_a: dict with keys {obj_id, domain, label, raw, signatures}
            obj_b: same format
            distance: overall Euclidean distance in signature space
            contributing_groups: top strategy groups driving proximity
            per_group_dists: {group_name: distance} for all groups

        Returns:
            Formatted prompt string.
        """
        # Build per-group distance table if we have the data
        group_table = ""
        if per_group_dists:
            sorted_groups = sorted(
                [(g, d) for g, d in per_group_dists.items() if np.isfinite(d)],
                key=lambda x: x[1]
            )
            lines = []
            for g, d in sorted_groups:
                desc = STRATEGY_GROUP_INFO.get(g, g)
                lines.append(f"  {g:12s}  d={d:.4f}  ({desc})")
            group_table = "\n".join(lines)

        # Top contributing groups
        if contributing_groups:
            top_groups_str = ", ".join(contributing_groups[:3])
        elif per_group_dists:
            finite = [(g, d) for g, d in per_group_dists.items() if np.isfinite(d)]
            finite.sort(key=lambda x: x[1])
            top_groups_str = ", ".join(g for g, _ in finite[:3])
        else:
            top_groups_str = "unknown"

        # Bridge context
        bridge_ctx = self._get_bridge_context(
            obj_a.get("domain", ""), obj_b.get("domain", ""))

        # Format raw properties
        def fmt_raw(raw: dict) -> str:
            if not raw:
                return "  (no raw properties)"
            lines = []
            for k, v in raw.items():
                lines.append(f"  {k}: {v}")
            return "\n".join(lines)

        # Format key signatures (only non-NaN, abbreviated)
        def fmt_sigs(sigs: dict) -> str:
            if not sigs:
                return "  (no signatures)"
            lines = []
            for k, v in sigs.items():
                if isinstance(v, list):
                    if all(x != x for x in v):  # all NaN
                        continue
                    # Abbreviate: first 4 values
                    vals = [f"{x:.3f}" for x in v[:4] if x == x]
                    if len(v) > 4:
                        vals.append("...")
                    lines.append(f"  {k}: [{', '.join(vals)}]")
                elif isinstance(v, (int, float)):
                    if v == v:  # not NaN
                        lines.append(f"  {k}: {v:.4f}")
            return "\n".join(lines) if lines else "  (all signatures NaN)"

        prompt = f"""You are a mathematician analyzing a potential cross-domain bridge found by a dissection tensor.

Two mathematical objects from different domains are geometrically close in a 145-dimensional signature space. Your task is to determine whether this proximity reflects a genuine mathematical relationship or is an artifact of the encoding.

## Object A
- Domain: {obj_a.get('domain', 'unknown')}
- Label: {obj_a.get('label', 'unknown')}
- ID: {obj_a.get('obj_id', 'unknown')}
- Properties:
{fmt_raw(obj_a.get('raw', {}))}
- Signature values:
{fmt_sigs(obj_a.get('signatures', {}))}

## Object B
- Domain: {obj_b.get('domain', 'unknown')}
- Label: {obj_b.get('label', 'unknown')}
- ID: {obj_b.get('obj_id', 'unknown')}
- Properties:
{fmt_raw(obj_b.get('raw', {}))}
- Signature values:
{fmt_sigs(obj_b.get('signatures', {}))}

## Distance
- Overall distance in signature space: {distance:.4f}
- Top contributing strategy groups: {top_groups_str}
{f"- Per-group distances:{chr(10)}{group_table}" if group_table else ""}

## Known cross-domain context
{bridge_ctx}

## Task
Classify this intersection as one of:
1. **KNOWN_THEOREM** — The proximity is explained by a known mathematical theorem or well-established relationship. Name the theorem or connection.
2. **NOVEL_BRIDGE** — The proximity suggests a genuine but previously unrecognized mathematical connection. Explain what makes it interesting and what further tests would confirm it.
3. **ARTIFACT** — The proximity is a consequence of the encoding method (e.g., both objects happen to have similar polynomial degree, similar conductor magnitude, or both have mostly-NaN signatures that default to similar fill values). Explain the artifact.
4. **UNCLEAR** — Insufficient information to classify. State what additional data would resolve it.

Respond in JSON format:
{{
  "verdict": "KNOWN_THEOREM|NOVEL_BRIDGE|ARTIFACT|UNCLEAR",
  "confidence": 0.0-1.0,
  "explanation": "Brief explanation of the mathematical reasoning",
  "mathematical_basis": "Specific theorem, conjecture, or structural argument",
  "further_tests": ["list of specific tests that could validate or falsify this bridge"]
}}"""
        return prompt

    def format_from_ids(self, obj_a_id: str, obj_b_id: str,
                        distance: float) -> str:
        """Format prompt from object IDs, looking up data from the tensor."""
        obj_a = self._get_object(obj_a_id) or {"obj_id": obj_a_id, "domain": obj_a_id.split("_")[0], "label": obj_a_id}
        obj_b = self._get_object(obj_b_id) or {"obj_id": obj_b_id, "domain": obj_b_id.split("_")[0], "label": obj_b_id}
        per_group = self._per_group_distances(obj_a_id, obj_b_id)
        return self.format_prompt(obj_a, obj_b, distance,
                                  per_group_dists=per_group)


# ============================================================
# TensorReasoner
# ============================================================

class TensorReasoner:
    """Two-tier LLM reasoner for cross-domain intersection classification.

    Tier 1 (local): ollama at localhost:11434
    Tier 2 (cloud): NVIDIA NemoClaw API (Qwen 3.5 397B)

    Both tiers are optional. Falls back gracefully:
      - No ollama -> skip to cloud
      - No API key -> save prompts for manual review
    """

    def __init__(self, local_model: str = None,
                 cloud_model: str = NVIDIA_MODEL,
                 confidence_threshold: float = LOCAL_CONFIDENCE_THRESHOLD,
                 output_dir: Path = None):
        """
        Args:
            local_model: ollama model name (default: auto-detect from LOCAL_MODELS)
            cloud_model: NemoClaw model ID
            confidence_threshold: below this, escalate from local to cloud
            output_dir: where to save prompts/results (default: convergence/data)
        """
        self.local_model = local_model
        self.cloud_model = cloud_model
        self.confidence_threshold = confidence_threshold
        self.output_dir = output_dir or (ROOT / "cartography/convergence/data")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._ollama_available = None
        self._nvidia_key = None
        self.formatter = IntersectionFormatter()

        self.stats = {"local_calls": 0, "cloud_calls": 0,
                      "escalations": 0, "saved_prompts": 0,
                      "artifacts_filtered": 0}

    # ----------------------------------------------------------
    # Availability checks
    # ----------------------------------------------------------

    def _check_ollama(self) -> bool:
        """Check if ollama is running and has a suitable model."""
        if self._ollama_available is not None:
            return self._ollama_available
        try:
            req = urllib.request.Request(
                f"{OLLAMA_BASE}/api/tags",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            available = [m["name"] for m in data.get("models", [])]
            # Auto-detect model if not specified
            if self.local_model is None:
                for candidate in LOCAL_MODELS:
                    for avail in available:
                        if candidate.split(":")[0] in avail:
                            self.local_model = avail
                            break
                    if self.local_model:
                        break
            self._ollama_available = self.local_model is not None
            if self._ollama_available:
                print(f"  [ollama] Available, using model: {self.local_model}")
            else:
                print(f"  [ollama] Running but no suitable model found. Available: {available}")
        except Exception:
            self._ollama_available = False
            print("  [ollama] Not available (not running or unreachable)")
        return self._ollama_available

    def _get_nvidia_key(self) -> Optional[str]:
        """Get NVIDIA API key from environment."""
        if self._nvidia_key is not None:
            return self._nvidia_key if self._nvidia_key != "" else None
        key = os.environ.get("NVIDIA_API_KEY", "")
        self._nvidia_key = key
        if key:
            print(f"  [NemoClaw] API key found, model: {self.cloud_model}")
        else:
            print("  [NemoClaw] No NVIDIA_API_KEY in environment")
        return key if key else None

    # ----------------------------------------------------------
    # LLM call implementations
    # ----------------------------------------------------------

    def _call_ollama(self, prompt: str, system: str = "") -> dict:
        """Call local ollama model. Returns raw response dict."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({
            "model": self.local_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 2048},
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        elapsed = time.time() - t0

        text = data.get("message", {}).get("content", "")
        return {
            "text": text,
            "model": self.local_model,
            "provider": "ollama",
            "elapsed_s": elapsed,
        }

    def _call_nvidia(self, prompt: str, system: str = "") -> dict:
        """Call NVIDIA NemoClaw API (OpenAI-compatible format)."""
        key = self._get_nvidia_key()
        if not key:
            raise ValueError("No NVIDIA_API_KEY available")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({
            "model": self.cloud_model,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.2,
        }).encode("utf-8")

        # SSL context for NVIDIA endpoint
        ctx = ssl.create_default_context()

        req = urllib.request.Request(
            NVIDIA_ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
            },
            method="POST",
        )
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        elapsed = time.time() - t0

        choices = data.get("choices", [])
        text = ""
        if choices:
            msg = choices[0].get("message", {})
            text = msg.get("content") or msg.get("reasoning_content") or ""

        return {
            "text": text.strip(),
            "model": self.cloud_model,
            "provider": "nvidia",
            "elapsed_s": elapsed,
            "usage": data.get("usage", {}),
        }

    # ----------------------------------------------------------
    # Response parsing
    # ----------------------------------------------------------

    @staticmethod
    def _parse_response(text: str) -> dict:
        """Parse LLM response into structured result.

        Handles markdown fences, trailing text, and common LLM JSON quirks.
        """
        cleaned = text.strip()

        # Strip markdown code fences
        if "```" in cleaned:
            lines = cleaned.split("\n")
            in_fence = False
            json_lines = []
            for line in lines:
                if line.strip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    json_lines.append(line)
            if json_lines:
                cleaned = "\n".join(json_lines)

        # Find the outermost JSON object
        start = cleaned.find("{")
        if start >= 0:
            depth = 0
            for i in range(start, len(cleaned)):
                if cleaned[i] == "{":
                    depth += 1
                elif cleaned[i] == "}":
                    depth -= 1
                    if depth == 0:
                        cleaned = cleaned[start:i + 1]
                        break

        try:
            result = json.loads(cleaned)
            # Validate required fields
            if "verdict" not in result:
                result["verdict"] = "UNCLEAR"
            if result["verdict"] not in VERDICTS:
                result["verdict"] = "UNCLEAR"
            if "confidence" not in result:
                result["confidence"] = 0.5
            result["confidence"] = float(result["confidence"])
            if "explanation" not in result:
                result["explanation"] = ""
            if "mathematical_basis" not in result:
                result["mathematical_basis"] = ""
            if "further_tests" not in result:
                result["further_tests"] = []
            return result
        except (json.JSONDecodeError, ValueError):
            return {
                "verdict": "UNCLEAR",
                "confidence": 0.0,
                "explanation": f"Failed to parse LLM response: {text[:500]}",
                "mathematical_basis": "",
                "further_tests": [],
                "parse_error": True,
            }

    # ----------------------------------------------------------
    # Core reasoning method
    # ----------------------------------------------------------

    def reason_about_intersection(self, obj_a: dict, obj_b: dict,
                                  distance: float,
                                  contributing_groups: list[str] = None,
                                  per_group_dists: dict = None) -> dict:
        """Reason about a single cross-domain intersection.

        Two-tier pipeline:
          1. Try local model first
          2. Escalate to cloud if: low confidence OR verdict is NOVEL_BRIDGE
          3. If neither tier available, save prompt for manual review

        Args:
            obj_a, obj_b: dicts with {obj_id, domain, label, raw, signatures}
            distance: overall distance in signature space
            contributing_groups: top strategy groups driving proximity
            per_group_dists: {group_name: distance} per strategy group

        Returns:
            dict with {verdict, confidence, explanation, mathematical_basis,
                       further_tests, provider, model, elapsed_s}
        """
        system = ("You are an expert mathematician specializing in cross-domain "
                  "connections: number theory, algebraic geometry, knot theory, "
                  "combinatorics, and mathematical physics. You are precise, "
                  "skeptical, and evidence-based. You never speculate without "
                  "flagging uncertainty.")

        prompt = self.formatter.format_prompt(
            obj_a, obj_b, distance, contributing_groups, per_group_dists)

        # Tier 1: local ollama
        if self._check_ollama():
            try:
                raw = self._call_ollama(prompt, system)
                result = self._parse_response(raw["text"])
                result["provider"] = raw["provider"]
                result["model"] = raw["model"]
                result["elapsed_s"] = raw["elapsed_s"]
                self.stats["local_calls"] += 1

                # Escalate if low confidence or NOVEL_BRIDGE
                needs_escalation = (
                    result["confidence"] < self.confidence_threshold
                    or result["verdict"] == "NOVEL_BRIDGE"
                )
                if needs_escalation and self._get_nvidia_key():
                    self.stats["escalations"] += 1
                    local_result = result
                    try:
                        raw_cloud = self._call_nvidia(prompt, system)
                        cloud_result = self._parse_response(raw_cloud["text"])
                        cloud_result["provider"] = raw_cloud["provider"]
                        cloud_result["model"] = raw_cloud["model"]
                        cloud_result["elapsed_s"] = raw_cloud["elapsed_s"]
                        cloud_result["local_result"] = local_result
                        self.stats["cloud_calls"] += 1
                        return cloud_result
                    except Exception as e:
                        result["cloud_error"] = str(e)
                        return result

                return result
            except Exception as e:
                print(f"  [ollama] Error: {e}")
                # Fall through to cloud

        # Tier 2: cloud NemoClaw
        if self._get_nvidia_key():
            try:
                raw = self._call_nvidia(prompt, system)
                result = self._parse_response(raw["text"])
                result["provider"] = raw["provider"]
                result["model"] = raw["model"]
                result["elapsed_s"] = raw["elapsed_s"]
                self.stats["cloud_calls"] += 1
                return result
            except Exception as e:
                print(f"  [NemoClaw] Error: {e}")

        # No models available — save prompt for manual review
        return self._save_for_review(obj_a, obj_b, distance, prompt)

    def _save_for_review(self, obj_a: dict, obj_b: dict,
                         distance: float, prompt: str) -> dict:
        """Save prompt to disk when no LLM is available."""
        review_dir = self.output_dir / "review_prompts"
        review_dir.mkdir(parents=True, exist_ok=True)

        slug = f"{obj_a.get('obj_id', 'a')}___{obj_b.get('obj_id', 'b')}"
        # Sanitize for filesystem
        slug = slug.replace("/", "_").replace("\\", "_")[:120]
        path = review_dir / f"{slug}.txt"
        path.write_text(prompt, encoding="utf-8")
        self.stats["saved_prompts"] += 1

        return {
            "verdict": "UNCLEAR",
            "confidence": 0.0,
            "explanation": "No LLM available. Prompt saved for manual review.",
            "mathematical_basis": "",
            "further_tests": [],
            "provider": "none",
            "model": "none",
            "elapsed_s": 0.0,
            "saved_prompt": str(path),
        }

    # ----------------------------------------------------------
    # Batch processing
    # ----------------------------------------------------------

    def batch_reason(self, intersections: list[tuple],
                     same_domain_filter: bool = True,
                     distance_threshold: float = 2.0) -> list[dict]:
        """Process a list of intersections through the two-tier pipeline.

        Args:
            intersections: list of (obj_a_id, obj_b_id, distance, n_shared_dims)
                           as returned by DissectionTensor.find_intersections()
            same_domain_filter: skip same-domain pairs (obvious artifacts)
            distance_threshold: skip pairs with distance above this

        Returns:
            list of result dicts, one per intersection (after filtering)
        """
        results = []
        n_total = len(intersections)
        n_filtered = 0

        for i, item in enumerate(intersections):
            obj_a_id, obj_b_id, distance, n_shared = item[:4]

            # Extract domains from obj_id prefix
            domain_a = obj_a_id.split("_")[0]
            domain_b = obj_b_id.split("_")[0]

            # Filter obvious artifacts
            if same_domain_filter and domain_a == domain_b:
                n_filtered += 1
                self.stats["artifacts_filtered"] += 1
                continue
            if distance > distance_threshold:
                n_filtered += 1
                self.stats["artifacts_filtered"] += 1
                continue

            print(f"  [{i+1}/{n_total}] {obj_a_id} <-> {obj_b_id} (d={distance:.3f})")

            # Build object dicts from IDs
            obj_a = self.formatter._get_object(obj_a_id) or {
                "obj_id": obj_a_id, "domain": domain_a, "label": obj_a_id}
            obj_b = self.formatter._get_object(obj_b_id) or {
                "obj_id": obj_b_id, "domain": domain_b, "label": obj_b_id}

            # Per-group distances if tensor is available
            per_group = self.formatter._per_group_distances(obj_a_id, obj_b_id)

            # Contributing groups = those with smallest finite distance
            contributing = []
            if per_group:
                finite = [(g, d) for g, d in per_group.items() if np.isfinite(d)]
                finite.sort(key=lambda x: x[1])
                contributing = [g for g, _ in finite[:3]]

            result = self.reason_about_intersection(
                obj_a, obj_b, distance, contributing, per_group)
            result["obj_a_id"] = obj_a_id
            result["obj_b_id"] = obj_b_id
            result["distance"] = distance
            result["n_shared_dims"] = n_shared
            results.append(result)

        print(f"\n  Processed {len(results)} intersections "
              f"({n_filtered} filtered as artifacts)")
        return results

    # ----------------------------------------------------------
    # Integration with explorer results
    # ----------------------------------------------------------

    def analyze_explorer_results(self, results_path: str) -> dict:
        """Load MAP-Elites archive or GA results and reason about intersections.

        Args:
            results_path: path to JSON file with explorer results.
                Supports formats:
                - MAP-Elites archive: {pair_key: {fail_mode: elite_dict}}
                - GA results: {"intersections": [...]} or list of tuples
                - Raw intersection list: [(obj_a, obj_b, dist, n_shared), ...]

        Returns:
            Report dict with summary statistics and per-intersection results.
        """
        path = Path(results_path)
        if not path.exists():
            return {"error": f"File not found: {results_path}"}

        data = json.loads(path.read_text(encoding="utf-8"))

        # Detect format and extract intersections
        intersections = []

        if isinstance(data, list):
            # Raw list of intersection tuples
            for item in data:
                if isinstance(item, (list, tuple)) and len(item) >= 3:
                    intersections.append(tuple(item))
                elif isinstance(item, dict) and "obj_a" in item:
                    intersections.append((
                        item["obj_a"], item["obj_b"],
                        item.get("distance", 0), item.get("n_shared", 0)
                    ))

        elif isinstance(data, dict):
            # MAP-Elites archive format
            if any("--" in k for k in list(data.keys())[:5]):
                for pair_key, modes in data.items():
                    if not isinstance(modes, dict):
                        continue
                    for mode, elite in modes.items():
                        if isinstance(elite, dict) and "distance" in elite:
                            intersections.append((
                                elite.get("obj_a", ""),
                                elite.get("obj_b", ""),
                                elite["distance"],
                                elite.get("n_shared", 0),
                            ))

            # GA / generic format with intersections key
            elif "intersections" in data:
                for item in data["intersections"]:
                    if isinstance(item, (list, tuple)):
                        intersections.append(tuple(item))
                    elif isinstance(item, dict):
                        intersections.append((
                            item.get("obj_a", item.get("obj_a_id", "")),
                            item.get("obj_b", item.get("obj_b_id", "")),
                            item.get("distance", 0),
                            item.get("n_shared", 0),
                        ))

        if not intersections:
            return {"error": "No intersections found in file", "path": str(path)}

        # Sort by distance (most interesting = closest)
        intersections.sort(key=lambda x: x[2])

        # Cap at top 50 to avoid excessive API calls
        intersections = intersections[:50]

        print(f"Analyzing {len(intersections)} intersections from {path.name}")
        results = self.batch_reason(intersections)

        # Build summary report
        verdicts = {}
        for r in results:
            v = r.get("verdict", "UNCLEAR")
            verdicts[v] = verdicts.get(v, 0) + 1

        novel = [r for r in results if r.get("verdict") == "NOVEL_BRIDGE"]
        known = [r for r in results if r.get("verdict") == "KNOWN_THEOREM"]

        report = {
            "source": str(path),
            "n_input": len(intersections),
            "n_analyzed": len(results),
            "verdict_counts": verdicts,
            "stats": self.stats,
            "novel_bridges": [
                {
                    "obj_a": r.get("obj_a_id"),
                    "obj_b": r.get("obj_b_id"),
                    "distance": r.get("distance"),
                    "confidence": r.get("confidence"),
                    "explanation": r.get("explanation"),
                    "mathematical_basis": r.get("mathematical_basis"),
                }
                for r in novel
            ],
            "known_theorems": [
                {
                    "obj_a": r.get("obj_a_id"),
                    "obj_b": r.get("obj_b_id"),
                    "distance": r.get("distance"),
                    "explanation": r.get("explanation"),
                }
                for r in known
            ],
            "all_results": results,
        }

        # Save report
        report_path = self.output_dir / "tensor_reasoner_report.json"
        report_path.write_text(
            json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"Report saved to {report_path}")

        return report


# ============================================================
# Main — demo the formatter on a sample intersection
# ============================================================

def main():
    """Demo: format a sample intersection prompt and show reasoning pipeline status."""
    print("=" * 70)
    print("Tensor Reasoner — Cross-Domain Intersection Classifier")
    print("=" * 70)

    # Sample intersection: an elliptic curve and a knot
    sample_a = {
        "obj_id": "ec_11.a1",
        "domain": "EC",
        "label": "11.a1",
        "raw": {
            "conductor": 11,
            "rank": 0,
            "torsion": 5,
            "analytic_rank": 0,
        },
        "signatures": {
            "s1_ap": [1.386, 0.693, 1.099, 0.693, 1.386, 0.693, 1.609, 0.693],
            "s3_ap": [0.5, 0.667, 0.8, 0.714, 0.727, 0.615],
            "s7_cond": [0, 0, 0, 0, 1],
            "s13": [2.485, -1.0, 3.0, 2.485],
            "s24_ap": [3.21, 3.93, 4.11, 0.87],
        },
    }

    sample_b = {
        "obj_id": "knot_5_1",
        "domain": "knot",
        "label": "5_1",
        "raw": {
            "crossing_number": 5,
            "determinant": 5,
        },
        "signatures": {
            "s1_alex": [1.609, 0.916, 1.253, 0.916, 1.609, 0.916, 1.853, 0.916],
            "s3_alex": [0.5, 0.333, 0.4, 0.429, 0.364, 0.308],
            "s7_det": [0, 0, 1, 0, 0],
            "s13": [1.946, 1.0, 2.0, 0.0],
            "s24_alex": [2.19, 1.79, 2.83, 0.65],
        },
    }

    sample_distance = 0.427
    sample_per_group = {
        "complex": 0.312,
        "mod_p": 0.189,
        "padic": 0.523,
        "disc_cond": 0.614,
        "entropy": 0.298,
    }

    # Format the prompt
    formatter = IntersectionFormatter()
    prompt = formatter.format_prompt(
        sample_a, sample_b, sample_distance,
        contributing_groups=["mod_p", "entropy", "complex"],
        per_group_dists=sample_per_group,
    )

    print(f"\n--- Sample Prompt ({len(prompt)} chars) ---")
    print(prompt[:2000])
    if len(prompt) > 2000:
        print(f"\n... [{len(prompt) - 2000} more chars] ...")

    # Initialize reasoner and check availability
    print(f"\n--- Reasoner Status ---")
    reasoner = TensorReasoner()
    reasoner._check_ollama()
    reasoner._get_nvidia_key()

    print(f"\n--- Running inference on sample ---")
    result = reasoner.reason_about_intersection(
        sample_a, sample_b, sample_distance,
        contributing_groups=["mod_p", "entropy", "complex"],
        per_group_dists=sample_per_group,
    )

    print(f"\n--- Result ---")
    print(f"  Verdict:     {result.get('verdict')}")
    print(f"  Confidence:  {result.get('confidence')}")
    print(f"  Provider:    {result.get('provider')}")
    print(f"  Model:       {result.get('model')}")
    print(f"  Elapsed:     {result.get('elapsed_s', 0):.1f}s")
    print(f"  Explanation: {result.get('explanation', '')[:200]}")
    if result.get("saved_prompt"):
        print(f"  Saved to:    {result['saved_prompt']}")

    print(f"\n--- Stats ---")
    for k, v in reasoner.stats.items():
        print(f"  {k}: {v}")

    return reasoner


if __name__ == "__main__":
    main()
