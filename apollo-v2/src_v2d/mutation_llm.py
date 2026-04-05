"""
mutation_llm.py — LLM-assisted mutation operators for Apollo v2c.

Uses a local coding model (Qwen2.5-Coder-7B-Instruct) for structural mutations:
- Route mutation: modify router_logic code
- Wiring mutation: rewire primitive connections
- Primitive swap: suggest replacement primitive

v2c additions:
- _generate_batch(): batched local generation
- set_client(): switch to HTTP client mode (shared LLM server)
"""

import re
import ast
import time
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

from genome import ALL_PRIMITIVES, PRIMITIVE_CATALOG
from logger import log_debug


class LLMMutator:
    """LLM-based mutation operator using a local coding model."""

    def __init__(self, model_name: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
                 device: str = "cuda", max_tokens: int = 1024,
                 temperature: float = 0.7, load_in_8bit: bool = False):
        self.model_name = model_name
        self.device = device
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.load_in_8bit = load_in_8bit
        self.model = None
        self.tokenizer = None
        self._loaded = False
        self._client = None  # LLMClient for server mode

    def set_client(self, client):
        """Switch to HTTP client mode.

        When a client is set, _generate() and _generate_batch() route
        through the HTTP client instead of the local model.

        Args:
            client: LLMClient instance (or any object with
                    generate(prompt, max_tokens, temperature) and
                    generate_batch(prompts, max_tokens, temperature))
        """
        self._client = client
        # Mark as loaded so mutation methods proceed
        self._loaded = True

    def load(self):
        """Load model and tokenizer."""
        if self._client is not None:
            # Server mode — no local model needed
            self._loaded = True
            return

        print(f"  Loading {self.model_name}...", flush=True)
        t0 = time.time()

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True
        )

        load_kwargs = {
            "trust_remote_code": True,
        }

        if self.device == "cpu":
            load_kwargs["dtype"] = torch.float16
            load_kwargs["device_map"] = "cpu"
        elif self.load_in_8bit:
            from transformers import BitsAndBytesConfig
            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
            load_kwargs["device_map"] = "auto"
        else:
            load_kwargs["dtype"] = torch.float16
            load_kwargs["device_map"] = "auto"

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, **load_kwargs
        )

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

        prompt_chars = len(prompt)
        t0 = time.time()

        # Server mode: route through HTTP client
        if self._client is not None:
            try:
                result = self._client.generate(
                    prompt, max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                elapsed = time.time() - t0
                log_debug(
                    f"LLM call: single | {prompt_chars}ch in | {len(result)}ch out | {elapsed:.1f}s | ok",
                    stage="llm",
                    data={"prompt_chars": prompt_chars, "output_chars": len(result),
                          "elapsed_s": round(elapsed, 2), "success": True, "mode": "single"}
                )
                return result
            except Exception:
                elapsed = time.time() - t0
                log_debug(
                    f"LLM call: single | {prompt_chars}ch in | 0ch out | {elapsed:.1f}s | fail",
                    stage="llm",
                    data={"prompt_chars": prompt_chars, "output_chars": 0,
                          "elapsed_s": round(elapsed, 2), "success": False, "mode": "single"}
                )
                return ""

        # Local mode
        if hasattr(self.tokenizer, 'apply_chat_template'):
            messages = [{"role": "user", "content": prompt}]
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            text = prompt

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                max_length=2048).to(self.model.device)

        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            generated = outputs[0][inputs['input_ids'].shape[1]:]
            result = self.tokenizer.decode(generated, skip_special_tokens=True)
            elapsed = time.time() - t0
            log_debug(
                f"LLM call: single | {prompt_chars}ch in | {len(result)}ch out | {elapsed:.1f}s | ok",
                stage="llm",
                data={"prompt_chars": prompt_chars, "output_chars": len(result),
                      "elapsed_s": round(elapsed, 2), "success": True, "mode": "single"}
            )
            return result
        except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
            # OOM recovery: clear cache and return empty
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elapsed = time.time() - t0
            log_debug(
                f"LLM call: single | {prompt_chars}ch in | 0ch out | {elapsed:.1f}s | fail",
                stage="llm",
                data={"prompt_chars": prompt_chars, "output_chars": 0,
                      "elapsed_s": round(elapsed, 2), "success": False, "mode": "single"}
            )
            return ""

    def _generate_batch(self, prompts: list) -> list:
        """Generate text from multiple prompts in parallel.

        Args:
            prompts: list of prompt strings

        Returns:
            list of generated text strings
        """
        if not prompts:
            return []

        if not self._loaded:
            self.load()

        total_prompt_chars = sum(len(p) for p in prompts)
        t0 = time.time()

        # Server mode: route through HTTP client
        if self._client is not None:
            try:
                results = self._client.generate_batch(
                    prompts, max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                elapsed = time.time() - t0
                total_output_chars = sum(len(r) for r in results)
                log_debug(
                    f"LLM call: batch({len(prompts)}) | {total_prompt_chars}ch in | {total_output_chars}ch out | {elapsed:.1f}s | ok",
                    stage="llm",
                    data={"prompt_chars": total_prompt_chars, "output_chars": total_output_chars,
                          "elapsed_s": round(elapsed, 2), "success": True, "mode": "batch",
                          "n_prompts": len(prompts)}
                )
                return results
            except Exception:
                elapsed = time.time() - t0
                log_debug(
                    f"LLM call: batch({len(prompts)}) | {total_prompt_chars}ch in | {elapsed:.1f}s | fail -> single fallback",
                    stage="llm",
                    data={"prompt_chars": total_prompt_chars, "elapsed_s": round(elapsed, 2),
                          "success": False, "mode": "batch", "n_prompts": len(prompts)}
                )
                # Fallback to one-at-a-time
                return [self._generate(p) for p in prompts]

        # Local batched generation
        texts = []
        for prompt in prompts:
            if hasattr(self.tokenizer, 'apply_chat_template'):
                messages = [{"role": "user", "content": prompt}]
                texts.append(self.tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True))
            else:
                texts.append(prompt)

        # Pad to equal length for batched generation
        self.tokenizer.pad_token = self.tokenizer.eos_token
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True,
                                truncation=True, max_length=2048).to(self.model.device)

        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                )

            results = []
            for i, output in enumerate(outputs):
                prompt_len = inputs['attention_mask'][i].sum()
                generated = output[prompt_len:]
                results.append(
                    self.tokenizer.decode(generated, skip_special_tokens=True)
                )
            elapsed = time.time() - t0
            total_output_chars = sum(len(r) for r in results)
            log_debug(
                f"LLM call: batch({len(prompts)}) | {total_prompt_chars}ch in | {total_output_chars}ch out | {elapsed:.1f}s | ok",
                stage="llm",
                data={"prompt_chars": total_prompt_chars, "output_chars": total_output_chars,
                      "elapsed_s": round(elapsed, 2), "success": True, "mode": "batch",
                      "n_prompts": len(prompts)}
            )
            return results
        except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elapsed = time.time() - t0
            log_debug(
                f"LLM call: batch({len(prompts)}) | {total_prompt_chars}ch in | {elapsed:.1f}s | fail -> single fallback",
                stage="llm",
                data={"prompt_chars": total_prompt_chars, "elapsed_s": round(elapsed, 2),
                      "success": False, "mode": "batch", "n_prompts": len(prompts)}
            )
            # Fallback: try one-at-a-time
            results = []
            for prompt in prompts:
                results.append(self._generate(prompt))
            return results

    # ------------------------------------------------------------------
    # Route mutation
    # ------------------------------------------------------------------

    def mutate_route(self, current_router: str, node_info: str,
                     param_keys: list[str]) -> str | None:
        """LLM modifies the router_logic code."""
        prompt = f"""You are modifying the routing logic for a reasoning tool.
The tool has these primitive nodes: {node_info}
Available parameters: {param_keys}

Current router code (receives prompt, candidates, outputs, params):
```python
{current_router}
```

Modify this router to improve scoring. The function receives:
- prompt: the question string
- candidates: list of candidate answer strings
- outputs: dict mapping node_id to primitive output (e.g. outputs['n0'])
- params: dict of evolvable float parameters

Rules:
- Return a list of float scores, one per candidate
- You may ONLY reference node IDs from the list above
- Use outputs.get('nX') to safely access node outputs (may be None)
- You may use re, math, numpy (as np)
- Do NOT import anything else
- Do NOT define classes

Return ONLY the modified router code body (no function def, no explanation):"""

        output = self._generate(prompt)
        code = self._extract_code_body(output)

        if code and self._validate_router_code(code):
            return code
        return None

    def mutate_route_prompt(self, current_router: str, node_info: str,
                            param_keys: list[str]) -> str:
        """Return the prompt for route mutation (for batching)."""
        return f"""You are modifying the routing logic for a reasoning tool.
The tool has these primitive nodes: {node_info}
Available parameters: {param_keys}

Current router code (receives prompt, candidates, outputs, params):
```python
{current_router}
```

Modify this router to improve scoring. The function receives:
- prompt: the question string
- candidates: list of candidate answer strings
- outputs: dict mapping node_id to primitive output (e.g. outputs['n0'])
- params: dict of evolvable float parameters

Rules:
- Return a list of float scores, one per candidate
- You may ONLY reference node IDs from the list above
- Use outputs.get('nX') to safely access node outputs (may be None)
- You may use re, math, numpy (as np)
- Do NOT import anything else
- Do NOT define classes

Return ONLY the modified router code body (no function def, no explanation):"""

    # ------------------------------------------------------------------
    # Wiring mutation
    # ------------------------------------------------------------------

    def mutate_wiring(self, organism_desc: str) -> str | None:
        """LLM suggests new wiring between primitives."""
        prompt = f"""You are rewiring a reasoning tool's primitive connections.

{organism_desc}

Suggest ONE wiring change: change which node's output feeds into which parameter.
Valid sources: "prompt", "candidates", "nX.output" (where X < target node index), "param.KEY"

Return ONLY a JSON object like:
{{"n2": {{"relations": "n0.output"}}}}

This means: change node n2's 'relations' input to come from n0's output.
No explanation, just the JSON:"""

        output = self._generate(prompt)
        match = re.search(r'\{[^{}]+\}', output)
        if match:
            return match.group(0)
        return None

    def mutate_wiring_prompt(self, organism_desc: str) -> str:
        """Return the prompt for wiring mutation (for batching)."""
        return f"""You are rewiring a reasoning tool's primitive connections.

{organism_desc}

Suggest ONE wiring change: change which node's output feeds into which parameter.
Valid sources: "prompt", "candidates", "nX.output" (where X < target node index), "param.KEY"

Return ONLY a JSON object like:
{{"n2": {{"relations": "n0.output"}}}}

This means: change node n2's 'relations' input to come from n0's output.
No explanation, just the JSON:"""

    # ------------------------------------------------------------------
    # Primitive swap
    # ------------------------------------------------------------------

    def swap_primitive(self, old_primitive: str, node_id: str,
                       organism_desc: str) -> str | None:
        """LLM suggests a replacement primitive."""
        catalog_str = "\n".join(
            f"  {cat}: {', '.join(names)}"
            for cat, names in PRIMITIVE_CATALOG.items()
        )

        prompt = f"""You are replacing a primitive in a reasoning tool.

Current tool structure:
{organism_desc}

The primitive at {node_id} is currently: {old_primitive}

Available primitives:
{catalog_str}

Which primitive should replace {old_primitive} at {node_id} to improve reasoning?
Consider what the surrounding nodes do and pick something complementary.

Return ONLY the primitive name (e.g. "bayesian_update"), nothing else:"""

        output = self._generate(prompt).strip()

        for prim in ALL_PRIMITIVES:
            if prim in output:
                return prim
        return None

    def swap_primitive_prompt(self, old_primitive: str, node_id: str,
                              organism_desc: str) -> str:
        """Return the prompt for primitive swap (for batching)."""
        catalog_str = "\n".join(
            f"  {cat}: {', '.join(names)}"
            for cat, names in PRIMITIVE_CATALOG.items()
        )
        return f"""You are replacing a primitive in a reasoning tool.

Current tool structure:
{organism_desc}

The primitive at {node_id} is currently: {old_primitive}

Available primitives:
{catalog_str}

Which primitive should replace {old_primitive} at {node_id} to improve reasoning?
Consider what the surrounding nodes do and pick something complementary.

Return ONLY the primitive name (e.g. "bayesian_update"), nothing else:"""

    # ------------------------------------------------------------------
    # Combine organisms (crossover-like)
    # ------------------------------------------------------------------

    def combine_organisms(self, org_a_desc: str, org_b_desc: str) -> str | None:
        """LLM-assisted crossover: suggest how to combine two organisms."""
        prompt = f"""You are combining two reasoning tools into one.

Tool A:
{org_a_desc}

Tool B:
{org_b_desc}

Write router logic that combines the strengths of both tools.
The router receives: prompt, candidates, outputs (dict of node outputs), params (dict of floats).
It must return a list of float scores, one per candidate.

Return ONLY the router code body (no function def):"""

        output = self._generate(prompt)
        code = self._extract_code_body(output)
        if code and self._validate_router_code(code):
            return code
        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_code_body(self, text: str) -> str | None:
        """Extract Python code from LLM output."""
        match = re.search(r'```python\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        match = re.search(r'```\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        lines = text.strip().split('\n')
        code_lines = []
        started = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('scores') or \
               stripped.startswith('return') or stripped.startswith('for ') or \
               stripped.startswith('if ') or '=' in stripped:
                started = True
            if started:
                code_lines.append(line)

        if code_lines:
            return '\n'.join(code_lines)
        return None

    def _validate_router_code(self, code: str) -> bool:
        """Check if router code is syntactically valid Python."""
        try:
            test = "def _route(prompt, candidates, outputs, params):\n"
            for line in code.strip().split('\n'):
                test += f"    {line}\n"
            ast.parse(test)
            return True
        except SyntaxError:
            return False

    def unload(self):
        """Free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        self._loaded = False
        self._client = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
