/* HC-T01: faithful reconstruction of Toussaint 2003 thesis section 1.5.
 *
 * Model, from SRC-PHD-2003 sections 1.5.1-1.5.4, Tables 1.6 and 1.7, and the
 * recovered StringRule class documentation (ART-CODE-STRINGRULECLASS).
 *
 *   genotype  = egg cell Psi(0) plus an ordered list of operators.
 *               An operator is one string whose first char is the promoter
 *               (lhs) and whose remainder is the rhs. That layout is taken
 *               verbatim from the recovered class documentation:
 *               "the first char represents the lhs whereas the rest gives the
 *               rule's rhs".
 *   develop   = one pass applying every operator in order to the egg cell.
 *               T = 1 per Table 1.7. Verified against the thesis's own worked
 *               example in section 1.5.1.
 *   1st type  = symbol replacement / duplication / deletion, equal
 *               probabilities, Poisson(alpha * len) per sequence.
 *               "mutations*N() gives the Poisson mean of the total number of
 *               mutations made" -- recovered StringRule::mutate docs.
 *   2nd type  = five structural rewrites, equal probabilities,
 *               Poisson(beta) per genotype.
 *   order     = second type first, then first type. Table 1.6.
 *
 * Build:  gcc -O3 -march=native -o hct01 hct01.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define ALPHA_N      8
#define TARGET_LEN   25
#define PERIOD       5
#define MAXSEQ       256      /* max length of any single sequence          */
#define MAXOPS       32       /* max operators in a genotype                */
#define MAXPHENO     512      /* max developed phenotype length             */
#define POPMAX       128

/* ------------------------------------------------------------------ rng */
typedef struct { uint64_t s; } Rng;
static inline uint64_t rnext(Rng *r){
    r->s += 0x9E3779B97F4A7C15ULL;
    uint64_t z = r->s;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}
static inline double runif(Rng *r){ return (rnext(r) >> 11) * 0x1.0p-53; }
static inline uint32_t rint_(Rng *r, uint32_t n){ return (uint32_t)(rnext(r) % n); }
static uint32_t rpois(Rng *r, double lam){
    if (lam <= 0.0) return 0;
    if (lam < 30.0){
        double L = exp(-lam), p = 1.0; uint32_t k = 0;
        do { k++; p *= runif(r); } while (p > L);
        return k - 1;
    }
    /* not needed at our rates, but keep it correct */
    double c = 0.767 - 3.36/lam, b = M_PI/sqrt(3.0*lam), a = b*lam, k = log(c)-lam-log(b);
    for(;;){
        double u = runif(r); if (u<=0||u>=1) continue;
        double x = (a - log((1.0-u)/u))/b;
        int32_t n = (int32_t)floor(x + 0.5);
        if (n < 0) continue;
        double v = runif(r);
        double y = a - b*x, t = 1.0 + exp(y);
        double lhs = y + log(v/(t*t));
        double rhs = k + n*log(lam) - lgamma((double)n + 1.0);
        if (lhs <= rhs) return (uint32_t)n;
    }
}

/* ------------------------------------------------------------- genotype */
typedef struct {
    uint8_t egg[MAXSEQ];  int egglen;
    uint8_t op[MAXOPS][MAXSEQ]; int oplen[MAXOPS];  /* op[i][0] = promoter */
    int nops;
    int used[MAXOPS];     /* set during development: was the rule applied?  */
} Geno;

typedef struct { uint8_t s[MAXPHENO]; int n; } Str;

static void geno_init_direct(Geno *g, const uint8_t *s, int n){
    memset(g, 0, sizeof(*g));
    memcpy(g->egg, s, n); g->egglen = n; g->nops = 0;
}

/* apply one rule to a buffer: replace every occurrence of promoter by rhs */
static int rule_apply(const uint8_t *rule, int rlen, uint8_t *buf, int blen,
                      uint8_t *out, int cap){
    uint8_t prom = rule[0];
    const uint8_t *rhs = rule + 1; int rhslen = rlen - 1;
    int o = 0, hits = 0;
    for (int i = 0; i < blen; i++){
        if (buf[i] == prom){
            hits++;
            if (o + rhslen > cap) return -1;
            memcpy(out + o, rhs, rhslen); o += rhslen;
        } else {
            if (o + 1 > cap) return -1;
            out[o++] = buf[i];
        }
    }
    return hits ? o : (memcpy(out, buf, blen), blen);
}

