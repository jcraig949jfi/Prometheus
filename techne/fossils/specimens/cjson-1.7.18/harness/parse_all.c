/* Techne harness: parse every file given; count parsed / rejected; a crash never returns. */
#include <stdio.h>
#include <stdlib.h>
#include "cJSON.h"
int main(int argc, char **argv) {
    long parsed = 0, rejected = 0;
    for (int i = 1; i < argc; i++) {
        FILE *f = fopen(argv[i], "rb"); if (!f) continue;
        fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
        char *buf = malloc(n + 1); fread(buf, 1, n, f); buf[n] = 0; fclose(f);
        cJSON *j = cJSON_ParseWithLength(buf, n);
        if (j) { char *out = cJSON_PrintUnformatted(j); if (out) free(out); cJSON_Delete(j); parsed++; } else rejected++;
        free(buf);
    }
    printf("files=%d parsed=%ld rejected=%ld crashed=0\n", argc - 1, parsed, rejected);
    return 0;
}
