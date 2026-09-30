# Arm A (LLM semantic synthesis) -- task spec given to a fresh agent

Currency: 2026-09-30. Written by Theseus BEFORE any Theseus run. The agent
that fills GENOMES.jsonl sees only this file and TUPLES.json.

## Task

For each tuple in TUPLES.json (30 triplets, 30 sextuplets of human
concepts), do what an LLM does when asked "what mechanism results from
combining these concepts?": synthesise ONE mechanism semantically, then
write it as an executable genome in the DSL below. One output line per
tuple, in TUPLES.json order, to GENOMES.jsonl:

  {"tid": "...", "idea": "<= 25 words naming the synthesised mechanism",
   "genome": {...}}

Use your own judgement about what the combination means. Do not try to be
random; do not try to be weird for its own sake; synthesise the mechanism
you think the combination suggests.

## DSL (the substrate)

State: C channels (1..4) over N = 32 cells, real-valued, plus a memory
field of the same shape. T = 128 steps. Rules apply SEQUENTIALLY in list
order every step; each rule reads the state the previous rule left.

genome = {
  "C": 1..4,
  "topo": {"kind": "ring"|"line"|"rrg"|"mean"|"star", "seed": int},
  "bc": "periodic"|"fixed0"|"reflect"|"absorb",
  "init": {"kind": "spike"|"random"|"gradient"|"blocks"|"alternate", "amp": float},
  "rules": [ {"op": ..., "src": [channels], "dst": channel, "p": [params]}, ... ]   1..14 rules
}
topo: ring/line = neighbours i-1, i+1; rrg = 3 random neighbours; mean =
every cell sees the global mean; star = cell 0 is a hub.

ops (n_src, params in order with bounds), x = dst channel, s = src channel:
  diffuse    1  [rate 0.01..0.5]            x += rate*(neighbour_mean(s) - x)
  advect     1  [shift int -3..3, rate 0.01..0.9]  x += rate*(roll(s, shift) - x)
  react      1..8 [coef -1..1, bias -1..1, g_1..g_n each -2..2]
                                            x += coef*tanh(prod_j (bias + g_j*tanh(s_j)))
  saturate   0  [level 0.2..5]             x = level*tanh(x/level)
  conserve   0  [strength 0.05..1]         x -= strength*(mean(x) - initial_mean(x))
  decay      0  [rate 0.005..0.3]          x *= (1 - rate)
  remember   1  [rate 0.02..0.9]           memory[dst] = (1-rate)*memory[dst] + rate*s
  recall     0  [rate -1..1]               x += rate*(memory[dst] - x)
  threshold  1  [th -1..1, gain -1..1]     x += gain*tanh(8*(s - th))
  replicate  1  [rate 0.02..0.9]           x += rate*max(neighbour_max(s) - x, 0)
  select     0  [frac 0.1..0.9, rate 0.02..0.6]  cells below the (1-frac) quantile shrink by rate
  mirror     0  [w 0.02..1]                x = (1-w)*x + w*reverse(x)
  coarse     1  [block int 1..3, rate 0.02..0.9]  x += rate*(blockmean_{2^block}(s) - x)
  delay      1  [lag int 1..8, rate -1..1]  x += rate*(s(t-lag) - x)
  wrap       0  [period 0.5..4]            x = mod(x + period/2, period) - period/2
  rank       0  [w 0.02..1]                blend x toward its rank profile
  drive      0  [amp -1..1, period int 2..32, cell_frac 0..0.999]  sinusoidal forcing at one cell
  gate       2  [th -1..1, rate -1..1]     where s1 > th: x += rate*(s2 - x)

"src" length must equal n_src (react: 1..8, and then p has 2 + n_src
entries). Channels are 0..C-1. Integers where marked int.
