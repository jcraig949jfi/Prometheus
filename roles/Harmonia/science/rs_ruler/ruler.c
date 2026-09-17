/* RS equivalence ruler -- calibration on RS_CALIBRATION_PAIR_001
 * Harmonia[m2-038758c6], 2026-09-16, Mechanism Archaeology Pipeline Amendment 3 N3.
 *
 * Both bodies are compiled UNMODIFIED from the fossil vault:
 *   a  reed-solomon-rockliff-1991/upstream/rs.c   (#included here with main renamed;
 *      compile-time mm=4 nn=15 tt=3 kk=9, pp = x^4+x+1)
 *   b  libfec-karn/upstream/tree/{init,encode,decode}_rs_int.c (compiled beside this
 *      file; init_rs_int(4, 0x13, 1, 1, 6, 0))
 *
 * The ruler drives both with the SAME information symbols and the SAME error
 * pattern, mapping between the two codeword conventions:
 *   Rockliff: recd[i] is the coefficient of X^i; recd[0..5] = parity, recd[6..14] = data,
 *             data[k] = coefficient of X^(k+6)
 *   Karn:     block[j] is the coefficient of X^(14-j); block[0..8] = data, block[9..14] = parity
 *   so Rockliff position i  <->  Karn index 14-i.
 *
 * Outcomes are read from the OUTPUT WORD, never from a return code alone:
 *   CORRECTED    output == transmitted codeword
 *   PASSTHROUGH  output == received (corrupted) word, unchanged
 *   MISCORRECTED neither
 * Karn's return value is recorded beside its outcome. Rockliff has no return value.
 *
 * Modes (argv[1]):
 *   pair        a vs b, the calibration proper
 *   self-karn   b vs b (cheat control: the ruler must find NO divergence)
 *   self-rock   a vs a (cheat control: the ruler must find NO divergence)
 *   mismap      a vs b with fcr=0 (negative control for the parameter mapping:
 *               R-ID-1 must read DIVERGENT)
 * argv[2] = trials per error count (default 2000), argv[3] = seed (default 20260916).
 * Output: one JSON object on stdout.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---- body a: Rockliff 1991, unmodified, main() renamed ---- */
#define main rockliff_main
#include "rs.c"
#undef main

/* ---- body b: Karn libfec, compiled separately; prototypes only ---- */
void *init_rs_int(int symsize, int gfpoly, int fcr, int prim, int nroots, int pad);
void  encode_rs_int(void *rs, unsigned int *data, unsigned int *parity);
int   decode_rs_int(void *rs, unsigned int *data, int *eras_pos, int no_eras);
void  free_rs_int(void *rs);

/* deterministic PRNG (no libc rand: host independence) */
static unsigned long long g_state;
static unsigned int rnd(void) {
    g_state = g_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (unsigned int)(g_state >> 33);
}

enum outcome { CORRECTED = 0, PASSTHROUGH = 1, MISCORRECTED = 2 };
static const char *OUT[] = {"CORRECTED", "PASSTHROUGH", "MISCORRECTED"};

static int mode_self_karn = 0, mode_self_rock = 0, mismap = 0;

/* --- adapters: both sides speak "Rockliff positions" to the ruler --- */

/* side A: encode d[0..8] -> full codeword cw[0..14] (Rockliff positions) */
static void a_encode(const int *d, int *cw) {
    int i;
    for (i = 0; i < kk; i++) data[i] = d[i];
    encode_rs();
    for (i = 0; i < nn - kk; i++) cw[i] = bb[i];
    for (i = 0; i < kk; i++) cw[i + nn - kk] = d[i];
}
/* side A: decode word w[0..14] in place; no return value exists */
static void a_decode(int *w) {
    int i;
    for (i = 0; i < nn; i++) recd[i] = index_of[w[i]];
    decode_rs();
    for (i = 0; i < nn; i++) w[i] = recd[i];
}

static void *krs;
/* side B: encode with Karn, returned in Rockliff positions */
static void b_encode(const int *d, int *cw) {
    unsigned int kd[9], kp[6];
    int i;
    for (i = 0; i < 9; i++) kd[i] = (unsigned int)d[8 - i];
    encode_rs_int(krs, kd, kp);
    for (i = 0; i < 9; i++) cw[14 - i] = (int)kd[i];
    for (i = 0; i < 6; i++) cw[14 - (9 + i)] = (int)kp[i];
}
/* side B: decode in place, returns Karn's count (-1 = uncorrectable flag) */
static int b_decode(int *w, int *eras_rock_pos, int n_eras) {
    unsigned int blk[15];
    int eras[15], i, r;
    for (i = 0; i < 15; i++) blk[14 - i] = (unsigned int)w[i];
    for (i = 0; i < n_eras; i++) eras[i] = 14 - eras_rock_pos[i];
    r = decode_rs_int(krs, blk, n_eras ? eras : NULL, n_eras);
    for (i = 0; i < 15; i++) w[i] = (int)blk[14 - i];
    return r;
}

