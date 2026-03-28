"""
mutation_llm.py — LLM-assisted mutation operators.

Supports multiple local coding models for benchmarking.
No API calls, no network after initial download. Runs on local GPU.
"""

import re
import ast
import time
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer


class LLMMutator:
    """LLM-based mutation operator. Loads a local coding model."""

    def __init__(self, model_name: str = "Qwen/Qwen2.5-Coder-3B-Instruct",
                 device: str = "cuda", max_tokens: int = 2048,
                 temperature: float = 0.7, load_in_8bit: bool = False):
        self.model_name = model_name
        self.device = device
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.load_in_8bit = load_in_8bit
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def load(self):
        """Load model and tokenizer."""
        print(f"  Loading {self.model_name}...", flush=True)
        t0 = time.time()

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True
        )

        load_kwargs = {
            "trust_remote_code": True,
            "torch_dtype": torch.float16,
        }

        # Try GPU first, fall back to CPU if segfault-prone
        if self.device == "cpu":
            load_kwargs["device_map"] = "cpu"
        elif self.load_in_8bit:
            load_kwargs["load_in_8bit"] = True
            load_kwargs["device_map"] = "auto"
        else:
            load_kwargs["device_map"] = "auto"

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, **load_kwargs
        )

        # Set pad token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self._loaded = True
        vram = torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0
        print(f"  Loaded in {time.time()-t0:.1f}s, VRAM: {vram:.1f}GB", flush=True)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def _generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        if not self._loaded:
            self.load()

        # Use chat template if available, otherwise raw prompt
        if hasattr(self.tokenizer, 'apply_chat_template'):
            messages = [{"role": "user", "content": prompt}]
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            text = prompt

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                max_length=4096).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        # Decode only the generated tokens
        generated = outputs[0][inputs['input_ids'].shape[1]:]
        return self.tokenizer.decode(generated, skip_special_tokens=True)

    def _extract_python_class(self, text: str) -> str:
        """Extract a Python class from LLM output (may contain markdown fences)."""
        # Try to find code between ```python ... ```
        match = re.search(r'```python\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try ``` ... ```
        match = re.search(r'```\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Look for class ReasoningTool
        match = re.search(r'(import.*?\n)*(class ReasoningTool.*)', text, re.DOTALL)
        if match:
            return match.group(0).strip()

        return text.strip()

    def _validate_output(self, source: str) -> bool:
        """Check if output is valid Python with ReasoningTool class."""
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return False

        has_class = False
        has_evaluate = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'ReasoningTool':
                has_class = True
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == 'evaluate':
                        has_evaluate = True
        return has_class and has_evaluate

    def splice(self, organism_source: str, gene_source: str) -> str:
        """LLM-assisted splice: incorporate a method from another tool."""
        # Truncate sources to fit context
        org_truncated = organism_source[:3000]
        gene_truncated = gene_source[:1000]

        prompt = f"""Here is a Python class that evaluates reasoning quality:

{org_truncated}

Here is a scoring method from a different reasoning tool:

{gene_truncated}

Modify the class to incorporate this scoring method into its evaluate() pipeline.
The new method should be called from evaluate() alongside existing methods.
Keep the class name ReasoningTool with evaluate(self, prompt, candidates) and confidence(self, prompt, answer) methods.
Use only numpy, math, re, zlib, collections. No other imports.
Return only the complete Python class."""

        output = self._generate(prompt)
        source = self._extract_python_class(output)

        if self._validate_output(source):
            return source
        return None

    def combine(self, parent_a_source: str, parent_b_source: str) -> str:
        """LLM-assisted crossover: combine two tools' strategies."""
        a_truncated = parent_a_source[:2500]
        b_truncated = parent_b_source[:2500]

        prompt = f"""Here are two Python classes that evaluate reasoning quality using different strategies:

Tool A:
{a_truncated}

Tool B:
{b_truncated}

Create a new ReasoningTool class that combines the best parsing approach from one tool
with the best scoring approach from the other. The combined tool should use both strategies
and integrate their scores.
Keep class name ReasoningTool with evaluate(self, prompt, candidates) and confidence(self, prompt, answer).
Use only numpy, math, re, zlib, collections. No other imports.
Return only the complete Python class."""

        output = self._generate(prompt)
        source = self._extract_python_class(output)

        if self._validate_output(source):
            return source
        return None

    def refactor(self, organism_source: str) -> str:
        """LLM-assisted simplification: remove dead code, improve structure."""
        truncated = organism_source[:4000]

        prompt = f"""Here is a Python reasoning evaluation class:

{truncated}

Improve this class by:
1. Removing any dead code or unused methods
2. Making the scoring logic more robust
3. Adding better handling of edge cases (empty strings, missing numbers)
Keep class name ReasoningTool with evaluate(self, prompt, candidates) and confidence(self, prompt, answer).
Use only numpy, math, re, zlib, collections. No other imports.
Return only the improved Python class."""

        output = self._generate(prompt)
        source = self._extract_python_class(output)

        if self._validate_output(source):
            return source
        return None

    def mutate_method(self, organism_source: str, method_name: str) -> str:
        """LLM-assisted method mutation: modify a specific method's logic."""
        truncated = organism_source[:4000]

        prompt = f"""Here is a Python reasoning evaluation class:

{truncated}

Modify the {method_name} method to use a different approach while keeping the same
input/output contract. Try one of: different distance metric, add structural parsing,
incorporate negation detection, or use statistical features.
Keep class name ReasoningTool with evaluate(self, prompt, candidates) and confidence(self, prompt, answer).
Use only numpy, math, re, zlib, collections. No other imports.
Return only the complete modified Python class."""

        output = self._generate(prompt)
        source = self._extract_python_class(output)

        if self._validate_output(source):
            return source
        return None

    def unload(self):
        """Free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        self._loaded = False
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def benchmark_models(models: list, organism_sources: list, tasks: list,
                     n_mutations: int = 20) -> dict:
    """Benchmark multiple LLM models on mutation quality.

    Args:
        models: list of model name strings
        organism_sources: list of source code strings to mutate
        tasks: list of task dicts for smoke testing
        n_mutations: mutations per model

    Returns:
        dict of model_name -> {viability_rate, discrimination_rate, avg_time, samples}
    """
    from compiler import smoke_test, compile_from_source
    from sandbox import check_imports
    import random

    results = {}

    for model_name in models:
        print(f"\n{'='*60}")
        print(f"Benchmarking: {model_name}")
        print(f"{'='*60}")

        mutator = LLMMutator(model_name=model_name, load_in_8bit=False)
        try:
            mutator.load()
        except Exception as e:
            print(f"  Failed to load: {e}")
            results[model_name] = {'error': str(e)}
            continue

        viable = 0
        discriminating = 0
        times = []
        samples = []

        for i in range(n_mutations):
            org_source = random.choice(organism_sources)
            donor_source = random.choice(organism_sources)

            # Alternate between mutation types
            t0 = time.time()
            try:
                if i % 3 == 0:
                    new_source = mutator.combine(org_source, donor_source)
                    mut_type = 'combine'
                elif i % 3 == 1:
                    new_source = mutator.mutate_method(org_source, '_score_candidate')
                    mut_type = 'mutate_method'
                else:
                    new_source = mutator.refactor(org_source)
                    mut_type = 'refactor'
            except Exception as e:
                new_source = None
                mut_type = 'error'

            elapsed = time.time() - t0
            times.append(elapsed)

            if new_source is not None:
                # Check imports
                ok, _ = check_imports(new_source)
                if ok:
                    result = compile_from_source(new_source)
                    if result.success:
                        runs, disc = smoke_test(new_source, tasks[0])
                        if runs:
                            viable += 1
                            if disc:
                                discriminating += 1
                            samples.append({
                                'type': mut_type,
                                'viable': True,
                                'discriminates': disc,
                                'source_len': len(new_source),
                            })

            status = "VIABLE+DISC" if (new_source and viable > len(samples) - 1 and samples and samples[-1].get('discriminates')) else \
                     "VIABLE" if (new_source and viable > 0 and samples) else "DEAD"
            print(f"  [{i+1:2d}/{n_mutations}] {mut_type:15s} {elapsed:5.1f}s {status}")

        # Unload to free GPU
        mutator.unload()

        rate_viable = viable / n_mutations if n_mutations > 0 else 0
        rate_disc = discriminating / n_mutations if n_mutations > 0 else 0
        avg_time = sum(times) / len(times) if times else 0

        results[model_name] = {
            'viable_rate': rate_viable,
            'discrimination_rate': rate_disc,
            'avg_time_seconds': avg_time,
            'n_mutations': n_mutations,
            'n_viable': viable,
            'n_discriminating': discriminating,
            'samples': samples,
        }

        print(f"\n  Results for {model_name}:")
        print(f"    Viable: {viable}/{n_mutations} = {rate_viable:.0%}")
        print(f"    Discriminating: {discriminating}/{n_mutations} = {rate_disc:.0%}")
        print(f"    Avg time: {avg_time:.1f}s")

    return results


if __name__ == '__main__':
    import sys, json
    sys.path.insert(0, str(Path(__file__).parent))

    from genome import create_seed_population
    from task_manager import TaskManager

    # Load test data
    tm = TaskManager()
    tasks = tm.get_evolution_tasks()

    pop = create_seed_population('F:/Prometheus/agents/hephaestus/forge/', 20)
    sources = [g.source_code for g in pop if g.source_code][:10]

    # Models to benchmark
    models = [
        "deepseek-ai/deepseek-coder-1.3b-instruct",
        "Qwen/Qwen2.5-Coder-3B-Instruct",
        "bigcode/starcoder2-3b",
    ]

    results = benchmark_models(models, sources, tasks, n_mutations=20)

    # Save results
    output_path = "F:/Prometheus/apollo/llm_benchmark_results.json"
    # Remove non-serializable samples for JSON
    for model in results:
        if 'samples' in results[model]:
            results[model]['samples'] = results[model].get('samples', [])[:5]
    Path(output_path).write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {output_path}")

    # Summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    for model, r in results.items():
        if 'error' in r:
            print(f"  {model}: FAILED ({r['error'][:60]})")
        else:
            print(f"  {model}:")
            print(f"    Viable: {r['viable_rate']:.0%} | Disc: {r['discrimination_rate']:.0%} | Time: {r['avg_time_seconds']:.1f}s")
