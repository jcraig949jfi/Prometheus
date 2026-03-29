"""
Geometric Algebra — multivectors, geometric product, rotors, reflections

Connects to: [clifford_algebra, linear_algebra, differential_geometry, topology]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

Convention for 2D multivectors: [scalar, e1, e2, e12]
Convention for 3D multivectors: [scalar, e1, e2, e3, e12, e13, e23, e123]
"""

import numpy as np

FIELD_NAME = "geometric_algebra"
OPERATIONS = {}


def geometric_product_2d(x):
    """Geometric product of two 2D multivectors.
    Input: array of length >= 8 (two multivectors [s,e1,e2,e12] concatenated).
    If shorter, pads with zeros. Output: array [s,e1,e2,e12].

    Rules: e1*e1=1, e2*e2=1, e1*e2=e12, e2*e1=-e12.
    Input: array. Output: array."""
    padded = np.zeros(8)
    padded[:min(len(x), 8)] = x[:min(len(x), 8)]
    a_s, a_1, a_2, a_12 = padded[0], padded[1], padded[2], padded[3]
    b_s, b_1, b_2, b_12 = padded[4], padded[5], padded[6], padded[7]

    # Geometric product table for Cl(2,0):
    # 1*1=1, 1*e1=e1, 1*e2=e2, 1*e12=e12
    # e1*e1=1, e1*e2=e12, e1*e12=e2
    # e2*e1=-e12, e2*e2=1, e2*e12=-e1
    # e12*e1=-e2, e12*e2=e1, e12*e12=-1
    r_s = a_s * b_s + a_1 * b_1 + a_2 * b_2 - a_12 * b_12
    r_1 = a_s * b_1 + a_1 * b_s - a_2 * b_12 + a_12 * b_2
    r_2 = a_s * b_2 + a_1 * b_12 + a_2 * b_s - a_12 * b_1
    r_12 = a_s * b_12 + a_1 * b_2 - a_2 * b_1 + a_12 * b_s

    return np.array([r_s, r_1, r_2, r_12])


OPERATIONS["geometric_product_2d"] = {
    "fn": geometric_product_2d,
    "input_type": "array",
    "output_type": "array",
    "description": "Geometric product of two 2D multivectors in Cl(2,0)"
}


def outer_product_2d(x):
    """Outer (wedge) product of two 2D vectors.
    Input: array [a1, a2, b1, b2] (two vectors). Output: array [0, 0, 0, a1*b2 - a2*b1].
    The result is a pure bivector. Input: array. Output: array."""
    padded = np.zeros(4)
    padded[:min(len(x), 4)] = x[:min(len(x), 4)]
    a1, a2, b1, b2 = padded[0], padded[1], padded[2], padded[3]
    # a ^ b = (a1*b2 - a2*b1) * e12
    bivector = a1 * b2 - a2 * b1
    return np.array([0.0, 0.0, 0.0, bivector])


OPERATIONS["outer_product_2d"] = {
    "fn": outer_product_2d,
    "input_type": "array",
    "output_type": "array",
    "description": "Outer (wedge) product of two 2D vectors yielding a bivector"
}


def inner_product_2d(x):
    """Inner (dot) product of two 2D vectors.
    Input: array [a1, a2, b1, b2]. Output: scalar.
    Input: array. Output: scalar."""
    padded = np.zeros(4)
    padded[:min(len(x), 4)] = x[:min(len(x), 4)]
    a1, a2, b1, b2 = padded[0], padded[1], padded[2], padded[3]
    return float(a1 * b1 + a2 * b2)


OPERATIONS["inner_product_2d"] = {
    "fn": inner_product_2d,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Inner product of two 2D vectors"
}


def rotor_from_angle(x):
    """Create a 2D rotor R = cos(theta/2) - sin(theta/2)*e12 from angle theta=x[0].
    Input: array. Output: array [cos(t/2), 0, 0, -sin(t/2)]."""
    theta = float(x[0])
    return np.array([np.cos(theta / 2), 0.0, 0.0, -np.sin(theta / 2)])


OPERATIONS["rotor_from_angle"] = {
    "fn": rotor_from_angle,
    "input_type": "array",
    "output_type": "array",
    "description": "2D rotor multivector for rotation by angle x[0]"
}


