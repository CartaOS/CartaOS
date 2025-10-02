# CartaOS Backend

This directory contains the Python/FastAPI backend for CartaOS.

## Setup

Assuming `uv` is installed on your system.

1.  **Navigate to the backend directory:**
    ```sh
    cd backend
    ```

2.  **Create and activate the virtual environment:**
    ```sh
    uv venv
    source .venv/bin/activate
    ```

3.  **Sync dependencies:**
    ```sh
    uv pip sync requirements.txt
    ```

## Running the Development Server

From within the `backend` directory, run:

```sh
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
