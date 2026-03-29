"""
Quaternion & Octonion Algebra -- Hypercomplex number systems and their geometry

Connects to: [rotation_groups, clifford_algebras, division_algebras, topology]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "quaternion_octonion"
OPERATIONS = {}


def quaternion_multiply(x):
    """Multiply two quaternions packed as [a1,b1,c1,d1,a2,b2,c2,d2].
    Input: array(8). Output: array(4)."""
    q1 = x[:4]
    q2 = x[4:8] if len(x) >= 8 else np.array([1.0, 0.0, 0.0, 0.0])
    a1, b1, c1, d1 = q1
    a2, b2, c2, d2 = q2
    return np.array([
        a1*a2 - b1*b2 - c1*c2 - d1*d2,
        a1*b2 + b1*a2 + c1*d2 - d1*c2,
        a1*c2 - b1*d2 + c1*a2 + d1*b2,
        a1*d2 + b1*c2 - c1*b2 + d1*a2
    ])

OPERATIONS["quaternion_multiply"] = {
    "fn": quaternion_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Hamilton product of two quaternions"
}


def quaternion_conjugate(x):
    """Conjugate of quaternion [w, x, y, z] -> [w, -x, -y, -z].
    Input: array(4+). Output: array(4)."""
    q = x[:4]
    return np.array([q[0], -q[1], -q[2], -q[3]])

OPERATIONS["quaternion_conjugate"] = {
    "fn": quaternion_conjugate,
    "input_type": "array",
    "output_type": "array",
    "description": "Quaternion conjugate (negate vector part)"
}


def quaternion_norm(x):
    """Norm of quaternion. Input: array(4+). Output: scalar."""
    q = x[:4]
    return np.sqrt(np.sum(q**2))

OPERATIONS["quaternion_norm"] = {
    "fn": quaternion_norm,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Euclidean norm of quaternion"
}


def quaternion_inverse(x):
    """Multiplicative inverse q* / |q|^2. Input: array(4+). Output: array(4)."""
    q = x[:4]
    norm_sq = np.sum(q**2)
    conj = np.array([q[0], -q[1], -q[2], -q[3]])
    return conj / norm_sq

OPERATIONS["quaternion_inverse"] = {
    "fn": quaternion_inverse,
    "input_type": "array",
    "output_type": "array",
    "description": "Quaternion multiplicative inverse"
}


def quaternion_rotate_vector(x):
    """Rotate vector v by unit quaternion q: q v q*.
    Input: array with q=[x0..x3], v=[x4,x5,x6]. Output: array(3)."""
    q = x[:4]
    v = x[4:7] if len(x) >= 7 else x[1:4]
    # Normalize quaternion
    q = q / np.linalg.norm(q)
    # v as pure quaternion [0, vx, vy, vz]
    v_quat = np.array([0.0, v[0] if len(v) > 0 else 0.0,
                        v[1] if len(v) > 1 else 0.0,
                        v[2] if len(v) > 2 else 0.0])
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
    # qvq*
    temp = quaternion_multiply(np.concatenate([q, v_quat]))
    result = quaternion_multiply(np.concatenate([temp, q_conj]))
    return result[1:4]

OPERATIONS["quaternion_rotate_vector"] = {
    "fn": quaternion_rotate_vector,
    "input_type": "array",
    "output_type": "array",
    "description": "Rotate 3D vector by unit quaternion via q*v*q_conj"
}


def slerp_interpolation(x):
    """Spherical linear interpolation between two unit quaternions.
    Input: array with q1=[x0..x3], q2=[x4..x7], t from remaining or default 0.5.
    Output: array(4)."""
    q1 = x[:4]
    q2 = x[4:8] if len(x) >= 8 else np.array([1.0, 0.0, 0.0, 0.0])
    t = x[8] if len(x) >= 9 else 0.5
    # Normalize
    q1 = q1 / np.linalg.norm(q1)
    q2 = q2 / np.linalg.norm(q2)
    dot = np.dot(q1, q2)
    # If negative dot, negate one to take shorter path
    if dot < 0:
        q2 = -q2
        dot = -dot
    dot = np.clip(dot, -1.0, 1.0)
    if dot > 0.9995:
        # Linear interpolation for very close quaternions
        result = q1 + t * (q2 - q1)
        return result / np.linalg.norm(result)
    theta = np.arccos(dot)
    sin_theta = np.sin(theta)
    result = (np.sin((1 - t) * theta) / sin_theta) * q1 + (np.sin(t * theta) / sin_theta) * q2
    return result

OPERATIONS["slerp_interpolation"] = {
    "fn": slerp_interpolation,
    "input_type": "array",
    "output_type": "array",
    "description": "SLERP between two unit quaternions"
}


# Octonion multiplication table (Fano plane convention)
# Basis: e0=1, e1..e7
# Using the common index-cycling convention
_OCTONION_MULT = np.zeros((8, 8, 8))

def _init_octonion_table():
    """Initialize octonion structure constants from Fano plane triples."""
    # Fano plane triples (i,j,k) where ei*ej = ek
    triples = [
        (1, 2, 4), (2, 3, 5), (3, 4, 6), (4, 5, 7),
        (5, 6, 1), (6, 7, 2), (7, 1, 3)
    ]
    global _OCTONION_MULT
    # e0 is identity
    for i in range(8):
        _OCTONION_MULT[0, i, i] = 1.0
        _OCTONION_MULT[i, 0, i] = 1.0
    # ei*ei = -1 for i>=1
    for i in range(1, 8):
        _OCTONION_MULT[i, i, 0] = -1.0
    # Fano plane triples
    for (i, j, k) in triples:
        _OCTONION_MULT[i, j, k] = 1.0
        _OCTONION_MULT[j, i, k] = -1.0  # anti-commutativity
        # Cyclic: j,k -> i
        _OCTONION_MULT[j, k, i] = 1.0
        _OCTONION_MULT[k, j, i] = -1.0
        # k,i -> j
        _OCTONION_MULT[k, i, j] = 1.0
        _OCTONION_MULT[i, k, j] = -1.0

_init_octonion_table()


def octonion_multiply(x):
    """Multiply two octonions packed as array(16). Non-associative!
    Input: array(16). Output: array(8)."""
    a = x[:8]
    b = x[8:16] if len(x) >= 16 else np.concatenate([np.array([1.0]), np.zeros(7)])
    result = np.zeros(8)
    for i in range(8):
        for j in range(8):
            for k in range(8):
                result[k] += _OCTONION_MULT[i, j, k] * a[i] * b[j]
    return result

OPERATIONS["octonion_multiply"] = {
    "fn": octonion_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Octonion product (non-associative Cayley-Dickson)"
}


def octonion_norm(x):
    """Norm of octonion. Input: array(8+). Output: scalar."""
    o = x[:8]
    return np.sqrt(np.sum(o**2))

OPERATIONS["octonion_norm"] = {
    "fn": octonion_norm,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Euclidean norm of octonion"
}


def octonion_conjugate(x):
    """Conjugate of octonion: negate all imaginary parts.
    Input: array(8+). Output: array(8)."""
    o = x[:8].copy()
    o[1:] = -o[1:]
    return o

OPERATIONS["octonion_conjugate"] = {
    "fn": octonion_conjugate,
    "input_type": "array",
    "output_type": "array",
    "description": "Octonion conjugate (negate imaginary parts)"
}


def fano_plane_structure_constants(x):
    """Return the 7x7 structure constant matrix for octonion imaginaries.
    Entry (i,j) gives the index k (1-7) such that e_i * e_j = +/- e_k,
    with sign encoded. Input: ignored. Output: matrix(7,7)."""
    result = np.zeros((7, 7))
    for i in range(1, 8):
        for j in range(1, 8):
            if i == j:
                result[i-1, j-1] = 0  # ei*ei = -e0, not an imaginary basis
                continue
            for k in range(1, 8):
                if _OCTONION_MULT[i, j, k] != 0:
                    result[i-1, j-1] = k * _OCTONION_MULT[i, j, k]
                    break
    return result

OPERATIONS["fano_plane_structure_constants"] = {
    "fn": fano_plane_structure_constants,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Fano plane structure constants for octonion imaginaries"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0,
                                         0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
