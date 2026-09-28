"""Counter-examples against schema.check (R1-1/R1-2/R1-5), classify.D7_MACHINERY_IBD (R1-3) and the NPE adapter (R1-5).
Run from the repo root:  python3 ~/wk/rev1/out/cx_schema_defs.py"""
import copy, json, os, sys
sys.path.insert(0, os.path.expanduser("~/Prometheus-worktrees/rev1"))
from archaeon.attribution import schema as S, classify as K, fixtures as F, assay as A
from archaeon.attribution.schema import seg
from archaeon.attribution.fixtures import base, perf, cap, mat

def show(tag, rec, extra=""):
    print("%-58s check=%s %s" % (tag, S.check(rec) or "VALID", extra))

print("== R1-2: the leak when BOTH process and carrier were mis-logged (the historical situation) ==")
# CX-2a: harness copy logged the way the engine logged it (organism executed_write), material provenance = the harness log.
r = base("cx.leak", "C", [perf("organism_code", "P")], "executed_write", mat(seg(0, 32, entity="P", src_lo=0, via="harness_log")))
r["aggregation"] = [{"label": "SELF_COPY", "rule": "native_flag", "convention": False}]
show("CX-2a harness_log material + organism process + SELF_COPY", r, "class=" + K.production_class(r))
# CX-2b: operator splice logged as organism write (Z80A-D05 shape), two donors, via operator_log, labelled self_reproduction by the donor
r = base("cx.splice", "child", [perf("organism_code", "donor")], "executed_write",
         mat(seg(0, 58, entity="donor", src_lo=0, via="operator_log"), seg(58, 64, entity="recipient", src_lo=58, via="operator_log"), n=64))
r["aggregation"] = [{"label": "reproduction", "rule": "native_flag", "convention": True}]
show("CX-2b operator_log material, organism process, 'reproduction' (convention)", r, "class=" + K.production_class(r))
# CX-2c: A14 exempts conventions entirely: a harness copy labelled 'replicator' as a declared convention is VALID
h = copy.deepcopy(F.TH014_LEAK["HARNESS_COPY"]); h["aggregation"] = [{"label": "replicator", "rule": "native_flag", "convention": True}]
show("CX-2c harness copy + 'replicator' convention=True", h)

print("\n== R1-1: 'no universal parent field anywhere but aggregation' is a substring filter ==")
r = copy.deepcopy(F.TH014_LEAK["SELF_CONSTRUCTED"]); r["native"]["parent_id"] = "P"; r["material"]["segments"][0]["parent"] = "P"
r["carrier"]["template"] = "P"; r["production"]["ancestor"] = "P"
show("CX-1a parent_id in native, 'parent' in a segment, template/ancestor keys", r)
r = copy.deepcopy(F.TH014_LEAK["SELF_CONSTRUCTED"]); r["state"]["apparent_fidelity"] = 1.0
show("CX-1b legitimate key 'apparent_fidelity' in state (REJECTED)", r)

print("\n== R1-5: resolution 'counts' disables A4; any count arithmetic passes ==")
r = base("cx.counts", "C", [perf("organism_code", "P")], "executed_write",
         {"unit": "byte", "n_units": 32, "resolution": "counts", "segments": [seg(0, 32, entity="P"), seg(0, 32, entity="Q"), seg(0, 32, "new_computed")]})
show("CX-5c three full-length overlapping segments", r, "donors=%s new=%s" % (S.donors(r), S.new_share(r)))
row = [0, 1, 2, "PAIR_EXECUTION", 0.5, 0.5, "writer", 10, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]   # 64 copied-from-own of 10 bytes written: impossible
rec, = A.bee_records({"births_rows": [row], "codeprov": [{"own_region": 0, "self_copied": 0, "foreign": 0, "elsewhere": 0}], "rid": "x"})
show("CX-5d impossible BEE row (own 64 > written 10)", rec, "donors=%s" % S.donors(rec))

print("\n== R1-5: NPE adapter turns WHERE/code-provenance into MATERIAL ==")
# In T-003 every counted position D has, by construction, the DONOR's byte value (npe_b6_replay.py docstring: 'VALUE: equals the
# donor's byte by construction of D'). The adapter nevertheless assigns these positions to the victim when the victim's original
# code executed the write.
d = {"results": [{"name": "toy", "births": [{"child": 7, "n": 64, "D": 40, "who_where_what": {"victim_ctx|victim_half|original": 40}}]}]}
rec, = A.npe_records(d)
show("CX-5e 40 positions carrying the donor's bytes, written by victim code", rec,
     "donors=%s class=%s" % (S.donors(rec), K.production_class(rec)))

