"""
Charon configuration — connection strings, constants, tuning parameters.
All paths relative or config-driven. No hardcoded drive letters.
"""

from pathlib import Path

# Paths
CHARON_ROOT = Path(__file__).parent.parent
DATA_DIR = CHARON_ROOT / "data"
DB_PATH = DATA_DIR / "charon.duckdb"
RAW_DIR = DATA_DIR / "raw"
REPORTS_DIR = CHARON_ROOT / "reports"

# LMFDB PostgreSQL mirror
LMFDB_PG = {
    "host": "devmirror.lmfdb.xyz",
    "port": 5432,
    "dbname": "lmfdb",
    "user": "lmfdb",
    "password": "lmfdb",
}

# Ingestion parameters
BATCH_SIZE = 5000           # rows per fetch from LMFDB
MAX_CONDUCTOR_PHASE1 = 50000   # start small, expand later
INVARIANT_PRIMES = 50       # number of primes in universal invariant vector

# The first 50 primes
FIRST_50_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223, 227, 229
]

# Embedding parameters
EMBEDDING_DIM = 16          # spectral embedding dimensions
KNN_K = 30                  # nearest neighbors — needs headroom for isogeny class siblings
EPSILON_BALL = None         # if set, use epsilon-ball instead of k-NN

# Quality gate thresholds
BRIDGE_RECOVERY_TARGET = 0.80   # minimum fraction of known bridges recovered as NN
INVARIANT_TOLERANCE = 1e-6      # max L2 distance for "matching" invariant vectors
