# AI Query Assistant — Backend

This repository contains the backend API and container orchestration for the AI Query Assistant. It provides a containerized environment that serves as the foundation for the entire application, including the API Gateway, the Python-powered intelligence layer, and the static UI assets.

- **Backend + Orchestration** (this repository): [ai-assistant-backend](https://github.com/kotalabhay/ai-assistant-backend)
- **Frontend UI**: [ai-assistant-ui](https://github.com/kotalabhay/ai-assistant-ui)

---

## Architecture Overview

The system is architected as a set of three isolated containers coordinated via Docker Compose. All client-side traffic enters through a single public-facing entry point (the Gateway) which handles routing to the appropriate internal service.

```text
Browser
  └── Gateway (nginx:1.25-alpine, port 80)
        ├── /             → UI (nginx, static React build)
        └── /api/v1/      → Backend (FastAPI, port 8000)
```

1.  **Gateway**: A standalone Nginx reverse proxy. It ensures the browser only communicates with a single origin, eliminating CORS complexity and providing a single layer for future SSL termination and load balancing.
2.  **UI**: A production-optimized Nginx container serving a pre-built React 19 application. It has no direct exposure to the host network.
3.  **Backend**: A FastAPI application running on Python 3.12. It handles authentication, input validation, and asynchronous communication with the Google Gemini API.

---

## Technology Decisions

### Why FastAPI?
FastAPI was chosen for its native support for asynchronous programming (`async/await`), which is critical when dealing with high-latency LLM calls. Its automatic integration with Pydantic for request validation ensures that the API contract is strictly followed, while the auto-generated OpenAPI (Swagger) documentation simplifies frontend integration and testing.

### Why an Nginx Gateway?
Using a dedicated Gateway container separates the routing logic from the application logic. This pattern mirrors production-grade deployments where a Load Balancer or Reverse Proxy sits in front of internal microservices. It also allows the backend and UI to communicate over a private Docker bridge network without exposing their internal ports to the host machine.

### Why this JWT approach?
The assignment requires JWT-based endpoint protection. We implemented a secure authentication boundary where the backend issues tokens via `/api/v1/auth/login` and verifies them using `fastapi_guard`. This approach was chosen as it represents the industry standard for securing decoupled SPAs, allowing for completely stateless API requests that carry their own authorization context.

---

## How to Run Locally

### 1. Clone both repositories
Ensure the two project folders sit in the same parent directory:
```bash
git clone https://github.com/kotalabhay/ai-assistant-backend
git clone https://github.com/kotalabhay/ai-assistant-ui
```

### 2. Configure Environment
```bash
cd ai-assistant-backend
cp .env.example .env
```

Define the following variables in `.env`:
- `GEMINI_API_KEY`: A valid Google AI Studio API key.
- `SECRET_KEY`: A random string used for signing JWT tokens.
- `ADMIN_USERNAME`: Username for local login.
- `ADMIN_PASSWORD`: Password for local login.
- `LLM_TIMEOUT_SECONDS`: (Optional) Defaults to 30.0.

### 3. Build and Start
```bash
docker compose up --build -d
```

The application is now accessible at `http://localhost/`.

---

## Project Structure

```text
ai-assistant-backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py        # Logic for issuing JWT tokens
│   │       ├── health.py      # System status endpoint
│   │       └── query.py       # Main LLM query processing route
│   ├── core/
│   │   ├── config.py          # Pydantic settings and environment loading
│   │   ├── llm.py             # Singleton Gemini client wrapper
│   │   └── security.py        # JWT verification logic
│   ├── models/
│   │   └── schemas.py         # Pydantic request/response data models
│   └── main.py                # FastAPI app initialization and middleware
├── nginx/
│   └── nginx.conf             # Gateway proxy configuration
├── Dockerfile             # Multi-stage image for backend service
├── docker-compose.yml     # Service orchestration manifest
├── requirements.txt       # Python dependency list
├── .env.example           # Template for environment variables
└── README.md              # Project documentation
```

---

## API Reference

### POST /api/v1/auth/login
Exchanges credentials for an access token.

- **Auth Requirement**: None
- **Request Body**: `{ "username": "admin", "password": "..." }`
- **Response Shape**: `{ "access_token": "...", "token_type": "bearer" }`
- **Error Codes**:
  - `401`: Invalid credentials.

### POST /api/v1/query
Submits a prompt to the AI assistant.

- **Auth Requirement**: `Authorization: Bearer <token>`
- **Request Body**: `{ "query": "string" }`
- **Response Shape**: `{ "response": "string" }`
- **Error Codes**:
  - `400`: Query cannot be empty.
  - `401`: Missing or invalid token.
  - `422`: Unprocessable entity (schema validation error).
  - `504`: LLM upstream timeout exceeded.
  - `502`: AI provider is unavailable.
  - `500`: Unexpected internal server error.

### GET /api/v1/health
Returns the current health status of the API.

- **Auth Requirement**: None
- **Response Shape**: `{ "status": "ok" }`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for LLM access. |
| `SECRET_KEY` | Yes | Secret string used to sign JWT signatures. |
| `ADMIN_USERNAME` | Yes | Local account username for authentication. |
| `ADMIN_PASSWORD` | Yes | Local account password for authentication. |
| `LLM_TIMEOUT_SECONDS` | No | Timeout in seconds for Gemini API calls. |

---

## Assumptions and Trade-offs

- **Static Authentication**: For the scope of this exercise, a single admin account is configured via environment variables. In a production system, this would be replaced by a database-backed user management system.
- **Statelessness**: The application does not persist chat history server-side. Each request is processed independently to minimize infrastructure complexity while maintaining clear, predictable scaling patterns.
- **Architectural Footprint**: As persistent storage was not a requirement for this specific scope, a database container (e.g., PostgreSQL) was omitted. This ensures a lightweight deployment suitable for evaluation and eliminates unnecessary side-effect management during the review process.
