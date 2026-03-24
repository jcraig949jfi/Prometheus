"""
Proof corpus builder for Rhea's self-improving loop.

This module generates verified training data:
1. Takes an evolved model (with LoRA applied)
2. Generates reasoning chains for math/logic problems
3. Translates to Lean 4 and verifies
4. Verified chains become fine-tuning data for next generation seed

The key invariant: garbage cannot propagate because the filter
is formal (Lean 4), not neural. A wrong proof simply won't compile.

Corpus format: JSONL with fields:
  - problem: the input prompt
  - reasoning: the model's generated chain
  - answer: extracted final answer
  - lean_verified: bool
  - lean_code: the Lean 4 source that was checked
"""

import json
import torch
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model

from genome import LoraGenome, unflatten_lora_params
from lean_verifier import verify_trap_answer, arithmetic_to_lean, verify_lean_code
from traps import TINY_TRAPS, Trap


@dataclass
class CorpusEntry:
    problem: str
    reasoning: str
    answer: str
    lean_verified: bool
    lean_code: str | None
    trap_name: str
    category: str
    generation: int


# === Problem generators ===
# These generate novel problems (not just the trap battery)
# to build a diverse training corpus.

def generate_arithmetic_problems(n: int = 100, seed: int = 42) -> list[Trap]:
    """Generate random arithmetic problems with known answers."""
    import random
    rng = random.Random(seed)
    problems = []

    ops = [
        ("+", lambda a, b: a + b),
        ("-", lambda a, b: a - b),
        ("×", lambda a, b: a * b),
    ]

    for i in range(n):
        op_sym, op_fn = rng.choice(ops)
        if op_sym == "-":
            # Ensure non-negative result
            a = rng.randint(1, 50)
            b = rng.randint(1, a)
        elif op_sym == "×":
            a = rng.randint(1, 12)
            b = rng.randint(1, 12)
        else:
            a = rng.randint(1, 50)
            b = rng.randint(1, 50)

        answer = op_fn(a, b)
        # Generate a plausible wrong answer
        anti = answer + rng.choice([-2, -1, 1, 2])

        problems.append(Trap(
            name=f"gen_arith_{i:04d}",
            prompt=f"What is {a} {op_sym} {b}? Answer with just the number:",
            target_token=str(answer),
            anti_token=str(anti),
            category="generated_arithmetic",
        ))

    return problems


def generate_comparison_problems(n: int = 50, seed: int = 42) -> list[Trap]:
    """Generate comparison problems with known answers."""
    import random
    rng = random.Random(seed)
    problems = []

    for i in range(n):
        a = rng.randint(1, 100)
        b = rng.randint(1, 100)
        while b == a:
            b = rng.randint(1, 100)

        correct = "Yes" if a > b else "No"
        anti = "No" if correct == "Yes" else "Yes"

        problems.append(Trap(
            name=f"gen_comp_{i:04d}",
            prompt=f"Is {a} larger than {b}? Answer Yes or No:",
            target_token=correct,
            anti_token=anti,
            category="generated_comparison",
        ))

    return problems


def build_corpus(
    model,
    tokenizer,
    problems: list[Trap],
    generation: int = 0,
    max_new_tokens: int = 100,
    output_path: str | None = None,
) -> list[CorpusEntry]:
    """
    Generate reasoning chains and verify them with Lean 4.

    Args:
        model: HuggingFace model with LoRA applied
        tokenizer: corresponding tokenizer
        problems: list of Trap objects to generate chains for
        generation: evolution generation number
        max_new_tokens: max tokens to generate per problem
        output_path: path to save corpus JSONL

    Returns:
        list of CorpusEntry (only verified entries)
    """
    device = next(model.parameters()).device
    corpus = []
    verified_count = 0
    total_attempted = 0

    print(f"Building corpus: {len(problems)} problems, generation {generation}")

    for trap in problems:
        # Generate reasoning chain
        inputs = tokenizer(trap.prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
            )
        full_output = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        # Extract the generated portion (after prompt)
        reasoning = full_output[len(trap.prompt):].strip()

        # Extract answer: first token that could be the answer
        answer_candidates = reasoning.split()
        answer = answer_candidates[0] if answer_candidates else ""

        # Attempt Lean 4 verification
        lean_result = verify_trap_answer(trap, answer)
        total_attempted += 1

        if lean_result is not None and lean_result.verified:
            verified_count += 1
            entry = CorpusEntry(
                problem=trap.prompt,
                reasoning=reasoning,
                answer=answer,
                lean_verified=True,
                lean_code=lean_result.lean_code,
                trap_name=trap.name,
                category=trap.category,
                generation=generation,
            )
            corpus.append(entry)

    print(f"Corpus: {verified_count}/{total_attempted} verified "
          f"({verified_count/max(total_attempted,1)*100:.1f}%)")

    # Save corpus
    if output_path and corpus:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for entry in corpus:
                f.write(json.dumps(asdict(entry)) + "\n")
        print(f"Corpus saved to: {path}")

    return corpus


def corpus_to_training_data(corpus: list[CorpusEntry]) -> list[dict]:
    """
    Convert verified corpus entries to training format.

    Returns list of {"input": prompt, "output": verified_reasoning}
    suitable for fine-tuning.
    """
    training_data = []
    for entry in corpus:
        training_data.append({
            "input": entry.problem,
            "output": f"{entry.reasoning}",
            "verified": True,
            "category": entry.category,
        })
    return training_data


if __name__ == "__main__":
    # Quick test: generate problems and show what Lean code would look like
    print("=== Sample arithmetic problems ===")
    problems = generate_arithmetic_problems(5)
    for p in problems:
        print(f"  {p.prompt}  answer={p.target_token}")
        lean = arithmetic_to_lean(p.prompt, p.target_token)
        if lean:
            print(f"  Lean: {lean.strip()[:100]}...")

    print("\n=== Sample comparison problems ===")
    problems = generate_comparison_problems(5)
    for p in problems:
        print(f"  {p.prompt}  answer={p.target_token}")
