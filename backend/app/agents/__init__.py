"""Agent pipeline mirroring the DeepLearning.AI / Neo4j course, wrapped so the
end user only fills a short form (no conversation):

    intent -> file_suggestion -> schema_proposal -> graph_construction
           -> resolve (enhancement) -> critic (enhancement) -> graphrag

`resolve` and `critic` are additions over the course reference implementation,
which flags entity resolution and evaluation as not-yet-implemented.
"""
from __future__ import annotations

import hashlib
import re


def make_uid(label: str, name: str) -> str:
    """Deterministic node id from (label, name) so repeated mentions merge."""
    key = f"{label.strip().lower()}::{str(name).strip().lower()}"
    key = re.sub(r"\s+", " ", key)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
