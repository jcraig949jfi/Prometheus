"""_draw_cell / wave_A redraw on Physics.validate() AssertionError (campaign.py:361-368, 410-416):
the 'uniform' dial draws are conditioned on validity. Which dials are skewed in A0 (5000 cells)?
Chi-square-ish: max |freq - 1/k| per dial, and the redraw rate."""
import os; os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import sys, collections, numpy as np
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
sys.path.insert(0, str(ROOT))
from prometheus.ananke import campaign as C
from prometheus.ananke.rng import H_int
A0=[r for r in rows() if r['wave']=='A0']
redraw=0
for i in range(C.CampaignConfig().a0_cells):
    s0=H_int(C.CampaignConfig().seed,0xA0,i); s,lv,ph=C._draw_cell(None,s0); redraw+= (s!=s0)
print("A0 cells needing >=1 redraw:", redraw, "/ 5000")
for dial, levels in C.DIALS.items():
    cnt=collections.Counter(r['levels'][dial] for r in A0)
    fr=np.array([cnt[l]/len(A0) for l in levels]); dev=np.abs(fr-1/len(levels)).max()
    if dev>0.03: print(f"  {dial:14s} expected {1/len(levels):.3f} observed {dict(zip(map(str,levels),fr.round(3)))}")