/* develop: one pass over all operators in order, T = 1 */
static void develop(Geno *g, Str *out){
    uint8_t a[MAXPHENO], b[MAXPHENO];
    int n = g->egglen; if (n > MAXPHENO) n = MAXPHENO;
    memcpy(a, g->egg, n);
    for (int k = 0; k < MAXOPS; k++) g->used[k] = 0;
    for (int k = 0; k < g->nops; k++){
        uint8_t prom = g->op[k][0];
        int hit = 0;
        for (int i = 0; i < n; i++) if (a[i] == prom){ hit = 1; break; }
        if (!hit) continue;
        int m = rule_apply(g->op[k], g->oplen[k], a, n, b, MAXPHENO);
        if (m < 0) { break; }              /* growth cap: stop developing   */
        g->used[k] = 1;
        memcpy(a, b, m); n = m;
    }
    memcpy(out->s, a, n); out->n = n;
}

/* -------------------------------------------------------------- fitness */
/* negative fraction of the 25 target positions whose symbol differs */
static double fitness(const Str *p, const uint8_t *target){
    int bad = 0;
    for (int i = 0; i < TARGET_LEN; i++){
        uint8_t c = (i < p->n) ? p->s[i] : 0xFF;
        if (c != target[i]) bad++;
    }
    return -(double)bad / (double)TARGET_LEN;
}

/* --------------------------------------------------- first-type mutation */
static void mutate_seq(Rng *r, uint8_t *s, int *len, double alpha,
                       double alpha_indel, int start){
    /* start = 0 mutates the promoter too; start = 1 protects it */
    int n = *len; if (n <= start) return;
    double lam = alpha * (double)(n - start);
    uint32_t k = rpois(r, lam);
    for (uint32_t m = 0; m < k; m++){
        if (n <= start) break;
        int i = start + (int)rint_(r, (uint32_t)(n - start));
        uint32_t kind;
        if (alpha_indel <= 0.0) kind = 0;              /* replacement only  */
        else kind = rint_(r, 3);
        if (kind == 0){
            s[i] = (uint8_t)rint_(r, ALPHA_N);
        } else if (kind == 1){
            if (n + 1 >= MAXSEQ) continue;
            memmove(s + i + 1, s + i, (size_t)(n - i)); n++;
        } else {
            if (n - 1 <= start) continue;
            memmove(s + i, s + i + 1, (size_t)(n - i - 1)); n--;
        }
    }
    *len = n;
}

static void mutate_first_type(Rng *r, Geno *g, double alpha, double alpha_indel,
                              int promoters_mutate){
    mutate_seq(r, g->egg, &g->egglen, alpha, alpha_indel, 0);
    for (int k = 0; k < g->nops; k++)
        mutate_seq(r, g->op[k], &g->oplen[k], alpha, alpha_indel,
                   promoters_mutate ? 0 : 1);
}

/* -------------------------------------------------- second-type mutation */
/* sequences of the genotype: index 0 = egg cell, 1..nops = operator strings */
static uint8_t *seq_ptr(Geno *g, int idx, int **len){
    if (idx == 0){ *len = &g->egglen; return g->egg; }
    *len = &g->oplen[idx-1]; return g->op[idx-1];
}

static void op_delete(Geno *g, int k){
    for (int i = k; i < g->nops - 1; i++){
        memcpy(g->op[i], g->op[i+1], MAXSEQ);
        g->oplen[i] = g->oplen[i+1];
    }
    g->nops--;
}

