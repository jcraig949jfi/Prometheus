# INV_E -- does Claude INDUCE alien rules, or does its success track COVERAGE?

Date: 2026-09-30. Analyst for Hecate. Read-only over existing pilot data; no model calls,
no git, no network. Follows ATTACK_C_alien_headlines.md item 1 (graph+rewrite: covered
states 2965/2965, uncovered 15/235) and goes family by family.

Inputs: hecate/alien/data/{public,answer_key,BASELINES}.json; hecate/alien/runs/claude/
{blind,active,reveal}.jsonl; hecate/alien/{systems,baselines,sandbox}.py.
Code: roles/Hecate/harvest_w2/INV_E_induction_vs_coverage.py (witnesses, OCD comparator,
receptive fields, sandbox runs; writes a pickle to the session scratchpad). Analysis
snippets an1..an5 import it (scratchpad, not committed; every number below is printed by
them). Run from F:/Prometheus-worktrees/hecate-base-role:

    python roles/Hecate/harvest_w2/INV_E_induction_vs_coverage.py   # 68 s, 60 lawful systems
    python <scratch>/an1.py ... an5.py

## 1. Definitions

Unit = one next-state COMPONENT of one held-out state (T5: 200 eval states per system,
Claude's step() code run through sandbox.run; T2: the 12 query predictions).

Witness (A systems; taint-tracked through the interpreter, so sequential updates carry the
entries of every earlier lookup that fed the value):
  tab_local   D_i[x_i][x_nb(i)]; compensated comp c: the D_j entries (j!=c, w_j!=0) of tot
  tab_rev     U_i[current x_nb(i)] in update order, plus taint of the neighbour
  graph_attr  G[x_i][sum nbrs mod 4]
  graph_flow  F[x_u][x_v] (ordered) for every edge touching the value, in edge order
  rewrite     T[(a,b)] for every scanned pair up to and incl. the first firing one
              ("no rule here" is an entry too); all components share it
  vm          ('P',c) instruction identity for every comp; + mix g[c,r_b], aff (c,r_b,r_z),
              tab T(c,r_b), jz/jnz (c,r_a) on the written register / pc
  map shear   h1(y); y' adds h2(x');   poly_sym g(x,y) / g(y,x) -> no finite witness:
              every eval state is uncovered except the ~1-4% whose (x,y) was observed
  linmix      witnesses of the latent base system; an observed comp unions all latent
              comps it mixes (so linmix is almost always uncovered)
COVERED = every witness key of that component was consulted at some observed source
(80 transitions blind; 2 runs + experiment sources for active).
RF coverage (second, family-agnostic notion, also for K): receptive field of comp i
computed exhaustively by perturbation; covered = (i, values on RF_i) seen at a source.

Comparators on the same units:
  local  = fit_localtab baseline (refit on the same transitions; unseen key -> identity)
  OCD    = coverage oracle: TRUE architecture + TRUE values of every seen entry + a
           "nothing happens" default for unseen entries (0 increment / no rule / no jump /
           register unchanged / G -> own value). Sanity: OCD with all keys seen == step on
           every sampled state (printed: 0 mismatches). OCD is the best a pure-coverage
           learner with the right architecture can do.
  ident  = next == current.
INDUCTION INDEX  II_loc = acc_unc(Claude) - acc_unc(local)   (as requested)
                 II_ocd = acc_unc(Claude) - acc_unc(OCD)     (sharper: removes architecture
                 and default-guess credit; >0 only if Claude knows unseen entries)

