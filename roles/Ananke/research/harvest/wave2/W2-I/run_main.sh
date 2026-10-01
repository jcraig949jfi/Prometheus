#!/bin/sh
# one process per cell (each well under 10 min wall), sequential
cd "$(dirname "$0")"
for c in bbef66a1 31cd2a8a 62a7fff9 c16d5231 4781b0a1 0a23398f f6b623cd c3d2d697 405e5c56 e06701a5 4316f167 72dd71d8 35c721fd e9196cae 8c37f32e 8743da7f 772ae210 1c12d560 18c218f5 15e58864 1a86071f 85ca202e ab089e45 a0a5244d 7b7b025e 613162a3; do
  [ -f out/main_$c.json ] || timeout 590 python transplant_hop.py main $c
done
