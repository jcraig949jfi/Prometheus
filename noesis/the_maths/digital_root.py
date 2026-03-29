"""
Digital Root — digital root, multiplicative persistence, additive persistence

Connects to: [number_theory, recreational_mathematics, digit_sequences]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "digital_root"
OPERATIONS = {}


def digital_root(x):
    """Compute digital root of each element. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    # Digital root: dr(n) = 1 + ((n-1) % 9) for n > 0, 0 for n=0
    result = np.where(vals == 0, 0, 1 + (vals - 1) % 9)
    return result.astype(np.int64)


OPERATIONS["digital_root"] = {
    "fn": digital_root,
    "input_type": "array",
    "output_type": "array",
    "description": "Digital root (repeated digit sum until single digit)"
}


def additive_persistence(x):
    """Count iterations of digit-sum until single digit. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    results = []
    for v in vals.ravel():
        count = 0
        n = int(v)
        while n >= 10:
            n = sum(int(d) for d in str(n))
            count += 1
        results.append(count)
    return np.array(results).reshape(vals.shape)


OPERATIONS["additive_persistence"] = {
    "fn": additive_persistence,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of digit-sum iterations to reach single digit"
}


def multiplicative_persistence(x):
    """Count iterations of digit-product until single digit. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    results = []
    for v in vals.ravel():
        count = 0
        n = int(v)
        while n >= 10:
            product = 1
            for d in str(n):
                product *= int(d)
            n = product
            count += 1
        results.append(count)
    return np.array(results).reshape(vals.shape)


OPERATIONS["multiplicative_persistence"] = {
    "fn": multiplicative_persistence,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of digit-product iterations to reach single digit"
}


def digit_sum(x):
    """Sum of digits of each element. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    results = np.array([sum(int(d) for d in str(int(v))) for v in vals.ravel()])
    return results.reshape(vals.shape)


OPERATIONS["digit_sum"] = {
    "fn": digit_sum,
    "input_type": "array",
    "output_type": "array",
    "description": "Sum of decimal digits"
}


def digit_product(x):
    """Product of digits of each element. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    results = []
    for v in vals.ravel():
        p = 1
        for d in str(int(v)):
            p *= int(d)
        results.append(p)
    return np.array(results).reshape(vals.shape)


OPERATIONS["digit_product"] = {
    "fn": digit_product,
    "input_type": "array",
    "output_type": "array",
    "description": "Product of decimal digits"
}


def kaprekar_routine(x):
    """Apply Kaprekar routine: sort digits desc - sort digits asc. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    results = []
    for v in vals.ravel():
        s = str(int(v))
        digits_desc = ''.join(sorted(s, reverse=True))
        digits_asc = ''.join(sorted(s))
        results.append(int(digits_desc) - int(digits_asc))
    return np.array(results).reshape(vals.shape)


OPERATIONS["kaprekar_routine"] = {
    "fn": kaprekar_routine,
    "input_type": "array",
    "output_type": "array",
    "description": "One step of Kaprekar routine (descending - ascending digit arrangement)"
}


def happy_number_test(x):
    """Test if numbers are happy (iterated sum of squares of digits reaches 1). Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    results = []
    for v in vals.ravel():
        n = int(v)
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = sum(int(d) ** 2 for d in str(n))
        results.append(1 if n == 1 else 0)
    return np.array(results).reshape(vals.shape)


OPERATIONS["happy_number_test"] = {
    "fn": happy_number_test,
    "input_type": "array",
    "output_type": "array",
    "description": "1 if happy number, 0 otherwise"
}


def narcissistic_check(x):
    """Check if n equals sum of its digits each raised to the power of digit count. Input: array. Output: array."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    results = []
    for v in vals.ravel():
        s = str(int(v))
        k = len(s)
        narc_sum = sum(int(d) ** k for d in s)
        results.append(1 if narc_sum == int(v) else 0)
    return np.array(results).reshape(vals.shape)


OPERATIONS["narcissistic_check"] = {
    "fn": narcissistic_check,
    "input_type": "array",
    "output_type": "array",
    "description": "1 if narcissistic (Armstrong) number, 0 otherwise"
}


def digit_frequency_entropy(x):
    """Shannon entropy of digit frequency distribution. Input: array. Output: scalar."""
    vals = np.asarray(np.abs(x), dtype=np.int64)
    all_digits = ''.join(str(int(v)) for v in vals.ravel())
    if len(all_digits) == 0:
        return 0.0
    counts = np.zeros(10)
    for d in all_digits:
        counts[int(d)] += 1
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log2(probs))
    return float(entropy)


OPERATIONS["digit_frequency_entropy"] = {
    "fn": digit_frequency_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of digit frequency across all values"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
