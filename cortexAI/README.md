# CortexAI

CortexAI is a small full-stack architecture built with React + Vite for the frontend and a Python FastAPI backend split into a gateway service and a dedicated auth service. The backend is organized as a UV workspace so shared code can be reused across packages.

## Architecture Overview

The project is composed of three main layers:

1. **Frontend** (`frontend/`)
2. **Backend Gateway** (`backend/gateway/`)
3. **Backend Auth Service** (`backend/services/auth/`)
4. **Shared Library** (`backend/shared/`)

### Frontend

- Built with React and Vite.
- Uses Firebase for client-side Google authentication.
- Sends the Firebase ID token to the backend auth service for login.
- Calls the backend through a shared Axios wrapper (`frontend/utils/axios.js`).
- The primary UI entrypoint is `frontend/src/pages/Home.jsx`.

### Backend Gateway

- Implemented in FastAPI at `backend/gateway/main.py`.
- Acts as a reverse proxy for the auth service under `/auth`.
- Provides a protected `/me` endpoint that verifies the session cookie and returns current user details.
- Uses `backend/gateway/middleware/auth.py` to enforce authentication by reading the `session` cookie and validating it against Redis.
- Uses `backend/gateway/utils/proxy.py` to forward requests to the auth service while preserving request data.
- Supports CORS through the shared utility in `backend/gateway/utils/cors.py`.

### Auth Service

- Implemented in FastAPI at `backend/services/auth/main.py`.
- Uses a startup lifespan to initialize:
  - MongoDB connection via `backend/services/auth/config/db.py`
  - Firebase admin SDK via `backend/services/auth/config/firebase.py`
  - Redis client via `backend/shared/redis/redis.py`
- Exposes authentication routes under `/auth` using the router in `backend/services/auth/controllers/auth.py`.
- Handles login by verifying Firebase ID tokens, creating or retrieving the user record, generating a session ID, and storing session data in Redis.
- Handles logout by deleting the session key from Redis and clearing the cookie.

### Shared Library

- Located at `backend/shared/` and packaged as a reusable workspace component.
- Provides shared Redis client initialization in `backend/shared/redis/redis.py`.
- Allows both gateway and auth service to reuse the same Redis connection logic.

## Data Flow

The main login and session flow works like this:

1. User clicks Google login in the frontend.
2. Firebase issues an ID token in the browser.
3. Frontend sends the token to `POST /auth/login`.
4. Auth service verifies the token with Firebase Admin.
5. Auth service creates or loads a user record from MongoDB.
6. Auth service generates a session ID, stores session data in Redis, and sets an HTTP-only cookie.
7. Frontend can call protected routes like `/me` through the gateway.
8. The gateway middleware validates the `session` cookie against Redis and returns user context.

## Workspace and Package Configuration

The backend is managed as a UV workspace in `backend/pyproject.toml` with the following members:

- `gateway`
- `services/auth`
- `shared`

This makes shared code available to both the gateway and auth service packages while keeping them isolated as individual FastAPI services.

## Environment Variables

The backend services use environment variables, typically loaded from `.env` files in each package directory:

- `PORT` - service port
- `AUTH_SERVICE_URL` - URL used by gateway proxy to forward auth requests
- `CHAT_SERVICE_URL` - URL used by gateway proxy to forward chat requests
- `AGENT_SERVICE_URL` - URL used by gateway proxy to forward agent requests
- `REDIS_URL` - Redis connection string
- Firebase credentials for auth service initialization
- MongoDB connection details in `backend/services/auth/config/db.py`

## Scripts and Entrypoints

### Backend

- `backend/gateway/main.py`
  - Entrypoint for the gateway service.
  - Creates the FastAPI app, registers CORS, and configures reverse proxy routes for `/auth`, `/chat`, and `/agent`.
  - Defines `/me` as a protected endpoint that uses `middleware/auth.py` to validate the session cookie stored in Redis.
  - Runs the gateway on the port configured by `PORT` with UVicorn and auto-reload enabled.

- `backend/services/auth/main.py`
  - Entrypoint for the auth service.
  - Uses a FastAPI lifespan context to initialize MongoDB, Redis, and Firebase Admin before serving requests.
  - Registers the auth router under `/auth` so login and logout routes are exposed with the correct prefix.
  - Runs the auth service on the port configured by `PORT` with UVicorn and auto-reload enabled.

- `backend/shared/redis/redis.py`
  - Shared Redis helper used by both gateway and auth services.
  - Centralizes Redis initialization so the same connection logic is reused across packages.

### Frontend

- `frontend/package.json` scripts:
  - `npm run dev` starts the Vite development server for the React frontend.
  - `npm run build` creates a production build of the frontend assets.
  - `npm run lint` runs ESLint across the frontend source files.
  - `npm run preview` serves the built frontend locally for previewing the production build.

- `frontend/src/pages/Home.jsx`
  - Primary UI page for login and conversation interactions.
  - Handles the Firebase sign-in flow and sends the Firebase ID token to the backend auth service.

## Running the Project

### Backend

Run each backend service from its package directory while exposing the backend workspace root on `PYTHONPATH`.

From the gateway package:

```bash
cd backend/gateway
PYTHONPATH=.. uv run main.py
```

From the auth package:

```bash
cd backend/services/auth
PYTHONPATH=../.. uv run main.py
```

From the chat package:

```bash
cd backend/services/chat
PYTHONPATH=../.. uv run main.py
```

From the agent package:

```bash
cd backend/services/agent
PYTHONPATH=../.. uv run main.py
```

If you prefer the workspace root, you can also run from `backend/`:

```bash
cd backend
uv run gateway/main.py
uv run services/auth/main.py
uv run services/chat/main.py
uv run services/agent/main.py
```

### Frontend

From the frontend root (`frontend/`):

```bash
cd frontend
npm install
npm run dev
```

## Important Files

- `backend/gateway/main.py` - gateway server entrypoint
- `backend/gateway/middleware/auth.py` - session validation middleware
- `backend/gateway/utils/proxy.py` - reverse proxy implementation
- `backend/services/auth/main.py` - auth service entrypoint
- `backend/services/auth/controllers/auth.py` - login/logout route handlers
- `backend/shared/redis/redis.py` - Redis client helper
- `frontend/src/pages/Home.jsx` - login UI and API integration

## Notes

- The gateway and auth service both run independently and communicate over HTTP.
- Redis is used for session storage, while MongoDB stores persistent user records.
- Firebase is used for user authentication and token verification.
- The shared backend package is designed to centralize cross-service helpers and reduce duplicate code.

---

This README is intended to explain the complete CortexAI architecture and should be kept updated as the project evolves.