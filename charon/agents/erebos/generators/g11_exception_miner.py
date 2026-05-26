"""Generator 11: Exception-Miner.

Per pivot/erebos_25_archetypes_spec_2026-05-26.md Phase 3.

Focuses on survivor-bias of a high-kill generator run. When most
claims from a parent generator REJECTED but a handful PROMOTED,
G11 hypothesizes that the survivors share a hidden property H
(some boolean / categorical that the parent didn't account for).

Erebos Implementation Spec:
- Input / Provenance: A pool of claims from a single generator
  with >=MIN_KILL_FRACTION kill rate and >=MIN_SURVIVORS survivors.
- Transformation: identify the survivors' shared payload tokens
  (intersection of composition_payload keys across survivors,
  minus the same intersection across all-emissions). The "novel
  shared key" set is the candidate hidden property H.
- Output Claim: "The isolated survivors of generator X are
  strictly defined by shared hidden property H = <key set>."
- Falsification Route: Generate new claims that possess H and
  feed them through the parent generator's battery. If they
  all FAIL battery (i.e., H is NOT actually predictive of
  survival), kill_pattern = out_of_sample_failure.
- Expected Kill Pattern: out_of_sample_failure.
- Loader Feasibility: Medium-B. Composition loader needs to
  read kill_ledger + scan for the hidden property.
- Reasoning Tier: R3 (abstraction: hidden property as the
  generator) + R4 (search: enumerate candidate properties).
"""
from __future__ import annotations

from collections import Counter
from typing import Optional

from charon.agents.erebos.generators._base import (
    ComposedClaim,
    SwarmState,
)


MIN_KILL_FRACTION = 0.50  # at least 50% rejected
MIN_SURVIVORS = 2          # need at least 2 PROMOTED to find shared property
MIN_TOTAL = 5              # need pool of at least 5 to have a kill rate


def _payload_keys(row: dict) -> set:
    extras = row.get("extras", {}) or {}
    payload = extras.get("composition_payload", {}) or {}
    return set(payload.keys())