def apply_rotor_2d(x):
    """Apply a 2D rotor to a vector: v' = R * v * R_reverse.
    Input: array [v1, v2, theta] (vector + rotation angle). Output: array [v1', v2'].
    Input: array. Output: array."""
    padded = np.zeros(3)
    padded[:min(len(x), 3)] = x[:min(len(x), 3)]
    v1, v2, theta = padded[0], padded[1], padded[2]

    c = np.cos(theta)
    s = np.sin(theta)
    # Rotation: R v R~ is standard 2D rotation
    v1_new = c * v1 - s * v2
    v2_new = s * v1 + c * v2
    return np.array([v1_new, v2_new])


OPERATIONS["apply_rotor_2d"] = {
    "fn": apply_rotor_2d,
    "input_type": "array",
    "output_type": "array",
    "description": "Rotate 2D vector by angle using rotor sandwich product R*v*R~"
}


def reflection_2d(x):
    """Reflect a 2D vector through a line defined by unit vector n.
    v' = n * v * n (in geometric algebra).
    Input: array [v1, v2, n1, n2]. Output: array [v1', v2'].
    Input: array. Output: array."""
    padded = np.zeros(4)
    padded[:min(len(x), 4)] = x[:min(len(x), 4)]
    v1, v2, n1, n2 = padded[0], padded[1], padded[2], padded[3]

    # Normalize n
    norm_n = np.sqrt(n1 ** 2 + n2 ** 2)
    if norm_n < 1e-15:
        return np.array([v1, v2])
    n1, n2 = n1 / norm_n, n2 / norm_n

    # Reflection formula: v' = n*v*n = 2*(v.n)*n - v (for unit n in Euclidean space)
    # Actually in GA: n*v*n reflects through the line perpendicular to n
    # The standard reflection through the line along n is: n*v*n^{-1}
    # For unit n: v' = 2(v.n)n - v reflects through line along n
    dot = v1 * n1 + v2 * n2
    r1 = 2 * dot * n1 - v1
    r2 = 2 * dot * n2 - v2
    return np.array([r1, r2])


OPERATIONS["reflection_2d"] = {
    "fn": reflection_2d,
    "input_type": "array",
    "output_type": "array",
    "description": "Reflect 2D vector through line defined by direction [n1,n2]"
}


def grade_projection(x):
    """Project a 2D multivector onto each grade.
    Input: array [s, e1, e2, e12, grade]. Output: array (grade-k component).
    Input: array. Output: array."""
    padded = np.zeros(5)
    padded[:min(len(x), 5)] = x[:min(len(x), 5)]
    mv = padded[:4]
    grade = int(padded[4]) % 3  # grades 0, 1, 2

    if grade == 0:
        return np.array([mv[0], 0.0, 0.0, 0.0])
    elif grade == 1:
        return np.array([0.0, mv[1], mv[2], 0.0])
    else:  # grade 2
        return np.array([0.0, 0.0, 0.0, mv[3]])


OPERATIONS["grade_projection"] = {
    "fn": grade_projection,
    "input_type": "array",
    "output_type": "array",
    "description": "Project 2D multivector onto specified grade (0=scalar, 1=vector, 2=bivector)"
}


def multivector_reverse(x):
    """Reverse of a 2D multivector: reverses order of basis vector factors.
    Grade k component gets sign (-1)^{k(k-1)/2}.
    Input: array [s, e1, e2, e12]. Output: array.
    Input: array. Output: array."""
    padded = np.zeros(4)
    padded[:min(len(x), 4)] = x[:min(len(x), 4)]
    # Grade 0: sign +1, Grade 1: sign +1, Grade 2: sign -1
    return np.array([padded[0], padded[1], padded[2], -padded[3]])


OPERATIONS["multivector_reverse"] = {
    "fn": multivector_reverse,
    "input_type": "array",
    "output_type": "array",
    "description": "Reverse (dagger) of 2D multivector: reverses basis vector ordering"
}


def multivector_norm(x):
    """Norm of a 2D multivector: |A| = sqrt(|<A * A~>_0|).
    Input: array [s, e1, e2, e12]. Output: scalar.
    Input: array. Output: scalar."""
    padded = np.zeros(4)
    padded[:min(len(x), 4)] = x[:min(len(x), 4)]
    a_s, a_1, a_2, a_12 = padded[0], padded[1], padded[2], padded[3]

    # A~ = [a_s, a_1, a_2, -a_12]
    # A * A~ scalar part = a_s^2 + a_1^2 + a_2^2 - a_12*(-a_12) = a_s^2 + a_1^2 + a_2^2 + a_12^2
    # Wait, need to compute properly via geometric product:
    # scalar part of A*A~
    rev = np.array([a_s, a_1, a_2, -a_12])
    # Use geometric product
    combined = np.zeros(8)
    combined[:4] = padded[:4]
    combined[4:] = rev
    product = geometric_product_2d(combined)
    scalar_part = product[0]
    return float(np.sqrt(abs(scalar_part)))


