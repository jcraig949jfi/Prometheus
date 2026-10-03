"""Offline ASTRA document checks; never a scientific qualification certificate.

No recursive source discovery, network access, third-party imports, or source
execution. Only fixed intake files and package documents are parsed. Other local
link targets are opened solely for line counts, after exclusion checks.
"""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from urllib.parse import unquote, urlsplit


PACKAGE = Path("docs/phase3/design/ASTRA-6.0")
FREEZE = "eeeda08bb45757298b3cb21ee22d816b44388aef"
BASE = "9a83cec2c81e1bcb0291f7d7ead7bf0e4271d6cb"
REQUIRED = (
    "PHASE3_META_ANALYSIS.md", "REQUIREMENTS.md", "RSE_ARCHITECTURE.md",
    "ENGINE_PORTFOLIO.md", "SALVAGE_MATRIX.md", "OPEN_QUESTIONS.md",
    "ASSUMPTIONS.md", "FALSIFIERS.md",
)
DOCUMENTS = REQUIRED + (
    "README.md", "FAILURE_TO_GATE_MAP.md", "MVP_90_DAYS.md", "process/STAGE_I_FREEZE.md",
    "process/VALIDATION.md", "process/REVIEW_PACKET_2026-10-01.md",
    "evidence/SISYPHUS_AUDIT.md", "evidence/TANTALUS_AUDIT.md",
    "evidence/TITYOS_AUDIT.md", "evidence/IXION_AUDIT.md",
    "evidence/PRIOR_ART_AND_CATALOGUES.md",
)
PERSPECTIVES = {"sisyphus": (528, 51), "tantalus": (528, 46),
                "tityos": (348, 74), "ixion": (398, 76)}
INTAKE = tuple(
    f"docs/phase3/intake/{seat}/{name}"
    for seat in PERSPECTIVES
    for name in ("REPORT.md", "artifact_index.jsonl", "engine_index.jsonl")
) + (
    "docs/phase3/intake/tityos/failure_taxonomy.md",
    "docs/phase3/intake/tityos/ruler_inventory.jsonl",
    "docs/phase3/intake/ixion/inference_dependency_map.md",
    "docs/phase3/intake/ixion/institutional_timeline.md",
)
CARD_FIELDS = (
    "Name / working descriptor", "Precise scientific question",
    "Organism physics", "Developmental physics", "World physics",
    "Evolutionary/search pressure", "Measurement stack",
    "Known-positive qualification", "Known-negative qualification",
    "Known-neutral qualification", "Cheap baseline", "Causal intervention",
    "Transfer test", "Primary hallucination risk", "Primary false-negative risk",
    "Expected compute", "Expected inference use", "Expected energy profile",
    "Dominant cost", "Reusable components / category / modifications",
    "New components required", "Kill criteria", "Successful evidence means",
    "Claim ceiling", "Historical failure -> requirement -> intervention",
    "Considered alternative", "Decisive experiment",
)
DECISIONS = ("KEEP", "HARDEN", "EXTRACT", "REBUILD", "RETIRE",
             "HISTORICAL CONTROL", "UNKNOWN")
REQUIREMENT = re.compile(r"\bR-[A-Z0-9]+-[A-Z0-9]+\b")
MAX_BYTES = 32 * 1024 * 1024
# Findings are counts only: never return matched text or exception messages.
SECRET_PATTERNS = (
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
    r"\b(?:sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b",
    r"(?i)\b(?:authorization\s*[:=]\s*bearer|bearer)\s+[A-Za-z0-9._~-]{16,}",
    r"(?i)[\"']?(?:api[_-]?key|access[_-]?token|password|secret[_-]?key)"
    r"[\"']?\s*[:=]\s*[\"'][A-Za-z0-9+/_.=-]{16,}[\"']",
)


def canonical_lf(data):
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def digest(data):
    return hashlib.sha256(canonical_lf(data)).hexdigest()


class Validation:
    """Only trusted labels, numeric counts and fixed error codes leave a check."""

    def __init__(self):
        self.errors = []
        self.metrics = {}

    def fail(self, code, source, line=None):
        item = {"code": code, "source": source}
        if line is not None:
            item["line"] = line
        self.errors.append(item)

    def summary(self):
        return {"status": "FAIL" if self.errors else "PASS",
                "error_count": len(self.errors), "errors": self.errors,
                "metrics": self.metrics, "scientific_qualification": "NOT_VERIFIED"}