class ExceptionMinerGenerator:
    id = "g11_exception_miner"
    name = "Exception Miner"
    spec_phase = 3
    feasibility_tier = "B"
    reasoning_tier = "R3"
    expected_kill_pattern = "out_of_sample_failure"

    def _group_by_generator(self, state: SwarmState) -> dict:
        """Bucket the Erebos self-ledger by the originating plugin
        (parent_plugin_id from claim_payload)."""
        out: dict[str, list[dict]] = {}
        for r in state.erebos_self_ledger:
            cp = r.get("claim_payload") or {}
            plugin = cp.get("plugin_id", "unknown")
            out.setdefault(plugin, []).append(r)
        return out

    def _high_kill_cohort_with_survivors(
        self, rows: list[dict]
    ) -> Optional[dict]:
        """Return the survivors + total + shared-key candidate
        if rows pass the high-kill cohort criteria, else None."""
        if len(rows) < MIN_TOTAL:
            return None
        survivors = [r for r in rows if r.get("verdict") == "PROMOTED"]
        rejected = [r for r in rows if r.get("verdict") == "REJECTED"]
        if len(survivors) < MIN_SURVIVORS:
            return None
        kill_rate = len(rejected) / max(1, len(rows))
        if kill_rate < MIN_KILL_FRACTION:
            return None
        # Find keys present in ALL survivors but NOT in all-rows
        survivor_keys = set.intersection(*(_payload_keys(r) for r in survivors))
        all_keys = set.union(*(_payload_keys(r) for r in rows))
        all_in_common = set.intersection(*(_payload_keys(r) for r in rows))
        # Hidden property candidate: keys in ALL survivors but NOT
        # in all-rows-in-common
        hidden = survivor_keys - all_in_common
        if not hidden:
            return None
        return {
            "survivors": survivors,
            "rejected": rejected,
            "total": rows,
            "kill_rate": kill_rate,
            "hidden_keys": sorted(hidden),
        }

    def applicable(self, state: SwarmState) -> bool:
        groups = self._group_by_generator(state)
        for plugin, rows in groups.items():
            cohort = self._high_kill_cohort_with_survivors(rows)
            if cohort is None:
                continue
            key = f"{self.id}|{plugin}|{','.join(cohort['hidden_keys'])}"
            if key not in state.tried_pairs:
                return True
        return False

    def generate(self, state: SwarmState) -> Optional[ComposedClaim]:
        groups = self._group_by_generator(state)
        for plugin, rows in sorted(
            groups.items(), key=lambda x: -len(x[1])
        ):
            cohort = self._high_kill_cohort_with_survivors(rows)
            if cohort is None:
                continue
            key = f"{self.id}|{plugin}|{','.join(cohort['hidden_keys'])}"
            if key in state.tried_pairs:
                continue
            return self._build_claim(plugin, cohort)
        return None

    def _build_claim(self, plugin_id: str, cohort: dict) -> ComposedClaim:
        survivors = cohort["survivors"]
        kill_rate = cohort["kill_rate"]
        hidden_keys = cohort["hidden_keys"]
        n_total = len(cohort["total"])
        n_surv = len(survivors)

        composed_id = (
            f"EREBOS-G11-survivors_of_{plugin_id}_share_{','.join(hidden_keys)[:40]}"
        )

        composition_text = (
            f"Exception-mining claim {composed_id}: "
            f"in the {n_total} emissions from generator `{plugin_id}`, "
            f"{int(kill_rate * 100)}% were REJECTED, but {n_surv} "
            f"PROMOTED. The hypothesis: those {n_surv} survivors are "
            f"strictly defined by the shared hidden property H = "
            f"{hidden_keys}. Falsification: generate new claims that "
            f"explicitly carry H and feed them through `{plugin_id}`'s "
            f"falsification route; if their survival rate matches the "
            f"baseline (~{kill_rate * 100:.0f}% rejection), H is NOT "
            f"actually a survival-discriminator (kill_pattern = "
            f"out_of_sample_failure)."
        )

        return ComposedClaim(
            plugin_id=self.id,
            composed_id=composed_id,
            input_provenance={
                "parent_plugin_id": plugin_id,
                "n_total_in_pool": n_total,
                "n_survivors": n_surv,
                "kill_rate": round(kill_rate, 4),
                "hidden_property_keys": hidden_keys,
                "survivor_record_ids": [s.get("record_id") for s in survivors[:5]],
            },
            transformation_description=(
                f"Bucket erebos_self_ledger by parent plugin_id; "
                f"identify cohorts with kill_rate >= "
                f"{MIN_KILL_FRACTION} AND survivors >= {MIN_SURVIVORS}; "
                f"intersect payload-keys across survivors; subtract "
                f"all-row intersection to find survivor-distinctive "
                f"keys."
            ),
            output_claim_text=composition_text,
            falsification_route=(
                f"Composition-aware loader generates new candidate "
                f"claims that explicitly include hidden_property_keys "
                f"{hidden_keys} in their composition_payload, then "
                f"runs them through the {plugin_id} falsification "
                f"route. Compare new-cohort survival rate to baseline."
                f" If new-cohort rate ~= baseline rate, hidden "
                f"property was coincidental -- kill_pattern = "
                f"out_of_sample_failure. Composition loader unbuilt; "
                f"v0.12+."
            ),
            expected_kill_pattern="out_of_sample_failure",
            loader_feasibility_note=(
                "Tier B: cohort detection runs in Erebos itself. "
                "Composition loader needs to invoke the parent "
                "generator's generate() with payloads stuffed with "
                "the hidden keys -- requires generator-side support "
                "for parameterized payload injection."
            ),
            parent_record_ids=[s.get("record_id", "") for s in survivors],
            composition_payload={
                "hidden_property_keys": hidden_keys,
                "parent_plugin_id": plugin_id,
                "baseline_kill_rate": kill_rate,
                "n_survivors": n_surv,
            },
            extras={"cohort_type": "high_kill_with_survivors"},
        )
