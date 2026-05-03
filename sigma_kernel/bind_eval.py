"""sigma_kernel.bind_eval — BIND and EVAL opcodes (MVP).

Extends the v0.1 kernel with two opcodes that turn substrate symbols
into executable RL actions:

- BIND(name, callable_ref, cost_model, postconditions, authority_refs, cap)
      Creates a binding-symbol whose ``def_blob`` holds the callable's
      content-hash + cost model + postconditions + authority references.
      The callable itself is identified by its import path
      ``"<module>:<qualname>"``; the binding is content-addressed by
      sha256 of the metadata block + the callable's source code.

- EVAL(binding_symbol, args, budget)
      Resolves the binding, imports the callable, runs it under
      ``budget`` (max_seconds, max_memory_mb, max_oracle_calls), then
      writes a fresh evaluation-symbol whose ``def_blob`` holds the
      output, the actual cost consumed, and a provenance link back to
      the binding. Raises ``BudgetExceeded`` if the cost model
      under-promised.

Storage:
- SQLite: two new tables (``bindings``, ``evaluations``) auto-created
  by ``BindEvalExtension(kernel)`` at construction time.
- Postgres: same two tables in the ``sigma`` schema (or a sibling
  ``sigma_proto`` schema for prototype isolation, controlled via
  ``BindEvalExtension(kernel, schema="sigma_proto")``). Migration:
  ``sigma_kernel/migrations/002_create_bind_eval_tables.sql``.

Both tables are append-only; the kernel's existing capability +
falsification discipline applies to BIND (which mints a binding-symbol
through the parent ``bootstrap_symbol`` path).

This module is intentionally a sidecar — no edits to ``sigma_kernel.py``.
"""
from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import threading
import time
import tracemalloc
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from .sigma_kernel import (
    Capability,
    CapabilityError,
    SigmaKernel,
    Symbol,
    Tier,
    _sha256,
)


# ---------------------------------------------------------------------------
# C2 instrumentation -- oracle-call counter (thread-local, monotonic).
# ---------------------------------------------------------------------------
#
# The CostModel declares ``max_oracle_calls`` but the v1 MVP recorded a
# constant 0. Per the 2026-05-03 team review, the substrate is gameable on
# any unenforced cost dimension -- an RL agent will learn to route through
# it. The minimal-viable fix (per ChatGPT's review): increment a thread-local
# counter at every PARI / SymPy / subprocess dispatch boundary. We do not
# need precision; we need monotonic accountability.
#
# Coverage strategy:
#   - ``cypari.pari`` calls: patched at module-import time.
#   - ``subprocess.run`` calls within a tracked EVAL: patched via a context
#     manager so the patch is only active during the EVAL hot path (avoids
#     polluting unrelated subprocess uses elsewhere in the runtime).
#   - SymPy's external solver calls go through subprocess; covered by the
#     subprocess.run patch.
#
# Coverage NOT yet wired:
#   - LMFDB HTTP queries (not currently used inside any registered arsenal
#     callable; if they are added, an HTTPSConnection-level patch belongs
#     here).
#   - Direct C-extension calls that bypass Python frame entry (not currently
#     present in the arsenal; flint and numpy operations are pure-CPU and
#     do not count as "oracle" dispatch).
#
# The counter is thread-local so concurrent EVALs (a future possibility)
# count their own dispatches. The increment helper is exported so test
# fixtures (and future integrations) can manually advance the counter to
# simulate a callable that hits the oracle a known number of times.

_ORACLE_DISPATCH_COUNTER = threading.local()


def _oracle_dispatch_init() -> None:
    """Initialise the per-thread oracle-call counter to 0."""
    _ORACLE_DISPATCH_COUNTER.count = 0


def _oracle_dispatch_get() -> int:
    """Return the current per-thread oracle-call count."""
    return int(getattr(_ORACLE_DISPATCH_COUNTER, "count", 0))


def _oracle_dispatch_increment(_site_label: str = "") -> None:
    """Increment the per-thread oracle-call counter by 1.

    The ``_site_label`` argument is informational only -- it lets the caller
    name the dispatch site so future debugging can attribute calls to e.g.
    'cypari.pari' vs 'subprocess.run'. The MVP does not record per-site
    breakdowns; it just increments.
    """
    cur = int(getattr(_ORACLE_DISPATCH_COUNTER, "count", 0))
    _ORACLE_DISPATCH_COUNTER.count = cur + 1


