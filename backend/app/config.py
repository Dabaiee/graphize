"""Central configuration, read from environment (set by docker-compose)."""
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("FASTGRAPH_MODEL", "claude-opus-4-8")

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "fastgraph")

UPLOAD_DIR = os.environ.get("FASTGRAPH_UPLOAD_DIR", "/data/uploads")

# Chunking for unstructured text.
CHUNK_SIZE = 1200          # characters
CHUNK_OVERLAP = 150        # characters

# Fan-out cap for parallel extraction calls.
MAX_EXTRACTION_CONCURRENCY = 6
