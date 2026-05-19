"""Lethe — anti-anchor miner via cold LLM probes (Charon child, MVP).

One tick = pick least-recently-probed conjecture, fire N cold DeepSeek
completions, score each against registered true-form (regex-based for
MVP; LLM-judge for v0.2), emit anti_anchor_candidate when false-form
rate >= threshold.

See `charon/agents/lethe/CHARTER.md` for the one-page brief.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from charon.agents._base import CharonAgent


# ---- conjecture catalog ---------------------------------------------------

# Each entry: id, prompt (cold question asked to the LLM, no system prompt),
# false_form_patterns (regex list — if any match, an anti-anchor candidate
# fires), true_form_summary (what the correct answer should resemble),
# citation (primary-source pin for the true form).
CONJECTURE_CATALOG: list[dict] = [
    {
        "id": "schinzel_zassenhaus",
        "prompt": "What is the current state of the Schinzel-Zassenhaus conjecture?",
        "false_form_patterns": [
            r"(?i)schinzel[- ]zassenhaus.*\b(open|unproven|conjectur(e|ed)|unresolved|remains)\b",
            r"(?i)\bopen problem\b.*schinzel",
        ],
        "true_form_summary": "Resolved by Dimitrov 2019 (arXiv:1912.12545); proved exp(log 2 / 4d) lower bound on house of non-cyclotomic algebraic integer.",
        "citation": "Dimitrov 2019 arXiv:1912.12545",
    },
    {
        "id": "catalan_mihailescu",
        "prompt": "What is the current status of Catalan's conjecture about consecutive perfect powers?",
        "false_form_patterns": [
            r"(?i)catalan.*\b(open|unproven|unresolved|conjecture(?:d)?\s+(but|remains|is\s+still))\b",
            r"(?i)catalan.*not\s+(yet\s+)?(proved|proven|resolved|settled)",
        ],
        "true_form_summary": "Settled by Mihailescu 2002. The only solution to x^p - y^q = 1 with x,y,p,q >= 2 is 3^2 - 2^3 = 1.",
        "citation": "Mihailescu 2002, J. Reine Angew. Math.",
    },
    {
        "id": "vinogradov_mean_value",
        "prompt": "What is the status of the Vinogradov mean value conjecture?",
        "false_form_patterns": [
            r"(?i)vinogradov.*mean\s*value.*\b(open|unproven|unresolved|remains\s+a\s+conjecture)\b",
        ],
        "true_form_summary": "Main conjecture settled by Wooley (efficient congruencing, 2016) and Bourgain-Demeter-Guth (decoupling, 2016). Constants and l-adic / p-adic variants remain open.",
        "citation": "Wooley 2016; Bourgain-Demeter-Guth 2016",
    },
    {
        "id": "mertens_conjecture",
        "prompt": "Is Mertens' conjecture (|M(x)| < sqrt(x) for all x) true?",
        "false_form_patterns": [
            r"(?i)mertens.*conjecture.*\b(open|unproven|true|holds|believed|conjectured\s+to\s+be\s+true)\b",
            r"(?i)mertens.*conjecture.*not\s+(yet\s+)?(disproved|disproven|settled)",
        ],
        "true_form_summary": "Disproved by Odlyzko-te Riele 1985 (counterexample exists below ~10^14 region). The weaker M(x) = O(sqrt x) is equivalent to RH.",
        "citation": "Odlyzko & te Riele 1985, J. Reine Angew. Math.",
    },
    {
        "id": "sato_tate_symk",
        "prompt": "Is the Sato-Tate conjecture for symmetric powers of non-CM elliptic curves known?",
        "false_form_patterns": [
            r"(?i)sato[- ]tate.*sym(metric)?\s*power.*\b(open|unproven|conjecture(?:d)?|unresolved)\b",
        ],
        "true_form_summary": "Sato-Tate for sym^k of non-CM elliptic curves over totally real fields settled by Newton-Thorne 2021. Higher-genus Sato-Tate (52 Sato-Tate groups for genus 2 per Fite-Kedlaya-Rotger-Sutherland) is a distinct problem.",
        "citation": "Newton-Thorne 2021, Publ. Math. IHES",
    },
    {
        "id": "ternary_goldbach",
        "prompt": "Is the ternary Goldbach conjecture (every odd integer > 5 is a sum of three primes) proved?",
        "false_form_patterns": [
            r"(?i)ternary\s+goldbach.*\b(open|unproven|unresolved|conjecture(?:d)?|remains)\b",
        ],
        "true_form_summary": "Settled unconditionally by Helfgott 2013. Every odd integer >= 7 is the sum of three primes. Binary Goldbach (even integers > 2 as sum of two primes) remains open.",
        "citation": "Helfgott 2013, arXiv:1305.2897 + arXiv:1312.7748",
    },
    {
        "id": "saxl_conjecture",
        "prompt": "What is the current status of the Saxl conjecture about symmetric group tensor squares?",
        "false_form_patterns": [
            r"(?i)saxl.*conjecture.*\b(solved|proved|proven|settled|established)\b",
            r"(?i)saxl.*(sellke|lee).*2025",
        ],
        "true_form_summary": "Open. Luo-Sellke 2017 proved the fourth-power relaxation; the tensor-square conjecture proper remains open. Lee 2025 arXiv:2512.15035 was withdrawn within 3 days due to mathematical gaps.",
        "citation": "Luo-Sellke 2017; Lee 2025 WITHDRAWN (arXiv:2512.15035)",
    },
    {
        "id": "sensitivity_conjecture",
        "prompt": "Is the sensitivity conjecture for Boolean functions resolved?",
        "false_form_patterns": [
            r"(?i)sensitivity\s+conjecture.*\b(open|unproven|conjecture(?:d)?|unresolved|remains)\b",
        ],
        "true_form_summary": "Settled by Huang 2019 (Annals of Mathematics). Sensitivity is at most polynomially smaller than block sensitivity; proof uses a clever combinatorial argument on the hypercube.",
        "citation": "Huang 2019, Annals of Mathematics",
    },
    {
        "id": "bounded_gaps_vs_twin_primes",
        "prompt": "Did Zhang Yitang prove the twin prime conjecture?",
        "false_form_patterns": [
            r"(?i)zhang.*prove(d|s)?.*twin\s*prime",
            r"(?i)twin\s+prime.*conjecture.*\b(prove(?:d|n)|solved|settled).*zhang",
        ],
        "true_form_summary": "No. Zhang 2013 proved infinitely many prime pairs differ by at most 70 million; subsequent work (Maynard, Polymath 8b) reduced this to <= 246. The twin prime conjecture (gap = 2) remains open.",
        "citation": "Zhang 2013; Maynard 2013; Polymath 8b",
    },
    {
        "id": "fermat_last_theorem_calibration",
        "prompt": "Is Fermat's Last Theorem proved?",
        "false_form_patterns": [
            # This is the calibration probe — LLMs should NOT get this wrong.
            # If they do, the catalog itself or the LLM is broken.
            r"(?i)fermat.*last\s*theorem.*\b(open|unproven|conjecture(?:d)?|unresolved)\b",
        ],
        "true_form_summary": "Yes. Wiles 1994 (with Taylor) proved x^n + y^n = z^n has no positive integer solutions for n >= 3.",
        "citation": "Wiles 1994, Annals of Mathematics; Taylor-Wiles 1995",
    },
]

# Probe configuration
N_SAMPLES_PER_CONJECTURE = 4  # cheap; expandable in v0.2
FALSE_FORM_THRESHOLD = 0.30  # >=30% false-form fires -> candidate
SAMPLE_TEMPERATURE = 0.7  # encourage variance to expose modal-emission failure


class LetheAgent(CharonAgent):
    """Anti-anchor miner. Picks one conjecture per tick, fires N cold
    LLM completions, scores against registered true-form, emits
    candidate when false-form rate >= threshold."""

    name = "Lethe"
    role = "anti-anchor miner via cold LLM probes against recently-settled conjectures"

    # ---- backlog ----------------------------------------------------------

    def self_generate_backlog(self) -> list[dict]:
        """Round-robin CONJECTURE_CATALOG sorted by last-probed-at ASC."""
        last = self.load_state("last_probed", {}) or {}
        decayed = set(self.load_state("decayed", []) or [])

        def _key(c: dict) -> str:
            return last.get(c["id"], "0000")

        active = [c for c in CONJECTURE_CATALOG if c["id"] not in decayed]
        return sorted(active, key=_key)

    # ---- probe ------------------------------------------------------------

    def _probe(self, conjecture: dict, n_samples: int) -> list[dict]:
        """Fire n_samples cold DeepSeek completions. Returns list of
        {sample_idx, text, false_form_fired (bool), matched_patterns}."""
        results: list[dict] = []
        for i in range(n_samples):
            text = self.deepseek_complete(
                prompt=conjecture["prompt"],
                system=None,  # cold — no priming
                max_tokens=400,
                temperature=SAMPLE_TEMPERATURE,
            )
            if not text:
                results.append({
                    "sample_idx": i,
                    "text": None,
                    "false_form_fired": False,
                    "matched_patterns": [],
                    "error": "deepseek_unavailable",
                })
                continue
            matched: list[str] = []
            for pat in conjecture["false_form_patterns"]:
                if re.search(pat, text):
                    matched.append(pat)
            results.append({
                "sample_idx": i,
                "text": text[:1500],
                "false_form_fired": bool(matched),
                "matched_patterns": matched,
            })
        return results

    # ---- artifact writers -------------------------------------------------

    def _emit_anti_anchor_candidate(
        self, conjecture: dict, samples: list[dict], emit_rate: float,
    ) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"anti_anchor_candidate_{conjecture['id']}_{utc}.md"
        lines: list[str] = []
        lines.append(f"# Lethe anti-anchor candidate — {conjecture['id']}")
        lines.append("")
        lines.append(f"- emitted_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- emitted_by: Lethe (charon/agents/lethe/daemon.py)")
        lines.append(f"- emit_rate: {emit_rate:.2%} (threshold {FALSE_FORM_THRESHOLD:.0%})")
        lines.append(f"- n_samples: {len(samples)}")
        lines.append(f"- citation: {conjecture['citation']}")
        lines.append("")
        lines.append("## True form (registered)")
        lines.append("")
        lines.append(conjecture["true_form_summary"])
        lines.append("")
        lines.append("## False forms observed")
        lines.append("")
        for s in samples:
            if not s.get("false_form_fired"):
                continue
            lines.append(f"### Sample {s['sample_idx']}")
            lines.append("")
            lines.append("```")
            lines.append((s.get("text") or "")[:600])
            lines.append("```")
            lines.append(f"matched patterns: {s.get('matched_patterns')}")
            lines.append("")
        lines.append("## Recommendation")
        lines.append("")
        lines.append("Surface to Aporia for primary-source verification + adjudication. If true-form pin holds, register as AA-CAND-* in `techne/registry/anti_anchors.jsonl` after Phylax-class review. The Saxl-class capture pattern applies: a confirmed candidate prevents fabrication propagation into the Learner training corpus.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Lethe (charon/agents/lethe/daemon.py). MVP candidate artifact; promotion to canonical anti-anchor requires Aporia + primary-source pin per techne/registry/anti_anchors.jsonl schema.*")
        return self.write_artifact(fname, "\n".join(lines))

    def _emit_null_probe(
        self, conjecture: dict, samples: list[dict], emit_rate: float,
    ) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"null_probe_{conjecture['id']}_{utc}.md"
        lines: list[str] = []
        lines.append(f"# Lethe null probe — {conjecture['id']}")
        lines.append("")
        lines.append(f"- emitted_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- emit_rate: {emit_rate:.2%} (below threshold {FALSE_FORM_THRESHOLD:.0%})")
        lines.append(f"- n_samples: {len(samples)}")
        lines.append("")
        lines.append("This conjecture was probed; LLM emissions did not exceed the false-form threshold this round. Null result is data — recorded for decay tracking. If emit_rate trends to zero over rolling 90 days, conjecture demotes to DECAYED.")
        lines.append("")
        return self.write_artifact(fname, "\n".join(lines))

    def _emit_self_audit_null(self, reason: str) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"self_audit_null_{utc}.md"
        return self.write_artifact(fname, f"# Lethe SELF_AUDIT_NULL\n\n- reason: {reason}\n- at: {datetime.now(timezone.utc).isoformat()}\n")

    # ---- run_tick ---------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "conjecture_probed": None,
            "emit_rate": None,
            "candidate_fired": False,
        }
        artifacts: list[str] = []

        backlog = self.self_generate_backlog()
        stats["backlog_remaining"] = max(0, len(backlog) - 1)

        if not backlog:
            try:
                if not dry_run:
                    out = self._emit_self_audit_null("all conjectures DECAYED — catalog needs refresh")
                    artifacts.append(str(out))
                    stats["artifacts_written"] += 1
                stats["items_processed"] += 1
            except Exception as e:
                self.log.exception(f"self_audit_null emit failed: {e}")
                stats["errors"] += 1
        else:
            conjecture = backlog[0]
            stats["conjecture_probed"] = conjecture["id"]
            try:
                if dry_run:
                    # Skip the API hit; just record the intent.
                    stats["items_processed"] += 1
                else:
                    samples = self._probe(conjecture, N_SAMPLES_PER_CONJECTURE)
                    n_fired = sum(1 for s in samples if s.get("false_form_fired"))
                    n_valid = sum(1 for s in samples if s.get("text") is not None)
                    emit_rate = (n_fired / n_valid) if n_valid > 0 else 0.0
                    stats["emit_rate"] = round(emit_rate, 3)
                    if n_valid == 0:
                        # DeepSeek unavailable; record but don't emit candidate
                        out = self._emit_self_audit_null(f"DeepSeek unavailable for {conjecture['id']} probe")
                        artifacts.append(str(out))
                        stats["artifacts_written"] += 1
                    elif emit_rate >= FALSE_FORM_THRESHOLD:
                        out = self._emit_anti_anchor_candidate(conjecture, samples, emit_rate)
                        artifacts.append(str(out))
                        stats["artifacts_written"] += 1
                        stats["candidate_fired"] = True
                    else:
                        out = self._emit_null_probe(conjecture, samples, emit_rate)
                        artifacts.append(str(out))
                        stats["artifacts_written"] += 1
                    stats["items_processed"] += 1
                    # Update last-probed state
                    last = self.load_state("last_probed", {}) or {}
                    last[conjecture["id"]] = datetime.now(timezone.utc).isoformat()
                    self.save_state("last_probed", last)
                    # Update emission-rate history for decay tracking
                    history = self.load_state("emission_history", {}) or {}
                    history.setdefault(conjecture["id"], []).append({
                        "at": datetime.now(timezone.utc).isoformat(),
                        "emit_rate": round(emit_rate, 3),
                        "n_samples": n_valid,
                    })
                    history[conjecture["id"]] = history[conjecture["id"]][-30:]
                    self.save_state("emission_history", history)
            except Exception as e:
                self.log.exception(f"probe failed for {conjecture['id']}: {e}")
                stats["errors"] += 1

        summary = (
            f"conjecture={stats['conjecture_probed']} "
            f"emit_rate={stats['emit_rate']} "
            f"candidate={stats['candidate_fired']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']}"
        )
        self.log_work(
            "lethe_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
