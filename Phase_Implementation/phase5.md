# Phase 5: Case Management UI

## Objective
Build a Next.js frontend for operations staff to review the AI's work and intervene on escalated cases.

## 1. Next.js Initialization
In the `frontend/` directory, initialize a Next.js application:
`npx create-next-app@latest .`
(Choose App Router, Tailwind CSS).

## 2. API Endpoints Needed (Backend)
Add these to your FastAPI server to support the frontend:
* `GET /api/cases`: Returns a list of all processed cases.
* `GET /api/cases/{case_id}`: Returns the full details of a specific case (the final `GraphState`).
* `POST /api/cases/{case_id}/override`: Allows a human to change the AI's decision.

## 3. Dashboard View (`/`)
* Build a data table displaying `case_id`, `doc_type`, `fraud_score`, and `final_decision`.
* Use color-coded badges (Green for Approve, Red for Reject, Yellow for Escalate).

## 4. Case Detail View (`/case/[id]`)
* **Left Panel:** Display the uploaded document image (fetch from backend static files).
* **Right Panel:** 
  * Show the Final Decision and Justification at the top.
  * Create collapsible accordions for each agent's output (e.g., click "Claims Extraction" to see the raw JSON extracted by the Claims Agent).
* **Action Buttons:** Allow humans to click "Override to Approve" or "Override to Reject" for escalated cases.

## 5. Testing Phase 5
Run `npm run dev` and ensure the frontend correctly fetches data from your running FastAPI server and displays the UI smoothly.
