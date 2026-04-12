"""Extract Python code from LLM responses."""

import re


# Signals that the model explicitly declined to implement.
# Only checked in prose OUTSIDE code blocks, and only when no code was found.
DECLINE_SIGNALS = [
    "not implementable",
    "cannot be implemented",
    "genuinely unproductive for code",
    "no meaningful implementation",
    "not feasible to implement",
    "i cannot produce",
    "unable to implement",
]


def _extract_code_blocks(response_text: str) -> str | None:
    """Try to extract Python code from response. Returns code or None."""
    # Try fenced python blocks first
    blocks = re.findall(r"```python\s*\n(.*?)```", response_text, re.DOTALL)
    if blocks:
        # Take the longest block (likely the full implementation)
        code = max(blocks, key=len).strip()
        if "class ReasoningTool" in code:
            return code
        # If the class isn't in the longest block, concatenate all blocks
        combined = "\n\n".join(b.strip() for b in blocks)
        if "class ReasoningTool" in combined:
            return combined
        # Return longest block anyway — validator will catch issues
        return code

    # Try generic code blocks
    blocks = re.findall(r"```\s*\n(.*?)```", response_text, re.DOTALL)
    if blocks:
        code = max(blocks, key=len).strip()
        if "class" in code or "def " in code:
            return code

    # Try to find a bare class definition
    match = re.search(
        r"(class ReasoningTool.*?)(?=\n\S|\Z)", response_text, re.DOTALL
    )
    if match:
        return match.group(1).strip()

    return None


def _strip_code_blocks(text: str) -> str:
    """Return response text with code blocks removed (prose only)."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def extract_code(response_text: str) -> tuple[str | None, str]:
    """Extract Python code from an LLM response.

    Code extraction runs FIRST. Decline signals are only checked in the
    prose outside code blocks, and only if no code was found. This prevents
    false positives from quoted Nous analysis text that contains words like
    "unproductive".

    Returns:
        (code, status) where status is one of:
        - "ok": code extracted successfully
        - "scrap:<reason>": model declined or no code found
    """
    if response_text is None:
        return None, "scrap:no_response"

    # Step 1: Try to extract code FIRST
    code = _extract_code_blocks(response_text)
    if code is not None:
        return code, "ok"

    # Step 2: No code found — check if the model explicitly declined
    # Only check prose outside code blocks to avoid false positives
    prose = _strip_code_blocks(response_text).lower()
    for signal in DECLINE_SIGNALS:
        if signal in prose:
            return None, f"scrap:model_declined ({signal})"

    return None, "scrap:no_code_found"
