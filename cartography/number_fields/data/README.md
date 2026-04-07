# Number Field Data (LMFDB)

## Source
Data downloaded from the [LMFDB](https://www.lmfdb.org/) (L-functions and Modular Forms DataBase).

- **Primary source**: PostgreSQL mirror at `devmirror.lmfdb.xyz:5432`
- **Fallback**: LMFDB REST API (`https://www.lmfdb.org/api/nf_fields/`)

## Selection criteria
- Degree: 1 through 6
- Absolute discriminant: <= 10000

## Fields
| Field | Description |
|-------|-------------|
| `label` | LMFDB label (e.g. `2.2.5.1`) |
| `degree` | Degree of the number field over Q |
| `disc_abs` | Absolute value of the discriminant |
| `disc_sign` | Sign of the discriminant (+1 or -1) |
| `class_number` | Class number h(K) |
| `class_group` | Class group as list of invariant factors |
| `regulator` | Regulator R(K) |

Additional fields may be present when downloaded via PostgreSQL (e.g. `signature`, `galois_label`, `galois_t`).

## Files
- `download_nf_fields.py` — Download script (run to refresh data)
- `number_fields.json` — Downloaded data

## Usage
```bash
pip install psycopg2-binary   # optional, for PostgreSQL path
python download_nf_fields.py
```

## Date
Downloaded: 2026-04-06
