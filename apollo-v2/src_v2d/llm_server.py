"""
llm_server.py — Shared LLM Server for Apollo v2c.

FastAPI server on localhost:8800. Loads Qwen once, serves generation requests.
Endpoints:
  POST /generate       — single prompt generation
  POST /generate_batch — batched prompt generation (max 8)
  GET  /health         — model status + VRAM info
"""

import subprocess
import sys

for pkg in ['fastapi', 'uvicorn']:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

import torch
import time
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# ── Configuration ────────────────────────────────────────────────────

MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"
MAX_BATCH_SIZE = 8

app = FastAPI(title="Apollo LLM Server", version="2c")

# ── Global model state ───────────────────────────────────────────────

_model = None
_tokenizer = None
_model_name = None


def _load_model():
    """Load the model into GPU with 8-bit quantization."""
    global _model, _tokenizer, _model_name

    print(f"Loading {MODEL_NAME} with 8-bit quantization...", flush=True)
    t0 = time.time()

    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if _tokenizer.pad_token is None:
        _tokenizer.pad_token = _tokenizer.eos_token

    quant_config = BitsAndBytesConfig(load_in_8bit=True)
    _model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
    )

    _model_name = MODEL_NAME
    vram = torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0
    print(f"Model loaded in {time.time() - t0:.1f}s, VRAM: {vram:.1f}GB", flush=True)


def _prepare_prompt(prompt: str) -> str:
    """Apply chat template if available."""
    if hasattr(_tokenizer, 'apply_chat_template'):
        messages = [{"role": "user", "content": prompt}]
        return _tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    return prompt


def _generate_single(prompt: str, max_tokens: int = 512,
                     temperature: float = 0.7) -> str:
    """Generate from a single prompt."""
    text = _prepare_prompt(prompt)
    inputs = _tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=2048).to(_model.device)

    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=max(temperature, 0.01),
            top_p=0.95,
            do_sample=True,
            pad_token_id=_tokenizer.pad_token_id,
        )

    generated = outputs[0][inputs['input_ids'].shape[1]:]
    return _tokenizer.decode(generated, skip_special_tokens=True)


def _generate_batch_internal(prompts: List[str], max_tokens: int = 512,
                             temperature: float = 0.7) -> List[str]:
    """Generate from multiple prompts in a single batched call."""
    texts = [_prepare_prompt(p) for p in prompts]

    inputs = _tokenizer(texts, return_tensors="pt", padding=True,
                        truncation=True, max_length=2048).to(_model.device)

    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=max(temperature, 0.01),
            top_p=0.95,
            do_sample=True,
            pad_token_id=_tokenizer.pad_token_id,
        )

    results = []
    for i, output in enumerate(outputs):
        prompt_len = inputs['attention_mask'][i].sum()
        generated = output[prompt_len:]
        results.append(_tokenizer.decode(generated, skip_special_tokens=True))
    return results


# ── Pydantic models ──────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7


class GenerateResponse(BaseModel):
    text: str


class BatchGenerateRequest(BaseModel):
    prompts: List[str]
    max_tokens: int = 512
    temperature: float = 0.7


class BatchGenerateResponse(BaseModel):
    texts: List[str]


class HealthResponse(BaseModel):
    status: str
    model: str
    vram_allocated_gb: float
    vram_total_gb: float


# ── Endpoints ────────────────────────────────────────────────────────

@app.on_event("startup")
def startup_event():
    _load_model()


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        t0 = time.time()
        text = _generate_single(req.prompt, req.max_tokens, req.temperature)
        elapsed = time.time() - t0
        print(f"[server] generate | 1 prompts | {elapsed:.1f}s", flush=True)
        return GenerateResponse(text=text)
    except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        raise HTTPException(status_code=503, detail=f"OOM error: {str(e)[:200]}")


@app.post("/generate_batch", response_model=BatchGenerateResponse)
def generate_batch(req: BatchGenerateRequest):
    if not req.prompts:
        return BatchGenerateResponse(texts=[])

    t0 = time.time()
    n_prompts = len(req.prompts)
    all_results = []
    # Chunk into batches of MAX_BATCH_SIZE
    for i in range(0, len(req.prompts), MAX_BATCH_SIZE):
        chunk = req.prompts[i:i + MAX_BATCH_SIZE]
        try:
            results = _generate_batch_internal(chunk, req.max_tokens, req.temperature)
            all_results.extend(results)
        except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            # Fallback: try one-at-a-time for this chunk
            try:
                for prompt in chunk:
                    text = _generate_single(prompt, req.max_tokens, req.temperature)
                    all_results.append(text)
            except (torch.cuda.OutOfMemoryError, RuntimeError) as e2:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                raise HTTPException(
                    status_code=503,
                    detail=f"OOM error even in single mode: {str(e2)[:200]}"
                )

    elapsed = time.time() - t0
    print(f"[server] batch | {n_prompts} prompts | {elapsed:.1f}s", flush=True)
    return BatchGenerateResponse(texts=all_results)


@app.get("/health", response_model=HealthResponse)
def health():
    vram_allocated = 0.0
    vram_total = 0.0
    if torch.cuda.is_available():
        vram_allocated = torch.cuda.memory_allocated() / 1e9
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1e9
    return HealthResponse(
        status="ok",
        model=_model_name or "not loaded",
        vram_allocated_gb=round(vram_allocated, 2),
        vram_total_gb=round(vram_total, 2),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)
