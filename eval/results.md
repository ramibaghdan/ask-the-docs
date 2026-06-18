# Evaluation Results

Questions: 20

## Aggregate

- Retrieval hit rate: 20/20 (100%)
- Groundedness: 20/20 (100%)
- Relevance: 20/20 (100%)
- Flagged for human review: 0/20

## Per question

| question | retrieval hit | grounded | relevant | flagged | top score |
|---|---|---|---|---|---|
| How do I declare a path parameter in FastAPI? | yes | yes | yes | no | 0.70 |
| How do I add numeric validations to a path parameter? | yes | yes | yes | no | 0.50 |
| How do I declare an optional query parameter? | yes | yes | yes | no | 0.57 |
| How do I add string validations like minimum length to a query parameter? | yes | yes | yes | no | 0.63 |
| How do I define a request body using a Pydantic model? | yes | yes | yes | no | 0.65 |
| How do I declare multiple body parameters in one request? | yes | yes | yes | no | 0.61 |
| How do I use nested models in a request body? | yes | yes | yes | no | 0.53 |
| How do I define a response model? | yes | yes | yes | no | 0.54 |
| How do I set a custom HTTP status code for a response? | yes | yes | yes | no | 0.60 |
| How do I handle errors and raise an HTTPException? | yes | yes | yes | no | 0.68 |
| How do I receive form data instead of JSON? | yes | yes | yes | no | 0.60 |
| How do I handle file uploads? | yes | yes | yes | no | 0.54 |
| How do I declare header parameters? | yes | yes | yes | no | 0.65 |
| How do I declare cookie parameters? | yes | yes | yes | no | 0.68 |
| How do I run tasks in the background after returning a response? | yes | yes | yes | no | 0.78 |
| How do I add metadata and configuration to a path operation? | yes | yes | yes | no | 0.79 |
| How do I structure a bigger application across multiple files? | yes | yes | yes | no | 0.54 |
| How do I add CORS middleware? | yes | yes | yes | no | 0.61 |
| How do I write tests for a FastAPI application? | yes | yes | yes | no | 0.65 |
| How do I use extra data types like UUID or datetime? | yes | yes | yes | no | 0.55 |

## Note

Groundedness and relevance are scored by an LLM-as-judge, which is a reasonable but imperfect evaluator. Treat these as a signal, not ground truth. The flagged column marks answers where retrieval similarity fell below the configured threshold and a human should review them.
