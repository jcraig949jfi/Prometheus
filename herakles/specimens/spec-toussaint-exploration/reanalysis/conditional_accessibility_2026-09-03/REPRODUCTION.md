# REPRODUCTION

Every number in the review packet comes from these four commands, run in this
directory, in this order. No new scientific compute occurs: nothing evolves,
nothing is simulated, and no detector is re-sampled. All four scripts read only
the frozen HC-T01 rows under `../../derived/`.

    python ra_audit.py                    # -> RA1_DATA_AUDIT.json
    python ra1.py                         # -> RA1_TIME_SERIES.csv
                                          #    RA1_SUMMARY.json
                                          #    RA1_NEGATIVE_CONTROLS.csv
    python ra1_sensitivity_and_k7.py      # -> RA1_SENSITIVITY_AND_K7.csv/.json
    python ra2.py                         # -> RA2_SUMMARY.json, RA2_DETAIL.csv

Then the verdict assembly step, which annotates RA1_SUMMARY.json in place with
the preregistered decision rule. It is embedded in the commit history rather
than in a separate script; rerunning it is not required to reproduce any
number, only the verdict labels.

Runtime: about 10 seconds for `ra1.py` including 2000 bootstrap and 2000
permutation replicates, under a second for the others.

Determinism: `ra1.py` seeds Python's RNG with 20260903 at module load, so the
bootstrap intervals and permutation p-values reproduce exactly.

## Spot checks a reviewer can run in a minute

Confirm the ceiling degeneracy that voids the original K7 window:

    python -c "
    import csv,glob,os,math
    rows={}
    for f in glob.glob('../../derived/grid/a0.03_b0.1_s*.csv'):
        s=int(os.path.basename(f)[:-4].split('_')[2][1:])
        for l in open(f):
            p=l.split(',')
            if len(p)>2: rows[(s,int(p[1]))]=float(p[2])
    seeds=sorted({s for s,_ in rows})
    F=[rows[(s,100)] for s in seeds]; G=[rows[(s,500)]-rows[(s,100)] for s in seeds]
    print('n',len(seeds))
    print('runs already at optimum at gen 100:',sum(1 for x in F if x==0.0))
    print('distinct gain values:',len({round(x,9) for x in G}))
    "

Confirm the machinery step in RA-2:

    python -c "
    import glob,os,math
    from collections import defaultdict
    b=defaultdict(list)
    for f in glob.glob('../../derived/grid/a0.03_b0.1_s*.csv'):
        for l in open(f):
            p=l.split(',')
            if len(p)>17: b[int(math.floor(float(p[17])))].append(float(p[4]))
    for k in sorted(b):
        if len(b[k])>=10: print('nops',k,'n',len(b[k]),'mean md %.3f'%(sum(b[k])/len(b[k])))
    "

Confirm that no beta=0.0 row has any operator:

    awk -F, '{if ($18+0 != 0) c++} END {print "nonzero nops rows in beta=0.0:", c+0}' ../../derived/grid/a*_b0.0_s*.csv
