"""
mutation_llm.py — LLM-assisted mutation operators for Apollo v2.

Uses a local coding model (Qwen2.5-Coder-3B-Instruct) for structural mutations:
- Route mutation: modify router_logic code
- Wiring mutation: rewire primitive connections
- Primitive swap: suggest replacement primitive

The LLM is a mutation operator, not a designer. Evolution provides
search pressure. The LLM provides structural intelligence.
"""

import re
import ast
import time
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

from genome import ALL_PRIMITIVES, PRIMITIVE_CATALOG


class LLMMutator:
    """LLM-based mutation operator using a local coding model."""

    def __init__(self, model_name: str = "Qwen/Qwen2.5-Coder-3B-Instruct",
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

    def load(self):
        """Load model and tokenizer."""
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
            return self.tokenizer.decode(generated, skip_special_tokens=True)
        except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
            # OOM recovery: clear cache and return empty
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return ""

    # ------------------------------------------------------------------
    # Route mutation
    # ------------------------------------------------------------------

    def mutate_route(self, current_router: str, node_info: str,
                     param_keys: list[str]) -> str | None:
        """LLM modifies the router_logic code.

        Args:
            current_router: Current router Python code
            node_info: e.g. "n0=bayesian_update, n1=solve_sat, n2=entropy"
            param_keys: Available parameter names

        Returns:
            New router code string, or None on failure.
        """
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

    # ------------------------------------------------------------------
    # Wiring mutation
    # ------------------------------------------------------------------

    def mutate_wiring(self, organism_desc: str) -> str | None:
        """LLM suggests new wiring between primitives.

        Returns JSON string with {node_id: {param: new_source}} or None.
        """
        prompt = f"""You are rewiring a reasoning tool's primitive connections.

{organism_desc}

Suggest ONE wiring change: change which node's output feeds into which parameter.
Valid sources: "prompt", "candidates", "nX.output" (where X < target node index), "param.KEY"

Return ONLY a JSON object like:
{{"n2": {{"relations": "n0.output"}}}}

This means: change node n2's 'relations' input to come from n0's output.
No explanation, just the JSON:"""

        output = self._generate(prompt)
        # Extract JSON from response
        match = re.search(r'\{[^{}]+\}', output)
        if match:
            return match.group(0)
        return None

    # ------------------------------------------------------------------
    # Primitive swap
    # ------------------------------------------------------------------

    def swap_primitive(self, old_primitive: str, node_id: str,
                       organism_desc: str) -> str | None:
        """LLM suggests a replacement primitive.

        Returns primitive name string or None.
        """
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

        # Extract primitive name
        for prim in ALL_PRIMITIVES:
            if prim in output:
                return prim
        return None

    # ------------------------------------------------------------------
    # Combine organisms (crossover-like)
    # ------------------------------------------------------------------

    def combine_organisms(self, org_a_desc: str, org_b_desc: str) -> str | None:
        """LLM-assisted crossover: suggest how to combine two organisms.

        Returns new router code that uses nodes from both parents.
        """
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
        # Try code fences first
        match = re.search(r'```python\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        match = re.search(r'```\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Take everything that looks like code (has = or return)
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
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
