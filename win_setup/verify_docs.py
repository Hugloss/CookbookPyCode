#!/usr/bin/env python3
"""Validate WSL setup docs without network access or executing examples."""

from __future__ import annotations

import ast
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
LINK_RE = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^```([a-zA-Z0-9_-]*)[ \t]*$")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$")


def github_anchor(value: str) -> str:
    value = html.unescape(value).lower().replace("`", "")
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[^\w -]", "", value)
    return re.sub(r" +", "-", value.strip())


def parse_markdown(label: str, source: str, failures: list[str]):
    headings: set[str] = set()
    links: list[str] = []
    code_blocks: list[tuple[str, str, str]] = []
    language: str | None = None
    block_lines: list[str] = []
    for line in source.splitlines():
        marker = FENCE_RE.fullmatch(line)
        if marker:
            if language is None:
                language = marker.group(1).lower()
                block_lines = []
            else:
                code_blocks.append((label, language, "\n".join(block_lines) + "\n"))
                language = None
            continue
        if language is None:
            heading = HEADING_RE.match(line)
            if heading:
                anchor = github_anchor(heading.group(1))
                if anchor in headings:
                    failures.append(f"{label}: duplicate heading anchor {anchor}")
                headings.add(anchor)
            links.extend(LINK_RE.findall(line))
        else:
            block_lines.append(line)
    if language is not None:
        failures.append(f"{label}: unclosed Markdown code fence")
    return headings, links, code_blocks


def syntax_check(args: list[str], source: str, label: str, failures: list[str]):
    result = subprocess.run(args, input=source, text=True, capture_output=True, check=False)
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip()
        failures.append(f"{label}: syntax failure: {message}")


def main() -> int:
    failures: list[str] = []
    anchors: dict[Path, set[str]] = {}
    links: list[tuple[Path, str]] = []
    blocks: list[tuple[str, str, str]] = []
    notebook_count = 0

    for path in sorted(ROOT.glob("*.md")):
        heads, targets, code = parse_markdown(
            path.name, path.read_text(encoding="utf-8"), failures
        )
        anchors[path.resolve()] = heads
        links.extend((path, target) for target in targets)
        blocks.extend(code)

    for path in sorted(ROOT.glob("*.ipynb")):
        notebook_count += 1
        try:
            notebook = json.loads(path.read_text(encoding="utf-8"))
            if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
                raise ValueError("missing nbformat 4 or notebook cells")
            for index, cell in enumerate(notebook["cells"]):
                if not isinstance(cell.get("source"), list):
                    raise ValueError(f"cell {index} does not have an array source")
                source = "".join(cell["source"])
                if cell.get("cell_type") == "markdown":
                    _, targets, code = parse_markdown(
                        f"{path.name}:cell{index}", source, failures
                    )
                    links.extend((path, target) for target in targets)
                    blocks.extend(code)
                elif cell.get("cell_type") == "code" and not source.lstrip().startswith("%"):
                    try:
                        ast.parse(source)
                    except SyntaxError as exc:
                        failures.append(f"{path.name}:cell{index}: invalid Python: {exc}")
        except (ValueError, TypeError) as exc:
            failures.append(f"{path.name}: invalid notebook: {exc}")

    for origin, target in links:
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            continue
        relative_path, _, fragment = target.partition("#")
        dest = ((origin.parent / unquote(relative_path)) if relative_path else origin).resolve()
        if not dest.is_file():
            failures.append(f"{origin.name}: missing link destination {target}")
        elif fragment and dest.suffix == ".md":
            if unquote(fragment) not in anchors.get(dest, set()):
                failures.append(f"{origin.name}: missing Markdown anchor {target}")

    bash = shutil.which("bash") if os.name != "nt" else None
    pwsh = shutil.which("pwsh")
    ps_parser = (
        "$tokens=$null; $errors=$null; "
        "[System.Management.Automation.Language.Parser]::ParseInput("
        "[Console]::In.ReadToEnd(),[ref]$tokens,[ref]$errors) | Out-Null; "
        "if ($errors.Count) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }"
    )
    counts = {"bash": 0, "powershell": 0}
    for label, language, source in blocks:
        if language in ("bash", "sh") and bash:
            syntax_check([bash, "-n"], source, label, failures)
            counts["bash"] += 1
        if language in ("powershell", "pwsh") and pwsh:
            syntax_check(
                [pwsh, "-NoProfile", "-NonInteractive", "-Command", ps_parser],
                source,
                label,
                failures,
            )
            counts["powershell"] += 1

    if not bash and not pwsh:
        failures.append("Neither Bash nor PowerShell is available for parsing")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1

    print(
        f"PASS: {len(anchors)} Markdown docs, {notebook_count} notebooks, "
        f"{len(links)} links, {len(blocks)} code fences; "
        f"{counts['bash']} Bash and {counts['powershell']} PowerShell syntax checks."
    )
    if not pwsh:
        print("PowerShell syntax is checked by the Windows CI job.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