static void mutate_second_type(Rng *r, Geno *g){
    int which = (int)rint_(r, 5);
    int nseq = 1 + g->nops;
    /* creation is possible with no operators; the others need one */
    if (g->nops == 0 && which != 4) which = 4;

    if (which == 4){
        /* generation of a new operator from a random subsequence */
        if (g->nops >= MAXOPS) return;
        int p = (int)rint_(r, (uint32_t)nseq);
        int *plen; uint8_t *ps = seq_ptr(g, p, &plen);
        int off = (p == 0) ? 0 : 1;                 /* skip promoter char   */
        int avail = *plen - off;
        int L = 2 + (int)rpois(r, 1.0);
        if (avail < L || L < 1) return;
        int i = off + (int)rint_(r, (uint32_t)(avail - L + 1));
        uint8_t prom = (uint8_t)rint_(r, ALPHA_N);
        /* "The new operator nu is inserted in the genome BEHIND the sequence p"
           -- Table 1.6. Position matters because operators are applied in
           order during development. Appending instead of inserting makes
           hierarchical encodings unreachable, because a rule extracted from
           the egg cell would be applied after the rules it feeds. */
        int nk = (p == 0) ? 0 : p;      /* egg -> slot 0; operator k -> k+1 */
        for (int q = g->nops; q > nk; q--){
            memcpy(g->op[q], g->op[q-1], MAXSEQ);
            g->oplen[q] = g->oplen[q-1];
        }
        if (p > 0 && nk <= p - 1) { /* ps may have moved; recompute below */ }
        g->op[nk][0] = prom;
        memcpy(g->op[nk] + 1, ps + i, (size_t)L);
        g->oplen[nk] = L + 1;
        g->nops++;
        /* the shift above may have moved the source sequence; re-resolve it */
        if (p > 0 && p - 1 >= nk) { ps = g->op[p]; plen = &g->oplen[p]; }
        /* inverse application of the new operator on p: replace matches */
        uint8_t tmp[MAXSEQ]; int o = 0;
        for (int q = 0; q < *plen; ){
            if (q >= off && q + L <= *plen && memcmp(ps + q, g->op[nk] + 1, (size_t)L) == 0){
                if (o >= MAXSEQ) break;
                tmp[o++] = prom; q += L;
            } else {
                if (o >= MAXSEQ) break;
                tmp[o++] = ps[q++];
            }
        }
        memcpy(ps, tmp, (size_t)o); *plen = o;
        return;
    }

    int k = (int)rint_(r, (uint32_t)g->nops);
    int p = (int)rint_(r, (uint32_t)nseq);
    int *plen; uint8_t *ps = seq_ptr(g, p, &plen);
    if (p == k + 1) return;                      /* do not rewrite itself   */

    if (which == 0){
        /* application of operator k on sequence p */
        uint8_t out[MAXSEQ];
        int m = rule_apply(g->op[k], g->oplen[k], ps, *plen, out, MAXSEQ);
        if (m > 0){ memcpy(ps, out, (size_t)m); *plen = m; }
    } else if (which == 1){
        /* inverse application: all matches of rhs in p become the promoter */
        int L = g->oplen[k] - 1; if (L < 1) return;
        const uint8_t *rhs = g->op[k] + 1;
        uint8_t tmp[MAXSEQ]; int o = 0, off = (p == 0) ? 0 : 1;
        for (int q = 0; q < *plen; ){
            if (q >= off && q + L <= *plen && memcmp(ps + q, rhs, (size_t)L) == 0){
                if (o >= MAXSEQ) break;
                tmp[o++] = g->op[k][0]; q += L;
            } else {
                if (o >= MAXSEQ) break;
                tmp[o++] = ps[q++];
            }
        }
        memcpy(ps, tmp, (size_t)o); *plen = o;
    } else if (which == 2){
        /* deletion of operator k, only if never applied during ontogenesis */
        Str ph; develop(g, &ph);
        if (!g->used[k]) op_delete(g, k);
    } else {
        /* apply operator k to every sequence, then delete it */
        for (int q = 0; q < 1 + g->nops; q++){
            if (q == k + 1) continue;
            int *ql; uint8_t *qs = seq_ptr(g, q, &ql);
            uint8_t out[MAXSEQ];
            int m = rule_apply(g->op[k], g->oplen[k], qs, *ql, out, MAXSEQ);
            if (m > 0){ memcpy(qs, out, (size_t)m); *ql = m; }
        }
        op_delete(g, k);
    }
}

static void mutate(Rng *r, Geno *g, double alpha, double alpha_indel,
                   double beta, int promoters_mutate){
    uint32_t nb = rpois(r, beta);
    for (uint32_t i = 0; i < nb; i++) mutate_second_type(r, g);
    mutate_first_type(r, g, alpha, alpha_indel, promoters_mutate);
}

/* ------------------------------------------------------------- detector */
typedef struct {
    double neutral_degree, modular_degree, mi_total, mi_aligned, mi_unaligned;
    double avgfit, genome_length, operator_count, operator_usage;
} Det;

