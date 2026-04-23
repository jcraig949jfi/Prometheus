"""Session manifest — declare-once versioning (T1, wave 0).

Rationale: Rule 2 of VERSIONING.md requires every symbol reference to
carry @v<N>. At session scale, the prose density of version suffixes is
high enough that reviewers flagged it as a token-fragmentation failure
mode (external review 2026-04-21 §R2/R3/R4 convergence).

Fix: per-session manifest at top-of-output declares authoritative versions
once, then prose uses bare aliases. Parser maps bare → versioned at
commit/handoff time. Analogous to Cargo.toml / package.json.

Format:

    ---
    uses:
      NULL_BSWCD: 2
      PATTERN_30: 1
      SHADOWS_ON_WALL: 1
    ---

    The NULL_BSWCD test on F043 showed ... and PATTERN_30 Level-3
    coupling was ...

Both forms are accepted by the parser:

    uses: [NULL_BSWCD@v2, PATTERN_30@v1]          # list-of-references
    uses: {NULL_BSWCD: 2, PATTERN_30: 1}          # mapping NAME->int
    uses:                                          # block-style mapping
      NULL_BSWCD: 2
      PATTERN_30: 1

Public API:

    parse_session_manifest(text) -> Dict[str, int]
    resolve_with_manifest(name, manifest, ...)   -> dict
    expand_references(text, manifest)             -> text with @vN added
    contract_references(text, manifest)           -> text with @vN stripped
    round_trip(text, manifest)                    -> (contracted == original)

Composition:
- T2 (status-lifecycle): manifest declares versions only; status lookup
  is a separate key (symbols:<NAME>:status). resolve_with_manifest
  passes include_archived through to resolve() for T2 gating.
- T3 (cross-version policy): if text contains both a bare name (covered
  by manifest) AND an inline NAME@v<M> where M != manifest's version,
  CROSS_VERSION_CONFLICT warning is emitted and the manifest wins per
  first-resolve-wins. T3 will document this resolution; T1 implements it.
"""
from __future__ import annotations

import re
import warnings
from typing import Dict, Iterable, Optional, Tuple

from .parse import _parse_frontmatter
# Import base resolver functions directly from the submodule.
# NOTE: `from . import resolve as _resolve_mod` does NOT work here because
# agora/symbols/__init__.py re-exports the `resolve` function, shadowing the
# submodule name in the package namespace (discovered 2026-04-22 via T1 tests).
from .resolve import resolve as _base_resolve, resolve_at as _base_resolve_at


_REF_PATTERN = re.compile(r'\b(?P<name>[A-Za-z_][A-Za-z0-9_-]*)@v(?P<version>\d+)\b')


class CrossVersionConflict(UserWarning):
    """Bare-name (manifest-bound) and an inline @v<M> reference disagree on version."""


def _extract_frontmatter_block(text: str) -> Optional[str]:
    """Return the frontmatter block between the leading --- and closing ---, or None."""
    if not text.startswith('---\n') and not text.startswith('---\r\n'):
        return None
    # find closing ---
    # Accept \n---\n or \n---\r\n or \n---$ at EOF
    m = re.search(r'\n---\s*(?:\n|\r\n|$)', text[4:])
    if m is None:
        return None
    return text[4:4 + m.start()]


def _normalize_version(raw) -> int:
    """Accept 2, '2', 'v2', '@v2'; return int version."""
    if isinstance(raw, int):
        if raw < 1:
            raise ValueError(f'manifest version must be >= 1, got {raw}')
        return raw
    s = str(raw).strip()
    if s.startswith('@'):
        s = s[1:]
    if s.startswith('v') or s.startswith('V'):
        s = s[1:]
    if not s.isdigit():
        raise ValueError(f'manifest version not parseable: {raw!r}')
    v = int(s)
    if v < 1:
        raise ValueError(f'manifest version must be >= 1, got {v}')
    return v


