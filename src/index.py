"""
index.py

Embed the document chunks and save them to a local vector store. The store is a plain
numpy array of embeddings plus the chunk metadata, pickled to disk. For a corpus this
size, numpy cosine similarity is fast enough and keeps the project free of heavy vector
database dependencies.

Run: python src/index.py
"""

import os
import pickle

import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

import config
import ingest

load_dotenv()


def embed_texts(client, texts, model):
    """Embed a list of texts, batched, returning a numpy array."""
    out = []
    batch = 100
    for i in range(0, len(texts), batch):
        resp = config.with_retries(
            lambda chunk=texts[i:i + batch]: client.embeddings.create(model=model, input=chunk)
        )
        out.extend([d.embedding for d in resp.data])
    return np.array(out, dtype=np.float32)


def build():
    chunks = ingest.load_chunks()
    print(f"embedding {len(chunks)} chunks with {config.EMBED_MODEL} ...")

    client = OpenAI(api_key=config.get_api_key())
    vectors = embed_texts(client, [c["text"] for c in chunks], config.EMBED_MODEL)

    # normalize so dot product equals cosine similarity
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vectors = vectors / norms

    os.makedirs(config.INDEX_DIR, exist_ok=True)
    with open(config.INDEX_FILE, "wb") as f:
        pickle.dump({"vectors": vectors, "chunks": chunks}, f)

    print(f"saved {len(chunks)} chunks to {config.INDEX_FILE}")


if __name__ == "__main__":
    build()
