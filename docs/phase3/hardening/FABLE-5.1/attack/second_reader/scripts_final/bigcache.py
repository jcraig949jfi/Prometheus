import sys, math, time
sys.dont_write_bytecode = True
import comp as C
t0 = time.time()
for cls, n, seed in ((C.CacheRot, 24000, 901), (C.Elim, 24000, 902)):
    sc = C.run(cls, n, C.h_main, seed)
    m, se = C.stat(sc)
    print("%s | ninth pair | n %d mean %.4f se %.4f | H16 %.4f | z vs bound %.2f | %.0f s" % (cls.name, n, m, se, C.H16, (m - C.H16) / se, time.time() - t0))
    sys.stdout.flush()
