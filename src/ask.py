"""
ask.py

Answer a question from the indexed FastAPI docs. Retrieves the most similar chunks, asks
the model to answer using only those chunks, and returns the answer with its sources. If
retrieval is weak, the answer is flagged as needing human review.

Run: python src/ask.py "How do I define a query parameter?"
"""

import sys
import pickle

import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

import config

load_dotenv()

SYSTEM_PROMPT = (
    "You answer questions about the FastAPI web framework using the provided documentation "
    "excerpts as your source. Base your answer on the excerpts and do not add facts from "
    "outside knowledge. If the excerpts are relevant to the question, answer it and include "
    "any code shown in the excerpts. Only reply that the documentation provided does not "
    "cover the question when the excerpts are clearly unrelated to it. Keep answers concise."
)


def load_store():
    try:
        with open(config.INDEX_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        raise SystemExit("No index found. Run: python src/index.py")


def embed_query(client, text):
    resp = config.with_retries(
        lambda: client.embeddings.create(model=config.EMBED_MODEL, input=[text])
    )
    v = np.array(resp.data[0].embedding, dtype=np.float32)
    n = np.linalg.norm(v)
    return v / n if n else v


def retrieve(store, qvec, top_k):
    sims = store["vectors"] @ qvec          # cosine sim (vectors are normalized)
    idx = np.argsort(-sims)[:top_k]
    return [(store["chunks"][i], float(sims[i])) for i in idx]


def answer_question(question, client=None, return_context=False):
    store = load_store()
    client = client or OpenAI(api_key=config.get_api_key())

    qvec = embed_query(client, question)
    hits = retrieve(store, qvec, config.TOP_K)
    top_score = hits[0][1] if hits else 0.0

    context = "\n\n".join(
        f"[{i+1}] ({h['source_file']} :: {h['heading']})\n{h['text']}"
        for i, (h, _) in enumerate(hits)
    )
    user_prompt = f"Documentation excerpts:\n\n{context}\n\nQuestion: {question}"

    resp = config.with_retries(lambda: client.chat.completions.create(
        model=config.GEN_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    ))
    answer = resp.choices[0].message.content.strip()

    needs_review = top_score < config.MIN_RETRIEVAL_SCORE
    sources = [{"source_file": h["source_file"], "heading": h["heading"], "score": s}
               for h, s in hits]

    result = {
        "question": question,
        "answer": answer,
        "sources": sources,
        "top_score": top_score,
        "needs_human_review": needs_review,
    }
    if return_context:
        result["context"] = context
    return result


def _print(result):
    print(f"\nQ: {result['question']}\n")
    print(result["answer"])
    print("\nSources:")
    for s in result["sources"]:
        print(f"  - {s['source_file']} :: {s['heading']}  (score {s['score']:.2f})")
    if result["needs_human_review"]:
        print("\n[flagged: low retrieval confidence, needs human review]")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python src/ask.py "your question"')
    _print(answer_question(" ".join(sys.argv[1:])))