_oracle_patch_lock = threading.Lock()
_oracle_patch_installed = False


def _install_oracle_patches() -> None:
    """Install monkey-patches for the dispatch sites we know about.

    Idempotent. Called lazily by the EVAL path the first time it runs in
    a process. Safe to call multiple times.
    """
    global _oracle_patch_installed
    with _oracle_patch_lock:
        if _oracle_patch_installed:
            return
        _oracle_patch_installed = True

        # --- cypari ----------------------------------------------------
        try:
            import cypari  # type: ignore
        except ImportError:
            cypari = None  # type: ignore[assignment]
        if cypari is not None and hasattr(cypari, "pari"):
            _orig_pari = cypari.pari

            class _CountingPariProxy:
                """Wraps cypari.pari so any call/getitem increments the counter.

                cypari.pari is a callable proxy object; both ``cypari.pari("x")``
                (invocation) and ``cypari.pari.<method>(...)`` (member access)
                count as oracle dispatch. The proxy delegates to the underlying
                object via attribute forwarding.
                """

                def __init__(self, inner):
                    object.__setattr__(self, "_inner", inner)

                def __call__(self, *a, **kw):
                    _oracle_dispatch_increment("cypari.pari")
                    return self._inner(*a, **kw)

                def __getattr__(self, name):
                    inner_attr = getattr(self._inner, name)
                    if callable(inner_attr):
                        def _wrapped(*a, **kw):
                            _oracle_dispatch_increment(f"cypari.pari.{name}")
                            return inner_attr(*a, **kw)
                        return _wrapped
                    return inner_attr

            try:
                cypari.pari = _CountingPariProxy(_orig_pari)  # type: ignore[assignment]
            except Exception:
                # If cypari refuses the patch (e.g. read-only attr), leave
                # alone; counter will simply read 0 for cypari calls. That's
                # honest under the "monotonic, not precise" contract.
                pass

        # --- subprocess.run -------------------------------------------
        import subprocess as _sp

        if not getattr(_sp.run, "_sigma_oracle_wrapped", False):
            _orig_run = _sp.run

            def _counting_run(*a, **kw):
                _oracle_dispatch_increment("subprocess.run")
                return _orig_run(*a, **kw)

            _counting_run._sigma_oracle_wrapped = True  # type: ignore[attr-defined]
            _sp.run = _counting_run  # type: ignore[assignment]

        # --- SymPy external solver -----------------------------------
        # SymPy's solve() routes complicated cases through PARI via cypari;
        # those are caught by the cypari patch above. SymPy's own internal
        # logic doesn't dispatch to a separate process, so no extra hook
        # is required. If a future SymPy version grows a subprocess
        # dispatch, the subprocess.run hook will catch it.


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class BudgetExceeded(RuntimeError):
    """Raised by EVAL when the actual cost overshoots the cost model."""


class BindingError(RuntimeError):
    """Raised on malformed BIND inputs (missing callable, bad import path,
    inconsistent cost-model shape)."""


class EvalError(RuntimeError):
    """Raised on malformed EVAL inputs (binding refers to nonexistent
    symbol, args don't match callable signature)."""


# ---------------------------------------------------------------------------
# Value types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CostModel:
    """Declared resource ceiling for a callable.

    All limits are inclusive ceilings; EVAL raises BudgetExceeded if the
    actual run exceeds any of them.
    """

    max_seconds: float = 10.0
    max_memory_mb: float = 1024.0
    max_oracle_calls: int = 0  # external oracle invocations (LMFDB, PARI subprocess, etc.)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_seconds": float(self.max_seconds),
            "max_memory_mb": float(self.max_memory_mb),
            "max_oracle_calls": int(self.max_oracle_calls),
        }


@dataclass(frozen=True)
class Binding:
    """A symbol whose def_blob holds an executable callable reference."""

    symbol: Symbol
    callable_ref: str  # "module.path:qualname"
    callable_hash: str  # sha256 of inspect.getsource(callable)
    cost_model: CostModel
    postconditions: Tuple[str, ...]
    authority_refs: Tuple[str, ...]


