"""
deepseek_client.py — DeepSeek API client for LLM mutations.

Drop-in alternative to the local Qwen server. Uses DeepSeek's
OpenAI-compatible API for code generation.
"""

import time
from logger import log_debug


class DeepSeekClient:
    """API client for DeepSeek code generation."""

    def __init__(self, api_key: str, model: str = "deepseek-chat",
                 base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def generate(self, prompt, max_tokens=512, temperature=0.7):
        """Generate text from a single prompt via DeepSeek API."""
        t0 = time.time()
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Python code mutation engine. Return ONLY code, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = response.choices[0].message.content or ""
            elapsed = time.time() - t0
            log_debug(
                f"DeepSeek call: {len(prompt)}ch in | {len(text)}ch out | {elapsed:.1f}s | ok",
                stage="llm",
                data={"prompt_chars": len(prompt), "output_chars": len(text),
                      "elapsed_s": round(elapsed, 2), "success": True,
                      "mode": "deepseek", "model": self.model}
            )
            return text
        except Exception as e:
            elapsed = time.time() - t0
            log_debug(
                f"DeepSeek call: {len(prompt)}ch in | {elapsed:.1f}s | fail: {str(e)[:80]}",
                stage="llm",
                data={"prompt_chars": len(prompt), "elapsed_s": round(elapsed, 2),
                      "success": False, "mode": "deepseek", "error": str(e)[:200]}
            )
            return ""

    def generate_batch(self, prompts, max_tokens=512, temperature=0.7,
                       max_workers: int = 8):
        """Generate text from multiple prompts. DeepSeek API has no batch
        endpoint, so we fan calls out via a ThreadPoolExecutor. Paid accounts
        handle 8 concurrent connections comfortably."""
        if not prompts:
            return []
        from concurrent.futures import ThreadPoolExecutor
        results = [""] * len(prompts)
        with ThreadPoolExecutor(max_workers=min(max_workers, len(prompts))) as ex:
            futures = {ex.submit(self.generate, p, max_tokens, temperature): i
                       for i, p in enumerate(prompts)}
            for fut in futures:
                i = futures[fut]
                try:
                    results[i] = fut.result()
                except Exception:
                    results[i] = ""
        return results

    def is_available(self):
        """Check if DeepSeek API is reachable."""
        try:
            result = self.generate("Say 'ok'", max_tokens=5, temperature=0.0)
            return len(result) > 0
        except Exception:
            return False

    def health(self):
        """Match the LLMClient interface."""
        return {
            "status": "ok",
            "model": self.model,
            "mode": "deepseek-api",
        }
