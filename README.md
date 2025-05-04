# STORM API Wrapper

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Dependency Management](https://img.shields.io/badge/dependencies-Poetry-orange.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) <!-- Assuming MIT, adjust if different -->

## Description

This project provides a FastAPI wrapper around the Stanford [STORM](https://github.com/stanford-oval/storm) project. It exposes STORM's knowledge generation capabilities via a simple REST API, processing requests and returning results in memory without writing intermediate or final files to disk (unlike the default STORM behavior). The entire application is containerized using Docker for easy deployment.

## Features

*   **FastAPI Interface:** Exposes STORM functionality through a clean `/storm` endpoint.
*   **Pydantic Validation:** Validates request inputs.
*   **In-Memory Processing:** Modified STORM integration to avoid writing output files to disk. Results are returned directly in the API response.
*   **JSON Response:** Returns generated articles as JSON.
*   **Streaming Support:** Supports streaming JSON responses via the `stream=true` query parameter.
*   **Configurable LLM & Search:** Currently configured to use Google Gemini and Serper Search.
*   **Dependency Management:** Uses Poetry for managing dependencies.
*   **Dockerized:** Includes a `Dockerfile` for building and running the application in a container.
*   **Testing:** Basic unit/integration tests using `pytest`.

## Project Structure

```
.
├── Dockerfile          # Docker configuration
├── poetry.lock         # Poetry lock file
├── pyproject.toml      # Poetry configuration and dependencies
├── README.md           # This file
├── .env.example        # Example environment variables file (create your own .env)
├── api/                # FastAPI application code
│   ├── __init__.py
│   ├── models.py       # Pydantic request/response models
│   └── routes.py       # API endpoint definitions
├── core/               # Core logic interacting with STORM
│   ├── __init__.py
│   ├── config.py       # Configuration loading (API keys)
│   └── gemini_storm_integration.py # Logic to run STORM with Gemini/Serper
├── storm/              # Submodule or copy of the original STORM project
│   └── ...
├── tests/              # Pytest tests
│   └── test_api.py
└── utils/              # Utility functions
    ├── __init__.py
    └── chunks.py       # Helper for streaming responses
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd storm-api
    ```

2.  **Install Poetry:** If you don't have Poetry installed, follow the instructions [here](https://python-poetry.org/docs/#installation).

3.  **Install Dependencies:**
    ```bash
    poetry install
    ```
    This command creates a virtual environment and installs all necessary dependencies specified in `pyproject.toml`.

4.  **Configure Environment Variables:**
    *   Create a `.env` file in the project root directory (where `pyproject.toml` is located).
    *   Add your API keys to the `.env` file. You can copy `.env.example` if it exists, or create it manually:
        ```dotenv
        # .env
        GOOGLE_API_KEY=your_google_gemini_api_key_here
        SERPER_API_KEY=your_serper_api_key_here
        ```
    *   Replace the placeholder values with your actual keys.

## Running the API Locally

Activate the Poetry virtual environment and run the FastAPI server using Uvicorn:

```bash
poetry shell
uvicorn api.routes:app --reload --host 0.0.0.0 --port 8000
```

*   `--reload`: Enables auto-reloading when code changes (useful for development).
*   `--host 0.0.0.0`: Makes the server accessible on your network (use `127.0.0.1` for local access only).
*   `--port 8000`: Specifies the port to run on.

The API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

## API Usage

### Endpoint: `/storm`

*   **Method:** `POST`
*   **Description:** Generates a knowledge article on the specified topic using STORM.
*   **Request Body (JSON):**
    ```json
    {
      "topic": "Your desired topic here",
      "stream": false
    }
    ```
    *   `topic` (string, required): The topic to generate an article about.
    *   `stream` (boolean, optional, default: `false`): If `true`, the response will be streamed as JSON chunks. If `false`, the full JSON response is returned at once.

*   **Example Request (using `curl`):**

    *   **Non-streaming:**
        ```bash
        curl -X POST "http://localhost:8000/storm" \
             -H "Content-Type: application/json" \
             -d '{"topic": "The history of artificial intelligence", "stream": false}'
        ```

    *   **Streaming:**
        ```bash
        curl -X POST "http://localhost:8000/storm" \
             -H "Content-Type: application/json" \
             -d '{"topic": "The future of renewable energy", "stream": true}' \
             --no-buffer
        ```
        (`--no-buffer` is recommended with `curl` for streaming).

*   **Success Response (Non-streaming, `stream: false`):**
    *   **Status Code:** `200 OK`
    *   **Body (JSON):**
        ```json
        {
          "article": "Generated article content..."
        }
        ```

*   **Success Response (Streaming, `stream: true`):**
    *   **Status Code:** `200 OK`
    *   **Body:** A stream of JSON chunks representing the final article object.

*   **Error Responses:**
    *   `400 Bad Request`: If the `topic` is empty.
    *   `500 Internal Server Error`: If there's an issue during STORM processing or configuration (e.g., missing API keys).

## Docker

1.  **Build the Docker Image:**
    ```bash
    docker build -t storm-api .
    ```

2.  **Run the Docker Container:**
    ```bash
    docker run -p 8000:8000 --env-file .env storm-api
    ```
    *   `-p 8000:8000`: Maps port 8000 on your host to port 8000 in the container.
    *   `--env-file .env`: Passes the environment variables from your local `.env` file into the container. Ensure your `.env` file is correctly populated.

The API will be accessible at `http://localhost:8000`.

## Testing

Tests are located in the `tests/` directory and use `pytest`.

1.  **Install Development Dependencies (if not already done):**
    ```bash
    poetry install --with dev
    ```

2.  **Run Tests:**
    ```bash
    poetry run pytest