def parse_session_manifest(source) -> Dict[str, int]:
    """Parse a session manifest from several input shapes.

    Accepts:
      - full text starting with `---\\n...\\n---\\n` (YAML frontmatter)
      - a pre-parsed frontmatter dict (from `parse._parse_frontmatter`)
      - the raw `uses:` value directly: list[str] or dict[str, int|str]

    Returns a dict mapping symbol NAME -> int version.
    Empty / absent manifest returns {}.
    """
    # Case 1: raw text with frontmatter
    if isinstance(source, str):
        block = _extract_frontmatter_block(source)
        if block is None:
            return {}
        fm = _parse_frontmatter(block)
        uses = fm.get('uses')
        if uses is None:
            return {}
        return parse_session_manifest(uses)
    # Case 2: full frontmatter dict
    if isinstance(source, dict) and 'uses' in source:
        return parse_session_manifest(source['uses'])
    # Case 3: 'uses' value as dict {NAME: v}
    if isinstance(source, dict):
        out: Dict[str, int] = {}
        for name, raw_v in source.items():
            name = str(name).strip()
            if not name:
                continue
            out[name] = _normalize_version(raw_v)
        return out
    # Case 4: list of references 'NAME@v<N>' or tuples
    if isinstance(source, (list, tuple)):
        out = {}
        for item in source:
            if isinstance(item, (tuple, list)) and len(item) == 2:
                out[str(item[0]).strip()] = _normalize_version(item[1])
                continue
            s = str(item).strip()
            if not s:
                continue
            m = re.match(r'^(?P<name>[A-Za-z_][A-Za-z0-9_-]*)@v(?P<v>\d+)$', s)
            if m:
                out[m.group('name')] = int(m.group('v'))
            else:
                raise ValueError(
                    f'manifest list item not in NAME@v<N> form: {s!r}'
                )
        return out
    raise TypeError(
        f'parse_session_manifest: unsupported source type {type(source).__name__}'
    )


def resolve_with_manifest(name, manifest: Dict[str, int], include_archived: bool = False):
    """Resolve a symbol via the manifest. Falls back to normal resolve() on miss.

    - If `name` is already in NAME@v<N> form, delegates to resolve_at (manifest
      is ignored for explicit references).
    - If `name` is a bare symbol name AND is in `manifest`, resolves at that
      version.
    - If `name` is a bare symbol name AND is NOT in `manifest`, falls through
      to resolve(name) which warns + returns latest.

    Lifecycle gating (T2) is honored: archived symbols raise
    SymbolArchivedError unless include_archived=True.
    """
    if '@v' in name:
        return _base_resolve_at(name, include_archived=include_archived)
    if name in manifest:
        return _base_resolve(
            name, version=manifest[name], include_archived=include_archived
        )
    return _base_resolve(name, include_archived=include_archived)


def expand_references(text: str, manifest: Dict[str, int], *, warn_conflicts: bool = True) -> str:
    """Rewrite bare symbol names → NAME@v<N> using the manifest.

    Called at commit/handoff time to produce fully-qualified prose.
    Preserves existing NAME@v<N> references; if one disagrees with the
    manifest, emits CrossVersionConflict (T3 policy: manifest wins).

    Only rewrites identifiers that look like symbol names:
        ([A-Za-z_][A-Za-z0-9_-]*)   NOT followed by '@v'

    and that are present in the manifest. Other uppercase tokens are
    left alone (so we don't corrupt random words).
    """
    if not manifest:
        return text

    # First pass: detect conflicts with existing @v<M> references
    if warn_conflicts:
        for m in _REF_PATTERN.finditer(text):
            n, v = m.group('name'), int(m.group('version'))
            if n in manifest and manifest[n] != v:
                warnings.warn(
                    f'CROSS_VERSION_CONFLICT: manifest binds {n}@v{manifest[n]} '
                    f'but inline reference {n}@v{v} found at position {m.start()}. '
                    f'Manifest wins in expand_references; use explicit `as` to override.',
                    CrossVersionConflict, stacklevel=2,
                )

    # Second pass: rewrite bare names
    # For each name in manifest, match bare occurrences (not followed by @v)
    # and not part of a longer identifier. Replace with NAME@v<N>.
    out = text
    # Sort by name-length desc so "NULL_BSWCD_EXT" isn't eaten by "NULL_BSWCD"
    for name in sorted(manifest, key=len, reverse=True):
        version = manifest[name]
        # Match name as a whole word, not followed by @v, not part of a longer identifier.
        # Using \b handles most cases; also guard against trailing -/_ word chars.
        pattern = re.compile(
            r'(?P<pre>(?:^|[^A-Za-z0-9_-]))'
            + re.escape(name)
            + r'(?![@A-Za-z0-9_-])'
        )
        out = pattern.sub(lambda m, v=version, n=name: f'{m.group("pre")}{n}@v{v}', out)
    return out


