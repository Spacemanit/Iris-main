#!/usr/bin/env python3
"""Initialize or locally audit a review. No network or third-party packages."""

import argparse
import json
import re
from pathlib import Path

KEY = r"[A-Za-z0-9][A-Za-z0-9_-]*"


def initialize(folder):
    folder.mkdir(parents=True, exist_ok=True)
    template = Path(__file__).resolve().parents[1] / "assets" / "review-template.md"
    files = {
        "brief.md": "# Review brief\n\nQuestion:\nAudience:\nScope/date range:\n"
        "Inclusion criteria:\nExclusion criteria:\nLength/style:\nAssumptions:\n",
        "search-log.md": "# Search log\n\n"
        "| Date | Tool/site | Exact query | Coverage/decisions |\n"
        "| --- | --- | --- | --- |\n",
        "evidence.json": "[]\n",
        "review.md": template.read_text(encoding="utf-8"),
    }
    for name, content in files.items():
        path = folder / name
        try:
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)
        except FileExistsError:
            print(f"Kept existing {name}")
        else:
            print(f"Created {name}")
    return 0


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def normalize_doi(value):
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I).lower()


def check(folder):
    errors, warnings = [], []
    try:
        ledger = json.loads((folder / "evidence.json").read_text(encoding="utf-8-sig"))
        draft = (folder / "review.md").read_text(encoding="utf-8-sig")
    except (OSError, ValueError) as exc:
        print(f"ERROR: Cannot read review inputs: {exc}")
        return 1
    if not isinstance(ledger, list):
        print("ERROR: evidence.json must contain a list of paper objects.")
        return 1

    # Remove template comments and fenced code examples from the citation scan.
    prose = re.sub(r"<!--.*?-->", "", draft, flags=re.S)
    prose = re.sub(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$", "", prose, flags=re.M | re.S)
    sections = re.split(r"^##\s+References\s*$", prose, maxsplit=1, flags=re.M | re.I)
    body = sections[0]
    bibliography = sections[1] if len(sections) == 2 else ""
    if len(sections) != 2:
        errors.append("Missing '## References' section.")
    cited = set()
    for group in re.findall(r"\[([^\]\n]*@[^\]\n]*)\]", body):
        parts = group.split(";")
        if any(not re.fullmatch(rf"\s*@{KEY}\s*", part) for part in parts):
            errors.append(f"Malformed working citation: [{group}]")
        cited.update(re.findall(rf"@({KEY})", group))
    if not cited:
        errors.append("Draft has no working citations; use [@Key] markers.")
    reference_keys = re.findall(rf"^\s*-\s+\*\*({KEY})\*\*\s*:", bibliography, flags=re.M)
    refs = set(reference_keys)
    for key in refs:
        if reference_keys.count(key) > 1:
            errors.append(f"Duplicate bibliography key: {key}")

    papers, identities = {}, {}
    for index, paper in enumerate(ledger, 1):
        if not isinstance(paper, dict):
            errors.append(f"Ledger item {index} must be an object.")
            continue
        key = paper.get("key")
        if not isinstance(key, str) or not re.fullmatch(KEY, key):
            errors.append(f"Ledger item {index} has an invalid key.")
            continue
        if key in papers:
            errors.append(f"Duplicate ledger key: {key}")
        papers[key] = paper
        title = paper.get("title", "")
        if not nonempty(title):
            errors.append(f"{key}: missing title.")
        url, source_path = paper.get("url", ""), paper.get("source_path", "")
        if not nonempty(url) and not nonempty(source_path):
            errors.append(f"{key}: provide a source URL or supplied source_path.")
        if nonempty(url) and not re.match(r"^https?://[^/\s]+", url):
            errors.append(f"{key}: source URL must start with http:// or https://.")
        if nonempty(source_path):
            path = Path(source_path)
            if not path.is_absolute():
                path = folder / path
            if not path.is_file():
                errors.append(f"{key}: supplied source_path does not exist: {source_path}")
        doi = paper.get("doi", "")
        if not isinstance(doi, str):
            errors.append(f"{key}: DOI must be a string (blank when unknown).")
            doi = ""
        doi = normalize_doi(doi)
        if doi and not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
            errors.append(f"{key}: malformed DOI syntax.")
        normalized_title = re.sub(r"[\W_]+", "", title.casefold()) if isinstance(title, str) else ""
        for kind, identity in (("DOI", doi), ("title", normalized_title)):
            if identity:
                previous = identities.setdefault((kind, identity), key)
                if previous != key:
                    warnings.append(f"Possible duplicate {kind}: {previous} and {key}; check versions.")
        if key not in cited:
            continue  # Uncited candidates may still be awaiting extraction.
        authors = paper.get("authors")
        if not isinstance(authors, list) or not authors or not all(nonempty(a) for a in authors):
            errors.append(f"{key}: cited paper needs an author-name list.")
        year = paper.get("year")
        if type(year) is not int or not 1000 <= year <= 9999:
            errors.append(f"{key}: cited paper needs a four-digit integer year.")
        if paper.get("metadata_verified") is not True:
            errors.append(f"{key}: cited paper's metadata is not marked verified.")
        if paper.get("access") not in ("full-text", "abstract"):
            errors.append(f"{key}: cited paper needs full-text or abstract evidence access.")
        elif paper["access"] == "abstract":
            warnings.append(f"{key}: abstract-only evidence; restrict claims accordingly.")
        if paper.get("publication_status") not in ("published", "preprint", "unknown"):
            errors.append(f"{key}: invalid publication_status.")
        elif paper["publication_status"] != "published":
            warnings.append(f"{key}: publication status is {paper['publication_status']}.")
        for field in ("method_context", "notes"):
            if not nonempty(paper.get(field)):
                errors.append(f"{key}: cited paper needs {field}.")
        for field in ("themes", "limitations"):
            value = paper.get(field)
            if not isinstance(value, list) or not value or not all(nonempty(item) for item in value):
                errors.append(f"{key}: cited paper needs a nonempty {field} list (note unknowns explicitly).")
        findings = paper.get("findings")
        if not isinstance(findings, list) or not findings:
            errors.append(f"{key}: cited paper has no extracted findings.")
        elif any(not isinstance(f, dict) or not nonempty(f.get("claim"))
                 or not nonempty(f.get("locator")) for f in findings):
            errors.append(f"{key}: every finding needs a claim and source locator.")

    for key in sorted(cited - papers.keys()):
        errors.append(f"Citation has no ledger entry: {key}")
    for key in sorted(cited - refs):
        errors.append(f"Citation has no bibliography entry: {key}")
    for key in sorted(refs - cited):
        errors.append(f"Bibliography entry is not cited: {key}")
    for key in sorted(refs - papers.keys()):
        errors.append(f"Bibliography entry has no ledger record: {key}")
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    print(f"Local audit: {len(cited)} cited papers, {len(errors)} errors, {len(warnings)} warnings.")
    print("Source truth and claim support require a separate manual check.")
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "check"))
    parser.add_argument("folder", type=Path, help="Folder containing the review files")
    args = parser.parse_args()
    try:
        return initialize(args.folder) if args.command == "init" else check(args.folder)
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
