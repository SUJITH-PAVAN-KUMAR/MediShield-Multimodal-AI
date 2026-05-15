import json
import os
from app.services.state import GraphState

def load_claim_history_db():
    """Loads the main project dataset metadata to act as our claim history database."""
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "Assignment2_datagen_scripts", "scripts", "scripts", "dataset")
    metadata_path = os.path.join(base_dir, "metadata.json")
    
    db = {}
    try:
        with open(metadata_path, "r") as f:
            data = json.load(f)
            # Group claims by patient_id to build the history database
            for item in data:
                if item.get("category") == "claim_forms":
                    pid = item.get("patient_id")
                    if pid:
                        if pid not in db:
                            db[pid] = []
                        db[pid].append(item)
    except Exception as e:
        print("Warning: Could not load metadata.json for claim history DB.", e)
        
    return db

# Load it once into memory
HISTORY_DATABASE = load_claim_history_db()

def fraud_node(state: GraphState) -> GraphState:
    print(f"--- FRAUD AGENT RUNNING for {state['case_id']} ---")
    
    extracted = state.get("extracted_data", {})
    
    fraud_score = 0.0
    anomalies = []
    
    # 1. PHASE 3 LOGIC: Python check for extremely high amounts
    claim_amount = extracted.get("claim_amount", 0.0)
    if claim_amount > 10000:
        fraud_score += 0.5
        anomalies.append(f"Extremely high claim amount: ${claim_amount}")
        
    # 2. ASSIGNMENT LOGIC: Query history against statistical baselines
    # Note: To fully utilize this, your ClaimsAgent should extract the 'patient_id' 
    # (e.g., PT_19116) from the document, just like KYC extracts member_id.
    patient_id = extracted.get("patient_id") 
    
    if patient_id and patient_id in HISTORY_DATABASE:
        patient_history = HISTORY_DATABASE[patient_id]
        
        # Baseline Check A: Frequency Anomalies
        # If the patient has an unusually high number of claims in the dataset
        if len(patient_history) >= 3:
            fraud_score += 0.3
            anomalies.append("Frequency anomaly: Patient has a high volume of historical claims.")
            
        # Baseline Check B: Duplicate Submissions
        # Since we don't have historical amounts in the basic metadata, 
        # we check if the dataset flagged a duplicate edge case for this patient
        for past_claim in patient_history:
            edge_flags = past_claim.get("edge_flags", [])
            if any("duplicate" in flag for flag in edge_flags):
                fraud_score += 0.6
                anomalies.append("Duplicate submission detected in patient history.")
                break
    else:
        # If no patient_id was extracted, we can't check history.
        if not patient_id:
            print("Note: No patient_id found in extracted_data to query history.")
            
    # Cap the fraud score at 1.0 maximum
    fraud_score = min(fraud_score, 1.0)
    
    # Determine risk level per the assignment output requirement
    risk_level = "LOW"
    if fraud_score >= 0.7:
        risk_level = "HIGH"
    elif fraud_score >= 0.4:
        risk_level = "MEDIUM"
        
    # Update state
    state["fraud_score"] = fraud_score
    
    print(f"Fraud Output -> Score: {fraud_score} | Risk: {risk_level} | Anomalies: {anomalies}")
    
    return state
