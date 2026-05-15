# Phase 4: Orchestrator & Final Pipeline Integration

## Objective
Wire all the specialist agents together using LangGraph's conditional routing, and add the final decision-making node.

## 1. Conditional Routing
Update your LangGraph definition:
* After the `classifier_node`, use `add_conditional_edges`.
* Create a routing function that looks at `state["doc_type"]`:
  * If `CLAIM_FORM` -> route to `claims_node` (and subsequently `policy_node`).
  * If `ID_DOCUMENT` -> route to `kyc_node`.
  * If `UNKNOWN` -> route directly to `orchestrator_node` with a flag to escalate.

## 2. The Orchestrator Agent (`orchestrator_node`)
* **Position:** The final node before `END`.
* **Task:** Make the final call.
* **Logic:** Look at all populated fields in the state (`kyc_result`, `policy_check`, `fraud_score`, `doc_type`).
* **Rules:**
  * `APPROVE`: All checks pass, fraud is low, policy covers it.
  * `REJECT`: KYC failed, or policy explicitly denies coverage.
  * `ESCALATE`: High fraud score, missing data, or `doc_type` is `UNKNOWN`.
* **Updates:** `state["final_decision"]` and `state["justification"]`.

## 3. Backend Integration
In your FastAPI app, update the `POST /api/upload` endpoint:
1. After saving the file, invoke your compiled LangGraph with the initial state.
2. Wait for the graph to complete.
3. Save the final `GraphState` to a simple local database (SQLite) or a JSON file so the UI can fetch it later.

## 4. Testing Phase 4
Upload a document via the FastAPI Swagger UI and watch the terminal logs. Verify it hits the classifier, routes to the correct specialist, hits the orchestrator, and outputs a logical Approve/Reject/Escalate decision.
