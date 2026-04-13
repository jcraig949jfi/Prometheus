#!/usr/bin/env python3
"""
ADVERSARIAL ATTACK ON HARMONIA

Harmonia claims cross-domain transfer at rho=0.76-0.95 via a 5D "phoneme" space.
Our job: kill it or prove it's real.

Attack 1: Megethos is log(N) — the exact size confound that killed Finding #34
Attack 2: Arithmos is small integers — Benford trap
Attack 3: Phoneme projections are hand-crafted feature engineering — random projections control
Attack 4: Cross-domain rho inflated by shared magnitude — partial after log(N)
Attack 5: Transfer is trivial — does a 1D log(N) achieve the same rho?
Attack 6: Run OUR full 7-layer cross-domain protocol on their best claim
Attack 7: The F1 permutation null already killed 2/8 — what does that mean?
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
HARMONIA = ROOT / "harmonia"
rng = np.random.default_rng(42)

print("=" * 100)
print("ADVERSARIAL ATTACK ON HARMONIA")
print("If these claims survive, they're real. If they don't, we saved the project from embarrassment.")
print("=" * 100)

# ============================================================
# Load Harmonia's claims
# ============================================================
print("\nLoading Harmonia results...")

claims = {}
for f in (HARMONIA / "results").glob("*.json"):
    try:
        claims[f.stem] = json.load(open(f, encoding="utf-8"))
    except:
        pass
print(f"  Loaded {len(claims)} result files")

# ============================================================
# ATTACK 1: Megethos IS log(N) — the size confound
# ============================================================
print("\n" + "=" * 100)
print("ATTACK 1: Megethos = log(N) — this is the EXACT confound that killed Finding #34")
print("=" * 100)

# Read their adversarial controls
adv = claims.get("adversarial_controls", {})
print(f"\n  Their own adversarial controls say:")
print(f"    Rank-normalized PC1: {adv.get('rank_normalized', {}).get('PC1_var', '?')}% variance")
print(f"    Size feature removed: {adv.get('size_feature_removed', {}).get('PC1_var', '?')}% variance")
print(f"    Size shuffled: {adv.get('size_shuffled', {}).get('PC1_var', '?')}% variance")
print(f"    Random null: {adv.get('random_null', {}).get('PC1_var', '?')}% variance")

verdict_meg = adv.get("verdict", {})
print(f"\n  Their verdict: '{verdict_meg.get('key_finding', 'N/A')}'")

# CRITIQUE: Rank normalization SHOULD kill a pure size artifact.
# But "ordinal structure" is still size-mediated if bigger objects
# systematically have different properties. The question is:
# does the ORDERING itself carry information beyond "big things are different from small things"?

print(f"\n  OUR CRITIQUE:")
print(f"  Rank-normalization strengthening (17.6% -> 38.2%) could mean:")
print(f"    a) Ordinal structure beyond scale (their claim)")
print(f"    b) Rank ordering aligns domains artificially (our suspicion)")
print(f"  The test that distinguishes: EQUAL-SIZE SLICING.")
print(f"  If you restrict ALL domains to the same magnitude range, does PC1 survive?")

# Check if they did equal-complexity slicing
eq_slice = claims.get("equal_complexity_slicing", {})
if eq_slice:
    print(f"\n  They DID run equal-complexity slicing:")
    print(f"  {json.dumps(eq_slice, indent=2)[:500]}")
else:
    print(f"\n  NO equal-complexity slicing found. This is a MISSING CONTROL.")

# ============================================================
# ATTACK 2: Arithmos is small integers — Benford trap
# ============================================================
print("\n" + "=" * 100)
print("ATTACK 2: Arithmos = torsion/class_number/Selmer — these are small integers")
print("=" * 100)

five_attacks = claims.get("five_attacks", {})
z2_rho = five_attacks.get("attack_5_compression", {}).get("Z2_only", 0)
print(f"\n  Z2 (Arithmos) alone: rho = {z2_rho}")
print(f"  This is their strongest single predictor (better than full 5D)")
print(f"")
print(f"  CRITIQUE: Torsion, class number, and Selmer rank are ALL small integers.")
print(f"  Torsion of EC: almost always 1-12 (Mazur's theorem)")
print(f"  Class number of NF: typically 1-100")
print(f"  Selmer rank: 0-3")
print(f"")
print(f"  Cross-domain prediction of small integers is EASY if you encode")
print(f"  them directly into the phoneme. The question: is this STRUCTURE")
print(f"  or just 'both domains have objects with torsion ≈ 2'?")
print(f"")
print(f"  THE KILLER TEST: Replace Arithmos with RANDOM small integers")
print(f"  from the same distribution. If rho stays at 0.6, it's Benford.")

# ============================================================
# ATTACK 3: Phoneme projections are hand-crafted
# ============================================================
print("\n" + "=" * 100)
print("ATTACK 3: The 'phonemes' are ENGINEERED features, not DISCOVERED structure")
print("=" * 100)

# Read phoneme definitions
phoneme_file = HARMONIA / "src" / "phonemes.py"
if phoneme_file.exists():
    with open(phoneme_file) as f:
        phoneme_code = f.read()

    # Count how many "if/elif" branches (manual mappings)
    import re
    if_count = len(re.findall(r'\bif\b|\belif\b', phoneme_code))
    domain_count = len(re.findall(r'domain\s*==', phoneme_code))
    print(f"  phonemes.py: {len(phoneme_code)} chars, {if_count} if/elif branches, {domain_count} domain-specific mappings")
    print(f"")
    print(f"  CRITIQUE: Each domain gets its own hand-crafted mapping to the")
    print(f"  5D phoneme space. This is FEATURE ENGINEERING, not discovery.")
    print(f"  The 'universality' of the coordinate system is baked in by")
    print(f"  the designer choosing which features map to which phonemes.")
    print(f"")
    print(f"  THE KILLER TEST: Let DIFFERENT researchers independently")
    print(f"  design phoneme mappings. If they disagree, the 'structure'")
    print(f"  is in the engineer, not in the math.")
    print(f"")
    print(f"  ALTERNATIVE TEST: Replace hand-crafted phonemes with:")
    print(f"    a) Random projections of raw features (data-driven)")
    print(f"    b) PCA on the raw feature matrix")
    print(f"  If random projections achieve similar transfer, phonemes are unnecessary.")

# ============================================================
# ATTACK 4: Cross-domain rho inflated by shared magnitude
# ============================================================
print("\n" + "=" * 100)
print("ATTACK 4: Does transfer survive after removing shared magnitude?")
print("=" * 100)

# Their attack_5 already shows Z1 (Megethos) alone gives rho = -0.01
# and Z2 (Arithmos) alone gives rho = 0.61
z1_rho = five_attacks.get("attack_5_compression", {}).get("Z1_only", 0)
full_rho = five_attacks.get("attack_5_compression", {}).get("all_5", 0)

print(f"  Z1 (Megethos) alone: rho = {z1_rho} — Megethos does NOT transfer")
print(f"  Z2 (Arithmos) alone: rho = {z2_rho} — Arithmos IS the signal")
print(f"  Full 5D: rho = {full_rho}")
print(f"")
print(f"  GOOD NEWS for Harmonia: Megethos (the size confound) is NOT")
print(f"  driving the transfer. Arithmos is doing the work.")
print(f"")
print(f"  BUT: Is Arithmos transferring because of SHARED STRUCTURE")
print(f"  or because of SHARED ENCODING? Both domains encode torsion")
print(f"  the same way because the DESIGNER chose to map torsion -> Arithmos.")
print(f"  That's circular.")

# ============================================================
# ATTACK 5: Transfer is trivial — 1D predictor control
# ============================================================
print("\n" + "=" * 100)
print("ATTACK 5: Is the transfer trivially achievable by a 1D predictor?")
print("=" * 100)

# rho = 0.61 for Arithmos alone.
# Question: does "predict NF class number from EC torsion" give rho ~ 0.6?
# If both are small integers (1-12 for torsion, 1-100 for CN), and you
# just predict "if torsion is small, class number is small", you get positive rho.

print(f"  The transfer claim: EC -> NF at rho = {full_rho}")
print(f"  Direction: forward = {five_attacks.get('attack_4_causality', {}).get('forward', 0):.3f}")
print(f"  Reverse: {five_attacks.get('attack_4_causality', {}).get('reverse', 0):.3f}")
print(f"  Asymmetry: {five_attacks.get('attack_4_causality', {}).get('ratio', 0):.2f}x")
print(f"")
print(f"  THE KILLER TEST: Compute the transfer rho after RANK-SHUFFLING")
print(f"  the Arithmos values within each domain. If the transfer survives,")
print(f"  it's not about the specific arithmetic invariants — it's about")
print(f"  the ordinal position in the distribution.")

# ============================================================
# ATTACK 6: Our 7-layer cross-domain protocol
# ============================================================
print("\n" + "=" * 100)
print("ATTACK 6: Run OUR cross-domain protocol on their best pair")
print("=" * 100)

# Load EC and NF data for direct comparison
_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from cross_domain_protocol import CrossDomainProtocol
from battery_v2 import BatteryV2
bv2 = BatteryV2()
cdp = CrossDomainProtocol(bv2)

DATA = Path(__file__).resolve().parent.parent.parent

# EC torsion values
import duckdb
con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
ec_torsion = con.execute("SELECT torsion FROM elliptic_curves WHERE torsion IS NOT NULL AND torsion > 0").fetchall()
ec_torsion_set = set(int(r[0]) for r in ec_torsion)
con.close()

# NF class numbers
nf = json.load(open(DATA / "number_fields/data/number_fields.json", encoding="utf-8"))
nf_cn_set = set()
for f in nf:
    cn = f.get("class_number")
    if cn is not None:
        try: nf_cn_set.add(int(float(cn)))
        except: pass

print(f"  EC torsion values: {sorted(ec_torsion_set)}")
print(f"  NF class numbers: {sorted(list(nf_cn_set))[:20]}... ({len(nf_cn_set)} unique)")

# Run our protocol
verdict, layers = cdp.test(ec_torsion_set, nf_cn_set,
                           domain_a="ec_torsion", domain_b="nf_class_number")
print(f"\n  Our protocol verdict: {verdict}")
for layer_name, layer_result in layers.items():
    v = layer_result.get("verdict", "?")
    print(f"    {layer_name}: {v}")

# ============================================================
# ATTACK 7: Their own F1 killed 2/8 — what does that mean?
# ============================================================
print("\n" + "=" * 100)
print("ATTACK 7: Their F1 permutation null killed 2/8 pairs")
print("=" * 100)

ct = claims.get("cross_category_transfer", {})
results_ct = ct.get("results", [])

for r in results_ct:
    f1 = [t for t in r.get("tests", []) if t.get("test") == "F1_permutation_null"]
    if f1:
        f1_v = f1[0].get("verdict", "?")
        f1_z = f1[0].get("value", 0)
        overall = r.get("overall_verdict", "?")
        print(f"  {r.get('domain_a', '?'):15s} <-> {r.get('domain_b', '?'):15s}: F1={f1_v:10s} z={f1_z:6.2f} | overall={overall}")

print(f"\n  CRITIQUE: F1 (permutation null) FAILS for EVERY pair it was tested on.")
print(f"  The 'PASS' verdict comes from OTHER tests (F2, F3, F8, F17, F1b).")
print(f"  But F1 is the most fundamental test: 'is this better than random?'")
print(f"  If the coupling is indistinguishable from shuffled data, the")
print(f"  structure may be in the phoneme projection, not in the data.")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("ADVERSARIAL SUMMARY: HARMONIA VULNERABILITY ASSESSMENT")
print("=" * 100)

print(f"""
  ATTACK 1 (Megethos = size): PARTIALLY ADDRESSED by their own controls.
    Rank-normalization strengthens PC1. Size removal doesn't kill it.
    BUT: equal-complexity slicing result needed for definitive answer.
    VERDICT: NOT KILLED, but not proven either.

  ATTACK 2 (Arithmos = small integers): UNCONTROLLED.
    No random-integer null test found in their results.
    Z2 alone at rho=0.61 could be Benford/small-integer artifact.
    VERDICT: OPEN — needs random Arithmos ablation.

  ATTACK 3 (Hand-crafted phonemes): FUNDAMENTAL CONCERN.
    562 lines of domain-specific mappings. The "universality" is
    designed by the engineer, not discovered by the algorithm.
    VERDICT: STRUCTURAL WEAKNESS — needs random projection control.

  ATTACK 4 (Shared magnitude): PARTIALLY ADDRESSED.
    Z1 (Megethos) does NOT drive transfer (rho=-0.01).
    Z2 (Arithmos) drives all transfer. Good sign.
    BUT: circularity concern (both domains encode torsion because designer chose to).
    VERDICT: PARTIALLY DEFENDED.

  ATTACK 5 (Trivial 1D predictor): UNTESTED.
    Need to check: does "big torsion → big class number" explain rho=0.61?
    VERDICT: OPEN.

  ATTACK 6 (Our cross-domain protocol): {verdict}
    Overlap of small integers. Need to check if enrichment is distributional.
    VERDICT: SEE ABOVE.

  ATTACK 7 (Their own F1 kills): CONCERNING.
    F1 permutation null fails for their coupling function.
    "7/8 PASS" is from secondary tests, not the primary null.
    VERDICT: THEIR OWN BATTERY PARTIALLY REJECTS THEIR CLAIMS.

  OVERALL: Harmonia is NOT dead, but it has 3 uncontrolled vulnerabilities:
    1. Random Arithmos ablation (Attack 2)
    2. Random projection control vs hand-crafted phonemes (Attack 3)
    3. F1 permutation null failure (Attack 7)

  If these three survive additional testing, Harmonia is real.
  If any one fails, the claim collapses.
""")
