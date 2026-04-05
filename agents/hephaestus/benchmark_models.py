#!/usr/bin/env python3
"""Benchmark free models for code generation quality."""

import json
import sys
import time
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path('src').resolve()))
from validator import validate
from test_harness import run_trap_battery, load_tool_from_code

# Load env keys — try root .env via keys.py first, fall back to eos/.env
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from keys import _load_env_file
    env_vars = _load_env_file()
except ImportError:
    env_vars = {}

if not env_vars:
    env_path = Path('../../agents/eos/.env')
    if env_path.exists():
        for line in env_path.read_text().strip().split('\n'):
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()

print("=== FREE MODEL CODE GENERATION BENCHMARK ===\n")
print("Testing across 5 concept combinations...\n")

# Load manifest and pick 5 diverse candidates
manifest = json.loads((Path('scrap_staging') / 'MANIFEST.json').read_text(encoding='utf-8'))
test_concepts = [
    manifest[7],
    manifest[17],
    manifest[33],
    manifest[45],
    manifest[50],
]

# Load actual code for testing
test_codes = {}
for tc in test_concepts:
    py_file = Path('scrap_staging') / f"{tc['name']}.py"
    if py_file.exists():
        test_codes[tc['name']] = py_file.read_text(encoding='utf-8')

print("Test concepts:")
for i, tc in enumerate(test_concepts, 1):
    print(f"  {i}. {tc['name'][:60]}")
print()

# Define models to test
models = {
    'github_gpt4o_mini': {
        'provider': 'GitHub Models',
        'model_id': 'gpt-4o-mini',
        'auth_env': 'GITHUB_TOKEN',
        'base_url': 'https://models.inference.ai.azure.com',
        'sdk': 'openai',
    },
    'groq_llama_8b': {
        'provider': 'Groq',
        'model_id': 'llama-3.1-8b-instant',
        'auth_env': 'GROQ_API_KEY',
        'base_url': 'https://api.groq.com/openai/v1',
        'sdk': 'openai',
    },
    'cerebras_qwen_235b': {
        'provider': 'Cerebras',
        'model_id': 'qwen-3-235b-a22b',
        'auth_env': 'CEREBRAS_API_KEY',
        'base_url': 'https://api.cerebras.ai/v1',
        'sdk': 'openai',
    },
    'gemini_flash': {
        'provider': 'Google Gemini',
        'model_id': 'gemini-2.0-flash',
        'auth_env': 'GOOGLE_AI_KEY',
        'sdk': 'gemini',
    },
    'nvidia_nemotron': {
        'provider': 'NVIDIA NemoClaw',
        'model_id': 'nvidia/nemotron-3-super-120b-a12b',
        'auth_env': 'NVIDIA_API_KEY',
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'sdk': 'openai',
    },
}

# Results tracking
results = defaultdict(lambda: {
    'success': 0,
    'timeout': 0,
    'api_error': 0,
    'no_code': 0,
    'invalid_syntax': 0,
    'runtime_error': 0,
    'test_pass': 0,
    'total_attempts': 0,
    'times': [],
    'errors': [],
})

print("Running tests...\n")

