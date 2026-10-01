#!/bin/sh
cd "$(dirname "$0")"
for c in bbef66a1 31cd2a8a 62a7fff9 c16d5231 4781b0a1 0a23398f f6b623cd; do
  [ -f out/fact_$c.json ] || timeout 590 python transplant_hop.py fact $c
done
for c in e2afff1c cd5b6fd6 a02aa099 bf82cb29 dcd404a9 ed16c553 2dccdaa5 78f3b0ec 4ab2ba01 00c5d3b6 1c0a1bc7 65d840a8 0187372b 63d17a90 369f5a5b; do
  [ -f out/lite_$c.json ] || timeout 590 python transplant_hop.py lite $c
done
