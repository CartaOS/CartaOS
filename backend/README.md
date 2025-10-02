# CartaOS Backend

This directory contains the Python/FastAPI backend for CartaOS.

## Setup

1.  **Navigate to the backend directory:**
    ```sh
    cd backend
    ```

2.  **Create and activate the virtual environment:**
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies using uv:**
    ```sh
    pip install uv
    uv pip install -r requirements.txt
    ```

## Running the Development Server

From within the `backend` directory, run:

```sh
cd app
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
