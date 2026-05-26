"""Subprocess-isolated sandbox worker for LLM-authored mutation testing.

Invoked by agents/_shared/llm_sandbox.sandbox_test() via subprocess.
Reads JSON from stdin: {apply_code, revert_code, agent_dict, state_dict}.
Writes JSON to stdout: {passed, error, snapshot, post_revert_state, state_restored}.

Isolation properties:
  - Fresh Python process (no inherited agent state)
  - Restricted builtins (no __import__, no open, no exec, no eval)
  - No agents/_shared/* imports in the worker — only stdlib + types
  - Subprocess time limit enforced by the parent
  - All I/O is JSON stdin/stdout; no filesystem write surface

Failure modes that are CAUGHT here:
  - AttributeError (mutation references attribute the agent doesn't have)
  - KeyError (mutation references missing dict key)
  - TypeError (mutation does math on the wrong type)
  - Syntax errors (apply_code or revert_code not valid Python)
  - Any uncaught exception during apply or revert
  - Missing or non-callable apply / revert
  - apply returns a snapshot that revert cannot accept
  - State not restored after revert (apply leaves residue revert misses)

Failure modes NOT caught here (deferred to v2c iter 4+):
  - Long-running infinite loops without builtin time gate
    (parent enforces wall-clock timeout via subprocess.run timeout=)
  - Side effects on a real agent (we test against MOCK agent only)
  - Memory leaks
"""
from __future__ import annotations

import json
import sys
import traceback
from copy import deepcopy
from types import SimpleNamespace


# Restricted builtins — only the subset that's safe + useful for a mutation.
# Notably ABSENT: __import__, open, eval, exec, compile, input, exit, quit,
# globals, locals, vars, setattr (allowed though — needed for tactic mutation),
# getattr (allowed), delattr (allowed).
SAFE_BUILTINS = {
    "True": True, "False": False, "None": None,
    "abs": abs, "all": all, "any": any, "bool": bool,
    "dict": dict, "enumerate": enumerate, "filter": filter,
    "float": float, "frozenset": frozenset, "getattr": getattr,
    "hasattr": hasattr, "hash": hash, "id": id, "int": int,
    "isinstance": isinstance, "issubclass": issubclass,
    "iter": iter, "len": len, "list": list, "map": map,
    "max": max, "min": min, "next": next, "object": object,
    "ord": ord, "chr": chr, "pow": pow, "print": print,
    "range": range, "repr": repr, "reversed": reversed,
    "round": round, "set": set, "setattr": setattr,
    "delattr": delattr, "slice": slice, "sorted": sorted,
    "str": str, "sum": sum, "tuple": tuple, "type": type,
    "zip": zip,
    # Exceptions the mutation may catch internally
    "Exception": Exception, "ValueError": ValueError,
    "KeyError": KeyError, "AttributeError": AttributeError,
    "TypeError": TypeError, "IndexError": IndexError,
    "RuntimeError": RuntimeError,
}


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except Exception as e:
        print(json.dumps({"passed": False,
                          "error": f"stdin parse failed: {e}",
                          "stage": "input_parse"}))
        return 1

    apply_code = payload.get("apply_code", "")
    revert_code = payload.get("revert_code", "")
    agent_dict = payload.get("agent_dict", {}) or {}
    state_dict = payload.get("state_dict", {}) or {}

    # Build mock agent as a SimpleNamespace so apply()/revert() can do
    # agent.attr access. Nested dicts become nested SimpleNamespaces only
    # at the top level — keep deep dicts as dicts (agents typically read
    # config[key] not agent.config.subkey).
    mock_agent = SimpleNamespace(**agent_dict)
    baseline_state = deepcopy(state_dict)
    working_state = deepcopy(state_dict)

    # Compile + exec apply_code in restricted namespace
    apply_ns = {"__builtins__": SAFE_BUILTINS}
    try:
        compiled_apply = compile(apply_code, "<llm_apply>", "exec")
        exec(compiled_apply, apply_ns)
    except SyntaxError as e:
        print(json.dumps({"passed": False, "stage": "apply_compile",
                          "error": f"SyntaxError: {e}"}))
        return 0
    except Exception as e:
        print(json.dumps({"passed": False, "stage": "apply_compile",
                          "error": f"{type(e).__name__}: {e}"}))
        return 0

    apply_fn = apply_ns.get("apply")
    if not callable(apply_fn):
        print(json.dumps({"passed": False, "stage": "apply_lookup",
                          "error": "apply_code did not define a callable named 'apply'"}))
        return 0

    # Run apply against the mock
    try:
        snapshot = apply_fn(mock_agent, working_state)
    except Exception as e:
        print(json.dumps({"passed": False, "stage": "apply_run",
                          "error": f"{type(e).__name__}: {e}",
                          "traceback": traceback.format_exc()}))
        return 0

    # Compile + exec revert_code
    revert_ns = {"__builtins__": SAFE_BUILTINS}
    try:
        compiled_revert = compile(revert_code, "<llm_revert>", "exec")
        exec(compiled_revert, revert_ns)
    except SyntaxError as e:
        print(json.dumps({"passed": False, "stage": "revert_compile",
                          "error": f"SyntaxError: {e}",
                          "snapshot": _safe_repr(snapshot)}))
        return 0
    except Exception as e:
        print(json.dumps({"passed": False, "stage": "revert_compile",
                          "error": f"{type(e).__name__}: {e}",
                          "snapshot": _safe_repr(snapshot)}))
        return 0

    revert_fn = revert_ns.get("revert")
    if not callable(revert_fn):
        print(json.dumps({"passed": False, "stage": "revert_lookup",
                          "error": "revert_code did not define a callable named 'revert'",
                          "snapshot": _safe_repr(snapshot)}))
        return 0

    # Run revert
    revert_error = None
    try:
        revert_fn(mock_agent, working_state, snapshot)
    except Exception as e:
        revert_error = f"{type(e).__name__}: {e}"

    state_restored = (working_state == baseline_state)

    result = {
        "passed": (revert_error is None and state_restored),
        "stage": "complete",
        "snapshot": _safe_repr(snapshot),
        "state_restored": state_restored,
        "revert_error": revert_error,
    }
    if not result["passed"]:
        if revert_error:
            result["error"] = f"revert raised: {revert_error}"
        else:
            result["error"] = (
                f"revert did not restore state. "
                f"baseline_keys={list(baseline_state.keys())}, "
                f"post_revert_keys={list(working_state.keys())}"
            )
    print(json.dumps(result))
    return 0


def _safe_repr(x):
    """Truncated repr for JSON safety."""
    try:
        return json.dumps(x)
    except Exception:
        try:
            return repr(x)[:500]
        except Exception:
            return "<unrepr-able>"


if __name__ == "__main__":
    sys.exit(main() or 0)