/* joint histogram over 9 bins (8 symbols + absent) */
#define BINS 9
static void detect_one(Rng *r, const Geno *parent, const Str *pphen,
                       const uint8_t *target, int S,
                       double alpha, double alpha_indel, double beta,
                       int promoters_mutate, Det *acc){
    static int cnt1[TARGET_LEN][BINS];
    static int cnt2[TARGET_LEN][TARGET_LEN][BINS][BINS];
    static int varcnt[TARGET_LEN];
    static int paircnt[TARGET_LEN][PERIOD];
    memset(cnt1, 0, sizeof(cnt1));
    memset(cnt2, 0, sizeof(cnt2));
    memset(varcnt, 0, sizeof(varcnt));
    memset(paircnt, 0, sizeof(paircnt));

    int neutral = 0; double fsum = 0.0;
    uint8_t pref[TARGET_LEN];
    for (int i = 0; i < TARGET_LEN; i++)
        pref[i] = (i < pphen->n) ? pphen->s[i] : 0xFF;

    for (int s = 0; s < S; s++){
        Geno c = *parent;
        mutate(r, &c, alpha, alpha_indel, beta, promoters_mutate);
        Str ph; develop(&c, &ph);
        fsum += fitness(&ph, target);

        int same = (ph.n == pphen->n);
        if (same) for (int i = 0; i < ph.n; i++) if (ph.s[i] != pphen->s[i]){ same = 0; break; }
        if (same) neutral++;

        uint8_t b[TARGET_LEN]; int varmask[TARGET_LEN];
        for (int i = 0; i < TARGET_LEN; i++){
            uint8_t c2 = (i < ph.n) ? ph.s[i] : 0xFF;
            b[i] = (c2 == 0xFF) ? (BINS-1) : c2;
            varmask[i] = (c2 != pref[i]);
            cnt1[i][b[i]]++;
            if (varmask[i]) varcnt[i]++;
        }
        for (int i = 0; i < TARGET_LEN; i++)
            for (int j = i+1; j < TARGET_LEN; j++)
                cnt2[i][j][b[i]][b[j]]++;
        for (int i = 0; i < TARGET_LEN; i++){
            if (!varmask[i]) continue;
            for (int k = 1; k <= 4; k++){
                int j = (i + k*PERIOD) % TARGET_LEN;
                if (varmask[j]) paircnt[i][k]++;
            }
        }
    }

    /* modular degree: sum over k of P(var at i+5k | var at i), mean over i */
    double md = 0.0;
    for (int i = 0; i < TARGET_LEN; i++){
        if (varcnt[i] == 0) continue;              /* contributes 0         */
        double s = 0.0;
        for (int k = 1; k <= 4; k++) s += (double)paircnt[i][k] / (double)varcnt[i];
        md += s;
    }
    md /= (double)TARGET_LEN;

    /* normalised pairwise mutual information */
    double H[TARGET_LEN];
    for (int i = 0; i < TARGET_LEN; i++){
        double h = 0.0;
        for (int a = 0; a < BINS; a++){
            if (!cnt1[i][a]) continue;
            double p = (double)cnt1[i][a] / (double)S;
            h -= p * log(p);
        }
        H[i] = h;
    }
    double mit = 0.0, mia = 0.0, miu = 0.0; long na = 0, nu = 0, nt = 0;
    for (int i = 0; i < TARGET_LEN; i++)
        for (int j = i+1; j < TARGET_LEN; j++){
            double mi = 0.0;
            for (int a = 0; a < BINS; a++){
                if (!cnt1[i][a]) continue;
                for (int b2 = 0; b2 < BINS; b2++){
                    int c12 = cnt2[i][j][a][b2];
                    if (!c12) continue;
                    double pij = (double)c12 / (double)S;
                    double pi = (double)cnt1[i][a] / (double)S;
                    double pj = (double)cnt1[j][b2] / (double)S;
                    mi += pij * log(pij / (pi * pj));
                }
            }
            double den = H[i] + H[j];
            double v = (den > 1e-12) ? (2.0 * mi / den) : 0.0;
            mit += v; nt++;
            if (((j - i) % PERIOD) == 0){ mia += v; na++; } else { miu += v; nu++; }
        }

    acc->neutral_degree += (double)neutral / (double)S;
    acc->modular_degree += md;
    acc->mi_total       += nt ? mit/(double)nt : 0.0;
    acc->mi_aligned     += na ? mia/(double)na : 0.0;
    acc->mi_unaligned   += nu ? miu/(double)nu : 0.0;
    acc->avgfit         += fsum / (double)S;
}