/* the two "sides" the ruler compares; self modes alias one body */
static void side1_encode(const int *d, int *cw) { if (mode_self_karn) b_encode(d, cw); else a_encode(d, cw); }
static void side1_decode(int *w)               { if (mode_self_karn) b_decode(w, NULL, 0); else a_decode(w); }
static void side2_encode(const int *d, int *cw) { if (mode_self_rock) a_encode(d, cw); else b_encode(d, cw); }
static int  side2_decode(int *w)               { if (mode_self_rock) { a_decode(w); return -99; } return b_decode(w, NULL, 0); }

static enum outcome classify(const int *out, const int *sent, const int *recv) {
    if (memcmp(out, sent, 15 * sizeof(int)) == 0) return CORRECTED;
    if (memcmp(out, recv, 15 * sizeof(int)) == 0) return PASSTHROUGH;
    return MISCORRECTED;
}

static void random_data(int *d) { int i; for (i = 0; i < 9; i++) d[i] = (int)(rnd() % 16); }

/* choose e distinct positions in 0..14 and nonzero error values */
static void random_errors(int e, int *pos, int *val) {
    int used[15] = {0}, i;
    for (i = 0; i < e; i++) {
        int p;
        do { p = (int)(rnd() % 15); } while (used[p]);
        used[p] = 1; pos[i] = p; val[i] = 1 + (int)(rnd() % 15);
    }
}

