# Ask the Docs

A retrieval-augmented question answering system over the FastAPI documentation, with an
evaluation harness that measures retrieval quality, answer groundedness, and flags
low-confidence answers for human review.

The answering half is the common part. The evaluation half is the point: it measures
whether the answers can be trusted, instead of assuming they can.

## What this project demonstrates

This is meant to show a capability, not a domain. It builds an AI system that makes
information easy to ask questions against, and then checks whether the answers can
actually be trusted: retrieval, grounded answers with citations, an evaluation harness,
and a flag that routes low-confidence answers to a human. FastAPI documentation is just a
clean, public set of docs to build it on. The same approach works on an internal knowledge
base, support or policy content, or any set of documents a team needs to search and rely on.

It goes with a separate data-integration project that maps public biomedical sources into a
Biolink knowledge graph. The domains are different on purpose. Both come down to the same
work: taking scattered or inconsistent information and turning it into something structured,
usable, and checkable.

## Demo

```
Q: How do I declare a path parameter?

A: You declare a path parameter using the same syntax as Python format strings:

   @app.get("/items/{item_id}")
   async def read_item(item_id: str):
       return {"item_id": item_id}

Sources:
  - path-params.md :: Declare a path parameter   (score 0.52)
  - path-params.md :: Path Parameters            (score 0.54)
```

On an out-of-scope question ("What is the capital of France?") the system declines instead
of guessing, and flags the question for human review, because retrieval similarity is far
below the threshold.

On the 20-question evaluation set: retrieval hit rate 20/20, groundedness 20/20, relevance
20/20. See [eval/results.md](eval/results.md). More examples, including the out-of-scope
refusal, are in [examples/sample_answers.md](examples/sample_answers.md).

## Why this exists

Teams increasingly put an LLM in front of their documentation so people can ask questions
instead of searching. The hard part is not building the assistant, it is knowing whether
its answers are correct and grounded in the source material. This project builds both: a
working documentation assistant, and a way to measure its answer quality and route weak
answers to a human.

## Two pillars

### 1. Retrieval-augmented answering
- Loads the FastAPI Markdown docs and splits them into chunks that respect headings.
- Embeds the chunks and stores them in a local vector store (numpy, no external database).
- For a question, retrieves the most similar chunks and asks the model to answer using
  only those chunks, returning the answer with the source file and heading it used.
- Flags an answer for human review when the best retrieval similarity is below a threshold.

### 2. Evaluation harness
- A question set with the doc section expected to answer each question.
- Scores the system on retrieval hit rate (did the right section get retrieved),
  groundedness (is the answer supported by the retrieved chunks), and relevance (does it
  address the question). Groundedness and relevance use an LLM-as-judge.
- Reports how many answers were flagged for human review.
- Writes a per-question table and aggregate summary to eval/results.md.

## Repository layout

```
ask-the-docs/
├── README.md
├── requirements.txt
├── .env.example            # OPENAI_API_KEY= (copy to .env, add your key)
├── data/
│   ├── docs/               # the FastAPI Markdown subset
│   └── README.md           # source, commit, license
├── src/
│   ├── config.py           # models, chunking, retrieval settings
│   ├── ingest.py           # load and chunk the docs
│   ├── index.py            # embed chunks, build the vector store
│   └── ask.py              # retrieve, answer, cite, flag
├── eval/
│   ├── questions.yaml      # evaluation questions + expected sources
│   ├── evaluate.py         # run, score, write results
│   └── results.md          # generated metrics (committed)
└── examples/
    └── sample_answers.md   # example answers with citations
```

## Run it

From the project root:

```
pip install -r requirements.txt
cp .env.example .env          # then add your OpenAI API key to .env

# add the FastAPI docs subset to data/docs/ (see data/README.md)

python src/index.py                                   # build the vector store
python src/ask.py "How do I declare a path parameter?"  # ask a question
python eval/evaluate.py                               # run the evaluation
```

## Evaluation results

See [eval/results.md](eval/results.md) for the metrics table. Groundedness and relevance
are scored by an LLM-as-judge, which is a reasonable but imperfect evaluator, so the scores
are a signal rather than ground truth. The flagged column marks answers where retrieval was
weak and a human should review them.

## Data and license

Runs over a subset of the FastAPI documentation (MIT licensed). See
[data/README.md](data/README.md) for source, commit, and attribution.

## Limitations and next steps

- Small corpus. This is a demonstration, not a production-scale index.
- The 20-question set is all in-scope and clearly covered by the docs, so a perfect score
  reflects a straightforward set. A harder, adversarial question set (ambiguous phrasing,
  answers spanning multiple pages, near-miss out-of-scope questions) would be a stronger
  stress test and is the natural next step.
- LLM-as-judge is imperfect; a human-labeled evaluation set would be stronger.
- Possible extensions: hybrid keyword and vector retrieval, reranking, a small web UI, and
  caching of embeddings.

## Engineering notes

- During development the evaluation caught two questions (CORS, testing) that the system
  declined to answer even though retrieval returned the correct pages. After ruling out
  retrieval depth and chunk size, the cause was an over-strict generation prompt. Loosening
  it to answer from relevant excerpts, while keeping the out-of-scope refusal, fixed it.
  This measure, diagnose, fix, re-measure loop is the point of the evaluation pillar.
- API calls use retry with exponential backoff and the evaluation paces its requests, so
  the pipeline tolerates rate limits instead of crashing.
