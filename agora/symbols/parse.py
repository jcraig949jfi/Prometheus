"""Minimal frontmatter + body parser for symbol MD files.

No yaml dependency. Handles:
- Scalar values: strings, ints, null
- Lists: [a, b, c] (single-line bracketed, comma-separated)
- Nothing fancier. Symbols that need real YAML should be refactored.
"""
from pathlib import Path
import json
import re


def parse_md(md_path):
    """Parse a symbol MD file, return dict with frontmatter + body sections."""
    text = Path(md_path).read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError(f"{md_path}: missing frontmatter (must start with ---)")
    # split frontmatter
    end = text.find('\n---\n', 4)
    if end < 0:
        raise ValueError(f"{md_path}: unterminated frontmatter")
    fm_block = text[4:end]
    body = text[end + 5:]
    fm = _parse_frontmatter(fm_block)
    # split body into H2 sections
    sections = _split_sections(body)
    return {
        'frontmatter': fm,
        'body': body,
        'sections': sections,
        'name': fm.get('name'),
        'type': fm.get('type'),
        'version': int(fm.get('version', 0)),
        'references': fm.get('references', []),
    }


def load_symbol(md_path):
    """Convenience: parse and return a dict ready for JSON serialization.

    md_path is normalized to forward-slash (POSIX) form so Windows and
    POSIX agents produce byte-identical symbol JSON.
    """
    md_path_norm = Path(md_path).as_posix() if md_path else None
    p = parse_md(md_path)
    fm = p['frontmatter']
    # previous_version: preserve None if absent; coerce empty-string to None
    pv = fm.get('previous_version')
    if pv == '' or pv is None:
        pv = None
    else:
        try:
            pv = int(pv)
        except (TypeError, ValueError):
            pass
    return {
        'name': fm.get('name'),
        'type': fm.get('type'),
        'version': int(fm.get('version') or 0),
        'version_timestamp': fm.get('version_timestamp'),
        'immutable': fm.get('immutable'),
        'previous_version': pv,
        'precision': fm.get('precision'),
        'proposed_by': fm.get('proposed_by'),
        'promoted_commit': fm.get('promoted_commit'),
        'references': fm.get('references') or [],
        'redis_key': fm.get('redis_key'),
        'implementation': fm.get('implementation'),
        'sections': p['sections'],
        'md_path': md_path_norm,
    }


def _parse_frontmatter(block):
    """YAML-ish: scalars, [a, b, c] lists, and nested blocks via 2-space indent.

    Supports:
        key: value                      # scalar
        key: [a, b, c]                  # list
        key:                            # nested block
          subkey: value
          subkey2: value
        key:                            # nested list of strings
          - first item
          - second item
    """
    lines = block.splitlines()
    out = {}
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line or line.startswith('#'):
            i += 1
            continue
        if line[0] == ' ' or line[0] == '\t':
            # leftover indent; skip
            i += 1
            continue
        if ':' not in line:
            i += 1
            continue
        k, _, v = line.partition(':')
        k = k.strip()
        v = v.strip()

        if v == '':
            # Either a nested block (key: then indented key: value) or a nested list
            block_lines = []
            j = i + 1
            while j < len(lines):
                nl = lines[j]
                if nl.strip() == '':
                    block_lines.append(nl)
                    j += 1
                    continue
                if nl[0] in (' ', '\t'):
                    block_lines.append(nl)
                    j += 1
                else:
                    break
            if block_lines:
                # Detect list-style (- item) vs dict-style (key: value)
                stripped = [l.strip() for l in block_lines if l.strip()]
                if stripped and all(s.startswith('-') for s in stripped):
                    out[k] = [s.lstrip('- ').strip() for s in stripped]
                else:
                    nested = {}
                    for bl in block_lines:
                        bl_s = bl.strip()
                        if not bl_s or bl_s.startswith('#'):
                            continue
                        if ':' in bl_s:
                            nk, _, nv = bl_s.partition(':')
                            nested[nk.strip()] = _coerce(nv.strip())
                    out[k] = nested
            else:
                out[k] = None
            i = j
            continue

        if v.lower() == 'null':
            out[k] = None
        elif v.startswith('[') and v.endswith(']'):
            inner = v[1:-1].strip()
            out[k] = [x.strip() for x in inner.split(',') if x.strip()] if inner else []
        else:
            out[k] = _coerce(v)
        i += 1
    return out


def _coerce(v):
    """Coerce a string scalar to int / bool / None / str."""
    v = v.strip()
    if v == '' or v.lower() == 'null':
        return None
    if v.lower() == 'true':
        return True
    if v.lower() == 'false':
        return False
    if v.lstrip('-').isdigit():
        return int(v)
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v


def _split_sections(body):
    """Split the body into {section_heading: text} by H2 markers."""
    sections = {}
    current = None
    buffer = []
    for line in body.splitlines():
        m = re.match(r'^##\s+(.+)$', line)
        if m:
            if current is not None:
                sections[current] = '\n'.join(buffer).strip()
            current = m.group(1).strip()
            buffer = []
        else:
            if current is not None:
                buffer.append(line)
    if current is not None:
        sections[current] = '\n'.join(buffer).strip()
    return sections
