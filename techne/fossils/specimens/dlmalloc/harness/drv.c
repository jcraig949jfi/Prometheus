/* Techne smoke: dlmalloc must hand out distinct, writable, non-overlapping blocks and free
   them without corruption. This exercises the allocator; it does not decompose it. */
#define USE_DL_PREFIX 1
#define ONLY_MSPACES 0
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
extern void* dlmalloc(size_t); extern void dlfree(void*); extern void* dlrealloc(void*, size_t);
int main(void){
  enum{N=2000}; void* p[N]; size_t sz[N];
  unsigned s=12345; for(int i=0;i<N;i++){ s=s*1103515245u+12345u; sz[i]=1+(s>>16)%4096;
    p[i]=dlmalloc(sz[i]); if(!p[i]){printf("NULL at %d\n",i);return 1;} memset(p[i], i&0xff, sz[i]); }
  /* verify writes survived (no overlap clobber) */
  for(int i=0;i<N;i++){ unsigned char* q=p[i]; for(size_t j=0;j<sz[i];j++) if(q[j]!=(i&0xff)){printf("CLOBBER at %d\n",i);return 2;} }
  for(int i=0;i<N;i+=2) dlfree(p[i]);            /* free half, realloc the rest */
  for(int i=1;i<N;i+=2){ p[i]=dlrealloc(p[i], sz[i]*2); if(!p[i]){printf("REALLOC NULL\n");return 3;} }
  for(int i=1;i<N;i+=2) dlfree(p[i]);
  printf("DLMALLOC_OK %d blocks, no clobber\n", N); return 0; }
