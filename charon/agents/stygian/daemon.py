"""Stygian — v10-battery attack worker (Charon child, MVP).

One tick = pick the next un-attacked-recently Atlas number-theoretic
problem from BL-C-001..010, write an attack-plan artifact with KillVector
stub fields + conditional anti-anchor candidate, persist
last-attempted-at state. Propose-only; the costly v10 battery execution
is downstream of this artifact, not inside this tick.

Mirrors Sophia's MVP discipline: real work, real backlog, no scorer
execution.

See `charon/agents/stygian/CHARTER.md` for the one-page brief.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from charon.agents._base import CharonAgent
from harmonia.agents._base import REPO_ROOT


BACKLOG_PATH = REPO_ROOT / "charon" / "BACKLOG.md"

# Parsed inline from BL-C-001..010 (charon/BACKLOG.md). Keeping this as a
# typed table rather than re-parsing the markdown each tick — the BACKLOG
# is the source of truth, this is the operational snapshot.
SEED_PROBLEMS: list[dict] = [
    {
        "id": "BL-C-001",
        "name": "Lehmer's conjecture (Mahler measure)",
        "hardness": "EXACTNESS_BARRIER",
        "domain": "polynomial_heights",
        "attack_vector": "v10 Tier A (F1-F14) on polynomial-family generation seeded near M~1.1762; Tier C representation-stress on Mahler vs height vs trace; Tier D magnitude against Smyth lower bound",
        "modal_llm_error": None,
        "hard5_collision_risk": "Lehmer-tau vs Lehmer-Mahler",
    },
    {
        "id": "BL-C-002",
        "name": "BSD rank distribution at higher conductor",
        "hardness": "REPRESENTATION_GAP",
        "domain": "elliptic_curves",
        "attack_vector": "v10 Tier A on rank-vs-conductor at conductor > 10^7; Tier D probe on 50/50 rank-0/rank-1 split; Tier C analytic-rank vs Mordell-Weil-rank (HARD-5)",
        "modal_llm_error": "'BSD rank distribution is 50/50 above conductor N' without isogeny-class/family conditioning",
        "hard5_collision_risk": "analytic-rank vs rank-via-BSD",
    },
    {
        "id": "BL-C-003",
        "name": "Mahler measure spectrum gaps",
        "hardness": "EXACTNESS_BARRIER",
        "domain": "polynomial_heights",
        "attack_vector": "v10 Tier A gap-detection in spectrum below threshold T; Tier B robustness; Tier C representation across degree/signature/Galois group",
        "modal_llm_error": None,
        "hard5_collision_risk": "spectrum vs infimum (BL-C-001 collision)",
    },
    {
        "id": "BL-C-004",
        "name": "Schinzel-Zassenhaus follow-on (post-Dimitrov 2019)",
        "hardness": "EXACTNESS_BARRIER",
        "domain": "polynomial_heights",
        "attack_vector": "v10 Tier A on Dimitrov 1/(4 deg) bound tightness; Tier C representation-stress",
        "modal_llm_error": "'Schinzel-Zassenhaus is open' (settled by Dimitrov 2019 arXiv:1912.12545)",
        "hard5_collision_risk": "Schinzel-Zassenhaus vs Schinzel (general)",
    },
    {
        "id": "BL-C-005",
        "name": "abc conjecture status (post-Mochizuki controversy)",
        "hardness": "REPRESENTATION_GAP + METHOD_GAP",
        "domain": "number_theory",
        "attack_vector": "v10 Tier A on Stewart-Yu unconditional bound vs conjectured bound; Tier C representation-stress on rad/q/log forms",
        "modal_llm_error": "'abc was proved by Mochizuki' (IUT not community-accepted; Stewart-Yu is the actual accepted unconditional)",
        "hard5_collision_risk": "strong-abc vs weak-abc",
    },
    {
        "id": "BL-C-006",
        "name": "Beal's conjecture (Tijdeman-Zagier follow-on)",
        "hardness": "EXACTNESS_BARRIER",
        "domain": "number_theory",
        "attack_vector": "v10 Tier A small-exponent classification; Tier B parametric family searches; Tier C Beal vs Tijdeman-Zagier formulations",
        "modal_llm_error": "Beal conflated with Fermat or Tijdeman-Zagier",
        "hard5_collision_risk": "Beal vs Tijdeman-Zagier vs FLT",
    },
    {
        "id": "BL-C-007",
        "name": "Catalan-Mihailescu adjacent (Pillai's conjecture)",
        "hardness": "EXACTNESS_BARRIER",
        "domain": "number_theory",
        "attack_vector": "v10 Tier A perfect-power gap detection; Tier C Pillai vs Catalan vs generalized-Catalan",
        "modal_llm_error": "'Catalan's conjecture is open' (settled by Mihailescu 2002)",
        "hard5_collision_risk": "Catalan vs Tijdeman vs Pillai",
    },
    {
        "id": "BL-C-008",
        "name": "Vinogradov mean value adjacent (post-Wooley / BDG 2016)",
        "hardness": "REPRESENTATION_GAP",
        "domain": "analytic_number_theory",
        "attack_vector": "v10 Tier A on Wooley/BDG main conjecture statement vs open follow-on; Tier C representation-stress on exact-constant variants",
        "modal_llm_error": "'Vinogradov mean value is open' (settled by Wooley + BDG 2016)",
        "hard5_collision_risk": "main conjecture vs constant-variants vs l-adic/p-adic analogues",
    },
    {
        "id": "BL-C-009",
        "name": "Goldbach exceptional set bound",
        "hardness": "EXACTNESS_BARRIER",
        "domain": "analytic_number_theory",
        "attack_vector": "v10 Tier A on current theta bound (Pintz: theta < 0.72); Tier C binary-Goldbach vs ternary-Goldbach (HARD-5)",
        "modal_llm_error": "Binary-Goldbach conflated with ternary (Helfgott 2013 settled ternary; binary remains open with exceptional-set bounds)",
        "hard5_collision_risk": "binary vs ternary Goldbach",
    },
    {
        "id": "BL-C-010",
        "name": "Twin prime gaps (post-Zhang-Maynard-Tao)",
        "hardness": "EXACTNESS_BARRIER",
        "domain": "analytic_number_theory",
        "attack_vector": "v10 Tier A on exact-H state (Polymath 8b: H <= 246); Tier C bounded-gaps vs twin-primes vs Hardy-Littlewood-k-tuples",
        "modal_llm_error": "'Zhang proved twin primes' (Zhang proved bounded gaps; twin prime conjecture H=2 remains open)",
        "hard5_collision_risk": "bounded-gaps vs twin-primes vs k-tuples",
    },
]


class StygianAgent(CharonAgent):
    """v10-battery attack worker. Picks one Atlas problem per tick and
    writes an attack-plan artifact + conditional anti-anchor candidate."""

    name = "Stygian"
    role = "v10-battery attack worker (BL-C-001..010 + Atlas continuation)"

    # ---- backlog ----------------------------------------------------------

    def self_generate_backlog(self) -> list[dict]:
        """Round-robin SEED_PROBLEMS sorted by last-attempted-at ASC.

        State: `last_attempted` is a dict mapping problem_id -> ISO timestamp.
        Problems never attempted sort earliest.
        """
        last = self.load_state("last_attempted", {}) or {}

        def _key(p: dict) -> str:
            return last.get(p["id"], "0000")

        ranked = sorted(SEED_PROBLEMS, key=_key)
        return ranked

    # ---- attack-plan artifact --------------------------------------------

    def _emit_attack_plan(self, problem: dict) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"attack_plan_{problem['id']}_{utc}.md"
        modal = problem.get("modal_llm_error")
        lines: list[str] = []
        lines.append(f"# Stygian attack plan — {problem['id']}")
        lines.append("")
        lines.append(f"- problem: {problem['name']}")
        lines.append(f"- hardness_signature: {problem['hardness']}")
        lines.append(f"- domain: {problem['domain']}")
        lines.append(f"- planned_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- planned_by: Stygian (charon/agents/stygian/daemon.py)")
        lines.append(f"- battery_version: v10 (FROZEN, 25 tests / 4 tiers)")
        lines.append(f"- hard5_collision_risk: {problem['hard5_collision_risk']}")
        lines.append("")
        lines.append("## Attack vector")
        lines.append("")
        lines.append(problem["attack_vector"])
        lines.append("")
        lines.append("## KillVector stub")
        lines.append("")
        lines.append("```")
        lines.append(f"problem_id: {problem['id']}")
        lines.append(f"hardness_signature: {problem['hardness']}")
        lines.append(f"falsifier_id: <TBD on execution — Tier A first sweep>")
        lines.append(f"kill_pattern: <TBD>")
        lines.append(f"competing_hypothesis_id: <TBD — register before run>")
        lines.append(f"calibration_tier: KC-001-class anchor required")
        lines.append(f"precision_floor: <TBD per battery tier>")
        lines.append(f"repair_attempt_id: <null until REWRITE proposed>")
        lines.append("```")
        lines.append("")
        if modal:
            lines.append("## Anti-anchor candidate (conditional)")
            lines.append("")
            lines.append("This problem's documented modal-LLM-emission failure mode:")
            lines.append("")
            lines.append(f"- false_form: `{modal}`")
            lines.append("- true_form: see CHARON BACKLOG entry; primary-source citation required at register-time")
            lines.append("- emit-candidate-on-execution: yes (this is one of the expected primary emissions)")
            lines.append("")
        else:
            lines.append("## Anti-anchor candidate")
            lines.append("")
            lines.append("No documented modal-LLM-emission failure for this problem. Attack proceeds without an a-priori anti-anchor candidate; emission may surface during execution.")
            lines.append("")
        lines.append("## Hard stops")
        lines.append("")
        lines.append("- v10 battery FROZEN; do NOT add tests.")
        lines.append("- HARD-5 discipline: every kill_ledger entry from this attack MUST name which coordinates were stressed and which collapse risks were avoided.")
        lines.append("- If attack surfaces a v11-eligible gap, file a P2 ticket to Aporia; do NOT escalate unilaterally.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Stygian (charon/agents/stygian/daemon.py). MVP attack-plan artifact; v10 battery execution downstream.*")
        return self.write_artifact(fname, "\n".join(lines))

    def _emit_self_audit_null(self, reason: str) -> Path:
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"self_audit_null_{utc}.md"
        lines = [
            "# Stygian SELF_AUDIT_NULL",
            "",
            f"- emitted_at: {datetime.now(timezone.utc).isoformat()}",
            f"- reason: {reason}",
            "",
            "Silent ticks are forbidden under the HARD-2 anti-gravitational-well",
            "discipline. This artifact records that the daemon ran, found nothing",
            "actionable, and explicitly named the absence.",
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
            "problem_attempted": None,
        }
        artifacts: list[str] = []

        backlog = self.self_generate_backlog()
        stats["backlog_remaining"] = max(0, len(backlog) - 1)

        if not backlog:
            try:
                if not dry_run:
                    out = self._emit_self_audit_null("empty SEED_PROBLEMS — backlog source missing")
                    artifacts.append(str(out))
                    stats["artifacts_written"] += 1
                stats["items_processed"] += 1
            except Exception as e:
                self.log.exception(f"self_audit_null emit failed: {e}")
                stats["errors"] += 1
        else:
            problem = backlog[0]
            stats["problem_attempted"] = problem["id"]
            try:
                if dry_run:
                    stats["items_processed"] += 1
                else:
                    out = self._emit_attack_plan(problem)
                    artifacts.append(str(out))
                    stats["items_processed"] += 1
                    stats["artifacts_written"] += 1
                    # Update last-attempted state
                    last = self.load_state("last_attempted", {}) or {}
                    last[problem["id"]] = datetime.now(timezone.utc).isoformat()
                    self.save_state("last_attempted", last)
            except Exception as e:
                self.log.exception(f"attack_plan emit failed for {problem['id']}: {e}")
                stats["errors"] += 1

        summary = (
            f"problem={stats['problem_attempted']} "
            f"processed={stats['items_processed']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']}"
        )
        self.log_work(
            "stygian_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
