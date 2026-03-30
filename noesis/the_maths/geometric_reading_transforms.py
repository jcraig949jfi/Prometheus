"""
Geometric Reading Transforms — Geometric transformations for reading symbol sequences

Connects to: [symbol_analysis_toolkit]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "geometric_reading_transforms"
OPERATIONS = {}


def boustrophedon_transform(x):
    """Apply boustrophedon (alternating direction) reading order to a 2D grid.
    Input: array (flattened row-major grid). Output: array in boustrophedon order.
    Even rows L->R, odd rows R->L (like ox-plowing)."""
    n = len(x)
    ncols = int(np.ceil(np.sqrt(n)))
    if ncols < 1:
        ncols = 1
    nrows = int(np.ceil(n / ncols))
    # Pad to fill grid
    padded = np.zeros(nrows * ncols)
    padded[:n] = x
    grid = padded.reshape(nrows, ncols)
    result = []
    for i in range(nrows):
        row = grid[i]
        if i % 2 == 1:
            row = row[::-1]
        result.extend(row)
    return np.array(result[:n])


OPERATIONS["boustrophedon_transform"] = {
    "fn": boustrophedon_transform,
    "input_type": "array",
    "output_type": "array",
    "description": "Boustrophedon (alternating L-R, R-L) reading of 2D grid"
}


def reverse_boustrophedon(x):
    """Reverse boustrophedon transform (Rongorongo-style: start R->L, alternate).
    Input: array (flattened grid). Output: array in reverse boustrophedon order.
    Rongorongo is read bottom-to-top, alternating R->L and L->R, with 180-degree rotation."""
    n = len(x)
    ncols = int(np.ceil(np.sqrt(n)))
    if ncols < 1:
        ncols = 1
    nrows = int(np.ceil(n / ncols))
    padded = np.zeros(nrows * ncols)
    padded[:n] = x
    grid = padded.reshape(nrows, ncols)
    # Rongorongo: bottom to top, first row R->L
    result = []
    for i in range(nrows - 1, -1, -1):
        row = grid[i]
        # Even rows from bottom: R->L, odd: L->R
        row_from_bottom = nrows - 1 - i
        if row_from_bottom % 2 == 0:
            row = row[::-1]
        result.extend(row)
    return np.array(result[:n])


OPERATIONS["reverse_boustrophedon"] = {
    "fn": reverse_boustrophedon,
    "input_type": "array",
    "output_type": "array",
    "description": "Reverse boustrophedon (Rongorongo-style bottom-up alternating)"
}


def spiral_reading_order(x):
    """Read a 2D grid in spiral order (outside-in, clockwise).
    Input: array (flattened grid). Output: array in spiral order."""
    n = len(x)
    ncols = int(np.ceil(np.sqrt(n)))
    if ncols < 1:
        return x.copy()
    nrows = int(np.ceil(n / ncols))
    padded = np.zeros(nrows * ncols)
    padded[:n] = x
    grid = padded.reshape(nrows, ncols)
    result = []
    top, bottom, left, right = 0, nrows - 1, 0, ncols - 1
    while top <= bottom and left <= right:
        # Right across top
        for j in range(left, right + 1):
            result.append(grid[top, j])
        top += 1
        # Down right side
        for i in range(top, bottom + 1):
            result.append(grid[i, right])
        right -= 1
        # Left across bottom
        if top <= bottom:
            for j in range(right, left - 1, -1):
                result.append(grid[bottom, j])
            bottom -= 1
        # Up left side
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(grid[i, left])
            left += 1
    return np.array(result[:n])


OPERATIONS["spiral_reading_order"] = {
    "fn": spiral_reading_order,
    "input_type": "array",
    "output_type": "array",
    "description": "Spiral (clockwise outside-in) reading of 2D grid"
}


def positional_encoding_1d(x):
    """Sinusoidal positional encoding for 1D sequence (Transformer-style).
    Input: array of values. Output: array of positional encodings (sin/cos interleaved).
    PE(pos, 2i) = sin(pos / 10000^{2i/d}), PE(pos, 2i+1) = cos(pos / 10000^{2i/d})."""
    n = len(x)
    d_model = n
    positions = np.arange(n)
    encodings = np.zeros(n)
    for i in range(n):
        if i % 2 == 0:
            encodings[i] = np.sin(positions[i] / (10000.0 ** (i / max(d_model, 1))))
        else:
            encodings[i] = np.cos(positions[i] / (10000.0 ** ((i - 1) / max(d_model, 1))))
    return encodings


OPERATIONS["positional_encoding_1d"] = {
    "fn": positional_encoding_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "1D sinusoidal positional encoding (Transformer-style)"
}


def positional_encoding_2d(x):
    """2D positional encoding for grid of symbols.
    Input: array (flattened grid). Output: array of 2D positional encoding magnitudes.
    Combines row and column sinusoidal encodings."""
    n = len(x)
    ncols = int(np.ceil(np.sqrt(n)))
    if ncols < 1:
        ncols = 1
    nrows = int(np.ceil(n / ncols))
    encodings = np.zeros(nrows * ncols)
    for idx in range(nrows * ncols):
        row = idx // ncols
        col = idx % ncols
        # 2D encoding: combine row and column frequencies
        enc_row = np.sin(row / (10000.0 ** (0.0 / max(ncols, 1))))
        enc_col = np.cos(col / (10000.0 ** (1.0 / max(nrows, 1))))
        encodings[idx] = np.sqrt(enc_row ** 2 + enc_col ** 2)
    return encodings[:n]


OPERATIONS["positional_encoding_2d"] = {
    "fn": positional_encoding_2d,
    "input_type": "array",
    "output_type": "array",
    "description": "2D positional encoding combining row and column sinusoidals"
}


def reading_direction_detect(x):
    """Detect likely reading direction by analyzing bigram asymmetry.
    Input: array of symbol indices. Output: array [forward_score, reverse_score, ratio].
    Higher conditional entropy in reverse suggests forward is the natural direction."""
    from collections import Counter
    symbols = np.round(x).astype(int)
    n = len(symbols)
    if n < 3:
        return np.array([0.0, 0.0, 1.0])

    def bigram_entropy(seq):
        bigram_counts = Counter()
        unigram_counts = Counter()
        for i in range(len(seq) - 1):
            bigram_counts[(seq[i], seq[i+1])] += 1
            unigram_counts[seq[i]] += 1
        H = 0.0
        total = len(seq) - 1
        for (s_i, s_j), count in bigram_counts.items():
            p_ij = count / total
            p_j_given_i = count / unigram_counts[s_i]
            H -= p_ij * np.log2(p_j_given_i + 1e-15)
        return H

    forward_H = bigram_entropy(symbols)
    reverse_H = bigram_entropy(symbols[::-1])
    # Lower conditional entropy = more predictable = likely reading direction
    ratio = forward_H / (reverse_H + 1e-15)
    return np.array([forward_H, reverse_H, ratio])


OPERATIONS["reading_direction_detect"] = {
    "fn": reading_direction_detect,
    "input_type": "array",
    "output_type": "array",
    "description": "Detect reading direction via bigram entropy asymmetry"
}


def mirror_line_transform(x):
    """Mirror each line of a grid (horizontal flip per row).
    Input: array (flattened grid). Output: array with each row reversed."""
    n = len(x)
    ncols = int(np.ceil(np.sqrt(n)))
    if ncols < 1:
        ncols = 1
    nrows = int(np.ceil(n / ncols))
    padded = np.zeros(nrows * ncols)
    padded[:n] = x
    grid = padded.reshape(nrows, ncols)
    mirrored = grid[:, ::-1]
    return mirrored.flatten()[:n]


OPERATIONS["mirror_line_transform"] = {
    "fn": mirror_line_transform,
    "input_type": "array",
    "output_type": "array",
    "description": "Mirror (horizontally flip) each row of the 2D grid"
}


def rotation_reading(x):
    """Read grid after 90-degree clockwise rotation.
    Input: array (flattened grid). Output: array in column-major (top-to-bottom, left-to-right)."""
    n = len(x)
    ncols = int(np.ceil(np.sqrt(n)))
    if ncols < 1:
        ncols = 1
    nrows = int(np.ceil(n / ncols))
    padded = np.zeros(nrows * ncols)
    padded[:n] = x
    grid = padded.reshape(nrows, ncols)
    # 90-degree CW rotation: transpose then flip rows
    rotated = np.rot90(grid, k=-1)
    return rotated.flatten()[:n]


OPERATIONS["rotation_reading"] = {
    "fn": rotation_reading,
    "input_type": "array",
    "output_type": "array",
    "description": "Read grid after 90-degree clockwise rotation"
}


def zigzag_reading_order(x):
    """Zigzag (diagonal) reading order of a 2D grid.
    Input: array (flattened grid). Output: array in zigzag diagonal order.
    Reads along anti-diagonals alternating direction (JPEG-style)."""
    n = len(x)
    ncols = int(np.ceil(np.sqrt(n)))
    if ncols < 1:
        ncols = 1
    nrows = int(np.ceil(n / ncols))
    padded = np.zeros(nrows * ncols)
    padded[:n] = x
    grid = padded.reshape(nrows, ncols)
    result = []
    for diag in range(nrows + ncols - 1):
        if diag % 2 == 0:
            # Go up-right
            r = min(diag, nrows - 1)
            c = diag - r
            while r >= 0 and c < ncols:
                result.append(grid[r, c])
                r -= 1
                c += 1
        else:
            # Go down-left
            c = min(diag, ncols - 1)
            r = diag - c
            while c >= 0 and r < nrows:
                result.append(grid[r, c])
                r += 1
                c -= 1
    return np.array(result[:n])


OPERATIONS["zigzag_reading_order"] = {
    "fn": zigzag_reading_order,
    "input_type": "array",
    "output_type": "array",
    "description": "Zigzag (anti-diagonal) reading order of 2D grid (JPEG-style)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
