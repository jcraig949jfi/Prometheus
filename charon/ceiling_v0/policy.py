"""One probe policy, shared by every arm. RESTORED 2026-08-22.

Any allowance a model does not spend, and every non-LLM arm's whole allowance, is
spent by this generator. Because it is identical everywhere, no arm can win on
data distribution — only on what it does with the data.

The policy draws a random sequence and runs it from every tag in turn. Running
the same sequence from all tags is what makes a word's behaviour comparable
across tags, which is the cheapest generically-useful thing to buy.
"""
from __future__ import annotations

import random
from typing import Iterator, List, Tuple

from universe import Universe


def probe_stream(uni: Universe, rng: random.Random) -> Iterator[Tuple[str, List[str]]]:
    while True:
        L = rng.randint(1, uni.spec.max_word_len)
        word = [rng.choice(uni.actions) for _ in range(L)]
        for tag in uni.tags:
            yield tag, list(word)
