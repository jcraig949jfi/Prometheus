import collections, sys
sys.path.insert(0, __file__.rsplit("checks",1)[0]+"checks")
from rows import rows, ROOT
R = rows()
print(len(R), "rows; unique ids", len({r['cell_id'] for r in R}))
c = collections.Counter((r['wave'], r['kind']) for r in R)
print(sorted(c.items()))
for k in ("evolve","transfer","adjudicate","census"):
    ex = next(r for r in R if r['kind']==k)
    print(k, "result keys", sorted(ex['result'].keys()), "labels" in ex, ex.get('labels'))