OPERATIONS["multivector_norm"] = {
    "fn": multivector_norm,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Norm of 2D multivector: sqrt(|scalar_part(A * A~)|)"
}


def bivector_from_vectors(x):
    """Compute the bivector (wedge product) of two 2D vectors.
    Input: array [a1, a2, b1, b2]. Output: scalar (the e12 coefficient).
    Input: array. Output: scalar."""
    padded = np.zeros(4)
    padded[:min(len(x), 4)] = x[:min(len(x), 4)]
    a1, a2, b1, b2 = padded[0], padded[1], padded[2], padded[3]
    return float(a1 * b2 - a2 * b1)


OPERATIONS["bivector_from_vectors"] = {
    "fn": bivector_from_vectors,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Bivector coefficient from wedge product of two 2D vectors"
}


def geometric_product_3d(x):
    """Geometric product of two 3D multivectors in Cl(3,0).
    Input: array of length >= 16 (two multivectors [s,e1,e2,e3,e12,e13,e23,e123] concatenated).
    Output: array [s,e1,e2,e3,e12,e13,e23,e123].

    Signature: e1^2 = e2^2 = e3^2 = 1.
    Input: array. Output: array."""
    padded = np.zeros(16)
    padded[:min(len(x), 16)] = x[:min(len(x), 16)]
    a = padded[:8]   # [s, e1, e2, e3, e12, e13, e23, e123]
    b = padded[8:16]

    # Multiplication table for Cl(3,0) basis: {1, e1, e2, e3, e12, e13, e23, e123}
    # Indices: 0=1, 1=e1, 2=e2, 3=e3, 4=e12, 5=e13, 6=e23, 7=e123
    #
    # Full product table (sign, result_index):
    # Built from: ei*ei=+1, ei*ej=-ej*ei for i!=j, e123=e1*e2*e3

    r = np.zeros(8)

    # Scalar (grade 0) output
    r[0] = (a[0]*b[0] + a[1]*b[1] + a[2]*b[2] + a[3]*b[3]
            - a[4]*b[4] - a[5]*b[5] - a[6]*b[6] - a[7]*b[7])

    # e1 output
    r[1] = (a[0]*b[1] + a[1]*b[0] - a[2]*b[4] - a[3]*b[5]
            + a[4]*b[2] + a[5]*b[3] - a[6]*b[7] - a[7]*b[6])

    # e2 output
    r[2] = (a[0]*b[2] + a[1]*b[4] + a[2]*b[0] - a[3]*b[6]
            - a[4]*b[1] + a[5]*b[7] + a[6]*b[3] + a[7]*b[5])

    # e3 output
    r[3] = (a[0]*b[3] + a[1]*b[5] + a[2]*b[6] + a[3]*b[0]
            - a[4]*b[7] - a[5]*b[1] - a[6]*b[2] - a[7]*b[4])

    # e12 output
    r[4] = (a[0]*b[4] + a[1]*b[2] - a[2]*b[1] + a[3]*b[7]
            + a[4]*b[0] - a[5]*b[6] + a[6]*b[5] + a[7]*b[3])

    # e13 output
    r[5] = (a[0]*b[5] + a[1]*b[3] - a[2]*b[7] - a[3]*b[1]
            + a[4]*b[6] + a[5]*b[0] - a[6]*b[4] - a[7]*b[2])

    # e23 output
    r[6] = (a[0]*b[6] + a[1]*b[7] + a[2]*b[3] - a[3]*b[2]
            - a[4]*b[5] + a[5]*b[4] + a[6]*b[0] + a[7]*b[1])

    # e123 output
    r[7] = (a[0]*b[7] + a[1]*b[6] - a[2]*b[5] + a[3]*b[4]
            + a[4]*b[3] - a[5]*b[2] + a[6]*b[1] + a[7]*b[0])

    return r


OPERATIONS["geometric_product_3d"] = {
    "fn": geometric_product_3d,
    "input_type": "array",
    "output_type": "array",
    "description": "Geometric product of two 3D multivectors in Cl(3,0)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
