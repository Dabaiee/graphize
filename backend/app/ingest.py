"""Turn uploaded files into normalized `Source` records.

A Source is either:
  - structured   -> tabular: {columns: [...], rows: [ {col: val}, ... ]}
  - unstructured -> free text, split into overlapping chunks

The agents downstream never touch raw files — they reason over Source records.
"""
from __future__ import annotations

import csv
import io
import json
import os
from dataclasses import dataclass, field
from typing import Any

from . import config


@dataclass
class Source:
    name: str                       # original filename
    kind: str                       # "structured" | "unstructured"
    columns: list[str] = field(default_factory=list)
    rows: list[dict[str, Any]] = field(default_factory=list)   # structured
    chunks: list[str] = field(default_factory=list)            # unstructured

    def preview(self, n: int = 5) -> str:
        """A short, human/LLM-readable sample used for intent + schema proposal."""
        if self.kind == "structured":
            head = self.rows[:n]
            return (
                f"[structured] {self.name} — columns: {self.columns}; "
                f"{len(self.rows)} rows. Sample: {json.dumps(head, default=str)[:800]}"
            )
        joined = " ".join(self.chunks)[:800]
        return f"[unstructured] {self.name} — {len(self.chunks)} chunks. Sample: {joined!r}"


def _chunk_text(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    size, overlap = config.CHUNK_SIZE, config.CHUNK_OVERLAP
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return [c for c in chunks if c]


def _read_pdf(path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(path)
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _read_docx(path: str) -> str:
    import docx

    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _read_csv(raw: str) -> tuple[list[str], list[dict[str, Any]]]:
    reader = csv.DictReader(io.StringIO(raw))
    columns = list(reader.fieldnames or [])
    rows = [dict(r) for r in reader]
    return columns, rows


def parse_file(path: str, filename: str) -> Source:
    """Parse one uploaded file into a Source."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".csv":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            columns, rows = _read_csv(f.read())
        return Source(name=filename, kind="structured", columns=columns, rows=rows)

    if ext == ".json":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
        # A JSON array of flat objects reads as a table; anything else is text.
        if isinstance(data, list) and data and all(isinstance(x, dict) for x in data):
            columns = sorted({k for row in data for k in row.keys()})
            return Source(name=filename, kind="structured", columns=columns, rows=data)
        return Source(
            name=filename, kind="unstructured",
            chunks=_chunk_text(json.dumps(data, indent=2, default=str)),
        )

    if ext == ".pdf":
        return Source(name=filename, kind="unstructured", chunks=_chunk_text(_read_pdf(path)))

    if ext == ".docx":
        return Source(name=filename, kind="unstructured", chunks=_chunk_text(_read_docx(path)))

    # .txt, .md, and everything else: treat as plain text.
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return Source(name=filename, kind="unstructured", chunks=_chunk_text(f.read()))
