"""
llm_server_alt.py — Parameterized alt-LLM server for the 2026-05-19 bake-off.

Same shape as llm_server.py (FastAPI on localhost), but model name and port
come from env vars so we can spin up Phi-4-mini / Granite / DeepSeek-Coder
on demand without editing source per candidate.

Env vars:
  LLM_ALT_MODEL_NAME   HF repo id or local path (REQUIRED)
  LLM_ALT_PORT         default 8801
  LLM_ALT_LOAD_IN_8BIT default "1" (set to "0" to disable)
  LLM_ALT_MAX_BATCH    default 8

Endpoints match llm_server.py exactly so LLMClient is a drop-in.
"""

import os
import subprocess
import sys

for pkg in ['fastapi', 'uvicorn']:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

import threading
import torch
import time
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_NAME = os.environ.get("LLM_ALT_MODEL_NAME")
if not MODEL_NAME:
    print("ERROR: LLM_ALT_MODEL_NAME env var not set", file=sys.stderr)
    sys.exit(2)

PORT = int(os.environ.get("LLM_ALT_PORT", "8801"))
LOAD_IN_8BIT = os.environ.get("LLM_ALT_LOAD_IN_8BIT", "1") == "1"
MAX_BATCH_SIZE = int(os.environ.get("LLM_ALT_MAX_BATCH", "8"))

app = FastAPI(title=f"Apollo Alt LLM Server ({MODEL_NAME})", version="bakeoff-1")

_model = None
_tokenizer = None
_model_name = None
_model_lock = threading.Lock()


def _load_model():
    global _model, _tokenizer, _model_name
    print(f"[alt-server] Loading {MODEL_NAME} (8bit={LOAD_IN_8BIT}) on port {PORT}...", flush=True)
    t0 = time.time()
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=False)
    if _tokenizer.pad_token is None:
        _tokenizer.pad_token = _tokenizer.eos_token

    load_kwargs = {"trust_remote_code": True, "device_map": "auto"}
    if LOAD_IN_8BIT:
        load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
    else:
        load_kwargs["dtype"] = torch.float16

    _model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, **load_kwargs)
    _model_name = MODEL_NAME
    vram = torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0
    print(f"[alt-server] Loaded in {time.time()-t0:.1f}s, VRAM: {vram:.1f}GB", flush=True)


def _prepare_prompt(prompt: str) -> str:
    if hasattr(_tokenizer, 'apply_chat_template'):
        try:
            return _tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False, add_generation_prompt=True,
            )
        except Exception:
            return prompt
    return prompt


def _generate_single(prompt, max_tokens=512, temperature=0.7):
    text = _prepare_prompt(prompt)
    inputs = _tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=2048).to(_model.device)
    with _model_lock:
        with torch.no_grad():
            outputs = _model.generate(
                **inputs, max_new_tokens=max_tokens,
                temperature=max(temperature, 0.01), top_p=0.95,
                do_sample=True, pad_token_id=_tokenizer.pad_token_id,
            )
    generated = outputs[0][inputs['input_ids'].shape[1]:]
    return _tokenizer.decode(generated, skip_special_tokens=True)


def _generate_batch_internal(prompts, max_tokens=512, temperature=0.7):
    texts = [_prepare_prompt(p) for p in prompts]
    inputs = _tokenizer(texts, return_tensors="pt", padding=True,
                        truncation=True, max_length=2048).to(_model.device)
    with _model_lock:
        with torch.no_grad():
            outputs = _model.generate(
                **inputs, max_new_tokens=max_tokens,
                temperature=max(temperature, 0.01), top_p=0.95,
                do_sample=True, pad_token_id=_tokenizer.pad_token_id,
            )
    results = []
    for i, output in enumerate(outputs):
        prompt_len = inputs['attention_mask'][i].sum()
        generated = output[prompt_len:]
        results.append(_tokenizer.decode(generated, skip_special_tokens=True))
    return results


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


@app.on_event("startup")
def startup_event():
    _load_model()


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        text = _generate_single(req.prompt, req.max_tokens, req.temperature)
        return GenerateResponse(text=text)
    except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        raise HTTPException(status_code=503, detail=f"OOM error: {str(e)[:200]}")


@app.post("/generate_batch", response_model=BatchGenerateResponse)
def generate_batch(req: BatchGenerateRequest):
    if not req.prompts:
        return BatchGenerateResponse(texts=[])
    all_results = []
    for i in range(0, len(req.prompts), MAX_BATCH_SIZE):
        chunk = req.prompts[i:i + MAX_BATCH_SIZE]
        try:
            all_results.extend(_generate_batch_internal(chunk, req.max_tokens, req.temperature))
        except (torch.cuda.OutOfMemoryError, RuntimeError):
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            for p in chunk:
                try:
                    all_results.append(_generate_single(p, req.max_tokens, req.temperature))
                except Exception:
                    all_results.append("")
    return BatchGenerateResponse(texts=all_results)


@app.get("/health", response_model=HealthResponse)
def health():
    vram_allocated = torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0.0
    vram_total = torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else 0.0
    return HealthResponse(
        status="ok", model=_model_name or "not loaded",
        vram_allocated_gb=round(vram_allocated, 2),
        vram_total_gb=round(vram_total, 2),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
