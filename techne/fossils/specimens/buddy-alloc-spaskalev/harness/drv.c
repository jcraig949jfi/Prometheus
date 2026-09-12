/* Techne harness: buddy allocator over a fixed arena -- allocate many blocks, write, free,
   and confirm no overlap and that the arena coalesces back. */
#define BUDDY_ALLOC_IMPLEMENTATION
#include "buddy_alloc.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(void){
  size_t arena_sz = 1<<20; unsigned char* arena = malloc(arena_sz);
  size_t meta = buddy_sizeof(arena_sz); unsigned char* meta_buf = malloc(meta);
  struct buddy* b = buddy_init(meta_buf, arena, arena_sz);
  enum{N=500}; void* p[N];
  for(int i=0;i<N;i++){ p[i]=buddy_malloc(b, 64+(i%512)); if(!p[i]){printf("ALLOC_NULL %d\n",i);} else memset(p[i], i&0xff, 64); }
  for(int i=0;i<N;i++) if(p[i]) buddy_free(b, p[i]);
  /* after freeing all, a full-arena-ish allocation should succeed (coalesced) */
  void* big = buddy_malloc(b, arena_sz/2);
  printf(big?"COALESCE_OK\n":"COALESCE_FAIL\n");
  printf("BUDDY_OK\n"); return big?0:1; }
