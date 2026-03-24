"""Extract Python code from LLM responses."""

import re


# Signals that the model considers the combination unimplementable
SCRAP_SIGNALS = [
    "unproductive",
    "not implementable",
    "cannot be implemented",
    "genuinely unproductive",
    "return none",
    "returning none",
    "not feasible",
    "no meaningful implementation",
]


def extract_code(response_text: str) -> tuple[str | None, str]:
    """Extract Python code from an LLM response.

    Returns:
        (code, status) where status is one of:
        - "ok": code extracted successfully
        - "scrap:<reason>": model declined or no code found
    """
    if response_text is None:
        return None, "scrap:no_response"

    text_lower = response_text.lower()

    # Check for explicit decline
    for signal in SCRAP_SIGNALS:
        if signal in text_lower:
            return None, f"scrap:model_declined ({signal})"

    # Try fenced code blocks first
    blocks = re.findall(r"```python\s*\n(.*?)```", response_text, re.DOTALL)
    if blocks:
        # Take the longest block (likely the full implementation)
        code = max(blocks, key=len).strip()
        if "class ReasoningTool" in code:
            return code, "ok"
        # If the class isn't in the longest block, concatenate all blocks
        combined = "\n\n".join(b.strip() for b in blocks)
        if "class ReasoningTool" in combined:
            return combined, "ok"
        # Return longest block anyway — validator will catch issues
        return code, "ok"

    # Try generic code blocks
    blocks = re.findall(r"```\s*\n(.*?)```", response_text, re.DOTALL)
    if blocks:
        code = max(blocks, key=len).strip()
        if "class" in code or "def " in code:
            return code, "ok"

    # Try to find a bare class definition
    match = re.search(
        r"(class ReasoningTool.*?)(?=\n\S|\Z)", response_text, re.DOTALL
    )
    if match:
        return match.group(1).strip(), "ok"

    return None, "scrap:no_code_found"
