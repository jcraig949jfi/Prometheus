"""
Xenolexicon Naming Engine

Generates compound names and human-approximation descriptions for captured
specimens. Uses the unsteered model as a "translator" — the model describes
the novel output without being influenced by the steering vector that
produced it.

Fallback: algorithmic names when the model produces unparseable responses.
"""

import re
import torch
from .seti_logger import slog


NAMING_PROMPT_TEMPLATE = """You are a lexicographer cataloging newly discovered mathematical concepts.
Given the following outputs produced by a novel computational process, create a compound name and a brief description.

The name should be:
- Composed of 2-4 recognizable English, Latin, or Greek roots smashed together (like German compound words)
- Pronounceable as a single word
- Evocative of what the concept seems to be about

The description should be:
- 1-3 sentences
- Honest about where language breaks down
- Written like a field biologist's notebook entry for a new species

Outputs from the process:
---
{outputs}
---

Respond in EXACTLY this format (no other text):
NAME: [compound name]
DESCRIPTION: [description]"""


def _parse_naming_response(text: str) -> tuple:
    """
    Extract NAME and DESCRIPTION from model output.
    Returns (name, description) or (None, None) on parse failure.
    """
    # Try to find NAME: and DESCRIPTION: markers
    name_match = re.search(r"NAME:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    desc_match = re.search(r"DESCRIPTION:\s*(.+?)(?:\n\n|$)", text, re.IGNORECASE | re.DOTALL)

    if name_match and desc_match:
        name = name_match.group(1).strip().strip('"\'')
        description = desc_match.group(1).strip().strip('"\'')

        # Validate: name should be 1-4 words, no longer than 50 chars
        if len(name) > 0 and len(name) <= 50 and len(name.split()) <= 5:
            return name, description

    return None, None


def _algorithmic_name(generation: int, layer: int, specimen_id: str) -> tuple:
    """
    Fallback naming when the model can't produce a parseable response.
    """
    short_hash = specimen_id[:6]
    name = f"XENO-{generation:03d}-L{layer}-{short_hash}"
    description = (f"Uncharacterized specimen from generation {generation}, "
                   f"layer {layer}. Awaiting human interpretation.")
    return name, description


def generate_specimen_name(
    model,
    outputs: dict,
    generation: int,
    layer: int,
    specimen_id: str,
    max_new_tokens: int = 128,
) -> tuple:
    """
    Generate a compound name and description for a captured specimen.

    Uses the UNSTEERED model to act as translator — the model describes
    the novel output without being influenced by the steering vector.

    Args:
        model: HookedTransformer (unsteered)
        outputs: dict of provocation_name → generated text
        generation: Generation number (for fallback naming)
        layer: Injection layer (for fallback naming)
        specimen_id: UUID (for fallback naming)
        max_new_tokens: Max tokens for naming response

    Returns:
        (name: str, description: str)
    """
    # Format outputs for the prompt (truncate each to avoid context overflow)
    output_lines = []
    for prov_name, text in outputs.items():
        # Extract just the generated portion (skip echoed prompt)
        # Truncate to 200 chars to keep naming prompt manageable
        clean = text.strip()[:200]
        output_lines.append(f"[{prov_name}]: {clean}")

    outputs_text = "\n".join(output_lines)
    prompt = NAMING_PROMPT_TEMPLATE.format(outputs=outputs_text)

    try:
        input_tokens = model.to_tokens(prompt)

        # Generate WITHOUT any hooks (unsteered)
        output_tokens = model.generate(
            input_tokens,
            max_new_tokens=max_new_tokens,
            stop_at_eos=True,
            verbose=False,
            prepend_bos=False,
        )

        response = model.to_string(output_tokens[0])
        # Extract only the generated portion
        prompt_pos = response.find(prompt)
        if prompt_pos != -1:
            response = response[prompt_pos + len(prompt):]

        name, description = _parse_naming_response(response)

        if name is not None:
            slog.info(f"Named specimen: '{name}' — {description[:80]}...")
            return name, description
        else:
            slog.warning(f"Naming parse failed, falling back to algorithmic name. "
                        f"Raw response: {response[:200]}")
            return _algorithmic_name(generation, layer, specimen_id)

    except Exception as e:
        slog.error(f"Naming generation failed: {e}")
        return _algorithmic_name(generation, layer, specimen_id)