def contract_references(text: str, manifest: Dict[str, int], *, warn_conflicts: bool = True) -> str:
    """Rewrite NAME@v<N> → NAME when manifest covers it at the same version.

    Called when ingesting external prose that is fully-qualified and
    a manifest is available — restores bare-alias density. Inline
    @v<M> where M != manifest[N] is LEFT AS-IS (it's a deliberate
    override) and emits CrossVersionConflict for visibility.
    """
    if not manifest:
        return text

    def _sub(m: re.Match) -> str:
        name = m.group('name')
        v = int(m.group('version'))
        if name in manifest:
            if manifest[name] == v:
                return name  # contract
            if warn_conflicts:
                warnings.warn(
                    f'CROSS_VERSION_CONFLICT: {name}@v{v} in text, '
                    f'manifest binds v{manifest[name]}. Preserving explicit @v{v}.',
                    CrossVersionConflict, stacklevel=2,
                )
        return m.group(0)

    return _REF_PATTERN.sub(_sub, text)


def find_conflicts(text: str, manifest: Dict[str, int]) -> list:
    """Return list of (name, inline_version, manifest_version, position) for
    every inline NAME@v<M> where M disagrees with manifest[name]. Does not
    emit warnings. For testing + T3 policy consumer."""
    out = []
    for m in _REF_PATTERN.finditer(text):
        n, v = m.group('name'), int(m.group('version'))
        if n in manifest and manifest[n] != v:
            out.append({
                'name': n,
                'inline_version': v,
                'manifest_version': manifest[n],
                'position': m.start(),
            })
    return out


def manifest_frontmatter(manifest: Dict[str, int]) -> str:
    """Emit a minimal YAML manifest frontmatter block for a manifest dict.

    Canonical form (reproducible for round-trip tests):

        ---
        uses:
          NULL_BSWCD: 2
          PATTERN_30: 1
        ---

    Symbol names are sorted alphabetically. Empty manifest returns
    '---\\nuses: {}\\n---\\n'.
    """
    if not manifest:
        return '---\nuses: {}\n---\n'
    lines = ['---', 'uses:']
    for name in sorted(manifest):
        lines.append(f'  {name}: {manifest[name]}')
    lines.append('---\n')
    return '\n'.join(lines)


def round_trip_ok(canonical_bare: str, manifest: Dict[str, int]) -> Tuple[bool, str]:
    """Test: contract(expand(x, M), M) == x for x in canonical (bare) form.

    The invariant: bare-alias prose is the canonical session form. Expanding
    to @v<N> at commit time and then contracting back under the same manifest
    must yield the original bare text — modulo any inline @v<M> overrides
    that were present as deliberate disagreements (those are preserved by
    contract but emit CrossVersionConflict; the round-trip intentionally
    skips conflict cases for purity).

    Returns (ok, diagnostic).
    """
    # Skip round-trip over conflicts (they're tested separately)
    if find_conflicts(canonical_bare, manifest):
        return False, 'input has pre-existing conflicts; round-trip undefined'
    rt = contract_references(
        expand_references(canonical_bare, manifest, warn_conflicts=False),
        manifest, warn_conflicts=False,
    )
    if rt == canonical_bare:
        return True, 'round-trip stable'
    for i, (a, b) in enumerate(zip(canonical_bare, rt)):
        if a != b:
            ctx_a = canonical_bare[max(0, i - 20):i + 20]
            ctx_b = rt[max(0, i - 20):i + 20]
            return False, f'diverge at {i}: orig={ctx_a!r} rt={ctx_b!r}'
    return False, f'length differs: orig={len(canonical_bare)} rt={len(rt)}'
