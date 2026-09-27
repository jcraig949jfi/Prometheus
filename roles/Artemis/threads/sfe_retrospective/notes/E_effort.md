# Effort and time-to-result (Artemis, 2026-09-27)

Two bounded measurements for the SFE retrospective (REPORT.md s0, s4).
Measured on ubu002 against origin/main + all origin/* seat branches as
fetched 2026-09-27 ~15:15Z. Pure ASCII.

## 1. Commits per ISO week touching each path group

Script (verbatim below) counts each commit once per group whose path
prefix it touches, deduplicated by SHA across all remote refs, author
date. Caveat: commits are a proxy for effort, not for science; NPE's
2,101 in W38 are dominated by its swarm lanes' automatic ledger commits.

    $ python3 effort.py
    week        SFE Vivari    PEW Archae    NPE    BEE    AGE    CWE    WTP    PTE Aphrod  Atlas  comms
    2026-W36      53      8     41     20      0      0      0      0      0      0      0      0      0
    2026-W37      30     29     15     91      0      0      0      0      0      0      0      0      6
    2026-W38      46     40     23    130   2101    109     11      0      0      0      0     10      1
    2026-W39       0      0      0     44      0     12     83     27     79     12     55      4      0

    --- effort.py ---
    # Commits per ISO week touching each path group, across origin/main + all origin seat branches (deduped by SHA).
    import subprocess, collections, datetime
    G = {
     "SFE": ["SerendipityFoundry/"], "Vivarium": ["vivarium/"], "PEW": ["evidence_wiki/"],
     "Archaeon": ["archaeon/"], "NPE": ["primordial/"], "BEE": ["prometheus/toolbox/","prometheus/z80atlas/","prometheus/atlas_bee/"],
     "AGE": ["Aether/"], "CWE": ["prometheus/cosmos/"], "WTP": ["ensorain/"], "PTE": ["prometheus/ananke/"],
     "Aphrodite": ["roles/Aphrodite/engine/"], "Atlas": ["atlas/"], "comms": ["comms/"],
    }
    out = subprocess.run(["git","log","--remotes=origin","--since=2026-03-01","--format=@%H %ad","--date=short","--name-only"],capture_output=True,text=True).stdout
    wk = collections.defaultdict(collections.Counter); seen=set(); cur=None
    for line in out.splitlines():
        if line.startswith("@"):
            h,d = line[1:].split(); cur = None if h in seen else (h,d); seen.add(h); hit=set(); continue
        if cur and line:
            for g,ps in G.items():
                if g not in hit and any(line.startswith(p) for p in ps):
                    hit.add(g); y,w,_ = datetime.date.fromisoformat(cur[1]).isocalendar(); wk[f"{y}-W{w:02d}"][g]+=1
    names=list(G); print("week     "+" ".join(f"{n[:6]:>6}" for n in names))
    for k in sorted(wk):
        print(k+"  "+" ".join(f"{wk[k][n]:>6}" for n in names))

First commits touching each core path (git log --remotes=origin
--reverse -- <path> | head -1): SerendipityFoundry d332658cf 2026-09-01;
evidence_wiki c711c5bf6 09-01; vivarium 8b940a165 09-05; archaeon
df0837064 09-05; comms 7466bd6ac 09-11; primordial a901ba0c9 09-14;
atlas 61c3985fc 09-19. Last: SerendipityFoundry 9cfcd3779 09-18;
vivarium 1db58c264 09-17; evidence_wiki 0d448387e 09-18;
archaeon/producer 7017dc79e 09-17.

Reading: SFE, Vivarium and PEW each drew 8-53 commits a week through
W38 and 0 in W39 (2026-09-21..27); in W39 Aether 83, Ensorain 79,
Aphrodite 55, Archaeon 44 (non-SFE packages), Cosmos 27, BEE 12, PTE 12.

## 2. Time from founding to first result

Committer dates (%cd) of the first commit that reports an adjudicated
result, against the seat's or code's founding commit. Committer date can
lag authoring on merged branches; differences under a day are not
meaningful.

| Engine | Founded | First adjudicated result | Days | New world kind? |
|---|---|---|---|---|
| SFE era (Harmonia on SFE, onemax) | 09-01 d332658cf | 09-04 100c755f5 M2 verification; 09-05 76081a23e S1-3 reclassified | 3-4 | no -- bitstring/onemax only |
| SFE era: first non-onemax world | 09-01 | 09-10 b91880a2d nk_landscape_v0 (executor, not a result) | 9 | yes, NK |
| SFE era: first campaign report | 09-01 | 09-16 0728e9989 CMP1 (compute in Archaeon's WSE harness) | 15 | Proteus VM, outside SFE |
| Aphrodite | 09-17 8b54a74b8 | 09-17 07fcc2509 RSI toys E1-E4 verdicts | 0 | yes |
| Crius | 09-18 2e89d60cb | 09-23 7069c0ce6 C2 closed (C0 prereg 09-18) | 0-5 | yes |
| Ares | 09-19 d1f22735a | 09-19 bb133d083 first report | 0 | yes |
| Nestor Z80 | 09-19 (directive) | 09-19 aa5833488 frozen campaign; 9d9ef1980 flags adjudicated | 0 | yes |
| Archaeon z80atlas | 09-19 c7610ea19 | 09-22 d50f5710a campaign packet | 3 | yes |
| Aether | 09-19 298c2a511 | 09-22 f1f6dd637 FIRST_LIGHT | 3 | yes |
| Cosmos CWE | 09-23 70ce535a2 | 09-23 54ca84228 C0 run 2 | 0 | yes |
| Ensorain WTP | 09-23 57ed9184e | 09-23 8fe17208b E0 | 0 | yes |
| Ananke PTE | 09-24 7acc2926c | 09-24 e35fb9704 C1 report | 0 | yes |

Reading: time to a first adjudicated result was short in both shapes
(3-4 days on SFE). What differs is time to a NEW KIND OF WORLD: in the
SFE era a new world had to become an executor kind the engine and the
Vivarium queue admit (9 days to NK; "0 of 69 inbox templates build
today", 87bab0877, 09-06), while each new engine arrived with its own
world and reached a verdict in 0-5 days.
