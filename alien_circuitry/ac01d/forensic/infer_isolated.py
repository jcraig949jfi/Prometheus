"""ISOLATED INFERENCE PROCESS.  Loads ONLY: model weights, a (n, 14) int64 array of raw digits, a scalar mean.
Imports nothing from alien_circuitry.  Never sees D, state ids, target ids, the corpus, or the universe.
Usage: python infer_isolated.py <weights.pt> <idx.npy> <out.npy> <mean> <emb> <hidden>
"""
import sys
import numpy as np
import torch, torch.nn as nn

SIZES = [7] * 7 + [2] * 7


class DigitNet(nn.Module):
    def __init__(self, emb, hidden):
        super().__init__()
        self.emb = nn.ModuleList([nn.Embedding(sz, emb) for sz in SIZES])
        self.mlp = nn.Sequential(nn.Linear(14 * emb, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def forward(self, idx):
        return self.mlp(torch.cat([e(idx[:, m]) for m, e in enumerate(self.emb)], dim=1)).squeeze(1)


if __name__ == "__main__":
    wpath, ipath, opath, mean, emb, hidden = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    sd = torch.load(wpath); net = DigitNet(emb, hidden); net.load_state_dict({k: v.float() for k, v in sd.items()}); net.eval()
    idx = torch.as_tensor(np.load(ipath))
    assert idx.shape[1] == 14 and int(idx[:, :7].max()) <= 6 and int(idx[:, 7:].max()) <= 1, "input is not 14 raw digits"
    with torch.no_grad():
        pred = torch.cat([net(idx[i:i + 65536]) for i in range(0, len(idx), 65536)]).numpy() + mean
    np.save(opath, pred)
    loaded = sorted(m for m in sys.modules if m.startswith("alien_circuitry"))
    print(f"isolated: rows={len(idx)} alien_circuitry_modules_loaded={loaded} D_in_memory=False")
