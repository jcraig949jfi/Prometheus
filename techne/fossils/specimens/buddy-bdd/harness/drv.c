/* Techne smoke: build (a & b) | (a & c) as a BDD and check its satisfying-assignment count.
   Over variables a,b,c the models are: a&b (c free)->{110,111}, a&c&!b->{101} = 3 total. */
#include <stdio.h>
#include "bdd.h"
int main(void){
  bdd_init(1000,100); bdd_setvarnum(3);
  BDD a=bdd_ithvar(0), b=bdd_ithvar(1), c=bdd_ithvar(2);
  BDD f = bdd_or(bdd_and(a,b), bdd_and(a,c));
  double sc = bdd_satcount(f);
  int nc = bdd_nodecount(f);
  printf("nodes=%d satcount=%.0f\n", nc, sc);
  if ((int)sc == 3) printf("BDD_OK\n"); else printf("BDD_BAD\n");
  bdd_done(); return (int)sc==3?0:1; }
