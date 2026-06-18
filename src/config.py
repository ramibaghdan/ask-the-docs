"""
config.py

One place for the knobs: model names, chunking, retrieval depth, paths. Keeping these
here means the rest of the code reads cleanly and a reviewer can see every setting at once.
"""

import os
import time


def with_retries(fn, tries=6, base_delay=2.0):
    """Call fn() and retry on transient errors (rate limits, brief network issues).

    Waits base_delay, then doubles each time (2s, 4s, 8s, ...). Raises the last error
    if all tries fail. This keeps the pipeline from crashing on a momentary 429.
    """
    last = None
    for attempt in range(tries):
        try:
            return fn()
        except Exception as e:
            msg = str(e).lower()
            transient = ("rate limit" in msg or "429" in msg or "timeout" in msg
                         or "temporarily" in msg or "overloaded" in msg)
            last = e
            if not transient or attempt == tries - 1:
                raise
            wait = base_delay * (2 ** attempt)
            print(f"  transient API error, retrying in {wait:.0f}s "
                  f"(attempt {attempt + 1}/{tries})")
            time.sleep(wait)
    raise last

# Provider: "openai" is the default. Generation and embeddings both go through OpenAI.
PROVIDER = os.getenv("DOCS_PROVIDER", "openai")

# Models
EMBED_MODEL = "text-embedding-3-small"     # OpenAI embedding model
GEN_MODEL = "gpt-4o-mini"                   # answer generation
JUDGE_MODEL = "gpt-4o-mini"                 # LLM-as-judge for evaluation

# Chunking
CHUNK_MAX_CHARS = 2200      # rough target size of a chunk
CHUNK_OVERLAP = 250         # characters of overlap between consecutive chunks

# Retrieval
TOP_K = 5                   # how many chunks to retrieve per question

# Seconds to wait between questions during evaluation. On a low rate-limit tier set this
# higher (for example 7) so the burst of calls stays under the limit. On a higher tier 0
# is fine. The retry helper covers anything that still trips the limit.
EVAL_PACING_SECONDS = 1.0

# Low-confidence flag: if the best retrieval similarity is below this, mark the answer
# as needing human review. Tunable; documented as a heuristic, not a guarantee.
MIN_RETRIEVAL_SCORE = 0.30

# Paths (relative to the project root; run scripts from the root)
DOCS_DIR = "data/docs"
INDEX_DIR = "index"             # where the built vector store is saved (git-ignored)
INDEX_FILE = "index/store.pkl"  # simple on-disk store

# API key is read from the environment (see .env.example). Never hard-code it.
def get_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key, "
            "or export it in your shell."
        )
    return key
