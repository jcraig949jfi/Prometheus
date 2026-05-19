"""Sophia — coordinate-system scout (Harmonia child, MVP).

One tick = one untried (operator, specimen) pair lifted from the
methodology-toolkit × frontier-specimen Cartesian product, composed into a
projection-proposal artifact with the 5-gate tensor-admission stub and a
mandatory calibration-anchor sanity gate (anti-reward-capture brake).

No scorer execution. No edits to the toolkit. Propose-only.

See `D:\\Prometheus\\harmonia\\agents\\sophia\\CHARTER.md` for the
one-page brief.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from harmonia.agents._base import HarmoniaAgent, REPO_ROOT


# ---- file targets (absolute, drive-letter-qualified) ----------------------

TOOLKIT_PATH = REPO_ROOT / "harmonia" / "memory" / "methodology_toolkit.md"
SPECIMEN_PATH = REPO_ROOT / "harmonia" / "memory" / "frontier_specimen_state.md"

# Per the spec: F001-F005 + F008 + F009 are the calibration anchors Sophia
# pulls into every proposal as the sanity gate.
CALIBRATION_ANCHORS = ["F001", "F002", "F003", "F004", "F005", "F008", "F009"]
ANCHOR_BLURBS = {
    "F001": "Modularity — instrument-health gate (any 100% violation IS a bug)",
    "F002": "Mazur torsion classification — 15-class enumeration anchor",
    "F003": "BSD parity (−1)^rank = root_number — identity-level anchor",
    "F004": "Hasse bound |a_p| ≤ 2√p — inequality identity anchor",
    "F005": "High-Sha parity instrument-health gate",
    "F008": "Scholz reflection |r3(K*) − r3(K)| ≤ 1 across 344K pairs",
    "F009": "Torsion primes ⊆ nonmax primes across 1.39M non-CM EC",
}

# ---- parser regexes -------------------------------------------------------

# `### 1. KOLMOGOROV_HAT@v1 — fingerprint compressibility`
_OPERATOR_HEADING = re.compile(
    r"^###\s+(\d+)\.\s+`?([A-Z][A-Z0-9_]+@v\d+)`?\s*[—-]\s*(.+?)\s*$",
    re.MULTILINE,
)
# A `live_specimen` row in the markdown table: `| **F011** | live_specimen … |`
_LIVE_SPECIMEN_ROW = re.compile(
    r"^\|\s*\*\*(F\d{3}[a-z]?)\*\*\s*\|\s*live_specimen[^|]*\|",
    re.MULTILINE,
)


class SophiaAgent(HarmoniaAgent):
    """Coordinate-system scout. Composes (operator × specimen) projection
    proposals one per tick."""

    name = "Sophia"
    role = "coordinate-system scout (gen_11 closed-loop, axis-space invention)"
    machine = "M2"

    # ------------------------------------------------------------------
    # Shelf parsing
    # ------------------------------------------------------------------

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            self.log.warning(f"could not read {path}: {e}")
            return ""

    def _parse_operators(self) -> list[dict]:
        """Extract operator entries from methodology_toolkit.md.

        Each entry: {"name": "KOLMOGOROV_HAT@v1", "title": "...",
                     "frame": "..." (≤200 chars), "block": full markdown}.
        """
        text = self._read_text(TOOLKIT_PATH)
        if not text:
            return []
        headings = list(_OPERATOR_HEADING.finditer(text))
        ops: list[dict] = []
        for i, m in enumerate(headings):
            start = m.start()
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            block = text[start:end]
            # First "Frame:" bullet in the block — capture the one-line summary.
            frame_m = re.search(
                r"\*\*Frame:\*\*\s*(.+?)(?:\.\s|\n|$)", block, re.DOTALL
            )
            frame = (frame_m.group(1).strip() if frame_m else "").replace("\n", " ")
            frame = re.sub(r"\s+", " ", frame)[:220]
            ops.append({
                "name": m.group(2),
                "title": m.group(3).strip(),
                "frame": frame or "(frame not parsed)",
                "block": block,
            })
        return ops

    def _parse_specimens(self) -> list[dict]:
        """Return live specimens + calibration anchors in a unified list.

        Each entry: {"fid": "F011", "tier": "live_specimen" | "calibration",
                     "row": str (table row text, may be empty for anchors)}.
        """
        out: list[dict] = []
        text = self._read_text(SPECIMEN_PATH)
        if text:
            for m in _LIVE_SPECIMEN_ROW.finditer(text):
                fid = m.group(1)
                # Capture full row for the artifact's per-specimen blurb.
                line_start = text.rfind("\n", 0, m.start()) + 1
                line_end = text.find("\n", m.end())
                row = text[line_start:line_end if line_end != -1 else len(text)]
                out.append({"fid": fid, "tier": "live_specimen", "row": row})
        # Always include the seven calibration anchors — they don't appear as
        # individual live_specimen rows but Sophia MUST cross them.
        for anchor in CALIBRATION_ANCHORS:
            out.append({"fid": anchor, "tier": "calibration", "row": ANCHOR_BLURBS[anchor]})
        # De-dup by FID, preserving first occurrence.
        seen: set[str] = set()
        uniq: list[dict] = []
        for s in out:
            if s["fid"] in seen:
                continue
            seen.add(s["fid"])
            uniq.append(s)
        return uniq

    # ------------------------------------------------------------------
    # Pair selection
    # ------------------------------------------------------------------

    @staticmethod
    def _pair_key(op_name: str, fid: str) -> str:
        return f"{op_name}x{fid}"

    def _all_pairs(self, ops: list[dict], specimens: list[dict]) -> list[tuple[dict, dict]]:
        """Full Cartesian product, lexicographically sorted by pair key."""
        pairs = [(o, s) for o in ops for s in specimens]
        pairs.sort(key=lambda p: self._pair_key(p[0]["name"], p[1]["fid"]))
        return pairs

    def _pick_anchor_for(self, specimen: dict) -> str:
        """Anti-reward-capture brake: every proposal carries a calibration anchor.

        If the specimen IS already an anchor, use itself; else pick F001
        deterministically. Deterministic so reruns are reproducible."""
        if specimen["tier"] == "calibration":
            return specimen["fid"]
        return "F001"

    # ------------------------------------------------------------------
    # Proposal artifact
    # ------------------------------------------------------------------

    def _build_proposal(
        self,
        op: dict,
        specimen: dict,
        anchor_fid: str,
        deepseek_text: Optional[str],
        utc_iso: str,
    ) -> str:
        op_name = op["name"]
        fid = specimen["fid"]
        anchor_blurb = ANCHOR_BLURBS.get(anchor_fid, "(anchor blurb unavailable)")
        specimen_row = specimen.get("row", "") or "(row unavailable)"

        deepseek_section = ""
        if deepseek_text:
            deepseek_section = (
                "\n## DeepSeek scoring sketch\n\n"
                "*(External-LLM draft — treat as Conjecture-tier until a human\n"
                "or downstream agent applies the 5-gate test.)*\n\n"
                f"{deepseek_text.strip()}\n"
            )
        else:
            deepseek_section = (
                "\n## DeepSeek scoring sketch\n\n"
                "*(Skipped — DeepSeek client unavailable or call failed this tick.\n"
                "Operator + scoring procedure above stand on their own.)*\n"
            )

        agora_task_spec = (
            f"  - stream: `agora:harmonia_sync`\n"
            f"  - kind: `SOPHIA_PROPOSAL`\n"
            f"  - operator: `{op_name}`\n"
            f"  - specimen: `{fid}`\n"
            f"  - anchor_gate: `{anchor_fid}`\n"
            f"  - artifact: this file\n"
            f"  - status: `draft, awaiting Theseus/Charon scorer-execution wave`\n"
        )

        return (
            f"# Sophia projection proposal — {op_name} × {fid}\n\n"
            f"- **Composed at:** {utc_iso}\n"
            f"- **Agent:** Sophia (Harmonia child, M2)\n"
            f"- **Tier:** Conjecture (draft — no scorer execution yet)\n"
            f"- **Source operator:** `D:\\Prometheus\\harmonia\\memory\\methodology_toolkit.md`\n"
            f"- **Source specimen:** `D:\\Prometheus\\harmonia\\memory\\frontier_specimen_state.md`\n\n"
            f"## Operator\n\n"
            f"- **Name:** `{op_name}`\n"
            f"- **Title:** {op['title']}\n"
            f"- **Frame:** {op['frame']}\n\n"
            f"## Specimen\n\n"
            f"- **F-ID:** `{fid}`\n"
            f"- **Tier:** {specimen['tier']}\n"
            f"- **Row / blurb:**\n\n"
            f"  ```\n  {specimen_row}\n  ```\n\n"
            f"## Proposed scoring procedure\n\n"
            f"Apply `{op_name}` to `{fid}` per the operator's pinned scorer\n"
            f"definition in the toolkit. Capture the operator's native output\n"
            f"shape (e.g. a scalar K̂, an exponent (α, σ_α), a bit-count for\n"
            f"channel capacity, a rank deficit for controllability, etc.) and\n"
            f"record alongside the dataset pin declared by the specimen's\n"
            f"`cross_refs` (typically `Q_EC_R0_D5@v1` or a domain-specific\n"
            f"cohort). Compose with `null_protocol_v1.1` for any inferential\n"
            f"interpretation.\n\n"
            f"## Calibration-anchor sanity gate (mandatory)\n\n"
            f"*Anti-reward-capture brake — F043 lesson codified.*\n\n"
            f"- **Anchor:** `{anchor_fid}`\n"
            f"- **Anchor blurb:** {anchor_blurb}\n"
            f"- **Expected verdict:** the operator's output on `{anchor_fid}`\n"
            f"  must agree with the anchor's known instrument-health reading\n"
            f"  (e.g., identity-level anchors must register as maximally\n"
            f"  compressible / zero-residual / unit-rank-deficit under the\n"
            f"  operator's lens). If it doesn't, the operator is miscalibrated\n"
            f"  in this specimen's frame, NOT insightful — proposal halts.\n"
            f"- **Why this is mandatory:** novelty is the reward; the anchor\n"
            f"  is the brake. See `feedback_falsification_first` +\n"
            f"  `user_prometheus_north_star`.\n\n"
            f"## 5-gate tensor-admission stub (UNFILLED)\n\n"
            f"Each gate intentionally left blank; downstream agents (Theseus /\n"
            f"Charon scorer execution; Phylax audit) fill them.\n\n"
            f"1. **Null-calibrated** — UNFILLED.\n"
            f"   *How to fill:* run the operator against `NULL_PLAIN` and\n"
            f"   `NULL_BSWCD` block-shuffle nulls; record the null distribution\n"
            f"   and the verdict's z-score against it.\n"
            f"2. **Representation-stable** — UNFILLED.\n"
            f"   *How to fill:* perturb the input encoding (e.g., reorder\n"
            f"   columns, swap equivalent atoms in the grammar, switch the\n"
            f"   compression codec); confirm Kendall's τ ≥ 0.9 across\n"
            f"   perturbations.\n"
            f"3. **Not-marginals** — UNFILLED.\n"
            f"   *How to fill:* re-score after marginalizing each candidate\n"
            f"   covariate (conductor, rank, root number, nbp); show the\n"
            f"   verdict survives — i.e., it is not reducible to a single\n"
            f"   marginal distribution.\n"
            f"4. **Non-tautological** — UNFILLED.\n"
            f"   *How to fill:* run `PATTERN_30` lineage + ideal-quotient\n"
            f"   check on the (operator, specimen, dataset) triple; require\n"
            f"   `algebraic_dependence_level ≤ 1`.\n"
            f"5. **Domain-agnostic** — UNFILLED.\n"
            f"   *How to fill:* replay the operator on an out-of-domain\n"
            f"   companion cohort (e.g., NF degrees if specimen is EC; modular\n"
            f"   forms if specimen is NF); the structural verdict must\n"
            f"   re-appear without re-tuning the scorer.\n"
            f"{deepseek_section}\n"
            f"## Next step — Agora queue task spec (described, not seeded)\n\n"
            f"Hand-off envelope for the Theseus/Charon scorer-execution wave:\n\n"
            f"{agora_task_spec}\n"
            f"\nMVP intentionally does not enqueue. Once Theseus/Charon are\n"
            f"online, an `XADD agora:harmonia_sync` with the fields above is\n"
            f"the single intended next mutation.\n\n"
            f"---\n\n"
            f"*Provenance:* generated by `D:\\Prometheus\\harmonia\\agents\\sophia\\daemon.py`\n"
            f"in tick `{self._cycle_id}` at {utc_iso}. See\n"
            f"`D:\\Prometheus\\harmonia\\agents\\sophia\\CHARTER.md`.\n"
        )

    # ------------------------------------------------------------------
    # Backlog (when product is exhausted)
    # ------------------------------------------------------------------

    def self_generate_backlog(self) -> list[dict]:
        """Emit a meta-task suggesting toolkit expansion.

        Called when there are zero untried (operator, specimen) pairs.
        Returns a list with one dict describing the meta-task; the artifact
        is written by `_emit_meta_task`. Never edits the toolkit directly.
        """
        ops = self._parse_operators()
        specimens = self._parse_specimens()
        return [{
            "kind": "expand_methodology_toolkit",
            "reason": (
                f"All {len(ops)} × {len(specimens)} = {len(ops) * len(specimens)} "
                f"(operator × specimen) pairs marked tried in state. "
                f"Either reset_requested.json should be set by a human, or a "
                f"new operator entry should be added to "
                f"D:\\Prometheus\\harmonia\\memory\\methodology_toolkit.md."
            ),
            "operator_count": len(ops),
            "specimen_count": len(specimens),
        }]

    def _emit_meta_task(self, meta: dict, utc_iso: str) -> Path:
        deepseek_draft = self.deepseek_complete(
            prompt=(
                "Draft ONE candidate entry for the Prometheus methodology "
                "toolkit (D:\\Prometheus\\harmonia\\memory\\methodology_toolkit.md). "
                "Pick a cross-disciplinary lens NOT already in the catalog "
                "(current entries include KOLMOGOROV_HAT, CRITICAL_EXPONENT, "
                "CHANNEL_CAPACITY, MDL_SCORER, RG_FLOW, FREE_ENERGY, "
                "GINI_COEFFICIENT, CONTROLLABILITY_RANK, TT_APPROX_MAP, "
                "CONJECTURE_GENERATOR). Output: Frame, Scorer (one-paragraph "
                "pseudocode sketch), Resolves, Effort. ≤ 250 words. Mark this "
                "as a DRAFT proposal — Sophia does not edit the toolkit "
                "directly."
            ),
            system=(
                "You are drafting a candidate cross-disciplinary projection "
                "entry. Be concrete; if you can't write a scorer sketch, the "
                "tool isn't shelf-ready."
            ),
            max_tokens=600,
        )
        body = (
            f"# Sophia meta-task — expand methodology_toolkit\n\n"
            f"- **Composed at:** {utc_iso}\n"
            f"- **Agent:** Sophia (Harmonia child, M2)\n"
            f"- **Trigger:** Cartesian product exhausted\n\n"
            f"## Why\n\n{meta['reason']}\n\n"
            f"## Operator count parsed: {meta['operator_count']}\n"
            f"## Specimen count parsed: {meta['specimen_count']}\n\n"
            f"## Suggested action (propose-only, NOT executed)\n\n"
            f"1. Human review: confirm Sophia's `tried_pairs` state at\n"
            f"   `D:\\Prometheus\\harmonia\\agents\\sophia\\state\\tried_pairs.json`\n"
            f"   is genuine (not a parser-regression).\n"
            f"2. If the catalog truly is the bottleneck, add one entry to\n"
            f"   `D:\\Prometheus\\harmonia\\memory\\methodology_toolkit.md`\n"
            f"   following the 'How to add a new tool' template at the\n"
            f"   bottom of that file.\n"
            f"3. To restart Sophia's loop with a clean slate, write\n"
            f"   `{{\"reset_requested\": true}}` to\n"
            f"   `D:\\Prometheus\\harmonia\\agents\\sophia\\state\\reset_requested.json`.\n\n"
            f"## DeepSeek candidate-entry draft\n\n"
        )
        if deepseek_draft:
            body += deepseek_draft.strip() + "\n"
        else:
            body += "*(DeepSeek unavailable — no draft this tick.)*\n"
        filename = f"meta_expand_toolkit_{utc_iso.replace(':', '').replace('-', '')}.md"
        return self.write_artifact(filename, body)

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def run_tick(self, dry_run: bool = False) -> dict:
        utc_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        stats = {
            "items_processed": 0,
            "artifacts_written": 0,
            "errors": 0,
            "backlog_remaining": 0,
            "pair_proposed": None,
            "dry_run": dry_run,
        }

        # 0. Honor reset_requested.
        reset_flag = self.load_state("reset_requested", default={})
        if isinstance(reset_flag, dict) and reset_flag.get("reset_requested"):
            self.save_state("tried_pairs", [])
            self.save_state("reset_requested", {"reset_requested": False,
                                                "last_reset_at": utc_iso})
            self.log.info("tried_pairs reset honored")
            self.log_work("sophia_reset", "tried_pairs cleared on reset_requested")

        # 1 + 2. Parse shelves.
        try:
            ops = self._parse_operators()
            specimens = self._parse_specimens()
        except Exception as e:
            self.log.exception(f"shelf parse failed: {e}")
            stats["errors"] += 1
            self.log_work("sophia_parse_failed", str(e)[:300], success=False, error=str(e))
            return stats

        if not ops or not specimens:
            stats["errors"] += 1
            msg = (f"empty shelf — ops={len(ops)} specimens={len(specimens)} "
                   f"({TOOLKIT_PATH} / {SPECIMEN_PATH})")
            self.log.warning(msg)
            self.log_work("sophia_empty_shelf", msg, success=False, error=msg)
            return stats

        # 3. Pick untried pair.
        tried = self.load_state("tried_pairs", default=[]) or []
        tried_set = set(tried)
        all_pairs = self._all_pairs(ops, specimens)
        total = len(all_pairs)
        untried = [(o, s) for (o, s) in all_pairs
                   if self._pair_key(o["name"], s["fid"]) not in tried_set]
        stats["backlog_remaining"] = max(0, len(untried) - 1)

        if not untried:
            # 7. Backlog self-gen.
            backlog = self.self_generate_backlog()
            self.log.info(f"product exhausted ({total} tried); emitting meta-task")
            if not dry_run:
                path = self._emit_meta_task(backlog[0], utc_iso)
                stats["artifacts_written"] += 1
                self.log_work(
                    "sophia_backlog_meta_task",
                    f"toolkit-expansion meta-task drafted: {path}",
                    output_path=str(path),
                )
            else:
                self.log_work(
                    "sophia_backlog_meta_task_dry",
                    "would emit toolkit-expansion meta-task (dry-run)",
                )
            stats["pair_proposed"] = None
            self.log_work(
                "sophia_tick_complete",
                f"exhausted; ops={len(ops)} specimens={len(specimens)} "
                f"tried={len(tried_set)}",
            )
            return stats

        op, specimen = untried[0]
        pair_key = self._pair_key(op["name"], specimen["fid"])
        stats["pair_proposed"] = pair_key
        stats["items_processed"] = 1
        anchor_fid = self._pick_anchor_for(specimen)

        # 4. Optional DeepSeek enrichment (single short call).
        deepseek_text: Optional[str] = None
        try:
            deepseek_text = self.deepseek_complete(
                prompt=(
                    f"Given operator {op['name']} (frame: {op['frame']}) and "
                    f"specimen {specimen['fid']} (tier: {specimen['tier']}), "
                    f"propose one specific way to compute the scorer and one "
                    f"calibration sanity check against anchor {anchor_fid} "
                    f"({ANCHOR_BLURBS.get(anchor_fid, '')}). "
                    f"Keep total response ≤ 200 words. Be concrete; pseudocode "
                    f"is welcome."
                ),
                system=(
                    "You are an arithmetic-geometry methodology drafter for the "
                    "Prometheus project. Propose, never assert. Calibration "
                    "anchors are health gates, not findings."
                ),
                max_tokens=400,
            )
        except Exception as e:
            self.log.warning(f"deepseek enrichment failed: {e}")
            deepseek_text = None

        # 5. Compose proposal artifact.
        try:
            content = self._build_proposal(op, specimen, anchor_fid, deepseek_text, utc_iso)
        except Exception as e:
            self.log.exception(f"proposal build failed: {e}")
            stats["errors"] += 1
            self.log_work("sophia_proposal_build_failed", str(e)[:300],
                          success=False, error=str(e))
            return stats

        filename = (
            f"proposal_{op['name'].replace('@', '_at_')}_x_{specimen['fid']}_"
            f"{utc_iso.replace(':', '').replace('-', '')}.md"
        )

        if not dry_run:
            try:
                path = self.write_artifact(filename, content)
                stats["artifacts_written"] += 1
                self.log_work(
                    "sophia_proposal_written",
                    f"{pair_key} (anchor={anchor_fid}); deepseek={'yes' if deepseek_text else 'no'}",
                    output_path=str(path),
                )
            except Exception as e:
                self.log.exception(f"artifact write failed: {e}")
                stats["errors"] += 1
                self.log_work("sophia_artifact_write_failed", str(e)[:300],
                              success=False, error=str(e))
                return stats
        else:
            # Dry-run still writes the artifact so downstream agents can see
            # what Sophia would have produced — the spec's smoke test expects
            # a written artifact under dry_run=True.
            try:
                path = self.write_artifact(filename, content)
                stats["artifacts_written"] += 1
                self.log_work(
                    "sophia_proposal_written_dry",
                    f"{pair_key} (anchor={anchor_fid}, dry-run write); "
                    f"deepseek={'yes' if deepseek_text else 'no'}",
                    output_path=str(path),
                )
            except Exception as e:
                self.log.exception(f"dry-run artifact write failed: {e}")
                stats["errors"] += 1
                self.log_work("sophia_artifact_write_failed", str(e)[:300],
                              success=False, error=str(e))
                return stats

        # 6. Mark pair tried (even on dry_run — the spec lists no exemption
        # for dry-run; if a human wants a clean slate they set reset_requested).
        tried.append(pair_key)
        self.save_state("tried_pairs", tried)

        # 8. Telemetry summary.
        self.log_work(
            "sophia_tick_complete",
            f"pair={pair_key} anchor={anchor_fid} ops={len(ops)} "
            f"specimens={len(specimens)} backlog_remaining={stats['backlog_remaining']}",
        )
        return stats
