#!/bin/sh
cd "$(dirname "$0")"
for c in bbef66a1 31cd2a8a 62a7fff9 c16d5231 4781b0a1 0a23398f f6b623cd; do
  [ -f out/hopscan_$c.json ] || timeout 590 python transplant_hop.py hopscan $c
done
for c in 4781b0a1 62a7fff9 bbef66a1 31cd2a8a c16d5231 0a23398f f6b623cd; do
  [ -f out/clique_$c.json ] || timeout 590 python transplant_hop.py clique $c
done
for c in 4ab2ba01 bf82cb29 cd5b6fd6 e06701a5 8743da7f; do
  [ -f out/fact2_$c.json ] || timeout 590 python transplant_hop.py fact2 $c
done