def guarded_path(root, path):
    """Reject lexical exclusions before stat/open, then reject symlink/junctions.

    Returns a reason code, not the untrusted destination or its contents.
    The caller supplies the trusted repository root; no glob or traversal occurs.
    """
    # Windows abspath can strip a trailing dot before our lexical checks.
    # Reject aliases on the supplied components before OS normalization.
    supplied = Path(path)
    components = supplied.parts[1:] if supplied.anchor else supplied.parts
    if any(part not in (".", "..") and
           (part != part.rstrip(" .") or ":" in part or re.search(r"~[0-9]", part))
           for part in components):
        return "UNSAFE_PATH_ALIAS"
    root = Path(os.path.abspath(root))
    path = Path(os.path.abspath(supplied))
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return "OUTSIDE_REPOSITORY"
    lowered = tuple(part.casefold() for part in parts)
    if any(part != part.rstrip(" .") or ":" in part or re.search(r"~[0-9]", part)
           for part in lowered):
        return "UNSAFE_PATH_ALIAS"
    for i, part in enumerate(lowered):
        if part == "roles" and i + 1 < len(parts):
            if lowered[i + 1] in ("dionysus", "epimetheus"):
                return "EXCLUDED_ROLE"
        if part == "design" and (i + 1 == len(parts) or lowered[i + 1] != "astra-6.0"):
            return "EXCLUDED_DESIGN"
        if (part.startswith(".env") or part in (".git", ".ssh", ".aws", ".azure")
                or re.search(r"secret|credential|password|cookie|session|token", part)
                or part in ("id_rsa", "id_ed25519", "id_ecdsa", ".netrc", ".npmrc")
                or part.endswith((".pem", ".key", ".p12", ".pfx", ".kdbx"))):
            return "EXCLUDED_SENSITIVE_PATH"
    current = root
    for part in parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            break
        except OSError:
            return "PATH_UNREADABLE"
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            return "EXCLUDED_REPARSE_POINT"
    return None


def read_allowed(root, path, result, source):
    reason = guarded_path(root, path)
    if reason:
        result.fail(reason, source)
        return None
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            result.fail("NOT_REGULAR_FILE", source)
            return None
        with path.open("rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            result.fail("FILE_TOO_LARGE", source)
            return None
        raw = canonical_lf(raw)
        text = raw.decode("utf-8")
    except FileNotFoundError:
        result.fail("MISSING_FILE", source)
        return None
    except (OSError, UnicodeError):
        result.fail("FILE_UNREADABLE", source)
        return None
    hits = sum(len(re.findall(pattern, text)) for pattern in SECRET_PATTERNS)
    if hits:
        result.metrics["secret_findings"] = result.metrics.get("secret_findings", 0) + hits
        result.fail("SECRET_PATTERN_DETECTED", source)
        return None
    return raw


def parse_jsonl(raw, result, source):
    records = []

    def reject_constant(_value):
        raise ValueError

    def unique_object(pairs):
        record = {}
        for key, value in pairs:
            if key in record:
                raise ValueError
            record[key] = value
        return record

    for number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line, parse_constant=reject_constant,
                                object_pairs_hook=unique_object)
            if not isinstance(record, dict):
                raise ValueError
        except (ValueError, RecursionError):
            result.fail("INVALID_JSONL_RECORD", source, number)
            continue
        records.append(record)
    return records


def ruler_aliases(records, result):
    source = "docs/phase3/intake/tityos/ruler_inventory.jsonl"
    ids = [row.get("ruler_id") for row in records]
    if any(not isinstance(key, str) or not re.fullmatch(r"TR-[0-9]{3}", key)
           for key in ids) or len(set(ids)) != len(ids):
        result.fail("INVALID_RULER_IDS", source)
        return {"status": "INVALID"}
    parent = {key: key for key in ids}

    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    available = False
    for row in records:
        available |= "same_instrument_as" in row
        aliases = row.get("same_instrument_as", [])
        if not isinstance(aliases, list):
            result.fail("INVALID_ALIAS_LIST", source)
            continue
        for alias in aliases:
            if not isinstance(alias, str) or alias not in parent:
                result.fail("INVALID_ALIAS_TARGET", source)
                continue
            parent[find(alias)] = find(row["ruler_id"])
    sizes = Counter(find(key) for key in parent)
    return {"status": "AVAILABLE" if available else "UNAVAILABLE",
            "groups": len(sizes) if available else None,
            "non_singleton_groups": sum(size > 1 for size in sizes.values()) if available else None}