print("\n== R1-3: D7 counter-examples ==")
dc = {"donor_capabilities": {"P": True, "J": False, "N": True}}
def rec_(eid, performers, m, caps, native=dc, dep=None):
    return base(eid, "C", performers, "executed_write", m, capability=caps, native=dict(native), dependence=dep or [])
# CX-3a universal-copier cargo: host H copies inert junk J (donor NOT capable). Any string is 'host-assisted copyable'; no locus of J
# matters, so knockout-defined machinery is empty -> RELATIONAL -> D7 True. Same event as cargo_without_capacity, but D7 flips.
r = rec_("cx.junk", [perf("host_organism", "H")], mat(seg(0, 32, entity="J", src_lo=0)),
         [cap("host_assisted_copy", True, {"neighbour": "host:H-class"}, machinery=[])])
show("CX-3a host copies inert junk J (J not capable)", r, "D7=%s D5=%s machinery_ibd=%s" % (K.D7_MACHINERY_IBD(r), K.D5_CAPACITY(r), K.machinery_ibd(r)))
# CX-3b von Neumann architecture: description loci [16,32) copied from P, constructor loci [0,16) BUILT from the description (computed).
# Child builds grandchildren the same way; a variant in the description is inherited by a child that still reproduces.
VAR = dict(F.VARIANT_OK, intervention="variant: flip a description byte in the donor before copying")
r = rec_("cx.vn", [perf("organism_code", "P")], mat(seg(0, 16, "new_computed"), seg(16, 32, entity="P", src_lo=16)),
         [cap("exact_self_copy", True, machinery=[3, 4, 5, 6, 12])], dep=[VAR])
show("CX-3b von Neumann constructor+description", r, "D7=%s D6_HEREDITARY=%s D5=%s" % (K.D7_MACHINERY_IBD(r), K.D6_HEREDITARY(r), K.D5_CAPACITY(r)))
r2 = copy.deepcopy(r); r2["capability"][0]["machinery_loci"] = list(range(0, 32))   # knockout of description loci also kills copying
print("   same, machinery = constructor+description (16/32 descend): D7(theta .5)=%s D7(theta .6)=%s" % (K.D7_MACHINERY_IBD(r2, .5), K.D7_MACHINERY_IBD(r2, .6)))
# CX-3c machinery_loci and donor_capabilities are unvalidated author inputs: the fixture's own trace_material case flips to
# 'reproduction' by listing the one descended locus as machinery.
t = copy.deepcopy(F.ADVERSARIAL["trace_material_constructed_copier"]["record"]); t["capability"][0]["machinery_loci"] = [0]
show("CX-3c trace_material with machinery_loci=[0]", t, "D7=%s (intended False)" % K.D7_MACHINERY_IBD(t))
t = copy.deepcopy(F.ADVERSARIAL["cargo_without_capacity"]["record"]); t["native"]["donor_capabilities"] = {"P": True}
print("   donor capability is read from rec['native'] (no A7 check): any record can assert {'P': True}")

print("\n== R1-3: which cases decide D7's uniqueness ==")
DIRECTIVE = ["homopolymer_painter", "exact_copier_no_heritable_variation", "cargo_without_capacity", "machinery_without_founder_bytes",
             "scaffolded_copier", "host_executed_copier", "recombined_offspring", "changed_encoding_conserved_function"]
for sub, keys in (("directive's 8 cases", DIRECTIVE), ("all 12", list(F.ADVERSARIAL))):
    ok = [n for n, fn in K.DEFINITIONS.items() if all(fn(F.ADVERSARIAL[k]["record"]) == F.ADVERSARIAL[k]["intended"]["reproduction"] for k in keys)]
    print("   perfect on %-20s: %s" % (sub, ok))

print("\n== R1-4: the E-002 self-cross, recorded as what it was (a PTE GA crossover operator, 64 units, a == b) ==")
r = base("cx.e002", "child", [perf("recombination_operator", "search.py crossover")], "recombination_operator",
         mat(seg(0, 32, entity="A", src_lo=0, via="operator_log"), seg(32, 64, entity="A", src_lo=32, via="operator_log"), n=64))
show("CX-4a faithful E-002 self-cross", r, "class=%s D7=%s (regression.py expects SELF_CONSTRUCTED, reproduction True)"
     % (K.production_class(r), K.D7_MACHINERY_IBD(r)))
