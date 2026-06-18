"""
ingest.py

Load the FastAPI markdown docs and split them into chunks for retrieval. Each chunk keeps
its source file and the nearest heading, so answers can cite where they came from.

Chunking strategy: split on markdown headings first (so chunks respect document structure),
then further split any oversized section into overlapping windows. This keeps related text
together instead of cutting mid-explanation.
"""

import os
import re
import glob

import config


def _split_long(text, max_chars, overlap):
    """Split a long string into overlapping windows on whitespace boundaries."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end < len(text):
            # back up to the last space so we do not cut a word
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return [c for c in chunks if c]


def load_chunks(docs_dir=None):
    docs_dir = docs_dir or config.DOCS_DIR
    paths = sorted(glob.glob(os.path.join(docs_dir, "**", "*.md"), recursive=True))
    if not paths:
        raise SystemExit(f"No .md files found under {docs_dir}. Add the FastAPI docs there.")

    chunks = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        rel = os.path.relpath(path, docs_dir)

        # Split into sections at markdown headings (## or #), keeping the heading line.
        parts = re.split(r"(?m)^(#{1,6}\s.*)$", text)
        # re.split with a capture group interleaves [pre, heading, body, heading, body, ...]
        current_heading = "(top of page)"
        buffer = parts[0]
        sections = []
        if buffer.strip():
            sections.append((current_heading, buffer))
        for i in range(1, len(parts), 2):
            heading = parts[i].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            sections.append((heading.lstrip("#").strip(), body))

        for heading, body in sections:
            body = body.strip()
            if not body:
                continue
            for piece in _split_long(body, config.CHUNK_MAX_CHARS, config.CHUNK_OVERLAP):
                chunks.append({
                    "text": piece,
                    "source_file": rel,
                    "heading": heading,
                })

    return chunks


if __name__ == "__main__":
    cs = load_chunks()
    print(f"loaded {len(cs)} chunks from {config.DOCS_DIR}")
    # show a sample so you can eyeball chunk quality
    for c in cs[:3]:
        print(f"\n--- {c['source_file']} :: {c['heading']} ---")
        print(c["text"][:300])