static void detect_pop(Rng *r, const Geno *pop, const Str *phen, int n,
                       const uint8_t *target, int S,
                       double alpha, double alpha_indel, double beta,
                       int promoters_mutate, Det *out){
    memset(out, 0, sizeof(*out));
    for (int i = 0; i < n; i++){
        detect_one(r, &pop[i], &phen[i], target, S, alpha, alpha_indel, beta,
                   promoters_mutate, out);
        Geno tmp = pop[i]; Str ph; develop(&tmp, &ph);
        int glen = tmp.egglen; int usage = 0;
        for (int k = 0; k < tmp.nops; k++){ glen += tmp.oplen[k]; usage += tmp.used[k]; }
        out->genome_length  += glen;
        out->operator_count += tmp.nops;
        out->operator_usage += usage;
    }
    out->neutral_degree/=n; out->modular_degree/=n; out->mi_total/=n;
    out->mi_aligned/=n; out->mi_unaligned/=n; out->avgfit/=n;
    out->genome_length/=n; out->operator_count/=n; out->operator_usage/=n;
}

/* --------------------------------------------------------------- driver */
typedef struct {
    int lambda, mu, gens, S;
    double alpha, alpha_indel, beta;
    int promoters_mutate;
    int exp1;                      /* 1 = correct-only selection (Exp 1)    */
    uint64_t seed_evo, seed_det;
    int probe;                     /* run the frozen cross-operator probe   */
    double beta_on, beta_off;
    const int *cks; int ncks;
    const char *tag;
} Cfg;

static uint8_t TARGET[TARGET_LEN];

static int cmp_by_fit(const void *a, const void *b){
    double x = ((const double*)a)[0], y = ((const double*)b)[0];
    return (x < y) ? 1 : (x > y) ? -1 : 0;   /* descending fitness */
}

static void run(Cfg c, FILE *out){
    Rng re = { c.seed_evo * 0x2545F4914F6CDD1DULL + 0x9E3779B9ULL };
    Rng rd = { c.seed_det * 0x2545F4914F6CDD1DULL + 0x1234567ULL };
    static Geno pop[POPMAX], par[POPMAX];
    static Str  phen[POPMAX];
    static double key[POPMAX][2];

    uint8_t egg1 = 0;                       /* symbol 'a' */
    for (int i = 0; i < c.lambda; i++){
        if (c.exp1) geno_init_direct(&pop[i], TARGET, TARGET_LEN);
        else        geno_init_direct(&pop[i], &egg1, 1);
    }
    int ck = 0;
    for (int g = 0; g <= c.gens; g++){
        for (int i = 0; i < c.lambda; i++) develop(&pop[i], &phen[i]);

        if (c.probe && ck < c.ncks && g == c.cks[ck]){
            Det don, doff;
            Rng r1 = rd; r1.s ^= (uint64_t)g * 0x100000001B3ULL;
            Rng r2 = rd; r2.s ^= (uint64_t)g * 0x100000001B3ULL + 7777ULL;
            detect_pop(&r1, pop, phen, c.lambda, TARGET, c.S,
                       c.alpha, c.alpha_indel, c.beta_on, c.promoters_mutate, &don);
            detect_pop(&r2, pop, phen, c.lambda, TARGET, c.S,
                       c.alpha, c.alpha_indel, c.beta_off, c.promoters_mutate, &doff);
            double bf = -1e9, mf = 0.0;
            int minlen = 1<<30, argmin = 0;
            for (int i = 0; i < c.lambda; i++){
                double f = fitness(&phen[i], TARGET);
                if (f > bf) bf = f; mf += f;
                Geno t = pop[i]; Str tp; develop(&t, &tp);
                int gl = t.egglen; for (int k=0;k<t.nops;k++) gl += t.oplen[k];
                /* only count genotypes that still encode the correct phenotype */
                if (fitness(&tp, TARGET) == 0.0 && gl < minlen){ minlen = gl; argmin = i; }
            }
            mf /= c.lambda;
            if (minlen == (1<<30)) minlen = -1;
            char gbuf[1024]; int gp = 0;
            {
                Geno t = pop[argmin];
                gp += snprintf(gbuf+gp, sizeof(gbuf)-gp, "<");
                for (int i=0;i<t.egglen && gp<900;i++) gbuf[gp++] = 'a'+t.egg[i];
                gp += snprintf(gbuf+gp, sizeof(gbuf)-gp, ">");
                for (int k=0;k<t.nops && gp<900;k++){
                    gp += snprintf(gbuf+gp, sizeof(gbuf)-gp, " %c:", 'a'+t.op[k][0]);
                    for (int i=1;i<t.oplen[k] && gp<900;i++) gbuf[gp++] = 'a'+t.op[k][i];
                }
                gbuf[gp] = 0;
            }
            fprintf(out,
              "%s,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,"
              "%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%d,%s\n",
              c.tag, g, bf, mf,
              don.modular_degree, doff.modular_degree,
              don.neutral_degree, doff.neutral_degree,
              don.mi_total, doff.mi_total,
              don.mi_aligned, doff.mi_aligned,
              don.mi_unaligned, doff.mi_unaligned,
              don.avgfit, doff.avgfit,
              don.genome_length, don.operator_count, don.operator_usage,
              don.mi_aligned - don.mi_unaligned, doff.mi_aligned - doff.mi_unaligned,
              minlen, gbuf);
            fflush(out);
            ck++;
        }
        if (g == c.gens) break;

        /* selection */
        int nsel = 0;
        if (c.exp1){
            int idx[POPMAX], m = 0;
            for (int i = 0; i < c.lambda; i++){
                if (fitness(&phen[i], TARGET) == 0.0) idx[m++] = i;
            }
            if (m == 0){ for (int i = 0; i < c.lambda; i++) idx[m++] = i; }
            for (int i = 0; i < c.mu; i++) par[nsel++] = pop[idx[rint_(&re,(uint32_t)m)]];
        } else {
            for (int i = 0; i < c.lambda; i++){
                key[i][0] = fitness(&phen[i], TARGET);
                key[i][1] = (double)i;
            }
            qsort(key, (size_t)c.lambda, sizeof(key[0]), cmp_by_fit);
            for (int i = 0; i < c.mu; i++) par[nsel++] = pop[(int)key[i][1]];
        }
        /* reproduction: clone the mu parents uniformly to lambda offspring */
        for (int i = 0; i < c.lambda; i++){
            Geno child = par[rint_(&re, (uint32_t)nsel)];
            mutate(&re, &child, c.alpha, c.alpha_indel, c.beta, c.promoters_mutate);
            pop[i] = child;
        }
    }
}

