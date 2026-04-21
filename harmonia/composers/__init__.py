"""harmonia.composers — operator-composition enumeration package.

Per `docs/prompts/gen_10_composition_enumeration.md`:
- `validator.py` — type-compatibility rules for composing symbols
- `scorer.py`    — expected-information-gain-per-compute-unit heuristic
- `enumerate.py` — driver that enumerates type-valid compositions,
                   scores them, and emits the top-N as Agora tasks

Entry point: `harmonia.composers.enumerate.main()`.
"""
from harmonia.composers.validator import is_valid_composition, compatibility_reason
from harmonia.composers.scorer import score_composition

__all__ = ["is_valid_composition", "compatibility_reason", "score_composition"]
