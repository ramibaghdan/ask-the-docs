# Sample Answers

Real output from the system over the FastAPI documentation. Two in-scope questions with
grounded answers and citations, and one out-of-scope question that the system correctly
declines instead of guessing.

## 1. In scope: CORS middleware

```
Q: How do I add CORS middleware?

A: To add CORS middleware in FastAPI, you can use the CORSMiddleware. Here is an
   example:

   from fastapi import FastAPI
   from starlette.middleware.cors import CORSMiddleware

   app = FastAPI()

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   This configuration allows all origins, methods, and headers, and can be customized.

Sources:
  - middleware.md :: Other middlewares            (score 0.61)
  - cors.md :: More info                          (score 0.57)
  - cors.md :: Simple requests                    (score 0.57)
  - cors.md :: Use CORSMiddleware                 (score 0.54)
  - cors.md :: CORS (Cross-Origin Resource Sharing) (score 0.51)
```

Note: the answer's import line uses starlette.middleware.cors. FastAPI also re-exports
this as fastapi.middleware.cors, which is the form the docs usually show. Both work. This
is a small example of the kind of detail the groundedness evaluation is meant to catch.

## 2. In scope: path parameters

```
Q: How do I declare a path parameter?

A: You declare a path parameter in FastAPI using the same syntax as Python format
   strings:

   from fastapi import FastAPI

   app = FastAPI()

   @app.get("/items/{item_id}")
   async def read_item(item_id: str):
       return {"item_id": item_id}

   The path parameter item_id is passed to the function as the argument item_id.
   Requesting /items/foo returns {"item_id": "foo"}.

Sources:
  - path-params.md :: Path convertor                              (score 0.55)
  - path-params.md :: Path Parameters                             (score 0.54)
  - path-params-numeric-validations.md :: Path Parameters and Numeric Validations (score 0.53)
  - path-params.md :: Declare a path parameter                    (score 0.52)
  - path-params.md :: OpenAPI support                             (score 0.52)
```

## 3. Out of scope: correctly declines

```
Q: What is the capital of France?

A: The documentation provided does not cover the question.

Sources (all low similarity):
  - request-forms.md :: Recap        (score 0.12)
  - first-steps.md :: ...            (score 0.11)
  - body.md :: Use the model         (score 0.11)

[flagged: low retrieval confidence, needs human review]
```

The retrieval scores are far below the threshold, so the system does not try to answer
from unrelated text. It declines and flags the question for human review. This is the
behavior that keeps a documentation assistant from inventing answers.