for model_key, model_cfg in models.items():
    print(f"[{model_key}] Testing {model_cfg['provider']}...", flush=True)

    auth_key = env_vars.get(model_cfg['auth_env'])
    if not auth_key:
        print(f"  ✗ SKIP: {model_cfg['auth_env']} not set\n")
        continue

    for tc in test_concepts:
        code = test_codes.get(tc['name'])
        if not code:
            continue

        prompt = f"""Fix this Python reasoning tool. It failed with: {tc['failure_reason']}

The code (first 1500 chars):
```python
{code[:1500]}
```

Fix ONLY the bug. Keep the class name ReasoningTool and methods evaluate() and confidence().
Return only the fixed code in a python code block."""

        start = time.time()

        try:
            if model_cfg['sdk'] == 'openai':
                from openai import OpenAI
                client = OpenAI(
                    api_key=auth_key,
                    base_url=model_cfg.get('base_url'),
                    timeout=20.0,
                )

                resp = client.chat.completions.create(
                    model=model_cfg['model_id'],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=2048,
                )
                generated = resp.choices[0].message.content

            elif model_cfg['sdk'] == 'gemini':
                import google.generativeai as genai
                genai.configure(api_key=auth_key)
                model = genai.GenerativeModel(model_cfg['model_id'])
                resp = model.generate_content(prompt)
                generated = resp.text

            elapsed = time.time() - start

            # Extract code
            blocks = re.findall(r'```python\s*\n(.*?)```', generated, re.DOTALL)
            if not blocks:
                blocks = re.findall(r'```\s*\n(.*?)```', generated, re.DOTALL)

            if not blocks:
                results[model_key]['no_code'] += 1
                results[model_key]['times'].append(elapsed)
                results[model_key]['total_attempts'] += 1
                continue

            fixed_code = blocks[0].strip()

            # Validate
            valid, reason = validate(fixed_code)
            if not valid:
                results[model_key]['invalid_syntax'] += 1
                results[model_key]['errors'].append(reason[:50])
                results[model_key]['times'].append(elapsed)
                results[model_key]['total_attempts'] += 1
                continue

            # Test
            try:
                tool = load_tool_from_code(fixed_code)
                test_res = run_trap_battery(tool)
                if test_res['passed']:
                    results[model_key]['test_pass'] += 1
                    results[model_key]['success'] += 1
                else:
                    results[model_key]['runtime_error'] += 1
                results[model_key]['times'].append(elapsed)
            except Exception as e:
                results[model_key]['runtime_error'] += 1
                results[model_key]['errors'].append(str(e)[:50])
                results[model_key]['times'].append(elapsed)

            results[model_key]['total_attempts'] += 1

        except TimeoutError:
            results[model_key]['timeout'] += 1
            results[model_key]['times'].append(time.time() - start)
            results[model_key]['total_attempts'] += 1
        except Exception as e:
            err_str = str(e)
            if 'timeout' in err_str.lower():
                results[model_key]['timeout'] += 1
            else:
                results[model_key]['api_error'] += 1
                results[model_key]['errors'].append(err_str[:50])
            results[model_key]['times'].append(time.time() - start)
            results[model_key]['total_attempts'] += 1

print("\n\n=== RESULTS ===\n")
print(f"{'Model':<30} {'Success':<8} {'Timeout':<8} {'API Err':<8} {'Syntax':<8} {'Runtime':<8} {'Avg Time':<8}")
print("-" * 90)

for model_key in sorted(models.keys()):
    if model_key not in results or results[model_key]['total_attempts'] == 0:
        continue

    r = results[model_key]
    success_rate = (r['success'] / r['total_attempts'] * 100) if r['total_attempts'] > 0 else 0
    avg_time = sum(r['times']) / len(r['times']) if r['times'] else 0

    print(f"{model_key:<30} {r['success']:<8} {r['timeout']:<8} {r['api_error']:<8} {r['invalid_syntax']:<8} {r['runtime_error']:<8} {avg_time:>6.1f}s")

print("\n\nDetailed breakdown:\n")
for model_key in sorted(models.keys()):
    if model_key not in results or results[model_key]['total_attempts'] == 0:
        continue

    r = results[model_key]
    total = r['total_attempts']
    print(f"{model_key}:")
    print(f"  Total attempts: {total}")
    print(f"  [PASS] Test passes: {r['test_pass']} ({r['test_pass']/total*100:.0f}%)")
    print(f"  [FAIL] Syntax errors: {r['invalid_syntax']} ({r['invalid_syntax']/total*100:.0f}%)")
    print(f"  [FAIL] Runtime errors: {r['runtime_error']} ({r['runtime_error']/total*100:.0f}%)")
    print(f"  [FAIL] No code generated: {r['no_code']} ({r['no_code']/total*100:.0f}%)")
    print(f"  [FAIL] Timeout: {r['timeout']} ({r['timeout']/total*100:.0f}%)")
    print(f"  [FAIL] API error: {r['api_error']} ({r['api_error']/total*100:.0f}%)")
    print(f"  Avg response time: {sum(r['times'])/len(r['times']):.1f}s")
    if r['errors']:
        print(f"  Sample errors: {r['errors'][:2]}")
    print()
