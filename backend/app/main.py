import os
import json
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.services.graph import graph_app

app = FastAPI(title="MediShield Document Intake API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. Mount static files so the UI can display the uploaded images
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Simple JSON Database
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "cases_db.json")
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

def read_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def write_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.get("/")
def read_root():
    return {"message": "MediShield API is running"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    case_id = str(uuid.uuid4())
    
    clean_original_name = file.filename.replace(" ", "_")
    safe_filename = f"{case_id}_{clean_original_name}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    initial_state = {
        "case_id": case_id,
        "file_path": file_path,
        "doc_type": "",
        "extracted_data": {},
        "kyc_result": {},
        "policy_check": {},
        "fraud_score": 0.0,
        "final_decision": "",
        "justification": ""
    }
    
    print(f"Triggering AI pipeline for {file.filename}...")
    final_state = graph_app.invoke(initial_state)
    
    # Save the relative image URL so the UI knows where to fetch the image
    final_state["image_url"] = f"/uploads/{safe_filename}"
    
    # 2. SAVE to our Database
    cases = read_db()
    cases.append(final_state)
    write_db(cases)
    
    return {
        "status": "success", 
        "case_id": case_id,
        "doc_type_identified": final_state.get("doc_type", ""),
        "final_decision": final_state.get("final_decision", ""),
        "justification": final_state.get("justification", "")
    }

# --- PHASE 5 NEW ENDPOINTS ---

@app.get("/api/cases")
def get_all_cases():
    """Returns a summary of all processed cases for the UI Dashboard."""
    cases = read_db()
    # We only send summary data to keep the dashboard fast
    summary = []
    for c in reversed(cases): # Newest first
        summary.append({
            "case_id": c["case_id"],
            "doc_type": c["doc_type"],
            "fraud_score": c.get("fraud_score", 0.0),
            "final_decision": c.get("final_decision", "UNKNOWN")
        })
    return summary

@app.get("/api/cases/{case_id}")
def get_case_details(case_id: str):
    """Returns the full GraphState for a specific case."""
    cases = read_db()
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise HTTPException(status_code=404, detail="Case not found")

@app.post("/api/cases/{case_id}/override")
def override_decision(case_id: str, payload: dict):
    """Allows a human operator to override the AI's decision."""
    new_decision = payload.get("decision")
    if new_decision not in ["APPROVE", "REJECT"]:
        raise HTTPException(status_code=400, detail="Invalid decision")
        
    cases = read_db()
    for c in cases:
        if c["case_id"] == case_id:
            c["final_decision"] = new_decision
            c["justification"] = f"[HUMAN OVERRIDE] {c.get('justification', '')}"
            write_db(cases)
            return {"status": "success", "new_decision": new_decision}
            
    raise HTTPException(status_code=404, detail="Case not found")
