# Phase 6: Testing, Evaluation & Polish

## Objective
Run the system against the generated dataset to calculate your final grade and implement bonus features.

## 1. Batch Evaluation Script
Create a script in the root directory (e.g., `evaluate.py`):
1. Read `dataset/metadata.json`.
2. Loop through every image defined in the metadata.
3. Send the image to your FastAPI `/api/upload` endpoint.
4. Record the system's `doc_type` and `final_decision`.

## 2. Calculate Metrics
Compare your system's outputs to the ground-truth in `metadata.json` to calculate the evaluation criteria from the assignment prompt:
* **Classification Accuracy:** (Correct Classifications / Total Documents) * 100
* **Decision Correctness:** (Correct Decisions / Total Decisions) * 100

*Goal: Achieve >70% overall score and >60% Decision Correctness.*

## 3. Tackle Bonus Challenges
Pick 1 or 2 bonus challenges from the assignment to stand out:
* **LangSmith Tracing:** Sign up for a free LangSmith account, set the environment variables, and watch your LangGraph traces populate in the cloud. This takes 5 minutes and is highly impressive.
* **Audit Export:** Add a button in the UI that uses a library like `jspdf` to generate a PDF report of the case details.
* **Confidence Calibration:** Have the Orchestrator output a confidence score (0.0-1.0) alongside its decision.

## 4. Final Walkthrough
Write a solid `README.md` explaining how to start the backend, start the frontend, and how to run the evaluation script. Your project is now complete!