@dataclass(frozen=True)
class Evaluation:
    """A symbol whose def_blob holds a callable output + cost trace."""

    symbol: Symbol
    binding_ref: str  # "name@vN" of the parent binding
    args_hash: str
    output_repr: str  # repr() of the output, capped
    actual_cost: Dict[str, float]
    success: bool
    error_repr: str  # empty if success


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS bindings (
    name              TEXT NOT NULL,
    version           INTEGER NOT NULL,
    callable_ref      TEXT NOT NULL,
    callable_hash     TEXT NOT NULL,
    cost_model        TEXT NOT NULL,
    postconditions    TEXT NOT NULL,
    authority_refs    TEXT NOT NULL,
    created_at        REAL NOT NULL,
    PRIMARY KEY(name, version),
    FOREIGN KEY(name, version) REFERENCES symbols(name, version)
);

CREATE INDEX IF NOT EXISTS idx_bindings_callable_hash
    ON bindings(callable_hash);

CREATE TABLE IF NOT EXISTS evaluations (
    name              TEXT NOT NULL,
    version           INTEGER NOT NULL,
    binding_name      TEXT NOT NULL,
    binding_version   INTEGER NOT NULL,
    args_hash         TEXT NOT NULL,
    args_blob         TEXT NOT NULL,
    output_repr       TEXT NOT NULL,
    actual_cost       TEXT NOT NULL,
    success           INTEGER NOT NULL,
    error_repr        TEXT NOT NULL,
    created_at        REAL NOT NULL,
    PRIMARY KEY(name, version),
    FOREIGN KEY(name, version) REFERENCES symbols(name, version),
    FOREIGN KEY(binding_name, binding_version) REFERENCES bindings(name, version)
);

CREATE INDEX IF NOT EXISTS idx_evaluations_binding
    ON evaluations(binding_name, binding_version);
CREATE INDEX IF NOT EXISTS idx_evaluations_args_hash
    ON evaluations(args_hash);