/* --------------------------------------------------------------- tests */
static int selftest(void){
    int fail = 0;
    /* thesis 1.5.1 worked example: Psi(0)=<a>, Pi = <a:ab>,<a:cd>,<b:adc>
       develops to <cdadc> after one pass, and <cdcdadcdc> after two. */
    Geno g; memset(&g, 0, sizeof(g));
    g.egg[0] = 0; g.egglen = 1;                    /* a */
    g.op[0][0]=0; g.op[0][1]=0; g.op[0][2]=1; g.oplen[0]=3;   /* a: a b */
    g.op[1][0]=0; g.op[1][1]=2; g.op[1][2]=3; g.oplen[1]=3;   /* a: c d */
    g.op[2][0]=1; g.op[2][1]=0; g.op[2][2]=3; g.op[2][3]=2; g.oplen[2]=4; /* b: a d c */
    g.nops = 3;
    Str p; develop(&g, &p);
    const char *want = "cdadc";
    int ok = (p.n == 5);
    if (ok) for (int i = 0; i < 5; i++) if (p.s[i] != (uint8_t)(want[i]-'a')) ok = 0;
    printf("%-4s worked example Psi(1) = cdadc          got=", ok?"PASS":"FAIL");
    for (int i=0;i<p.n;i++) putchar('a'+p.s[i]); putchar('\n');
    if (!ok) fail++;

    /* two passes should give cdcdadcdc */
    Geno g2 = g; memcpy(g2.egg, p.s, (size_t)p.n); g2.egglen = p.n;
    Str p2; develop(&g2, &p2);
    const char *want2 = "cdcdadcdc";
    int ok2 = (p2.n == 9);
    if (ok2) for (int i = 0; i < 9; i++) if (p2.s[i] != (uint8_t)(want2[i]-'a')) ok2 = 0;
    printf("%-4s worked example Psi(2) = cdcdadcdc      got=", ok2?"PASS":"FAIL");
    for (int i=0;i<p2.n;i++) putchar('a'+p2.s[i]); putchar('\n');
    if (!ok2) fail++;

    /* direct encoding of the target develops to the target, fitness 0 */
    Geno g3; geno_init_direct(&g3, TARGET, TARGET_LEN);
    Str p3; develop(&g3, &p3);
    int ok3 = (p3.n == TARGET_LEN) && (fitness(&p3, TARGET) == 0.0);
    printf("%-4s direct encoding of target -> fitness 0\n", ok3?"PASS":"FAIL");
    if (!ok3) fail++;

    /* the thesis's minimal length-11 representation <ffff> + f:abcde */
    Geno g4; memset(&g4, 0, sizeof(g4));
    for (int i=0;i<5;i++) g4.egg[i] = 5;            /* fffff */
    g4.egglen = 5;
    g4.op[0][0] = 5;                                 /* promoter f */
    for (int i=0;i<5;i++) g4.op[0][1+i] = (uint8_t)i;/* abcde */
    g4.oplen[0] = 6; g4.nops = 1;
    Str p4; develop(&g4, &p4);
    int ok4 = (p4.n == TARGET_LEN) && (fitness(&p4, TARGET) == 0.0);
    int glen4 = g4.egglen + g4.oplen[0];
    printf("%-4s compact encoding fffff + f:abcde -> target, genome length %d (thesis says 11)\n",
           (ok4 && glen4==11)?"PASS":"FAIL", glen4);
    if (!(ok4 && glen4==11)) fail++;

    /* beta = 0 can never create an operator */
    Rng r = { 12345 };
    Geno g5; geno_init_direct(&g5, TARGET, TARGET_LEN);
    int ops = 0;
    for (int i = 0; i < 20000; i++){
        Geno c = g5; mutate(&r, &c, 0.03, 0.0, 0.0, 1);
        ops += c.nops;
    }
    printf("%-4s beta=0 creates no operators in 20000 draws (total ops %d)\n",
           ops==0?"PASS":"FAIL", ops);
    if (ops) fail++;

    /* beta > 0 does create operators */
    ops = 0;
    for (int i = 0; i < 20000; i++){
        Geno c = g5; mutate(&r, &c, 0.03, 0.0, 0.1, 1);
        ops += c.nops;
    }
    printf("%-4s beta=0.1 creates operators in 20000 draws (total ops %d)\n",
           ops>0?"PASS":"FAIL", ops);
    if (!ops) fail++;

    /* determinism: same seed, same trajectory */
    Rng ra = { 999 }, rb = { 999 };
    Geno ca = g5, cb = g5;
    for (int i = 0; i < 500; i++){
        mutate(&ra, &ca, 0.03, 0.0, 0.1, 1);
        mutate(&rb, &cb, 0.03, 0.0, 0.1, 1);
    }
    int okd = (ca.egglen == cb.egglen) && (ca.nops == cb.nops) &&
              (memcmp(ca.egg, cb.egg, (size_t)ca.egglen) == 0);
    printf("%-4s deterministic replay from identical seed\n", okd?"PASS":"FAIL");
    if (!okd) fail++;

    printf("selftest: %d failures\n", fail);
    return fail;
}

