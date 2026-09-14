/* Techne harness: LMDB crash-consistency. modes: commit | crash | count */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "lmdb.h"
static void die(const char *m, int rc) { fprintf(stderr, "%s: %s\n", m, mdb_strerror(rc)); exit(2); }
int main(int argc, char **argv) {
    if (argc < 3) return 2;
    const char *path = argv[1], *mode = argv[2];
    MDB_env *env; MDB_dbi dbi; MDB_txn *txn; MDB_val k, v; char kb[32], vb[32]; int rc, i;
    mdb_env_create(&env); mdb_env_set_mapsize(env, 64u << 20);
    if ((rc = mdb_env_open(env, path, 0, 0664))) die("env_open", rc);
    if (!strcmp(mode, "commit") || !strcmp(mode, "crash")) {
        int lo = strcmp(mode, "commit") ? 1000 : 0, hi = strcmp(mode, "commit") ? 1500 : 1000;
        if ((rc = mdb_txn_begin(env, NULL, 0, &txn))) die("txn_begin", rc);
        if ((rc = mdb_dbi_open(txn, NULL, 0, &dbi))) die("dbi_open", rc);
        for (i = lo; i < hi; i++) {
            sprintf(kb, "key%06d", i); sprintf(vb, "val%06d", i);
            k.mv_size = strlen(kb); k.mv_data = kb; v.mv_size = strlen(vb); v.mv_data = vb;
            if ((rc = mdb_put(txn, dbi, &k, &v, 0))) die("put", rc);
        }
        if (!strcmp(mode, "crash")) { printf("crashing with %d uncommitted puts in an open write transaction\n", hi - lo); fflush(stdout); _exit(1); }
        if ((rc = mdb_txn_commit(txn))) die("commit", rc);
        printf("committed %d entries\n", hi - lo);
    } else {
        MDB_stat st;
        if ((rc = mdb_txn_begin(env, NULL, MDB_RDONLY, &txn))) die("txn_begin", rc);
        if ((rc = mdb_dbi_open(txn, NULL, 0, &dbi))) die("dbi_open", rc);
        mdb_stat(txn, dbi, &st);
        printf("entries=%zu\n", (size_t) st.ms_entries);
        sprintf(kb, "key%06d", 1200); k.mv_size = strlen(kb); k.mv_data = kb;
        rc = mdb_get(txn, dbi, &k, &v);
        printf("uncommitted key1200 present? %s\n", rc == MDB_NOTFOUND ? "no" : "YES");
        printf("%s\n", (st.ms_entries == 1000 && rc == MDB_NOTFOUND) ? "RECOVERY OK" : "RECOVERY FAILED");
        mdb_txn_abort(txn);
    }
    mdb_env_close(env);
    return 0;
}
