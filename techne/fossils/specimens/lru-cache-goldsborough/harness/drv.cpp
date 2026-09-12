/* Techne harness: LRU must evict the least-recently-used key on overflow; and a working set
   larger than capacity must THRASH (near-zero hit rate). */
#include <cstdio>
#include <lru/lru.hpp>
int main(){
  {
    LRU::Cache<int,int> c(3);
    c.insert(1,1); c.insert(2,2); c.insert(3,3);   /* recency front->back: 3,2,1 ; LRU = 1 */
    c.insert(4,4);                                 /* full -> evicts the LRU key (1) */
    printf("has1=%d has2=%d has3=%d has4=%d\n",
           (int)c.contains(1),(int)c.contains(2),(int)c.contains(3),(int)c.contains(4));
    if (!c.contains(1) && c.contains(2) && c.contains(3) && c.contains(4)) printf("LRU_EVICT_OK\n");
    else printf("LRU_EVICT_BAD\n");
  }
  {
    LRU::Cache<int,int> c(10); int hits=0, N=100000;
    for(int k=0;k<N;k++){ int key=k%1000;          /* working set 1000 >> capacity 10 */
      if(c.contains(key)) hits++; else c.insert(key,key); }
    double hr=100.0*hits/N; printf("thrash_hit_rate=%.2f%%\n", hr);
    if (hr < 5.0) printf("LRU_THRASH_CONFIRMED\n");
  }
  return 0; }