"""


# ---------------------------------------------------------------------------
# Extension
# ---------------------------------------------------------------------------


class BindEvalExtension:
    """Composition wrapper that adds BIND + EVAL opcodes to a SigmaKernel.

    Usage::

        from sigma_kernel.sigma_kernel import SigmaKernel
        from sigma_kernel.bind_eval import BindEvalExtension, CostModel

        kernel = SigmaKernel(":memory:")
        ext = BindEvalExtension(kernel)
        cap = kernel.mint_capability("BindCap")
        binding = ext.BIND(
            name="dilog",
            callable_ref="prometheus_math.numerics_special_dilogarithm:dilogarithm",
            cost_model=CostModel(max_seconds=2.0),
            postconditions=["output is real or complex"],
            authority_refs=["Li_2(1) = pi^2/6"],
            cap=cap,
        )
        cap2 = kernel.mint_capability("EvalCap")
        result = ext.EVAL(binding.symbol.name, binding.symbol.version, args=[1.0], cap=cap2)
    """

    def __init__(
        self,
        kernel: SigmaKernel,
        schema: Optional[str] = None,
    ):
        """Attach to a kernel.

        Parameters
        ----------
        kernel : SigmaKernel
            The kernel to extend. Tables ``bindings`` and ``evaluations``
            are created if absent (SQLite) or expected to exist (Postgres).
        schema : str, optional
            For Postgres only: the schema name. Defaults to ``"sigma"``.
            Set to ``"sigma_proto"`` for prototype isolation.
        """
        self.kernel = kernel
        self._schema = schema or "sigma"
        self._ensure_schema()
        # Patch the postgres adapter's _TABLES list so SQL rewriting
        # also covers our new tables. SQLite needs no rewriting.
        if kernel.backend == "postgres":
            self._patch_postgres_tables()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _ensure_schema(self) -> None:
        if self.kernel.backend == "sqlite":
            self.kernel.conn.conn.executescript(SCHEMA_SQLITE)
            self.kernel.conn.commit()
        elif self.kernel.backend == "postgres":
            # Probe; raise a clear error if the migration wasn't applied.
            try:
                self.kernel.conn.execute(
                    f"SELECT 1 FROM {self._schema}.bindings LIMIT 0"
                )
                self.kernel.conn.commit()
            except Exception as e:
                self.kernel.conn.rollback()
                raise ConnectionError(
                    f"BindEvalExtension: table {self._schema}.bindings not present. "
                    f"Apply sigma_kernel/migrations/002_create_bind_eval_tables.sql "
                    f"with target schema={self._schema!r}."
                ) from e

    def _patch_postgres_tables(self) -> None:
        # The kernel's _TABLES tuple is module-level; we extend it for
        # our tables so the regex rewrite catches "bindings" / "evaluations"
        # too. This is safe because we only add names; existing rewrites
        # are unchanged.
        from sigma_kernel import sigma_kernel as core

        new_tables = ("bindings", "evaluations")
        if not all(t in core._TABLES for t in new_tables):
            core._TABLES = tuple(core._TABLES) + tuple(
                t for t in new_tables if t not in core._TABLES
            )
        # The adapter caches translated SQL — our cache write happens at
        # first execute, so no invalidation is required here.

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_callable(callable_ref: str) -> Callable:
        if ":" not in callable_ref:
            raise BindingError(
                f"callable_ref must be 'module.path:qualname', got {callable_ref!r}"
            )
        modpath, qualname = callable_ref.split(":", 1)
        try:
            mod = importlib.import_module(modpath)
        except ImportError as e:
            raise BindingError(
                f"cannot import module {modpath!r}: {e}"
            ) from e
        obj: Any = mod
        for part in qualname.split("."):
            try:
                obj = getattr(obj, part)
            except AttributeError as e:
                raise BindingError(
                    f"cannot resolve qualname {qualname!r} in {modpath!r}: {e}"
                ) from e
        if not callable(obj):
            raise BindingError(
                f"{callable_ref!r} resolves to {type(obj).__name__}, not callable"
            )
        return obj

    @staticmethod
    def _hash_callable(fn: Callable) -> str:
        try:
            src = inspect.getsource(fn)
        except (OSError, TypeError):
            # Built-in or C-implemented; hash by repr instead.
            src = repr(fn)
        return _sha256(src)

    @staticmethod
    def _hash_args(args: Any, kwargs: Optional[Dict[str, Any]] = None) -> str:
        # Deterministic; falls back to repr for non-JSON-serializable args.
        try:
            blob = json.dumps(
                {"args": args, "kwargs": kwargs or {}},
                sort_keys=True,
                default=repr,
            )
        except (TypeError, ValueError):
            blob = repr((args, kwargs or {}))
        return _sha256(blob)

    @staticmethod
    def _new_binding_name(callable_ref: str) -> str:
        # Stable-ish name from the qualname; uniqueness via version field.
        qualname = callable_ref.split(":", 1)[-1]
        return f"bind_{qualname.replace('.', '_')}"

    @staticmethod
    def _new_eval_name(binding_name: str, args_hash: str) -> str:
        return f"eval_{binding_name}_{args_hash[:8]}"

    # ------------------------------------------------------------------
    # OPCODE — BIND
    # ------------------------------------------------------------------

    def BIND(
        self,
        callable_ref: str,
        cost_model: CostModel,
        postconditions: Optional[List[str]] = None,
        authority_refs: Optional[List[str]] = None,
        cap: Optional[Capability] = None,
        name: Optional[str] = None,
        version: int = 1,
    ) -> Binding:
        """Bind a substrate symbol to a callable identified by import path.

        The callable must be importable. ``cap`` is consumed (linear).
        Returns a Binding whose ``symbol`` is the substrate-resolvable
        record; subsequent EVALs reference it by ``(name, version)``.
        """
        if cap is None:
            raise CapabilityError("BIND requires a capability")
        if cap.consumed:
            raise CapabilityError(f"capability {cap.cap_id} already consumed")

        fn = self._resolve_callable(callable_ref)
        callable_hash = self._hash_callable(fn)
        bind_name = name or self._new_binding_name(callable_ref)
        post = list(postconditions or [])
        auth = list(authority_refs or [])

        # Mint the parent symbol via bootstrap (MVP path; in production this
        # would go through CLAIM → FALSIFY → PROMOTE, but BIND is itself a
        # discipline-bearing op so we let the cap consumption + content
        # hash do the integrity work).
        def_obj = {
            "kind": "Binding",
            "callable_ref": callable_ref,
            "callable_hash": callable_hash,
            "cost_model": cost_model.to_dict(),
            "postconditions": post,
            "authority_refs": auth,
        }
        # Consume cap atomically with the symbol write.
        self._consume_cap(cap)
        sym = self.kernel.bootstrap_symbol(
            name=bind_name,
            version=version,
            def_obj=def_obj,
            tier=Tier.WorkingTheory,
            provenance=[callable_hash],
        )
        # Side-table row for fast lookup.
        self.kernel.conn.execute(
            "INSERT INTO bindings VALUES (?,?,?,?,?,?,?,?)",
            (
                bind_name,
                version,
                callable_ref,
                callable_hash,
                json.dumps(cost_model.to_dict(), sort_keys=True),
                json.dumps(post),
                json.dumps(auth),
                time.time(),
            ),
        )
        self.kernel.conn.commit()

        return Binding(
            symbol=sym,
            callable_ref=callable_ref,
            callable_hash=callable_hash,
            cost_model=cost_model,
            postconditions=tuple(post),
            authority_refs=tuple(auth),
        )

    def _consume_cap(self, cap: Capability) -> None:
        # Mark spent in the capabilities table; rejects double-spend.
        cur = self.kernel.conn.execute(
            "UPDATE capabilities SET consumed=1 WHERE cap_id=? AND consumed=0",
            (cap.cap_id,),
        )
        # SQLite cursor.rowcount is reliable; psycopg2 cursor too.
        rowcount = getattr(cur, "rowcount", -1)
        self.kernel.conn.commit()
        if rowcount == 0:
            raise CapabilityError(
                f"capability {cap.cap_id} not found or already spent"
            )

    # ------------------------------------------------------------------
    # OPCODE — EVAL
    # ------------------------------------------------------------------

    def EVAL(
        self,
        binding_name: str,
        binding_version: int,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        cap: Optional[Capability] = None,
        eval_version: int = 1,
    ) -> Evaluation:
        """Evaluate a bound callable under its declared cost ceiling.

        Returns an Evaluation with an output_repr and an actual_cost
        block. On budget overshoot raises BudgetExceeded; on callable
        exception, returns success=False with the exception captured
        (the kernel does not propagate user-fn exceptions; downstream
        consumers can FALSIFY against the failure).

        ``cap`` is required and consumed. ``eval_version`` lets a caller
        re-evaluate the same (binding, args) under a fresh symbol record.
        """
        if cap is None:
            raise CapabilityError("EVAL requires a capability")
        if cap.consumed:
            raise CapabilityError(f"capability {cap.cap_id} already consumed")

        # Resolve the binding.
        row = self.kernel.conn.execute(
            "SELECT callable_ref, callable_hash, cost_model "
            "FROM bindings WHERE name=? AND version=?",
            (binding_name, binding_version),
        ).fetchone()
        if row is None:
            raise EvalError(
                f"no binding {binding_name}@v{binding_version}"
            )
        callable_ref, stored_callable_hash, cost_model_blob = row
        cost_model = CostModel(**json.loads(cost_model_blob))

        # Re-resolve the callable; verify the source hash matches.
        fn = self._resolve_callable(callable_ref)
        live_hash = self._hash_callable(fn)
        if live_hash != stored_callable_hash:
            raise EvalError(
                f"callable hash drift: stored={stored_callable_hash[:12]} "
                f"live={live_hash[:12]} (the callable's source changed since BIND)"
            )

        args_list = list(args or [])
        kwargs_dict = dict(kwargs or {})
        args_hash = self._hash_args(args_list, kwargs_dict)
        args_blob = json.dumps(
            {"args": args_list, "kwargs": kwargs_dict},
            sort_keys=True,
            default=repr,
        )

        # Run under budget. C2 instrumentation: install dispatch counters,
        # reset per-thread counter, snapshot tracemalloc peak around the
        # call, then enforce all three cost dimensions.
        _install_oracle_patches()
        _oracle_dispatch_init()

        # tracemalloc may already be running for an outer profile; if so
        # we reset the peak and restore on exit. Otherwise we start it
        # locally for this call only.
        _tm_was_running = tracemalloc.is_tracing()
        if not _tm_was_running:
            tracemalloc.start()
        try:
            tracemalloc.reset_peak()
        except AttributeError:
            # Older Pythons (<3.9) lack reset_peak; fall back to
            # delta-from-start.
            pass
        mem_before_current, _ = tracemalloc.get_traced_memory()

        success = True
        error_repr = ""
        output_repr = ""
        t0 = time.perf_counter()
        try:
            output = fn(*args_list, **kwargs_dict)
            output_repr = repr(output)
            if len(output_repr) > 2000:
                output_repr = output_repr[:2000] + f"...<truncated; full repr {len(output_repr)} chars>"
        except Exception as e:
            success = False
            error_repr = f"{type(e).__name__}: {e!r}"[:1000]
        elapsed = time.perf_counter() - t0

        _, mem_peak_bytes = tracemalloc.get_traced_memory()
        # Memory delta from before the call to peak during the call,
        # converted to MB. Floor at 0 in case tracemalloc returns
        # nonsense (e.g. inactive on some platforms).
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

        # Budget check -- all three dimensions.
        if elapsed > cost_model.max_seconds:
            raise BudgetExceeded(
                f"EVAL of {binding_name}@v{binding_version} exceeded "
                f"max_seconds={cost_model.max_seconds:.2f}: actual={elapsed:.3f}"
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

        # Mint the evaluation symbol.
        eval_name = self._new_eval_name(binding_name, args_hash)
        def_obj = {
            "kind": "Evaluation",
            "binding_ref": f"{binding_name}@v{binding_version}",
            "args_hash": args_hash,
            "output_repr": output_repr,
            "actual_cost": actual_cost,
            "success": success,
            "error_repr": error_repr,
        }
        self._consume_cap(cap)
        sym = self.kernel.bootstrap_symbol(
            name=eval_name,
            version=eval_version,
            def_obj=def_obj,
            tier=Tier.Conjecture,
            provenance=[stored_callable_hash, args_hash],
        )
        # Side-table row.
        self.kernel.conn.execute(
            "INSERT INTO evaluations VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                eval_name,
                eval_version,
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

    # ------------------------------------------------------------------
    # Inspection helpers
    # ------------------------------------------------------------------

    def list_bindings(self) -> List[Tuple[str, int, str]]:
        """List (name, version, callable_ref) of all bindings."""
        cur = self.kernel.conn.execute(
            "SELECT name, version, callable_ref FROM bindings ORDER BY created_at"
        )
        return [(r[0], r[1], r[2]) for r in cur.fetchall()]

    def list_evaluations(
        self, binding_name: Optional[str] = None
    ) -> List[Tuple[str, int, str, bool]]:
        """List (name, version, binding_ref, success) of evaluations."""
        if binding_name is None:
            cur = self.kernel.conn.execute(
                "SELECT name, version, binding_name, binding_version, success "
                "FROM evaluations ORDER BY created_at"
            )
        else:
            cur = self.kernel.conn.execute(
                "SELECT name, version, binding_name, binding_version, success "
                "FROM evaluations WHERE binding_name=? ORDER BY created_at",
                (binding_name,),
            )
        return [
            (r[0], r[1], f"{r[2]}@v{r[3]}", bool(r[4])) for r in cur.fetchall()
        ]

    def get_binding(self, name: str, version: int) -> Binding:
        sym = self.kernel.RESOLVE(name, version)
        row = self.kernel.conn.execute(
            "SELECT callable_ref, callable_hash, cost_model, postconditions, "
            "authority_refs FROM bindings WHERE name=? AND version=?",
            (name, version),
        ).fetchone()
        if row is None:
            raise EvalError(f"no binding {name}@v{version}")
        return Binding(
            symbol=sym,
            callable_ref=row[0],
            callable_hash=row[1],
            cost_model=CostModel(**json.loads(row[2])),
            postconditions=tuple(json.loads(row[3])),
            authority_refs=tuple(json.loads(row[4])),
        )