int main(int argc, char **argv){
    for (int i = 0; i < TARGET_LEN; i++) TARGET[i] = (uint8_t)(i % PERIOD);

    if (argc > 1 && strcmp(argv[1], "selftest") == 0) return selftest();

    /* args: run tag exp1 gens lambda mu alpha alpha_indel beta S seed_evo
             seed_det promoters_mutate probe beta_on beta_off ck1,ck2,... */
    if (argc < 17){ fprintf(stderr, "bad args\n"); return 2; }
    Cfg c; int a = 2;
    c.tag = argv[a++];
    c.exp1 = atoi(argv[a++]);
    c.gens = atoi(argv[a++]);
    c.lambda = atoi(argv[a++]);
    c.mu = atoi(argv[a++]);
    c.alpha = atof(argv[a++]);
    c.alpha_indel = atof(argv[a++]);
    c.beta = atof(argv[a++]);
    c.S = atoi(argv[a++]);
    c.seed_evo = strtoull(argv[a++], NULL, 10);
    c.seed_det = strtoull(argv[a++], NULL, 10);
    c.promoters_mutate = atoi(argv[a++]);
    c.probe = atoi(argv[a++]);
    c.beta_on = atof(argv[a++]);
    c.beta_off = atof(argv[a++]);
    static int cks[512]; int n = 0;
    if (a < argc){
        char *s = argv[a]; char *tok = strtok(s, ",");
        while (tok && n < 512){ cks[n++] = atoi(tok); tok = strtok(NULL, ","); }
    }
    c.cks = cks; c.ncks = n;
    run(c, stdout);
    return 0;
}
