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
    """Convenience: parse and return a dict ready for JSON serialization."""
    p = parse_md(md_path)
    fm = p['frontmatter']
    return {
        'name': fm['name'],
        'type': fm['type'],
        'version': int(fm.get('version', 0)),
        'proposed_by': fm.get('proposed_by'),
        'promoted_commit': fm.get('promoted_commit'),
        'references': fm.get('references', []),
        'redis_key': fm.get('redis_key'),
        'implementation': fm.get('implementation'),
        'sections': p['sections'],
        'md_path': str(md_path),
    }


def _parse_frontmatter(block):
    """Tiny YAML-ish: key: value, and key: [a, b, c] for lists."""
    out = {}
    for line in block.splitlines():
        line = line.rstrip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            continue
        k, _, v = line.partition(':')
        k = k.strip()
        v = v.strip()
        if v == '' or v.lower() == 'null':
            out[k] = None
        elif v.startswith('[') and v.endswith(']'):
            inner = v[1:-1].strip()
            out[k] = [x.strip() for x in inner.split(',') if x.strip()] if inner else []
        elif v.lstrip('-').isdigit():
            out[k] = int(v)
        else:
            # strip surrounding quotes if any
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            out[k] = v
    return out


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
