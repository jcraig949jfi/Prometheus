"""Round-trip + raise-on-invalid-type tests for the contract-change
window 2026-05-08 Tier 3 hardening: SigmaKernel.CLAIM kill_path
string-typing.

Closes T-2026-05-07-ST-fire29-002 (P2-normal).
"""
from __future__ import annotations

import pytest

from sigma_kernel.sigma_kernel import SigmaKernel, Tier


class TestClaimKillPathTyping:

    def _kernel(self) -> SigmaKernel:
        return SigmaKernel(":memory:")

    def test_string_kill_path_accepted(self):
        k = self._kernel()
        claim = k.CLAIM(
            target_name="t1",
            hypothesis="h",
            evidence={"x": 1},
            kill_path="out_of_band:M=1.5_outside_(1.001,1.18)",
            target_tier=Tier.Conjecture,
        )
        assert claim.kill_path == "out_of_band:M=1.5_outside_(1.001,1.18)"

    def test_empty_string_kill_path_accepted(self):
        """Empty string is valid kill_path (substrate is permissive on
        free-form string CONTENT, only the type is now enforced)."""
        k = self._kernel()
        claim = k.CLAIM(
            target_name="t2",
            hypothesis="h",
            evidence={"x": 1},
            kill_path="",
            target_tier=Tier.Conjecture,
        )
        assert claim.kill_path == ""

    def test_int_kill_path_rejected_with_typeerror(self):
        """Per ST-fire29-002: pre-fix accepted; post-fix raises TypeError
        with the actual received type in the message."""
        k = self._kernel()
        with pytest.raises(TypeError, match="kill_path must be a str"):
            k.CLAIM(
                target_name="t3",
                hypothesis="h",
                evidence={"x": 1},
                kill_path=12345,  # type: ignore
                target_tier=Tier.Conjecture,
            )

    def test_none_kill_path_rejected(self):
        k = self._kernel()
        with pytest.raises(TypeError, match="kill_path must be a str"):
            k.CLAIM(
                target_name="t4",
                hypothesis="h",
                evidence={"x": 1},
                kill_path=None,  # type: ignore
                target_tier=Tier.Conjecture,
            )

    def test_list_kill_path_rejected(self):
        k = self._kernel()
        with pytest.raises(TypeError, match="kill_path must be a str"):
            k.CLAIM(
                target_name="t5",
                hypothesis="h",
                evidence={"x": 1},
                kill_path=["out_of_band", "M=1.5"],  # type: ignore
                target_tier=Tier.Conjecture,
            )

    def test_error_message_includes_received_type(self):
        k = self._kernel()
        with pytest.raises(TypeError) as excinfo:
            k.CLAIM(
                target_name="t6",
                hypothesis="h",
                evidence={"x": 1},
                kill_path=42,  # type: ignore
                target_tier=Tier.Conjecture,
            )
        msg = str(excinfo.value)
        assert "int" in msg  # actual received type
        assert "42" in msg   # actual received value (repr)
