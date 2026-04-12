"""
llm_client.py — HTTP Client for Apollo LLM Server.

Drop-in replacement for direct model access. Routes generation
requests to the shared FastAPI server at localhost:8800.
"""

import requests


class LLMClient:
    """HTTP client for the shared LLM server."""

    def __init__(self, base_url="http://localhost:8800"):
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt, max_tokens=512, temperature=0.7):
        """Generate text from a single prompt via the server."""
        resp = requests.post(
            f"{self.base_url}/generate",
            json={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["text"]

    def generate_batch(self, prompts, max_tokens=512, temperature=0.7):
        """Generate text from multiple prompts via the server."""
        resp = requests.post(
            f"{self.base_url}/generate_batch",
            json={
                "prompts": prompts,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json()["texts"]

    def health(self):
        """Check server health."""
        return requests.get(f"{self.base_url}/health", timeout=5).json()

    def is_available(self):
        """Check if the server is reachable."""
        try:
            h = self.health()
            return h.get("status") == "ok"
        except Exception:
            return False
