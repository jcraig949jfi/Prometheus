// Techne harness: LevelDB write-ahead-log recovery. modes: write lo hi | crash lo hi | count
#include <cstdio>
#include <cstdlib>
#include <string>
#include <unistd.h>
#include "leveldb/db.h"
int main(int argc, char** argv) {
    if (argc < 3) return 2;
    std::string path = argv[1], mode = argv[2];
    leveldb::DB* db; leveldb::Options o; o.create_if_missing = true;
    leveldb::Status s = leveldb::DB::Open(o, path, &db);
    if (!s.ok()) { fprintf(stderr, "open: %s\n", s.ToString().c_str()); return 2; }
    if (mode == "write" || mode == "crash") {
        int lo = atoi(argv[3]), hi = atoi(argv[4]); char k[32], v[32];
        for (int i = lo; i < hi; i++) { snprintf(k, 32, "key%06d", i); snprintf(v, 32, "val%06d", i); db->Put(leveldb::WriteOptions(), k, v); }
        if (mode == "crash") { printf("crashing after %d acknowledged unsynced puts (no Close)\n", hi - lo); fflush(stdout); _exit(1); }
        printf("wrote %d\n", hi - lo); delete db;
    } else {
        long n = 0; leveldb::Iterator* it = db->NewIterator(leveldb::ReadOptions());
        for (it->SeekToFirst(); it->Valid(); it->Next()) n++;
        delete it; std::string val; bool have = db->Get(leveldb::ReadOptions(), "key002400", &val).ok();
        printf("count=%ld key002400 present? %s\n%s\n", n, have ? "yes" : "NO", (n == 2500 && have) ? "RECOVERY OK" : "RECOVERY FAILED");
        delete db;
    }
    return 0;
}
