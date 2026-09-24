from fastapi import FastAPI

app = FastAPI(
    title="EBRAINS Research Data Explorer",
    description=(
        "A research software prototype for retrieving, normalizing, "
        "indexing, and exposing scientific metadata from EBRAINS."
    ),
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
