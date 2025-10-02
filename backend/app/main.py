from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint for the API."""
    return {"Hello": "World"}


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify service status."""
    return {"status": "ok"}