## 2. Blind T5, A systems, table-witness coverage (component level)

    group              cov     n sys claude  local  ident
    A:graph_attr       True 4646   4  1.000  0.553  0.380
    A:graph_flow       True 4400   4  1.000  0.564  0.501
    A:rewrite          True 8724   8  1.000  0.762  0.799
    A:shear            True  702   2  1.000  0.547  0.071
    A:tab_rev          True 1000   1  1.000  1.000  0.124
    A:vm_long          True 1442   2  1.000  0.874  0.639
    A:vm_lin           True 4054   6  0.973  0.839  0.487
    A:tab_local        True 2570   4  0.874  0.914  0.493
    A:linmix:tab_local True  895   3  0.254  0.222  0.254
    A (all)            True 28535 40 0.960  0.711  0.543

    tab-UNCOVERED      n     claude  OCD    local  II_loc II_ocd  claude-right&OCD-wrong
    graph_attr        154    0.000  0.000  0.143  -0.14  +0.00       0
    graph_flow        400    0.583  1.000  0.463  +0.12  -0.42       0
    rewrite           876    0.902  0.902  0.756  +0.15  +0.00       0
    tab_local        1430    0.384  0.483  0.448  -0.06  -0.10      81
    vm_lin            746    0.319  0.299  0.318  +0.00  +0.02      54
    vm_long           158    0.525  0.177  0.108  +0.42  +0.35      66
    shear              98    1.000  0.010  0.061  +0.94  +0.99      97
    poly_sym         1148    1.000  0.054  0.054  +0.95  +0.95    1086
    linmix:tab_local 2105    0.206  0.336  0.209  -0.00  -0.13     235
    linmix:poly_sym  1150    0.031  0.046  0.046  -0.01  -0.01      33
    ALL A            8265    0.437  0.358  0.281  +0.16  +0.08    1652
    (tab_rev has 0 uncovered components)

Pure-table generators pooled (graph_attr, graph_flow, rewrite, tab_local, vm_lin):
Claude 1810/3606 = 0.502, OCD 2104/3606 = 0.583 -> II_ocd = -0.08.

State level (reconciles with ATTACK_C): graph covered 1403/1403 exact, any-uncovered
15/197 (OCD 77/197); rewrite covered 2908/2908, any-uncovered 216/292 (OCD 216/292 --
every uncovered rewrite success is the "no rule fires" default; ATTACK_C did not count
non-firing pairs as witnesses, hence its 0/38). poly_sym 574/574 uncovered exact, shear
54/54, vm_long 83/158 (OCD 28/158).

T2 (12 queries) reproduces the pattern: ALL A uncovered Claude 0.428 / OCD 0.367 / local
0.255; poly_sym 1.000 (70), shear 1.000 (7), vm_long 0.444 (9), graph_attr 0/11, graph_flow
0.615 vs OCD 1.000, rewrite = OCD, tab_local 0.367 vs OCD 0.459.

## 3. Where the uncovered successes come from (an2, an3)

Uncovered components, Claude-correct x identity-correct (cl&id, cl&!id, !cl&id, !cl&!id):
    graph_attr    0    0    0  154      poly_sym   62 1086   0   0
    graph_flow   81  152  107   60      shear       6   92   0   0
    rewrite     712   78   10   76      tab_local 445  104 202 679
    vm_lin      156   82   62  446      vm_long    17   66  11  64

By unseen-key type (Claude / local):
    graph_attr:G  154  0.000/0.143     vm_lin:g    506  0.115/0.138  (arbitrary table)
    tab_local:D  1430  0.384/0.448     vm_lin:J     96  0.708/0.281  (zero-test form)
    rewrite:R     876  0.902/0.756     vm_lin:P    108  1.000/1.000  (unseen instr, untouched)
    graph_flow:F  400  0.583/0.463     vm_long:aff  78  0.654/0.064  (affine, induced)
    shear:h1/h2    98  1.000/~0.05     vm_long:T    79  0.392/0.152  (permutation)
    poly_sym:g   1148  1.000/0.054

