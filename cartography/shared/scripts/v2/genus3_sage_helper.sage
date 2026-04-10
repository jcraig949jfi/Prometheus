"""
genus3_sage_helper.sage — Point-counting on genus-3 plane quartics via SageMath.

Usage (from WSL):
    sage genus3_sage_helper.sage <input_json> <output_json>

Input JSON format:
{
  "curves": [
    {"id": "2940", "poly": "x^3*y + x^3*z + ..."},
    ...
  ],
  "primes": [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
}

Output JSON format:
{
  "results": [
    {"id": "2940", "a_p": {5: 1, 7: -2, ...}, "point_counts": {5: 5, 7: 10, ...}},
    ...
  ]
}

For a smooth plane quartic C: f(x,y,z) = 0 in P^2:
  - genus = (4-1)(4-2)/2 = 3
  - #C(F_p) = #{(x:y:z) in P^2(F_p) : f(x,y,z) = 0}
  - a_p = p + 1 - #C(F_p)  (trace of Frobenius)
"""

import json
import sys
import time


class SageEncoder(json.JSONEncoder):
    """JSON encoder that handles Sage Integer/RealNumber types."""
    def default(self, obj):
        try:
            return int(obj)
        except (TypeError, ValueError):
            pass
        try:
            return float(obj)
        except (TypeError, ValueError):
            pass
        return super().default(obj)


def dump_json(obj, fp, **kwargs):
    """json.dump with SageEncoder."""
    json.dump(obj, fp, cls=SageEncoder, **kwargs)

def count_points_projective(f, p):
    """Count points on the projective curve f(x,y,z)=0 over F_p.

    Enumerate all points in P^2(F_p) and count zeros of f.
    P^2(F_p) has p^2 + p + 1 points.

    We use three affine charts:
      Chart 1 (z=1): (x, y, 1) for x, y in F_p  -> p^2 points
      Chart 2 (z=0, y=1): (x, 1, 0) for x in F_p -> p points
      Chart 3 (z=0, y=0): (1, 0, 0)               -> 1 point
    Total: p^2 + p + 1 = #P^2(F_p). Correct.
    """
    Fp = GF(p)
    R_p = PolynomialRing(Fp, 'x,y,z')
    x_p, y_p, z_p = R_p.gens()

    # Convert polynomial to F_p
    try:
        f_p = R_p(f)
    except Exception as e:
        return None, str(e)

    count = 0

    # Chart 1: z = 1
    for a in range(p):
        for b in range(p):
            if f_p(Fp(a), Fp(b), Fp(1)) == 0:
                count += 1

    # Chart 2: z = 0, y = 1
    for a in range(p):
        if f_p(Fp(a), Fp(1), Fp(0)) == 0:
            count += 1

    # Chart 3: z = 0, y = 0, x = 1
    if f_p(Fp(1), Fp(0), Fp(0)) == 0:
        count += 1

    return count, None


def process_curves(input_path, output_path):
    with open(input_path, 'r') as f:
        data = json.load(f)

    curves = data['curves']
    primes = data['primes']

    # Set up the polynomial ring over Q
    R = PolynomialRing(QQ, 'x,y,z')
    x, y, z = R.gens()

    results = []
    total = len(curves)

    for idx, curve in enumerate(curves):
        cid = curve['id']
        poly_str = curve['poly']
        t0 = time.time()

        # Parse the polynomial
        try:
            f = R(poly_str)
        except Exception as e:
            results.append({
                'id': cid,
                'error': f'parse error: {str(e)}',
                'a_p': {},
                'point_counts': {}
            })
            continue

        a_p = {}
        point_counts = {}
        errors = []

        for p in primes:
            # Skip primes dividing the conductor (bad primes)
            try:
                cond_int = int(cid)
                if cond_int % p == 0:
                    continue
            except ValueError:
                pass

            count, err = count_points_projective(f, p)
            if err:
                errors.append(f'p={p}: {err}')
                continue

            point_counts[str(p)] = int(count)
            a_p[str(p)] = int(p + 1 - count)

        elapsed = time.time() - t0
        result = {
            'id': cid,
            'a_p': a_p,
            'point_counts': point_counts,
        }
        if errors:
            result['errors'] = errors

        results.append(result)

        # Save intermediate results every 10 curves
        if (idx + 1) % 10 == 0 or idx == total - 1:
            with open(output_path, 'w') as f:
                dump_json({'results': results, 'completed': int(idx + 1), 'total': int(total)}, f, indent=2)
            print(f'  [{idx+1}/{total}] Saved. Last curve {cid} took {elapsed:.1f}s')

    # Final save
    with open(output_path, 'w') as f:
        dump_json({'results': results, 'completed': int(total), 'total': int(total)}, f, indent=2)
    print(f'Done. {total} curves processed.')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: sage genus3_sage_helper.sage <input.json> <output.json>')
        sys.exit(1)
    process_curves(sys.argv[1], sys.argv[2])
