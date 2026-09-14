/* Techne harness: writer progress under continuous reader pressure, for a chosen rwlock kind.
   usage: starve reader|writer <seconds> <n_readers> */
#define _GNU_SOURCE
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
static pthread_rwlock_t lk; static volatile int stop = 0; static volatile long reads = 0, writes = 0;
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec + t.tv_nsec*1e-9; }
static void *reader(void *a){ while(!stop){ pthread_rwlock_rdlock(&lk); for (volatile int i=0;i<2000;i++); __sync_fetch_and_add(&reads,1); pthread_rwlock_unlock(&lk);} return 0; }
static void *writer(void *a){ while(!stop){ pthread_rwlock_wrlock(&lk); __sync_fetch_and_add(&writes,1); pthread_rwlock_unlock(&lk); for (volatile int i=0;i<200;i++);} return 0; }
int main(int argc, char **argv){
    if (argc < 4) return 2;
    int secs = atoi(argv[2]), nr = atoi(argv[3]);
    pthread_rwlockattr_t at; pthread_rwlockattr_init(&at);
    int kind = strcmp(argv[1],"writer")==0 ? PTHREAD_RWLOCK_PREFER_WRITER_NONRECURSIVE_NP : PTHREAD_RWLOCK_PREFER_READER_NP;
    pthread_rwlockattr_setkind_np(&at, kind); pthread_rwlock_init(&lk, &at);
    pthread_t r[64], w; for (int i=0;i<nr;i++) pthread_create(&r[i],0,reader,0);
    usleep(20000); pthread_create(&w,0,writer,0);
    double t0=now(); sleep(secs); stop=1; for (int i=0;i<nr;i++) pthread_join(r[i],0); pthread_join(w,0);
    double dt=now()-t0;
    printf("kind=%s readers=%d seconds=%.1f reader_acquisitions=%ld writer_acquisitions=%ld writer_per_second=%.1f\n",
        kind==PTHREAD_RWLOCK_PREFER_READER_NP ? "PREFER_READER" : "PREFER_WRITER_NONRECURSIVE", nr, dt, reads, writes, writes/dt);
    return 0;
}
