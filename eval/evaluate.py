"""
evaluate.py

Run the RAG system over the evaluation question set and score it on three things:
  1. retrieval hit rate: did a correctly-sourced chunk appear in the retrieved set?
  2. groundedness: is the answer supported by the retrieved chunks? (LLM-as-judge)
  3. relevance: does the answer address the question? (LLM-as-judge)
Also reports how many answers were flagged for human review.

Writes a per-question table and an aggregate summary to eval/results.md.

LLM-as-judge is a reasonable but imperfect evaluator. The scores are a signal, not ground
truth. This is stated in the output.

Run: python eval/evaluate.py
"""

import os
import sys
import time
import yaml

# make src importable when run from the project root
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from openai import OpenAI
from dotenv import load_dotenv

import config
import ask

load_dotenv()

JUDGE_GROUNDED = (
    "You are checking whether an answer is fully supported by the provided documentation "
    "excerpts. Reply with one word: GROUNDED if every claim in the answer is supported by "
    "the excerpts, or UNSUPPORTED if the answer includes claims not found in the excerpts."
)
JUDGE_RELEVANT = (
    "You are checking whether an answer addresses the question asked. Reply with one word: "
    "RELEVANT if it answers the question, or OFFTOPIC if it does not."
)


def judge(client, system, content):
    resp = config.with_retries(lambda: client.chat.completions.create(
        model=config.JUDGE_MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": content}],
        temperature=0,
    ))
    return resp.choices[0].message.content.strip().upper()


def main():
    with open(os.path.join(os.path.dirname(__file__), "questions.yaml")) as f:
        questions = yaml.safe_load(f)

    client = OpenAI(api_key=config.get_api_key())
    rows = []
    hits = grounded = relevant = flagged = 0

    for q in questions:
        # small pause between questions to stay under low rate limits; the retry
        # helper in config handles any bursts that still hit the limit.
        time.sleep(config.EVAL_PACING_SECONDS)
        r = ask.answer_question(q["question"], client=client, return_context=True)

        # retrieval hit: expected source substring appears in any retrieved source_file
        expect = q.get("expect_source_contains", "")
        hit = any(expect in s["source_file"] for s in r["sources"]) if expect else False

        g = judge(client, JUDGE_GROUNDED,
                  f"Excerpts:\n{r['context']}\n\nAnswer:\n{r['answer']}")
        rel = judge(client, JUDGE_RELEVANT,
                    f"Question: {r['question']}\n\nAnswer:\n{r['answer']}")

        is_grounded = g.startswith("GROUNDED")
        is_relevant = rel.startswith("RELEVANT")
        hits += hit
        grounded += is_grounded
        relevant += is_relevant
        flagged += r["needs_human_review"]

        rows.append({
            "question": r["question"],
            "hit": hit,
            "grounded": is_grounded,
            "relevant": is_relevant,
            "flagged": r["needs_human_review"],
            "top_score": r["top_score"],
        })

    n = len(questions)
    lines = []
    lines.append("# Evaluation Results\n")
    lines.append(f"Questions: {n}\n")
    lines.append("## Aggregate\n")
    lines.append(f"- Retrieval hit rate: {hits}/{n} ({100*hits//n if n else 0}%)")
    lines.append(f"- Groundedness: {grounded}/{n} ({100*grounded//n if n else 0}%)")
    lines.append(f"- Relevance: {relevant}/{n} ({100*relevant//n if n else 0}%)")
    lines.append(f"- Flagged for human review: {flagged}/{n}\n")
    lines.append("## Per question\n")
    lines.append("| question | retrieval hit | grounded | relevant | flagged | top score |")
    lines.append("|---|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| {r['question']} | {'yes' if r['hit'] else 'no'} | "
            f"{'yes' if r['grounded'] else 'no'} | {'yes' if r['relevant'] else 'no'} | "
            f"{'yes' if r['flagged'] else 'no'} | {r['top_score']:.2f} |"
        )
    lines.append("\n## Note\n")
    lines.append(
        "Groundedness and relevance are scored by an LLM-as-judge, which is a reasonable "
        "but imperfect evaluator. Treat these as a signal, not ground truth. The flagged "
        "column marks answers where retrieval similarity fell below the configured "
        "threshold and a human should review them."
    )

    out = os.path.join(os.path.dirname(__file__), "results.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {out}")
    print(f"hit rate {hits}/{n}, grounded {grounded}/{n}, relevant {relevant}/{n}, flagged {flagged}/{n}")


if __name__ == "__main__":
    main()