int main(int argc, char **argv) {
    const char *mode = argc > 1 ? argv[1] : "pair";
    int trials = argc > 2 ? atoi(argv[2]) : 2000;
    unsigned long long seed = argc > 3 ? strtoull(argv[3], NULL, 10) : 20260916ULL;
    int e, t, i;
    int fcr = 1;

    if (!strcmp(mode, "self-karn")) mode_self_karn = 1;
    else if (!strcmp(mode, "self-rock")) mode_self_rock = 1;
    else if (!strcmp(mode, "mismap")) { mismap = 1; fcr = 0; }
    else if (strcmp(mode, "pair")) { fprintf(stderr, "unknown mode\n"); return 2; }

    generate_gf(); gen_poly();
    krs = init_rs_int(4, 0x13, fcr, 1, 6, 0);
    if (!krs) { printf("{\"error\":\"init_rs_int failed\"}\n"); return 3; }

    printf("{\n \"mode\": \"%s\", \"trials_per_error_count\": %d, \"seed\": %llu,\n", mode, trials, seed);

    /* R-ID-1: parity identity over random data blocks */
    {
        int d[9], cw1[15], cw2[15], bad = 0;
        g_state = seed ^ 0x1111ULL;
        for (t = 0; t < trials; t++) {
            random_data(d); side1_encode(d, cw1); side2_encode(d, cw2);
            if (memcmp(cw1, cw2, sizeof cw1)) bad++;
        }
        printf(" \"R-ID-1\": {\"blocks\": %d, \"parity_mismatch\": %d, \"verdict\": \"%s\"},\n",
               trials, bad, bad ? "DIVERGENT" : "IDENTICAL");
    }

    /* R-ID-2 (e = 0..3) and R-DIV-1 (e = 4), plus e = 5, 6 for the shape */
    printf(" \"by_error_count\": {\n");
    for (e = 0; e <= 6; e++) {
        int d[9], sent[15], recv[15], w1[15], w2[15], pos[15], val[15];
        long joint[3][3] = {{0}};           /* [side1 outcome][side2 outcome] */
        long karn_ret_hist[8] = {0};        /* index 0 = -1, 1..7 = count 0..6 */
        long out_identical = 0, karn_flag_and_rock_pass = 0, karn_flag = 0;
        long side2_corrected_count_eq_e = 0, karn_corrects_beyond_t = 0;
        g_state = seed ^ (0x2222ULL * (unsigned long long)(e + 1));
        for (t = 0; t < trials; t++) {
            int r;
            random_data(d); side1_encode(d, sent);
            memcpy(recv, sent, sizeof sent);
            random_errors(e, pos, val);
            for (i = 0; i < e; i++) recv[pos[i]] ^= val[i];
            memcpy(w1, recv, sizeof recv); memcpy(w2, recv, sizeof recv);
            side1_decode(w1);
            r = side2_decode(w2);
            {
                enum outcome o1 = classify(w1, sent, recv), o2 = classify(w2, sent, recv);
                joint[o1][o2]++;
                if (memcmp(w1, w2, sizeof w1) == 0) out_identical++;
                if (r == -1) { karn_flag++; if (o1 == PASSTHROUGH) karn_flag_and_rock_pass++; }
                if (r >= -1 && r <= 6) karn_ret_hist[r + 1]++;
                if (o2 == CORRECTED && r == e) side2_corrected_count_eq_e++;
                if (r > 3 && o2 == CORRECTED) karn_corrects_beyond_t++;
            }
        }
        printf("  \"%d\": {\"trials\": %d, \"output_words_identical\": %ld,\n", e, trials, out_identical);
        printf("   \"joint\": {");
        {
            int a, b, first = 1;
            for (a = 0; a < 3; a++) for (b = 0; b < 3; b++) if (joint[a][b]) {
                printf("%s\"side1_%s__side2_%s\": %ld", first ? "" : ", ", OUT[a], OUT[b], joint[a][b]); first = 0;
            }
        }
        printf("},\n   \"side2_return_hist\": {");
        { int first = 1; for (i = 0; i < 8; i++) if (karn_ret_hist[i]) { printf("%s\"%d\": %ld", first ? "" : ", ", i - 1, karn_ret_hist[i]); first = 0; } }
        printf("},\n   \"side2_flag_minus1\": %ld, \"side2_flag_and_side1_passthrough\": %ld,\n", karn_flag, karn_flag_and_rock_pass);
        printf("   \"side2_corrected_with_count_eq_e\": %ld, \"side2_corrected_beyond_t\": %ld}%s\n",
               side2_corrected_count_eq_e, karn_corrects_beyond_t, e < 6 ? "," : "");
    }
    printf(" },\n");

    /* R-DIV-2: erasures -- side b only has the interface. Two rows:
       4 erasures + 1 error (2*1 + 4 = 6 <= 2t) and 6 erasures + 0 errors. */
    if (!mode_self_rock) {
        int d[9], sent[15], recv[15], w[15], pos[15], val[15], r, ok46 = 0, ok60 = 0;
        g_state = seed ^ 0x3333ULL;
        for (t = 0; t < trials; t++) {
            int epos[6], ev[6];
            random_data(d); b_encode(d, sent); memcpy(recv, sent, sizeof sent);
            random_errors(5, pos, val);                 /* 5 distinct positions: 4 erased + 1 error */
            for (i = 0; i < 5; i++) recv[pos[i]] ^= val[i];
            for (i = 0; i < 4; i++) epos[i] = pos[i];
            memcpy(w, recv, sizeof recv);
            r = b_decode(w, epos, 4);
            if (r == 5 && classify(w, sent, recv) == CORRECTED) ok46++;
            random_data(d); b_encode(d, sent); memcpy(recv, sent, sizeof sent);
            random_errors(6, pos, val);
            for (i = 0; i < 6; i++) { recv[pos[i]] ^= val[i]; ev[i] = pos[i]; }
            memcpy(w, recv, sizeof recv);
            r = b_decode(w, ev, 6);
            if (r == 6 && classify(w, sent, recv) == CORRECTED) ok60++;
        }
        printf(" \"R-DIV-2\": {\"side2_4eras_1err_corrected\": %d, \"side2_6eras_corrected\": %d, \"trials\": %d,\n", ok46, ok60, trials);
        printf("  \"side1_erasure_interface\": \"NONE (rs.c header: 'does not handle erasures at present'; decode_rs() takes no erasure positions)\",\n");
        printf("  \"verdict\": \"CAPABILITY_ASYMMETRY (not a divergence on shared inputs)\"},\n");
    }
    printf(" \"bodies\": {\"a\": \"reed-solomon-rockliff-1991/upstream/rs.c\", \"b\": \"libfec-karn/upstream/tree/{init,encode,decode}_rs_int.c + int.h rs-common.h init_rs.h encode_rs.h decode_rs.h\"}\n}\n");
    free_rs_int(krs);
    return 0;
}
