# Phase 1: Foundation & Backend Setup

## Objective
Set up the core project structure, initialize the FastAPI backend, and create the ingestion endpoint to receive document uploads.

## 1. Project Structure Setup
Organize your workspace to keep the frontend and backend separate.

```text
Capestone Project/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Config and constants
│   │   ├── models/       # Pydantic schemas
│   │   ├── services/     # LangGraph and Agents logic
│   │   └── main.py       # FastAPI entry point
│   ├── uploads/          # Directory to store uploaded files
│   ├── requirements.txt
│   └── .env              # API keys (OpenAI/Anthropic)
├── frontend/             # Next.js app (Phase 5)
└── dataset/              # Your generated data
```

## 2. Environment Variables
Create a `.env` file in the `backend/` folder:
```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## 3. FastAPI Initialization
In `backend/app/main.py`, set up your basic FastAPI application with CORS enabled so your Next.js frontend can communicate with it later.

## 4. Ingestion Endpoint
Create an endpoint `POST /api/upload` that:
1. Accepts a `UploadFile` (FastAPI).
2. Generates a unique UUID for `case_id`.
3. Saves the file to the `backend/uploads/` directory.
4. Returns a JSON response with the `case_id` and status.

## 5. Testing Phase 1
* Run the server: `uvicorn app.main:app --reload`
* Open `http://localhost:8000/docs` in your browser.
* Use the Swagger UI to upload an image from your `dataset` folder and verify it saves correctly in the `uploads/` folder.