vm_long detail (#entries of that instruction seen -> Claude right/wrong):
  aff: SYS-14818 5 and 13 seen -> 44/44 right; SYS-70612 3 seen -> 7/34 right.
  T (permutation of 7): 6 seen -> 5/5 right (completion by elimination); 4 seen -> 17/28;
  1 seen -> 9/32.

What the code does on unseen entries (read from blind t5):
  graph_attr SYS-12423: literal G table T=[[2,0,2,0],[0,0,0,0],...]; unseen G[1][3] (true 3)
    filled with 0 -> 72/72 wrong. SYS-82332 same (G[2][1] true 3, filled 0, 82 wrong).
  graph_flow SYS-87863 (blind): a COMPACT RULE, not a table: "high gives 1 to low if d>=2
    or (d==1 and high==3)". Unseen F[0][3]=F[3][0]=0 but the rule transfers on (0,3):
    167 wrong where the default-0 oracle is right. Induction attempted, over-generalised.
  poly_sym SYS-34934: k=(22(x+y)+1); x'=x+x(x-1)k -- an equivalent closed form, not the
    generator's polynomial. shear SYS-28905: exact h1,h2 polynomials. Genuine induction.
  linmix poly_sym SYS-41174: dict of the 60 observed transitions, fallback (8,19) for
    everything else -- pure memorisation, eval 0.
  tab_local SYS-80858: five full 5x5 VALUE tables on chosen index pairs (F2[b][c],
    F3[a][d], ...), unseen cells filled with guesses -- table fit, wrong architecture for
    the compensated component.

## 4. K vs A (receptive-field coverage; K has no tables)

    blind T5      cov    n    claude  local  ident  II_loc
    K:graph      unc  4120    0.977  0.583  0.446  +0.39
    K:map        unc  1358    1.000  0.185  0.053  +0.82
    K:rewrite    unc  3737    1.000  0.686  0.730  +0.31
    K:tab        unc  2434    1.000  0.515  0.531  +0.49
    K:vm         unc  1793    1.000  0.822  0.772  +0.18
    K  ALL       unc 13442    0.993  0.591  0.544  +0.40   (covered 4958: 1.000)
    A:graph      unc  8496    0.962  0.515  0.432  +0.45
    A:map        unc  3200    0.636  0.159  0.055  +0.48
    A:rewrite    unc  8374    0.990  0.734  0.807  +0.26
    A:tab        unc  4733    0.277  0.287  0.291  -0.01
    A:vm         unc  4871    0.861  0.699  0.554  +0.16
    A  ALL       unc 29674    0.809  0.532  0.495  +0.28   (covered 7126: 0.980)
T2: K unc 0.995 (II_loc +0.43), A unc 0.810 (+0.28); same family ordering.

Reading: at the level of LOCAL INPUT PATTERNS both classes generalise far beyond what was
seen (K ~1.0, A graph/rewrite ~0.96-0.99): Claude induces the update ARCHITECTURE --
which positions feed which, one table shared by every site/position, scan order. At the
level of TABLE ENTRIES, A success equals coverage except in the algebraic generators.

## 5. Active experimentation (an4; 2 runs + <=10 experiments; 10 A + 4 K)

    sid        kind         blind unc   active unc  active cov  local(act) eval b->a
    SYS-19722  vm_lin        16/203      51/174     558/626      61/174   0.724->0.761
    SYS-45738  vm_lin        34/150      20/204     559/596      36/204   0.830->0.724
    SYS-80858  tab_local     37/131      68/197     702/803      81/197   0.784->0.770
    SYS-87863  graph_flow   233/400     835/835     365/365     335/835   0.861->1.000
    SYS-99585  rewrite      228/228     462/462     738/738     380/462   1.000->1.000
    SYS-28905  shear         57/57      147/147     253/253      15/147   1.000->1.000
    SYS-34934  poly_sym     382/382     368/368      32/32       34/368   1.000->1.000
    (26937 graph_flow, 29535 tab_rev, 58162 rewrite: 0 uncovered, all 1.000)
    A pooled: blind unc 0.680 (local 0.398); active unc 0.817 (local 0.395); active cov 0.970
    K pooled: unc 1.000 both ways.
    II_ocd active: graph_flow +0.42, poly_sym +0.91, shear +0.90, rewrite +0.00,
                   tab_local -0.22, vm_lin +0.02; ALL A +0.33 (blind +0.08).

Experiments mostly buy COVERAGE: SYS-80858 components uncovered with 2 runs but covered
by experiments -> 311/392 right; still uncovered -> 68/197. Arbitrary tables (tab_local,
vm_lin) stay at OCD level. The one real rise is SYS-87863 graph_flow: its targeted runs
led to a different compact rule ("|x-y|==2 -> both to the mean; {2,3} swap") that is
exact. Active-unseen F entries there: (1,3)=+1, (2,0)=-1 (mirrors seen), (2,1)=0,
(3,3)=0. 348 components right where OCD is wrong -- all antisymmetry-recoverable (see 6).

## 6. Revealed rules (reveal T2, 25 lawful systems; table printed in full)

    blind-uncovered components: A reveal 148/148 vs blind 84/148; K 439/439 vs 435/439
    covered: A 680/680 reveal (blind 670/680); tab_local 81/81 unc and 99/99 cov.
Yes: with the table in hand accuracy is 1.000 everywhere, including tab_local where blind
failed even on covered entries. The shortfall is knowledge of entries/architecture, not
simulation.

## 7. Adversarial loop

E1 (my conclusion): on A systems built from arbitrary tables, Claude's accuracy on
components whose table entries were never observed is at or below a coverage oracle;
uncovered successes are defaults; real induction happens only where the generator has a
compressible parametric form (polynomial, affine, permutation, zero-test) and at the
architecture level.

E2 (strongest alternative): Claude infers STRUCTURE -- conservation laws, antisymmetry,
compensation -- that constrains uncovered entries, so its uncovered behaviour is lawful
even when wrong, and the coverage metric hides real induction.
Test: on states with >=1 uncovered component where the prediction is wrong, does the
prediction satisfy the planted invariant? (rand = uncovered comps of the truth replaced
by uniform values; nontriv = prediction changes an uncovered component.)

    kind             invariant        wrong  claude_ok  local_ok  rand_ok
    graph_flow       sum conserved       62    1.00      0.34      0.12   (62/62 nontriv)
    vm_lin           sum w r mod 7      284    1.00      0.95      0.23   (172 nontriv held,
                                                                        112 = no change)
    rewrite          weights mod k       38    1.00      0.58      0.25   (5 nontriv, 33 no change)
    tab_local        sum w x mod 5      247    0.59      0.19      0.20   (125 held/80 broken)
    tab_local cyc    sum w x +1         67    0.18      0.08      0.43
    linmix:tab_local latent conserved   416    1.00      0.22      0.20   (0 nontriv: code ~identity)

Antisymmetry test (graph_flow SYS-87863, unseen keys whose mirror is seen or diagonal):
  blind: recoverable 80/80 right (F[3][3]=0), not recoverable 153 right / 167 wrong.
  active: recoverable 835 right, of which 348 where the default oracle is wrong.
Hidden-symmetry test (linmix poly_sym, planted commutes_swap in latent coords): Claude's
code commutes with the hidden sigma on 192/200 (SYS-41174) -- ARTEFACT: the code returns
the constant (8,19) on every eval state; 0/200 on the other two.

Verdict on E2: PARTLY TRUE, does not overturn E1. Claude's models do carry structure that
holds on uncovered states: exchange/conservation in graph_flow (62/62 nontrivial errors
conserve; antisymmetry gives 348 above-oracle components in active), coupled register
updates in vm_lin, and partial compensation in tab_local (0.59 vs 0.20 random). But (a)
conservation constrains FORM, not the arbitrary VALUES -- errors are invariant-respecting
yet still errors, and the pooled table families stay at II_ocd -0.08; (b) in blind
graph_flow the structural rule over-generalised and lost 167 components the default
would win; (c) many "lawful" errors are just "predict no change", which conserves
anything. Structure inference is real but shows up as invariant-respecting mistakes and
antisymmetry completion, not as knowledge of unseen entries.

Distinguishing prediction checked: if E2 were the main story, uncovered accuracy should
exceed OCD on conserved generators. It does not: graph_flow -0.42 blind, vm_lin +0.02,
rewrite 0.00, tab_local -0.10. Only active graph_flow (+0.42) fits E2.

## 8. Caveats

- Taint witnesses are conservative (a consulted entry whose value was 0 still "touches"
  the component), which inflates "uncovered-but-correct"; OCD absorbs this.
- "Consulted" is not "revealed": a blocked flow or summed increments can hide an entry's
  value. Covered-wrong (tab_local 0.874, vm_lin 0.973) mixes this with architecture error.
- Two poly_sym codes (SYS-59756, SYS-96628) are rejected by the sandbox for calling a
  local lambda; scored here unsandboxed with the sandbox builtins (both 1.000), as in
  ATTACK_C.
- Clamp experiments add their sources to active coverage (slight overcount of the clamped
  component); clamp pairs are not given to the local baseline.
- One dataset draw; per-family n is 1-8 systems. Coverage is generator luck per seed.
- linmix systems: Claude never found the latent coordinates, so coverage is moot there.

## Summary (<=120 words)

Claude's success on table-driven aliens is coverage, not induction of entries: on
uncovered components of graph_attr, graph_flow, rewrite, tab_local and vm_lin it scores
0.50 vs 0.58 for a coverage oracle with a no-change default (II_ocd -0.08); every
uncovered rewrite success is the "no rule" default; unseen graph_attr cells are filled
with 0. Real induction exists where the law is parametric: poly_sym and shear 1.00 on
fully uncovered states (II +0.95), vm_long affine/permutation completion (+0.35), and at
the architecture level (RF-uncovered A 0.81, K 0.99). Errors often respect planted
conservation laws, and active experiments once recovered entries via antisymmetry, but
structure constrains form, not values. Active mostly buys coverage; revealed rules give
1.000 everywhere.
