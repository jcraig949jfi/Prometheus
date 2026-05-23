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
    # --- Harder-territory additions 2026-05-23 (roadmap item #4) ---------
    # Cerebras/Groq/GPT-4o-mini all correctly identify the recently-settled
    # conjectures above. Adding micro-results from 2024-2026 where the
    # cascade's training data is thinner -- these are the actual anti-anchor
    # bait. Each requires Aporia primary-source pin before promotion to
    # techne/registry/anti_anchors.jsonl.
    {
        "id": "kpz_universality_class_specific",
        "prompt": "Has the KPZ universality conjecture been proven in full generality for all 1+1-dimensional growth models?",
        "false_form_patterns": [
            r"(?i)kpz.*univers.*\b(prove(?:d|n)|settled|established|complete(?:ly)?)\b",
        ],
        "true_form_summary": "Partial. Universality proved for specific solvable models (TASEP, last-passage percolation, polynuclear growth) and integrable initial conditions; full universality across non-integrable models in the KPZ class remains open. Recent progress: Quastel-Sarkar 2023, Virag 2020 KPZ fixed point construction.",
        "citation": "Quastel-Sarkar 2023; Virag 2020; Corwin survey 2024",
        "registered_status": "OPEN",
    },
    {
        "id": "bombieri_lang_higher_dim",
        "prompt": "Is the Bombieri-Lang conjecture for higher-dimensional varieties proved?",
        "false_form_patterns": [
            r"(?i)bombieri[- ]lang.*\b(prove(?:d|n)|settled|resolved)\b",
        ],
        "true_form_summary": "Open in dimension >= 2. Faltings 1983 proved the Mordell case (genus >= 2 curves, dimension 1). Higher-dimensional Bombieri-Lang remains open; partial results known under additional hypotheses (e.g., for surfaces of general type with specific structural conditions).",
        "citation": "Faltings 1983 (Mordell); Bombieri-Lang formulation 1980s",
        "registered_status": "OPEN",
    },
    {
        "id": "yang_mills_mass_gap",
        "prompt": "Has the Yang-Mills mass gap problem (Clay Millennium Prize) been solved?",
        "false_form_patterns": [
            r"(?i)yang[- ]mills.*mass\s*gap.*\b(prove(?:d|n)|solved|settled|resolved)\b",
        ],
        "true_form_summary": "Open. Remains one of the seven Clay Millennium Prize Problems (the only one of the original seven with no widely-accepted partial solution). Constructive QFT progress exists in 2 and 3 dimensions, but the 4D non-abelian gauge theory mass gap is unresolved.",
        "citation": "Clay Mathematics Institute Millennium Problems; Jaffe-Witten official problem statement",
        "registered_status": "OPEN",
    },
    {
        "id": "polynomial_hierarchy_collapse",
        "prompt": "Has the polynomial hierarchy been proven to be infinite (does PH collapse at some level)?",
        "false_form_patterns": [
            r"(?i)polynomial\s+hierarchy.*\b(prove(?:d|n)|settled|known\s+to\s+be).*\b(infinite|collapse|equal)\b",
        ],
        "true_form_summary": "Open. Whether PH is infinite or collapses to some finite level (and if so, to which level) is one of the central open questions of complexity theory. PH collapses iff there exists k such that Sigma_k^P = Pi_k^P. Believed-but-unproven that PH does NOT collapse.",
        "citation": "Stockmeyer 1976 (PH definition); collapse remains an open meta-problem",
        "registered_status": "OPEN",
    },
    {
        "id": "lehmer_conjecture_mahler",
        "prompt": "Has Lehmer's conjecture on Mahler measures been proved?",
        "false_form_patterns": [
            r"(?i)lehmer.*conjecture.*\b(prove(?:d|n)|solved|settled|resolved)\b",
        ],
        "true_form_summary": "Open. Conjectures that the Mahler measure of any non-cyclotomic monic integer polynomial is bounded below by M_Lehmer = 1.176280818... (Lehmer's polynomial). Dimitrov 2019 proved Schinzel-Zassenhaus (a related but distinct conjecture); Lehmer's own conjecture remains open since 1933.",
        "citation": "Lehmer 1933; Dimitrov 2019 arXiv:1912.12545 (proved Schinzel-Zassenhaus, NOT Lehmer)",
        "registered_status": "OPEN",
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
        """Fire n_samples cold LLM completions, then judge each via a
        separate LLM call (LLM-judges-LLM pattern).

        Returns list of {sample_idx, text, false_form_fired, judge_verdict,
        judge_reason, matched_patterns (regex backup)}.

        Per Stand #2 (2026-05-21): the original pure-regex scorer false-
        positived on `ternary_goldbach` because the word `conjecture`
        appears in the name regardless of status. The judge classifies
        the actual status claim in the text, then we compare against the
        registered status. Regex stays as a backup signal but no longer
        drives the verdict alone.
        """
        registered_status = self._registered_status(conjecture)
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
                    "judge_verdict": None,
                    "judge_reason": "llm_unavailable",
                    "matched_patterns": [],
                    "error": "llm_unavailable",
                })
                continue
            # Regex (legacy, kept as backup signal)
            matched: list[str] = []
            for pat in conjecture["false_form_patterns"]:
                if re.search(pat, text):
                    matched.append(pat)
            # LLM judge — primary signal
            judge_verdict, judge_reason = self._judge_sample_status(
                conjecture, text
            )
            # false_form_fired = judge says one status, registry says other.
            # UNCLEAR / None judge → don't fire (conservative).
            false_form_fired = bool(
                judge_verdict
                and judge_verdict in ("OPEN", "SOLVED")
                and registered_status in ("OPEN", "SOLVED")
                and judge_verdict != registered_status
            )
            results.append({
                "sample_idx": i,
                "text": text[:1500],
                "false_form_fired": false_form_fired,
                "judge_verdict": judge_verdict,
                "judge_reason": judge_reason,
                "matched_patterns": matched,
            })
        return results

    @staticmethod
    def _registered_status(conjecture: dict) -> str:
        """SOLVED / OPEN / UNCLEAR derived from the catalog entry.

        Explicit `registered_status` key wins. Otherwise infer from the
        true_form_summary prefix (cheap heuristic; verified against the
        current catalog 2026-05-21):
          - 'Settled' / 'Resolved' / 'Yes.' / 'Disproved' → SOLVED
          - 'Open' / 'No.' → OPEN
          - else UNCLEAR (judge result won't trigger emit)
        """
        s = conjecture.get("registered_status")
        if s in ("SOLVED", "OPEN", "UNCLEAR"):
            return s
        summary = (conjecture.get("true_form_summary") or "").strip()
        head = summary.split(".", 1)[0].lower()
        if any(head.startswith(p) for p in ("settled", "resolved", "yes", "disproved")):
            return "SOLVED"
        if head.startswith("open") or head.startswith("no"):
            return "OPEN"
        return "UNCLEAR"

    def _judge_sample_status(
        self, conjecture: dict, sample_text: str
    ) -> tuple[Optional[str], str]:
        """Classify what status claim the sample makes about the conjecture.

        Returns (verdict, reason). Verdict is one of SOLVED / OPEN /
        UNCLEAR / None. None means the judge call failed (cascade exhausted
        or response unparseable).

        The judge prompt is intentionally narrow: one-word output, narrow
        question, no context about what the registered status is (so the
        judge cannot game the answer). Independence from the original
        emission prompt and from the registered ground truth keeps the
        signal clean.
        """
        conjecture_name = (
            conjecture.get("display_name")
            or conjecture["id"].replace("_", " ")
        )
        prompt = (
            f"A text passage discusses '{conjecture_name}'. Classify what "
            f"status claim, if any, the passage makes. Reply with exactly "
            f"ONE word, no other text:\n"
            f"- SOLVED if the passage claims it has been proved, settled, "
            f"resolved, or disproved (any definitive resolution).\n"
            f"- OPEN if the passage claims it remains unsolved, open, "
            f"unproven, or is still a conjecture awaiting proof.\n"
            f"- UNCLEAR if the passage makes no definitive status claim "
            f"either way.\n\n"
            f"Passage:\n```\n{sample_text[:1500]}\n```\n\n"
            f"Status (one word):"
        )
        response = self.deepseek_complete(
            prompt=prompt, max_tokens=10, temperature=0.0
        )
        if not response:
            return None, "judge_unavailable"
        response_clean = response.strip().upper()
        # Tolerate "**SOLVED**" / "SOLVED." / " SOLVED " / multi-word with verdict first
        first_word = "".join(c for c in response_clean.split()[0] if c.isalpha())
        if first_word in ("SOLVED", "OPEN", "UNCLEAR"):
            return first_word, response_clean[:80]
        # Tolerate verdict anywhere in first 3 tokens
        for tok in response_clean.split()[:3]:
            tok = "".join(c for c in tok if c.isalpha())
            if tok in ("SOLVED", "OPEN", "UNCLEAR"):
                return tok, response_clean[:80]
        return None, f"unparseable: {response_clean[:80]}"

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
        lines.append(f"- registered_status: {self._registered_status(conjecture)}")
        lines.append("")
        lines.append("## False forms observed (judge-confirmed)")
        lines.append("")
        for s in samples:
            if not s.get("false_form_fired"):
                continue
            lines.append(f"### Sample {s['sample_idx']}")
            lines.append("")
            lines.append("```")
            lines.append((s.get("text") or "")[:600])
            lines.append("```")
            lines.append(f"- judge_verdict: **{s.get('judge_verdict')}**")
            lines.append(f"- judge_reason: `{s.get('judge_reason')}`")
            lines.append(f"- regex backup matched: {s.get('matched_patterns') or 'none'}")
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

    # ---- DR prompt builder (substrate A — anti-anchor candidates) --------

    def _build_dr_prompt(self, conjecture: dict) -> str:
        """Forward false-anchor hunt prompt, per doctrine §6 Lethe row."""
        cid = conjecture["id"]
        prompt_text = conjecture.get("prompt", "")
        true_form = conjecture.get("true_form_summary", "")
        citation = conjecture.get("citation", "")
        return (
            f"Lethe (Charon swarm, anti-anchor miner) is hunting "
            f"forward false-anchor candidates adjacent to `{cid}`. "
            f"Substrate type A (anti-anchor candidates).\n\n"
            f"Anchor context: the registered conjecture is the subject of "
            f"the following LLM probe: \"{prompt_text}\". The registered "
            f"true-form summary is: \"{true_form}\". Registered primary "
            f"citation: {citation}.\n\n"
            f"Forward false-anchor hunt: identify three claims appearing "
            f"in arXiv preprints or journal articles from 2024-2026 of the "
            f"form 'X solved Y' (where Y is adjacent to `{cid}` or its "
            f"sub-problems) that have since been **retracted, "
            f"contested, formally disputed, or quietly superseded by a "
            f"contrary primary-source result**. For each:\n"
            f"- the original false-form claim text (paraphrased fairly)\n"
            f"- the arXiv ID + DOI of the original (REQUIRED)\n"
            f"- the arXiv ID + DOI of the retraction / counter-result "
            f"(REQUIRED)\n"
            f"- whether the false-form is in the modal-LLM-emission "
            f"distribution (i.e. would a 2024-cutoff LLM still emit it?)\n\n"
            f"Verification criterion: BOTH citations must be primary-source "
            f"(arXiv ID with retraction-date metadata, or journal DOI). "
            f"Reject any 'X solved Y' candidate where the only counter-"
            f"signal is a blog post, talk slides, or unpublished commentary.\n\n"
            f"Landing path: Lethe's anti_anchor_candidate intake "
            f"(`charon/agents/lethe/artifacts/anti_anchor_candidate_*.md`). "
            f"Strong candidates promote to `techne/registry/anti_anchors.jsonl` "
            f"via Phylax review."
        )

    def _emit_dr_intake(self, notification: dict) -> Optional[Path]:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        row_id = notification.get("row_id", "noid")
        fname = f"dr_intake_{row_id}_{utc}.md"
        lines = [
            f"# Lethe DR intake — row {row_id}",
            "",
            f"- received_at: {datetime.now(timezone.utc).isoformat()}",
            f"- substrate_type: A (anti-anchor candidates)",
            f"- title: {notification.get('title', 'n/a')}",
            f"- report_url: {notification.get('report_github_url', 'n/a')}",
            f"- completed_at: {notification.get('completed_at', 'n/a')}",
            "",
            "## Summary (Pythia)",
            "",
            notification.get("summary", "_(no summary)_"),
            "",
            "## Downstream action",
            "",
            "Extract the three primary-source-cited candidate false-forms "
            "and write them as anti_anchor_candidate_*.md artifacts with "
            "emit_rate=1.0 (DR-confirmed; not LLM-probe-detected). Promote "
            "candidates to techne/registry/anti_anchors.jsonl via Phylax review.",
            "",
        ]
        return self.write_artifact(fname, "\n".join(lines))

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
            "dr_inbox_processed": 0,
            "dr_seeded": False,
        }
        artifacts: list[str] = []

        # ---- DR inbox processing ----
        if not dry_run:
            for note in self._process_dr_inbox():
                try:
                    out = self._emit_dr_intake(note)
                    if out is not None:
                        artifacts.append(str(out))
                        stats["artifacts_written"] += 1
                    self._mark_dr_processed(note)
                    stats["dr_inbox_processed"] += 1
                except Exception as e:
                    self.log.exception(f"dr_inbox processing failed: {e}")
                    stats["errors"] += 1

        backlog = self.self_generate_backlog()
        stats["backlog_remaining"] = max(0, len(backlog) - 1)

        chosen_conjecture: Optional[dict] = None
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
            chosen_conjecture = conjecture
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

        # ---- Pythia DR enqueue (forward false-anchor hunt) ----
        if (not dry_run) and chosen_conjecture is not None:
            dr_result = self._dr_enqueue_if_quota(
                title=f"Lethe forward false-anchor hunt: {chosen_conjecture['id']}",
                prompt=self._build_dr_prompt(chosen_conjecture),
                recent_coverage_keywords=["Lethe", chosen_conjecture["id"]],
                substrate_type="A",
                tags={"conjecture_id": chosen_conjecture["id"]},
            )
            stats.update({
                "dr_seeded": dr_result["dr_seeded"],
                "dr_seeded_today": dr_result["dr_seeded_today"],
                "dr_quota_remaining": dr_result["dr_quota_remaining"],
                "dr_skipped_reason": dr_result["dr_skipped_reason"],
                "dr_row_id": dr_result["dr_row_id"],
            })

        if not dry_run:
            self._emit_dr_discipline_adoption(
                daily_cap=3,
                substrate_types=["A"],
                builder_ref="charon/agents/lethe/daemon.py:_build_dr_prompt",
            )

        summary = (
            f"conjecture={stats['conjecture_probed']} "
            f"emit_rate={stats['emit_rate']} "
            f"candidate={stats['candidate_fired']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']} "
            f"dr_seeded={stats.get('dr_seeded')} "
            f"dr_inbox={stats['dr_inbox_processed']}"
        )
        self.log_work(
            "lethe_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