def table_rows(text):
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("|"):
            yield number, [part.strip() for part in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def check_structure(documents, result):
    requirements = documents.get("REQUIREMENTS.md", "")
    ids = re.findall(r"^### (R-[A-Z]{3}-[0-9]{2}) \|", requirements, re.M)
    groups = re.findall(r"^## ([0-9]+)\. ", requirements, re.M)
    result.metrics["requirements"] = {"definitions": len(ids), "unique": len(set(ids)),
                                      "groups": len(groups)}
    if (len(ids) != 48 or len(set(ids)) != 48
            or groups != [str(i) for i in range(1, 17)]
            or len({key.split("-")[1] for key in ids}) != 16
            or any(n != 3 for n in Counter(key.split("-")[1] for key in ids).values())):
        result.fail("REQUIREMENT_CENSUS", "REQUIREMENTS.md")
    for name, text in documents.items():
        for number, line in enumerate(text.splitlines(), 1):
            if any(key not in ids for key in REQUIREMENT.findall(line)):
                result.fail("UNKNOWN_REQUIREMENT", name, number)

    portfolio = documents.get("ENGINE_PORTFOLIO.md", "")
    cards = list(re.finditer(r"^### Q([0-9]+)\. .+$", portfolio, re.M))
    counts = []
    if [m.group(1) for m in cards] != [str(i) for i in range(1, 7)]:
        result.fail("ENGINE_CARD_CENSUS", "ENGINE_PORTFOLIO.md")
    for i, card in enumerate(cards):
        end = cards[i + 1].start() if i + 1 < len(cards) else len(portfolio)
        # A following section is not part of the final card.
        body = re.split(r"^## ", portfolio[card.end():end], maxsplit=1, flags=re.M)[0]
        fields = [(cells[0], cells[1]) for _, cells in table_rows(body)
                  if len(cells) == 2 and cells[0] != "Required field"
                  and not re.fullmatch(r"[: -]+", cells[0])]
        counts.append(len(fields))
        if Counter(key for key, _ in fields) != Counter(CARD_FIELDS) or any(not value for _, value in fields):
            result.fail("ENGINE_CARD_FIELDS", "ENGINE_PORTFOLIO.md", portfolio[:card.start()].count("\n") + 1)
    result.metrics["engine_card_fields"] = counts

    failures = re.findall(r"^### (T[0-9]{2}) / FG[0-9]{2}:",
                          documents.get("FAILURE_TO_GATE_MAP.md", ""), re.M)
    result.metrics["failure_classes"] = len(failures)
    if failures != [f"T{i:02}" for i in range(1, 25)]:
        result.fail("FAILURE_CLASS_CENSUS", "FAILURE_TO_GATE_MAP.md")
    check_salvage(documents.get("SALVAGE_MATRIX.md", ""), result)
    main = documents.get("PHASE3_META_ANALYSIS.md", "")
    sections = re.findall(r"^## ([0-9]+)\. ", main, re.M)
    questions = re.findall(r"^### Q([0-9]+)\s*[-.:]", main, re.M)
    result.metrics["main_report"] = {"sections": len(sections), "answers": len(questions)}
    if sections != [str(i) for i in range(1, 26)]:
        result.fail("MAIN_SECTION_CENSUS", "PHASE3_META_ANALYSIS.md")
    if questions != [str(i) for i in range(1, 11)]:
        result.fail("MAIN_QUESTION_CENSUS", "PHASE3_META_ANALYSIS.md")


def check_salvage(text, result):
    ids, counts, declared = [], Counter(), {}
    axes = Counter()
    for number, cells in table_rows(text):
        if not cells:
            continue
        first = cells[0].replace("**", "")
        match = re.match(r"^(C[0-9]{2}) / ([SI]) / ", first)
        if match:
            ids.append(match[1])
            if len(cells) != 7 or cells[4] not in DECISIONS:
                result.fail("SALVAGE_ROW_FORMAT", "SALVAGE_MATRIX.md", number)
                continue
            counts[cells[4], match[2]] += 1
            axis = cells[6].split("/")
            if len(axis) != 3 or axis[0] not in ("Y", "N") or axis[1] not in ("core", "fragment", "none", "?") or axis[2] not in ("Y", "N", "?"):
                result.fail("SALVAGE_AXES", "SALVAGE_MATRIX.md", number)
            else:
                axes["conceptual_yes"] += axis[0] == "Y"
                axes["runtime_" + axis[1]] += 1
                axes["wrapper_" + axis[2]] += 1
        elif re.match(r"^C[0-9]", first):
            result.fail("SALVAGE_ROW_FORMAT", "SALVAGE_MATRIX.md", number)
        elif first in DECISIONS or first == "Total":
            try:
                values = [int(cell.replace("**", "")) for cell in cells[1:]]
                if len(values) != 3 or first in declared:
                    raise ValueError
                declared[first] = values
            except ValueError:
                result.fail("SALVAGE_SUMMARY_FORMAT", "SALVAGE_MATRIX.md", number)
    if Counter(ids) != Counter(f"C{i:02}" for i in range(1, 57)):
        result.fail("SALVAGE_ROW_CENSUS", "SALVAGE_MATRIX.md")
    decisions = {}
    for decision in DECISIONS:
        s, i = counts[decision, "S"], counts[decision, "I"]
        decisions[decision] = {"S": s, "I": i, "total": s + i}
        if declared.get(decision) != [s, i, s + i]:
            result.fail("SALVAGE_DECISION_ARITHMETIC", "SALVAGE_MATRIX.md")
    totals = [sum(counts[d, kind] for d in DECISIONS) for kind in ("S", "I")]
    if declared.get("Total") != totals + [sum(totals)]:
        result.fail("SALVAGE_TOTAL_ARITHMETIC", "SALVAGE_MATRIX.md")
    result.metrics["salvage"] = {"rows": len(ids), "decisions": decisions, "axes": dict(axes)}


def markdown_links(text, result, source):
    """Package subset: inline, full/collapsed references, known shortcuts.

    Fences and inline code are ignored. Balanced parentheses in inline URLs are
    supported; reference definitions may use <destinations> and quoted titles.
    """
    lines, fence = [], None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append((number, re.sub(r"(`+).*?\1", "", line)))
    definitions, bodies = {}, []
    normalize = lambda label: " ".join(label.casefold().split())
    destination = re.compile(r'^\s*(?:<([^>]+)>|(\S+?))(?:\s+[\"\'].*[\"\'])?\s*$')
    for number, line in lines:
        match = re.match(r"^\s{0,3}\[([^\]]+)\]:\s*(.*)$", line)
        if not match:
            bodies.append((number, line))
            continue
        target = destination.fullmatch(match[2])
        if target is None:
            result.fail("MALFORMED_LINK_DEFINITION", source, number)
            continue
        label = normalize(match[1])
        if label in definitions:
            result.fail("DUPLICATE_LINK_DEFINITION", source, number)
        definitions[label] = target[1] or target[2]
        yield number, definitions[label]
    for number, line in bodies:
        # Remove complete inline links before looking for reference links.
        inline = re.compile(r"!?\[[^\]\n]*\]\(")
        while True:
            match = inline.search(line)
            if match is None:
                break
            depth, end, escaped, angled = 1, match.end(), False, False
            start = end
            while end < len(line) and depth:
                char = line[end]
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "<":
                    angled = True
                elif char == ">":
                    angled = False
                elif not angled and char == "(":
                    depth += 1
                elif not angled and char == ")":
                    depth -= 1
                end += 1
            if depth:
                result.fail("MALFORMED_INLINE_LINK", source, number)
                line = line[:match.start()]
                break
            target = destination.fullmatch(line[start:end - 1])
            if target is None:
                result.fail("MALFORMED_INLINE_LINK", source, number)
            else:
                yield number, target[1] or target[2]
            line = line[:match.start()] + " " + line[end:]
        for match in re.finditer(r"!?\[([^\]]+)\]\[([^\]]*)\]", line):
            label = normalize(match[2] or match[1])
            if label not in definitions:
                result.fail("UNDEFINED_LINK_REFERENCE", source, number)
        # Known shortcut references are already checked via their definitions.
        # Unmatched [text] is ordinary prose, not necessarily a broken link.


def check_links(root, documents, result):
    counts = Counter()
    line_counts = {}
    for name, text in documents.items():
        source_path = root / PACKAGE / name
        for number, destination in markdown_links(text, result, name):
            counts["destinations"] += 1
            try:
                link = urlsplit(destination)
                if link.scheme.lower() in ("http", "https", "mailto"):
                    counts["external_not_fetched"] += 1
                    continue
                if link.scheme or link.netloc or link.query:
                    raise ValueError
                local = unquote(link.path).replace("\\", "/")
                if "\x00" in local or local.startswith("/") or re.match(r"^[A-Za-z]:", local):
                    raise ValueError
                path = Path(os.path.abspath(source_path.parent / local)) if local else source_path
            except ValueError:
                result.fail("UNSAFE_LINK", name, number)
                continue
            reason = guarded_path(root, path)
            if reason:
                counts["blocked_before_open"] += 1
                result.fail(reason, name, number)
                continue
            try:
                if not path.exists():
                    result.fail("MISSING_LINK_TARGET", name, number)
                    continue
                fragment = unquote(link.fragment)
                if not fragment:
                    counts["existence_checked"] += 1
                    continue
                if not (fragment.startswith("L") or re.match(r"^l[0-9]", fragment)):
                    counts["non_line_fragment_not_checked"] += 1
                    continue
                span = re.fullmatch(r"L([0-9]+)(?:-L?([0-9]+))?", fragment)
                if span is None:
                    result.fail("MALFORMED_LINE_RANGE", name, number)
                    continue
                start, end = int(span[1]), int(span[2] or span[1])
                if start < 1 or end < start:
                    result.fail("MALFORMED_LINE_RANGE", name, number)
                    continue
                if path not in line_counts:
                    info = path.stat()
                    if not stat.S_ISREG(info.st_mode):
                        result.fail("LINK_TARGET_NOT_FILE", name, number)
                        continue
                    if info.st_size > MAX_BYTES:
                        result.fail("LINK_TARGET_TOO_LARGE", name, number)
                        continue
                    # No decode, content search, imports, or further link traversal.
                    with path.open("rb") as handle:
                        line_counts[path] = sum(1 for _ in handle)
                if end > line_counts[path]:
                    result.fail("LINE_RANGE_OUT_OF_BOUNDS", name, number)
                else:
                    counts["line_ranges_checked"] += 1
            except (OSError, ValueError):
                result.fail("LINK_TARGET_UNREADABLE", name, number)
    result.metrics["links"] = dict(counts)


def git_output(root, arguments):
    completed = subprocess.run(
        ["git", "--no-pager", "-C", str(root)] + arguments,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=20, check=False,
    )
    if completed.returncode or len(completed.stdout) > MAX_BYTES:
        raise ValueError
    return canonical_lf(completed.stdout)


def frozen_sources(root):
    # Four fixed, read-only Git calls. No logs, global diffs or content searches.
    for commit in (FREEZE, BASE):
        resolved = git_output(root, ["rev-parse", "--verify", commit + "^{commit}"])
        if resolved.decode("ascii").strip() != commit:
            raise ValueError
    return {name: git_output(root, ["show", "--no-ext-diff", "--no-textconv",
                                   f"{FREEZE}:{PACKAGE.as_posix()}/{name}"])
            for name in ("REQUIREMENTS.md", "RSE_ARCHITECTURE.md")}


def check_freeze(documents, frozen, result):
    req = documents.get("REQUIREMENTS.md", "").encode("utf-8")
    arch = documents.get("RSE_ARCHITECTURE.md", "").encode("utf-8")
    original = canonical_lf(frozen["RSE_ARCHITECTURE.md"])
    req_ok = canonical_lf(req) == canonical_lf(frozen["REQUIREMENTS.md"])
    original_ok = len(original.splitlines()) == 201
    arch = canonical_lf(arch)
    arch_ok = (original_ok and arch.startswith(original)
               and (original.endswith(b"\n") or arch == original
                    or arch[len(original):].startswith(b"\n")))
    if not req_ok:
        result.fail("REQUIREMENTS_FREEZE_CHANGED", "REQUIREMENTS.md")
    if not arch_ok:
        result.fail("ARCHITECTURE_FREEZE_CHANGED", "RSE_ARCHITECTURE.md")
    result.metrics["freeze"] = {"requirements_equal_lf": req_ok,
                                "architecture_original_201_line_prefix": arch_ok,
                                "architecture_appendix_lines": max(0, len(arch.splitlines()) - 201)}


def validate(root):
    root = Path(os.path.abspath(root))
    result = Validation()
    result.metrics["secret_findings"] = 0
    documents, document_hashes, sources, records = {}, {}, [], {}
    for name in DOCUMENTS:
        raw = read_allowed(root, root / PACKAGE / name, result, name)
        if raw is not None:
            documents[name] = raw.decode("utf-8")
            document_hashes[name] = digest(raw)
            if not raw.strip():
                result.fail("EMPTY_DOCUMENT", name)
    result.metrics["required_documents"] = {"expected": 8,
                                            "readable": sum(name in documents for name in REQUIRED)}
    check_structure(documents, result)
    check_links(root, documents, result)
    for source in INTAKE:
        raw = read_allowed(root, root / source, result, source)
        entry = {"path": source, "status": "READ" if raw is not None else "UNAVAILABLE"}
        if raw is not None:
            entry.update(sha256_lf=digest(raw), bytes_lf=len(raw), lines=len(raw.splitlines()))
            if source.endswith(".jsonl"):
                records[source] = parse_jsonl(raw, result, source)
                entry["records"] = len(records[source])
        sources.append(entry)
    census, totals = {}, Counter()
    for seat, expected in PERSPECTIVES.items():
        census[seat] = {}
        for index, kind in enumerate(("artifact", "engine")):
            source = f"docs/phase3/intake/{seat}/{kind}_index.jsonl"
            count = len(records[source]) if source in records else None
            census[seat][kind] = count
            if count != expected[index]:
                result.fail("INTAKE_RECORD_COUNT", source)
            if count is not None:
                totals[kind] += count
    ruler_source = "docs/phase3/intake/tityos/ruler_inventory.jsonl"
    rulers = records.get(ruler_source)
    if rulers is None or len(rulers) != 152:
        result.fail("RULER_RECORD_COUNT", ruler_source)
    result.metrics["intake"] = {"perspectives": census, "parsed_totals": dict(totals),
                                "expected_totals": {"artifact": 1802, "engine": 247},
                                "ruler_records": len(rulers) if rulers is not None else None,
                                "aliases": ruler_aliases(rulers, result) if rulers is not None else {"status": "UNAVAILABLE"}}
    frozen_hashes = {}
    try:
        frozen = frozen_sources(root)
        check_freeze(documents, frozen, result)
        frozen_hashes = {name: digest(raw) for name, raw in frozen.items()}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        result.fail("FREEZE_GIT_UNAVAILABLE", "freeze")
    manifest = {"schema_version": 1, "normalization": "UTF-8 bytes; CRLF/CR to LF; no other changes",
                "freeze_commit": FREEZE, "base_commit": BASE,
                "frozen_sha256_lf": frozen_hashes, "sources": sources,
                "document_sha256_lf": document_hashes,
                "scientific_qualification": "NOT_VERIFIED"}
    return result, manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).absolute().parents[5])
    parser.add_argument("--write-manifest", action="store_true",
                        help="Write only evidence/source_manifest.json; never edit Markdown")
    args = parser.parse_args(argv)
    root = Path(os.path.abspath(args.root))
    result, manifest = validate(root)
    target = root / PACKAGE / "evidence/source_manifest.json"
    reason = guarded_path(root, target)
    if reason:
        result.fail(reason, "evidence/source_manifest.json")
    elif args.write_manifest:
        try:
            # The package/evidence directory must already exist; no arbitrary mkdir.
            manifest["validation"] = result.summary()
            target.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        except OSError:
            result.fail("MANIFEST_WRITE_FAILED", "evidence/source_manifest.json")
    else:
        raw = read_allowed(root, target, result, "evidence/source_manifest.json")
        if raw is not None:
            try:
                stored = json.loads(raw)
                if not isinstance(stored, dict) or any(stored.get(key) != value for key, value in manifest.items()):
                    result.fail("MANIFEST_MISMATCH", "evidence/source_manifest.json")
            except (ValueError, RecursionError):
                result.fail("MANIFEST_INVALID_JSON", "evidence/source_manifest.json")
    print(json.dumps(result.summary(), indent=2, sort_keys=True))
    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())