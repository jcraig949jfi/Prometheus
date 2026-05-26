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
from charon.agents._shared_queues import stygian_priority_queue
from charon.agents.stygian.executor import execute_attack
from harmonia.agents._base import REPO_ROOT


BACKLOG_PATH = REPO_ROOT / "charon" / "BACKLOG.md"

# Every Nth backlog tick forces SEED_PROBLEMS rotation (skips queue).
# At N=3 with the 20-min rotation cycle, BL-C-* problems land roughly
# every 60 min even when Hecate's stygian_priority queue is saturated.
# Set to 1 to disable the queue entirely; set to a large N to deprioritize
# SEED rotation. See self_generate_backlog docstring for rationale.
SEED_FORCE_EVERY_N = 3

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
        """Backlog source, in priority order:
          1. Hecate-fed stygian_priority queue (closed-loop edge from
             gradient archaeology — synthetic 'problems' wrapping each
             unconsumed kill_pattern cluster). Skipped on forced-SEED
             ticks (see SEED_FORCE_EVERY_N).
          2. SEED_PROBLEMS rotation (round-robin by last-attempted-at ASC,
             static curated work; always appended after queue rows so
             the queue can drain).

        Forced-SEED interleave: every SEED_FORCE_EVERY_N tick, the queue
        is skipped entirely so curated SEED_PROBLEMS get rotation
        pressure even when Hecate keeps the queue saturated. Without
        this, opportunistic queue work (e.g., HECATE-* meta-tests
        without registered loaders) starves the curated BL-C-* roster
        indefinitely. Counter persists in agent state so the cadence
        survives daemon restarts.
        """
        counter = int(self.load_state("backlog_tick_counter", 0) or 0) + 1
        self.save_state("backlog_tick_counter", counter)
        force_seed = (counter % SEED_FORCE_EVERY_N == 0)

        ranked: list[dict] = []
        if not force_seed:
            try:
                queue = stygian_priority_queue()
                queue_rows = queue.read_unconsumed(limit=10, sort_key="cluster_size")
                for r in queue_rows:
                    ranked.append(self._wrap_queue_row_as_problem(r))
            except Exception as e:
                self.log.warning(f"stygian_priority queue read failed: {e}")

        last = self.load_state("last_attempted", {}) or {}

        def _key(p: dict) -> str:
            return last.get(p["id"], "0000")

        ranked.extend(sorted(SEED_PROBLEMS, key=_key))
        return ranked

    def _wrap_queue_row_as_problem(self, row: dict) -> dict:
        """Convert a stygian_priority queue row into a problem-shaped dict
        that _emit_attack_plan can consume. The provenance fields survive
        on the dict so the artifact can cite the originating queue row.

        Source-aware id prefix so the executor routes correctly:
          - hecate-sourced -> 'HECATE-<kp>' (executor short-circuits;
            HECATE-meta-test loader deferred to v0.6+)
          - pollux-sourced -> 'POLLUX-<pair_name>' (executor short-
            circuits same way; POLLUX-meta-test loader could ship later
            but for now Stygian's value is the attack_plan + provenance)
          - default -> 'QUEUE-<kp>'
        """
        source = row.get("source", "unknown")
        kp = row.get("kill_pattern", "unknown")
        if source == "erebos":
            composed_id = row.get("erebos_composed_id", "?")
            prob_id = f"EREBOS-{composed_id}"
            name = f"Erebos composed intersection-claim: {composed_id}"
            attack_vector = (
                f"v10 battery on the Erebos-composed intersection-"
                f"claim {composed_id}. The composer paired a Stygian "
                f"PROMOTED row (record_id "
                f"`{row.get('erebos_stygian_record_id')}`) with a "
                f"Pollux PROMOTED row (record_id "
                f"`{row.get('erebos_pollux_record_id')}`) into a "
                f"restricted-subset claim. Goal: does the composition "
                f"survive battery validation, or do the parent verdicts "
                f"turn out to be independent (composition coincidental)?"
            )
            hardness = "HEPHAESTUS_COMPOSED"
            return {
                "id": prob_id,
                "name": name,
                "hardness": hardness,
                "domain": "composed_intersection_claim",
                "attack_vector": attack_vector,
                "modal_llm_error": None,
                "hard5_collision_risk": "potential -- composed claim may smuggle assumptions from either parent verdict",
                "_queue_row_id": row.get("id"),
                "_queue_source": source,
                "_queue_payload": row,
            }
        if source == "pollux":
            pair_name = row.get("pollux_pair_name", "?")
            prob_id = f"POLLUX-{pair_name}"
            name = (
                f"Pollux survivor pair: {pair_name} "
                f"({row.get('pollux_subset_a_desc', '')} vs "
                f"{row.get('pollux_subset_b_desc', '')})"
            )
            attack_vector = (
                f"v10 battery on the survivor-correlation Pollux flagged: "
                f"raw spearman {row.get('pollux_corr_raw')}, "
                f"normalized spearman {row.get('pollux_corr_norm')} "
                f"on n={row.get('cluster_size')} paired records. "
                f"Goal: does the correlation that survived mean-spacing "
                f"normalization also survive F1-F14 + F15-F23 testing, or "
                f"does the battery surface a confound Pollux's two-test "
                f"normalization missed?"
            )
            hardness = "POLLUX_SURVIVOR"
        elif source == "hecate":
            prob_id = f"HECATE-{kp}"
            name = f"Hecate-emergent kill_pattern: {kp}"
            attack_vector = (
                f"v10 battery against kill_pattern `{kp}` (cluster size "
                f"{row.get('cluster_size')}, mi_z {row.get('mi_z')}). "
                f"Goal: does the emergent cluster survive when attacked as "
                f"a first-class kill_pattern, or does it dissolve under "
                f"battery-class verification? Top generator: "
                f"`{row.get('top_generator', 'unknown')}`."
            )
            hardness = "EMERGENT_CLUSTER"
        else:
            prob_id = f"QUEUE-{kp}"
            name = f"queue-fed problem from {source}: {kp}"
            attack_vector = f"v10 battery against opportunistic queue target {kp}"
            hardness = "QUEUE_OPPORTUNISTIC"
        return {
            "id": prob_id,
            "name": name,
            "hardness": hardness,
            "domain": "kill_ledger_geometry",
            "attack_vector": attack_vector,
            "modal_llm_error": None,
            "hard5_collision_risk": f"potential -- {source} payload may collide with existing kill_pattern primitives",
            "_queue_row_id": row.get("id"),
            "_queue_source": source,
            "_queue_payload": row,
        }

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
        # Provenance section for queue-fed problems (Hecate -> Stygian edge)
        queue_payload = problem.get("_queue_payload")
        queue_source = problem.get("_queue_source")
        if queue_payload and queue_source:
            lines.append("## Provenance")
            lines.append("")
            lines.append(f"- queue: `stygian_priority` (file: `charon/agents/_shared_queues/stygian_priority.jsonl`)")
            lines.append(f"- source agent: `{queue_source}`")
            lines.append(f"- queue_row_id: `{queue_payload.get('id')}`")
            lines.append(f"- enqueued_at: {queue_payload.get('ts')}")
            lines.append(f"- originating cluster_size: {queue_payload.get('cluster_size')}")
            lines.append(f"- originating mi_z: {queue_payload.get('mi_z')}")
            lines.append(f"- originating mi_observed: {queue_payload.get('mi_observed')} bits")
            lines.append(f"- originating ledger_dir: `{queue_payload.get('hecate_ledger_dir')}`")
            lines.append("")
            lines.append("Closed-loop edge per Stand #1 (2026-05-21): Hecate's gradient archaeology surfaced this kill_pattern as an emergent cluster; Stygian attacks it under the v10 battery to test whether the cluster survives first-class kill_pattern verification. The kill_ledger row this attack emits feeds back into Hecate's next analysis.")
            lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Stygian (charon/agents/stygian/daemon.py). MVP attack-plan artifact; v10 battery execution downstream.*")
        return self.write_artifact(fname, "\n".join(lines))

    def _emit_dr_intake(self, notification: dict) -> Optional[Path]:
        """Write a Stygian-side intake artifact for a completed Pythia DR.

        The artifact pins the GitHub URL into the substrate, names the
        BL-C problem it informs, and stubs the downstream KillVector
        enrichment so the next attack_plan for that problem can fold
        primary-literature citations into competing_hypothesis_id.
        """
        utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        row_id = notification.get("row_id", "noid")
        fname = f"dr_intake_{row_id}_{utc}.md"
        tags = notification.get("tags") or {}
        problem_id = tags.get("problem_id") if isinstance(tags, dict) else None
        lines: list[str] = []
        lines.append(f"# Stygian DR intake — row {row_id}")
        lines.append("")
        lines.append(f"- received_at: {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"- queue_ref: {notification.get('queue_ref', 'n/a')}")
        lines.append(f"- title: {notification.get('title', 'n/a')}")
        lines.append(f"- problem_id: {problem_id or 'n/a'}")
        lines.append(f"- substrate_type: A (falsification data)")
        lines.append(f"- completed_at: {notification.get('completed_at', 'n/a')}")
        lines.append(f"- report_path: `{notification.get('report_path', 'n/a')}`")
        lines.append(f"- report_url: {notification.get('report_github_url', 'n/a')}")
        lines.append("")
        lines.append("## Summary (Pythia)")
        lines.append("")
        lines.append(notification.get("summary", "_(no summary supplied)_"))
        lines.append("")
        lines.append("## Downstream action")
        lines.append("")
        lines.append(
            "On next attack_plan emission for the named problem, fold the "
            "primary citations from the report into competing_hypothesis_id "
            "and update the BACKLOG entry's `modal_llm_error` if the report "
            "surfaced a clearer false-form."
        )
        lines.append("")
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

    # ---- DR prompt builder (substrate type A — falsification) ------------

    def _build_dr_prompt(self, problem: dict) -> str:
        """Structured DR ask for the current attack target.

        Five disciplines per `aporia/doctrine/dr_prompt_discipline.md` §3:
        names requester (Stygian), specifies substrate type A, sets
        verification criterion (arXiv ID + date), pre-declares landing
        path (attack_plan artifact), and the caller suppresses re-fire
        via `_recent_dr_coverage()`.
        """
        pid = problem["id"]
        name = problem["name"]
        modal = problem.get("modal_llm_error")
        modal_block = (
            f"\nDocumented modal-LLM-emission failure mode for this target: "
            f"`{modal}`. Confirm or refute against current primary literature."
        ) if modal else ""
        return (
            f"Stygian (Charon swarm, falsification battery operator) is "
            f"preparing a v10-battery attack on open problem `{pid}` "
            f"({name}). Substrate type A (falsification data).\n\n"
            f"Survey 2024-2026 primary-literature attacks on this target. "
            f"Identify the two strongest published attempts (most-cited or "
            f"most-cited-against), summarise for each:\n"
            f"- the precise statement attacked (NOT a general framing)\n"
            f"- the technique/method invoked\n"
            f"- the verdict reached and whether it has been retracted, "
            f"contested, or subsequently extended\n"
            f"- the hardness-signature classification "
            f"(EXACTNESS_BARRIER / REPRESENTATION_GAP / METHOD_GAP / "
            f"COUPLED_DIFFICULTY / CONCEPTUAL_ABSENCE) that best fits.\n"
            f"{modal_block}\n\n"
            f"Verification criterion: every claim must cite an arXiv ID + DOI "
            f"published 2024 or later; distinguish the original conjecture "
            f"from any partial / variant settled in the interim "
            f"(HARD-5 discipline — see this problem's documented collision "
            f"risk: `{problem.get('hard5_collision_risk', '<none>')}`).\n\n"
            f"Landing path: Stygian's attack_plan artifact for `{pid}` "
            f"(`charon/agents/stygian/artifacts/attack_plan_{pid}_*.md`); "
            f"primary citations enrich the KillVector stub's "
            f"competing_hypothesis_id field when the v10 battery executes."
        )

    # ---- run_tick ---------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        stats: dict[str, Any] = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "problem_attempted": None,
            "dr_inbox_processed": 0,
            "dr_seeded": False,
            "dr_seeded_today": 0,
            "dr_quota_remaining": 0,
        }
        artifacts: list[str] = []

        # ---- DR inbox processing (process Pythia replies before new work) ----
        if not dry_run:
            inbox = self._process_dr_inbox()
            for note in inbox:
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

        # ---- main work: pick a problem, emit attack plan ----
        backlog = self.self_generate_backlog()
        stats["backlog_remaining"] = max(0, len(backlog) - 1)

        chosen: Optional[dict] = None
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
            chosen = problem
            stats["problem_attempted"] = problem["id"]
            queue_row_id = problem.get("_queue_row_id")
            stats["from_queue"] = bool(queue_row_id)
            # Surface the interleave counter so we can audit cadence
            stats["backlog_tick_counter"] = int(
                self.load_state("backlog_tick_counter", 0) or 0
            )
            stats["force_seed_tick"] = (
                stats["backlog_tick_counter"] % SEED_FORCE_EVERY_N == 0
            )
            try:
                if dry_run:
                    stats["items_processed"] += 1
                else:
                    out = self._emit_attack_plan(problem)
                    artifacts.append(str(out))
                    stats["items_processed"] += 1
                    stats["artifacts_written"] += 1
                    # Execute the v10 battery (MVP1: BL-C-001 only; other
                    # problems short-circuit with UNVERIFIED rows). The
                    # executor emits a kill_ledger row in Theseus's shape
                    # so Hecate's gradient-archaeology consumes it. See
                    # pivot/stygian_executor_scoping_2026-05-21.md.
                    try:
                        exec_stats = execute_attack(
                            problem, attack_plan_path=str(out)
                        )
                        stats.update(exec_stats)
                    except Exception as e:
                        self.log.exception(f"executor crashed for {problem['id']}: {e}")
                        stats["errors"] += 1
                        stats["executor_invoked"] = False
                    # Mark queue row consumed so we don't re-pick it next tick
                    if queue_row_id:
                        try:
                            stygian_priority_queue().mark_consumed(
                                queue_row_id, by="stygian"
                            )
                        except Exception as e:
                            self.log.warning(
                                f"failed to mark queue row consumed: {e}"
                            )
                    # Update last-attempted state (also for queue-fed problems,
                    # so the same kill_pattern doesn't immediately bounce back
                    # from SEED_PROBLEMS rotation)
                    last = self.load_state("last_attempted", {}) or {}
                    last[problem["id"]] = datetime.now(timezone.utc).isoformat()
                    self.save_state("last_attempted", last)
            except Exception as e:
                self.log.exception(f"attack_plan emit failed for {problem['id']}: {e}")
                stats["errors"] += 1

        # ---- Pythia DR enqueue (cap-aware, doctrine-conformant) ----
        if (not dry_run) and chosen is not None:
            dr_result = self._dr_enqueue_if_quota(
                title=f"Stygian primary-literature survey: {chosen['id']} ({chosen['name']})",
                prompt=self._build_dr_prompt(chosen),
                recent_coverage_keywords=["Stygian", chosen["id"]],
                substrate_type="A",
                tags={"problem_id": chosen["id"], "hardness": chosen["hardness"]},
            )
            stats.update({
                "dr_seeded": dr_result["dr_seeded"],
                "dr_seeded_today": dr_result["dr_seeded_today"],
                "dr_quota_remaining": dr_result["dr_quota_remaining"],
                "dr_skipped_reason": dr_result["dr_skipped_reason"],
                "dr_row_id": dr_result["dr_row_id"],
            })

        # One-time adoption signal per aporia/doctrine/dr_prompt_discipline.md §8
        if not dry_run:
            self._emit_dr_discipline_adoption(
                daily_cap=3,
                substrate_types=["A"],
                builder_ref="charon/agents/stygian/daemon.py:_build_dr_prompt",
            )

        summary = (
            f"problem={stats['problem_attempted']} "
            f"processed={stats['items_processed']} "
            f"artifacts={stats['artifacts_written']} "
            f"errors={stats['errors']} "
            f"dr_inbox={stats['dr_inbox_processed']} "
            f"dr_seeded={stats['dr_seeded']} "
            f"dr_quota_remaining={stats['dr_quota_remaining']}"
        )
        self.log_work(
            "stygian_tick_complete",
            summary=summary,
            output_path=artifacts[0] if artifacts else None,
            success=stats["errors"] == 0,
        )
        return stats
