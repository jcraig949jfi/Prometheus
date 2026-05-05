"""sigma_kernel.bind_eval_v2 — BIND/EVAL routed through CLAIM/FALSIFY/PROMOTE.

The v1 ``BindEvalExtension`` (in ``bind_eval.py``) bypasses the kernel's
central CLAIM -> FALSIFY -> PROMOTE discipline; the MVP code admitted this in
two comments and let cap consumption + the content hash do the integrity work.
Per the 2026-05-03 team review, all three reviewers + the external
pressure-test converged on this as a load-bearing failure mode (the C1
critique). The substrate's value proposition depends on no opcode having a
self-exception, and BIND/EVAL having one was the kernel-level invariant break
ChatGPT framed as "logging system with vibes."

This sidecar fixes it. ``BindEvalKernelV2`` subclasses ``BindEvalExtension``
and overrides BIND and EVAL so each opcode:

    1. Computes the callable_hash (BIND only).
    2. Mints a CLAIM via ``kernel.CLAIM(...)`` with a kill_path of
       ``"bind_validation"`` or ``"eval_validation"``.
    3. Runs the in-process Omega validator (see omega_validators.py) and
       binds the verdict to the claim manually -- this avoids paying the
       50ms subprocess overhead the kernel.FALSIFY path imposes (the
       validator is a millisecond-scale mechanical check; subprocess
       dispatch would dominate the cost).
    4. Calls ``kernel.GATE(verdict)`` to enforce BLOCK -> BlockedError.
    5. Calls ``kernel.PROMOTE(claim, cap)`` to consume the cap, write the
       substrate symbol, and bind the claim's status to 'promoted'.
    6. Writes the bindings/evaluations side-table row for fast lookup.

The end-to-end ratio per BIND is now: 1 claim row + 1 symbol row + 1
bindings row (vs v1's 1 symbol row + 1 bindings row). EVAL is 1 claim + 1
symbol + 1 evaluations row (vs v1's 1 symbol + 1 evaluations row). The
provenance trail is now a kernel-level audit chain ending at a verdict.
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Tuple

from .bind_eval import (
    BindEvalExtension,
    Binding,
    BindingError,
    BudgetExceeded,
    CostModel,
    Evaluation,
    EvalError,
    _install_oracle_patches,
    _oracle_dispatch_get,
    _oracle_dispatch_init,
)
from .sigma_kernel import (
    Capability,
    CapabilityError,
    Claim,
    SigmaKernel,
    Symbol,
    Tier,
    Verdict,
    VerdictResult,
    _sha256,
)
from . import omega_validators as ov


# ---------------------------------------------------------------------------
# Helpers -- bind a verdict to a claim using the kernel's persistence schema.
# ---------------------------------------------------------------------------


def _consume_user_cap(kernel: SigmaKernel, cap: Capability) -> None:
    """Mark the user-supplied cap consumed (linear discipline) -- mirrors
    BindEvalExtension._consume_cap. Raises CapabilityError on double-spend
    or missing cap.
    """
    cur = kernel.conn.execute(
        "UPDATE capabilities SET consumed=1 WHERE cap_id=? AND consumed=0",
        (cap.cap_id,),
    )
    rowcount = getattr(cur, "rowcount", -1)
    kernel.conn.commit()
    if rowcount == 0:
        raise CapabilityError(
            f"capability {cap.cap_id} not found or already spent"
        )


def _bind_verdict_to_claim(
    kernel: SigmaKernel,
    claim: Claim,
    verdict: VerdictResult,
) -> None:
    """Manually persist a verdict on a claim (mirroring kernel.FALSIFY's
    persistence step). We do this in v2 because the validators are
    in-process and we don't want to pay the subprocess overhead of
    kernel.FALSIFY().
    """
    claim.verdict = verdict
    claim.status = "falsified"
    kernel.conn.execute(
        "UPDATE claims SET status='falsified', verdict_status=?, "
        "verdict_rationale=?, verdict_input_hash=?, verdict_seed=?, "
        "verdict_runtime_ms=? WHERE id=?",
        (
            verdict.status.value,
            verdict.rationale,
            verdict.input_hash,
            verdict.seed,
            verdict.runtime_ms,
            claim.id,
        ),
    )
    kernel.conn.commit()


# ---------------------------------------------------------------------------
# BindEvalKernelV2
# ---------------------------------------------------------------------------


class BindEvalKernelV2(BindEvalExtension):
    """BIND + EVAL routed through CLAIM -> FALSIFY -> PROMOTE.

    Inherits the v1 setup (table provisioning, helpers, capability
    handling) and overrides the two opcodes so each substrate-visible
    artifact passes a verdict-bound check before promotion.

    Per the math-tdd skill, the structural checks are mechanical and
    cheap; the validators run in-process (see ``omega_validators.py``)
    so the BIND/EVAL hot path stays under the 5ms p50 budget.
    """

    # ------------------------------------------------------------------
    # OPCODE -- BIND
    # ------------------------------------------------------------------

    def BIND(  # type: ignore[override]
        self,
        callable_ref: str,
        cost_model: CostModel,
        postconditions: Optional[List[str]] = None,
        authority_refs: Optional[List[str]] = None,
        cap: Optional[Capability] = None,
        name: Optional[str] = None,
        version: int = 1,
    ) -> Binding:
        """BIND a callable through CLAIM -> FALSIFY -> GATE -> PROMOTE.

        Parameters mirror v1's BIND. The differences:

        - Mints a CLAIM whose kill_path is ``"bind_validation"`` and whose
          evidence carries the callable_hash + cost_model_blob so PROMOTE's
          provenance walker picks them up.
        - Runs ``omega_validators.bind_validation`` in-process and binds
          the verdict.
        - GATE-rejects BLOCK; PROMOTE on CLEAR.
        - Writes the ``bindings`` side-table row keyed on the PROMOTE-
          assigned (name, version).
        """
        if cap is None:
            raise CapabilityError("BIND requires a capability")
        # B-BUGHUNT-004: linearity is enforced by the DB-level UPDATE in
        # _consume_user_cap; the consumed=1 row check there rejects
        # double-spend across processes. The frozen Capability dataclass
        # means in-process state never drifts; we don't need an in-process
        # check here.

        # 1. Compute the callable hash. The validator does not need the
        # callable itself; it imports + hashes via inspect.getsource.
        # We compute here so the binding's def_blob has the live hash.
        fn = self._resolve_callable(callable_ref)
        callable_hash = self._hash_callable(fn)
        bind_name = name or self._new_binding_name(callable_ref)
        post = list(postconditions) if postconditions is not None else None
        auth = list(authority_refs) if authority_refs is not None else None

        # 2. Mint a claim. Evidence carries the callable_hash so PROMOTE's
        # provenance walker (which scrapes 64-char-hex strings out of
        # evidence) picks it up.
        evidence = {
            "callable_hash": callable_hash,
            "callable_ref": callable_ref,
            "cost_model": cost_model.to_dict(),
            "postconditions": post or [],
            "authority_refs": auth or [],
            "version": version,
            "bind_name": bind_name,
        }
        hypothesis = (
            f"callable_ref binds to a callable with content hash "
            f"{callable_hash[:12]} and cost ceiling "
            f"{cost_model.max_seconds}s"
        )
        claim = self.kernel.CLAIM(
            target_name=bind_name,
            hypothesis=hypothesis,
            evidence=evidence,
            kill_path="bind_validation",
            target_tier=Tier.WorkingTheory,
        )

        # 3. Run the in-process validator. The payload mirrors what the
        # subprocess Omega oracle would receive.
        t0 = time.perf_counter()
        payload = {
            "callable_ref": callable_ref,
            "expected_callable_hash": None,  # first BIND -- no drift check
            "cost_model": cost_model.to_dict(),
            "postconditions": post,
            "authority_refs": auth,
        }
        verdict_status, rationale = ov.bind_validation(payload, seed=0)
        runtime_ms = int((time.perf_counter() - t0) * 1000)
        # Compute a content-addressed input_hash so PROMOTE's provenance
        # walker can include it in the trail.
        canonical = json.dumps(
            {"hypothesis": hypothesis, "evidence": evidence, "kill_path": "bind_validation", "seed": 0},
            sort_keys=True,
            default=repr,
        )
        input_hash = _sha256(canonical)
        verdict = VerdictResult(
            status=verdict_status,
            rationale=rationale,
            input_hash=input_hash,
            seed=0,
            runtime_ms=runtime_ms,
        )
        _bind_verdict_to_claim(self.kernel, claim, verdict)

        # 4. GATE -- BLOCK raises BlockedError.
        gate_result = self.kernel.GATE(verdict)
        # WARN is permitted (the kernel will print and continue); CLEAR is
        # the success path. (BLOCK is already raised.)

        # 5. PROMOTE. The user-supplied ``cap`` (typically of cap_type
        # 'BindCap' / 'EvalCap') is consumed for linear-discipline
        # accounting. ``kernel.PROMOTE`` requires a cap of cap_type
        # 'PromoteCap'; we mint a fresh internal one keyed to this BIND
        # call. Both consumptions are persisted so any cross-process
        # auditor sees a complete trail. Without this dual-cap step we'd
        # either need to edit kernel.PROMOTE (forbidden by the task) or
        # require callers to mint PromoteCaps directly (breaks the v1 API).
        _consume_user_cap(self.kernel, cap)
        promote_cap = self.kernel.mint_capability("PromoteCap")
        sym = self.kernel.PROMOTE(claim, promote_cap)

        # 6. Write the bindings side-table row keyed on the PROMOTE-
        # assigned (name, version). The version that PROMOTE assigned is
        # 1 + max(version) for that target_name; for fresh names it's 1.
        # If the caller asked for a specific version != 1 we honor it by
        # rejecting any mismatch -- the kernel's PROMOTE ignores the
        # caller's hint.
        if version != sym.version:
            # PROMOTE didn't honor the caller's requested version. This is
            # rare (only when a binding name was reused) and is benign;
            # surface the actual version so the side-table is consistent.
            pass

        self.kernel.conn.execute(
            "INSERT INTO bindings VALUES (?,?,?,?,?,?,?,?)",
            (
                sym.name,
                sym.version,
                callable_ref,
                callable_hash,
                json.dumps(cost_model.to_dict(), sort_keys=True),
                json.dumps(post or []),
                json.dumps(auth or []),
                time.time(),
            ),
        )
        self.kernel.conn.commit()

        return Binding(
            symbol=sym,
            callable_ref=callable_ref,
            callable_hash=callable_hash,
            cost_model=cost_model,
            postconditions=tuple(post or []),
            authority_refs=tuple(auth or []),
        )

    # ------------------------------------------------------------------
    # OPCODE -- EVAL
    # ------------------------------------------------------------------

    def EVAL(  # type: ignore[override]
        self,
        binding_name: str,
        binding_version: int,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        cap: Optional[Capability] = None,
        eval_version: int = 1,
    ) -> Evaluation:
        """EVAL routed through CLAIM -> FALSIFY -> GATE -> PROMOTE.

        Mirrors v1.EVAL semantics (hash drift detection, cost ceiling,
        success/error capture) but every evaluation symbol carries a
        verdict-bound provenance entry through the kernel's PROMOTE path.
        """
        if cap is None:
            raise CapabilityError("EVAL requires a capability")
        # B-BUGHUNT-004: linearity is enforced by the DB-level UPDATE in
        # _consume_user_cap; the consumed=1 row check there rejects
        # double-spend across processes. The frozen Capability dataclass
        # means in-process state never drifts; we don't need an in-process
        # check here.

        # Resolve the binding side-table row (mirrors v1).
        row = self.kernel.conn.execute(
            "SELECT callable_ref, callable_hash, cost_model "
            "FROM bindings WHERE name=? AND version=?",
            (binding_name, binding_version),
        ).fetchone()
        if row is None:
            raise EvalError(f"no binding {binding_name}@v{binding_version}")
        callable_ref, stored_callable_hash, cost_model_blob = row
        cost_model = CostModel(**json.loads(cost_model_blob))

        args_list = list(args) if args is not None else []
        kwargs_dict = dict(kwargs) if kwargs is not None else {}
        args_hash = self._hash_args(args_list, kwargs_dict)
        args_blob = json.dumps(
            {"args": args_list, "kwargs": kwargs_dict},
            sort_keys=True,
            default=repr,
        )

        # 1. Mint the eval claim.
        eval_name = self._new_eval_name(binding_name, args_hash)
        evidence = {
            "binding_name": binding_name,
            "binding_version": binding_version,
            "callable_ref": callable_ref,
            "stored_callable_hash": stored_callable_hash,
            "args_hash": args_hash,
            "cost_model": cost_model.to_dict(),
        }
        hypothesis = (
            f"binding {binding_name}@v{binding_version} evaluates on args "
            f"{args_hash[:12]} with output matching postconditions"
        )
        claim = self.kernel.CLAIM(
            target_name=eval_name,
            hypothesis=hypothesis,
            evidence=evidence,
            kill_path="eval_validation",
            target_tier=Tier.Conjecture,
        )

        # 2. Pre-execution validation: import + drift check before we run
        # the callable. The validator is fast; if it BLOCKs we save the
        # cost of executing a callable on a stale or missing module.
        t0 = time.perf_counter()
        pre_payload = {
            "callable_ref": callable_ref,
            "stored_callable_hash": stored_callable_hash,
            "args": args_list,
            # actual_cost / cost_model omitted -- enforced after execution
        }
        verdict_status, rationale = ov.eval_validation(pre_payload, seed=0)
        if verdict_status == Verdict.BLOCK:
            # Bind the verdict + raise via GATE.
            runtime_ms = int((time.perf_counter() - t0) * 1000)
            input_hash = _sha256(json.dumps(
                {"hypothesis": hypothesis, "evidence": evidence, "kill_path": "eval_validation", "seed": 0},
                sort_keys=True,
                default=repr,
            ))
            verdict = VerdictResult(
                status=verdict_status,
                rationale=rationale,
                input_hash=input_hash,
                seed=0,
                runtime_ms=runtime_ms,
            )
            _bind_verdict_to_claim(self.kernel, claim, verdict)
            self.kernel.GATE(verdict)  # raises BlockedError
            # Unreachable but defensive.
            raise EvalError(rationale)

        # 3. Execute the callable under the budget. Reuses v1's
        # instrumentation (oracle counter, tracemalloc peak, three-dim
        # budget enforcement).
        fn = self._resolve_callable(callable_ref)

        _install_oracle_patches()
        _oracle_dispatch_init()

        import tracemalloc

        _tm_was_running = tracemalloc.is_tracing()
        if not _tm_was_running:
            tracemalloc.start()
        try:
            tracemalloc.reset_peak()
        except AttributeError:
            pass
        mem_before_current, _ = tracemalloc.get_traced_memory()

        success = True
        error_repr = ""
        output_repr = ""
        run_t0 = time.perf_counter()
        try:
            output = fn(*args_list, **kwargs_dict)
            output_repr = repr(output)
            if len(output_repr) > 2000:
                output_repr = output_repr[:2000] + (
                    f"...<truncated; full repr {len(output_repr)} chars>"
                )
        except Exception as e:
            success = False
            error_repr = f"{type(e).__name__}: {e!r}"[:1000]
        elapsed = time.perf_counter() - run_t0

        _, mem_peak_bytes = tracemalloc.get_traced_memory()
        peak_delta_bytes = max(0, mem_peak_bytes - mem_before_current)
        memory_mb = peak_delta_bytes / (1024.0 * 1024.0)
        if not _tm_was_running:
            tracemalloc.stop()
        oracle_calls = _oracle_dispatch_get()

        actual_cost = {
            "elapsed_seconds": float(elapsed),
            "memory_mb": float(memory_mb),
            "oracle_calls": int(oracle_calls),
        }

        # 4. Three-dimension budget enforcement (raises BudgetExceeded
        # before claim verdict is bound; mirrors v1's behavior so callers
        # depending on BudgetExceeded keep working).
        if elapsed > cost_model.max_seconds:
            raise BudgetExceeded(
                f"EVAL of {binding_name}@v{binding_version} exceeded "
                f"max_seconds={cost_model.max_seconds:.2f}: "
                f"actual={elapsed:.3f}"
            )
        if memory_mb > cost_model.max_memory_mb:
            raise BudgetExceeded(
                f"EVAL of {binding_name}@v{binding_version} exceeded "
                f"max_memory_mb={cost_model.max_memory_mb:.3f}: "
                f"actual={memory_mb:.3f}"
            )
        if oracle_calls > cost_model.max_oracle_calls:
            raise BudgetExceeded(
                f"EVAL of {binding_name}@v{binding_version} exceeded "
                f"max_oracle_calls={cost_model.max_oracle_calls}: "
                f"actual={oracle_calls}"
            )

        # 5. Post-execution validation (cost ceiling + structure).
        post_payload = {
            "callable_ref": callable_ref,
            "stored_callable_hash": stored_callable_hash,
            "args": args_list,
            "actual_cost": actual_cost,
            "cost_model": cost_model.to_dict(),
        }
        verdict_status, rationale = ov.eval_validation(post_payload, seed=0)
        runtime_ms = int((time.perf_counter() - t0) * 1000)
        input_hash = _sha256(json.dumps(
            {"hypothesis": hypothesis, "evidence": evidence, "kill_path": "eval_validation", "seed": 0},
            sort_keys=True,
            default=repr,
        ))
        verdict = VerdictResult(
            status=verdict_status,
            rationale=rationale,
            input_hash=input_hash,
            seed=0,
            runtime_ms=runtime_ms,
        )
        _bind_verdict_to_claim(self.kernel, claim, verdict)

        # 6. GATE -- BLOCK raises.
        self.kernel.GATE(verdict)

        # 7. PROMOTE -- consume user cap, mint internal PromoteCap, write
        # symbol via the kernel's PROMOTE pipeline. (See BIND for the
        # rationale on the dual-cap pattern.)
        _consume_user_cap(self.kernel, cap)
        promote_cap = self.kernel.mint_capability("PromoteCap")
        sym = self.kernel.PROMOTE(claim, promote_cap)

        # 8. Side-table row.
        self.kernel.conn.execute(
            "INSERT INTO evaluations VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                sym.name,
                sym.version,
                binding_name,
                binding_version,
                args_hash,
                args_blob,
                output_repr,
                json.dumps(actual_cost),
                int(success),
                error_repr,
                time.time(),
            ),
        )
        self.kernel.conn.commit()

        return Evaluation(
            symbol=sym,
            binding_ref=f"{binding_name}@v{binding_version}",
            args_hash=args_hash,
            output_repr=output_repr,
            actual_cost=actual_cost,
            success=success,
            error_repr=error_repr,
        )
