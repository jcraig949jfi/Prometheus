"""U3: TorchRollout.tick() captured as a torch CUDA graph -- brain forward, action decode,
descriptor counters and world update replayed as one graph per step (ticks_per_graph=1), or
as a static multi-step graph (ticks_per_graph=K; the T % K leftover ticks run eagerly).

Every tensor the graph reads or writes (TorchRollout.state()) is allocated once by the first
load() and then refilled in place: a new genome batch or seed set of the same shape is COPIED
into the captured tensors, never rebound. A new shape or a new brain cheat re-captures.
Warmup and capture really execute ticks, so state is restored from a fresh eager load after.
"""
from __future__ import annotations

import torch

from .rollout import TorchRollout

WARMUP = 3


class GraphRollout(TorchRollout):
    def __init__(self, g7, device="cuda", world_cheat: str = "", ticks_per_graph: int = 1):
        if torch.device(device).type != "cuda":
            raise ValueError("CUDA graphs need a cuda device")
        super().__init__(g7, device, world_cheat)
        self.K = max(1, min(int(ticks_per_graph), g7.T))
        self.graph, self.key = None, None

    def _capture(self) -> None:
        side = torch.cuda.Stream()
        with torch.cuda.stream(side):
            for _ in range(WARMUP):
                self.tick()
        torch.cuda.current_stream().wait_stream(side)
        self.graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.graph):
            for _ in range(self.K):
                self.tick()

    def load(self, g, seeds, cheat: bool = False) -> None:
        key = (len(g[1]), len(seeds), bool(cheat))
        if self.graph is None or key != self.key:
            TorchRollout.load(self, g, seeds, cheat)
            self._capture()
            self.key = key
        fresh = TorchRollout(self.g7, self.device, self.world.cheat)
        fresh.load(g, seeds, cheat)
        for dst, src in zip(self.state(), fresh.state()):
            dst.copy_(src)
        self.P, self.k = fresh.P, fresh.k

    def run(self, g, seeds, cheat: bool = False):
        self.load(g, seeds, cheat)
        full, rest = divmod(self.g7.T, self.K)
        for _ in range(full):
            self.graph.replay()
        for _ in range(rest):
            self.tick()
        return self.result()
