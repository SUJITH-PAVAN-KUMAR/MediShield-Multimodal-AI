import os
import json
import random
import requests
import time

# Configuration
API_URL = "http://127.0.0.1:8000/api/upload"
BASE_DIR = os.path.dirname(__file__)
DATASET_DIR = os.path.join(BASE_DIR, "..", "Assignment2_datagen_scripts", "scripts", "scripts", "dataset")
METADATA_FILE = os.path.join(DATASET_DIR, "metadata.json")
SAMPLE_SIZE = 15  # Testing 15 documents

# Map metadata categories to what the Classifier AI actually outputs
CATEGORY_MAP = {
    "claim_forms": "CLAIM_FORM",
    "id_documents": "ID_DOCUMENT",
    "discharge_summaries": "DISCHARGE_SUMMARY",
    "prescriptions": "PRESCRIPTION",
    "amendments": "POLICY_AMENDMENT",
    "unknown": "UNKNOWN",
}

def run_evaluation():
    print("Loading metadata...")
    try:
        with open(METADATA_FILE, "r") as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"Failed to load metadata.json: {e}")
        return
        
    test_sample = random.sample(metadata, min(SAMPLE_SIZE, len(metadata)))
    
    classification_correct = 0
    decision_correct = 0
    total_processed = 0
    
    print(f"\n--- Starting Evaluation on {len(test_sample)} documents ---\n")
    
    for item in test_sample:
        # The metadata stores the full absolute path already
        file_path = item["file_path"]
        
        # If it's a relative path, resolve it
        if not os.path.isabs(file_path):
            file_path = os.path.join(DATASET_DIR, file_path.replace("./", ""))
        
        expected_category = CATEGORY_MAP.get(item["category"], "UNKNOWN")
        is_fraud = item.get("fraud_label", False)
        
        # Ground truth: If fraud=True, we expect REJECT or ESCALATE. Otherwise APPROVE.
        expected_decisions = ["REJECT", "ESCALATE"] if is_fraud else ["APPROVE"]

        print(f"Testing: {item['doc_id']} (Expected: {expected_category}, Fraud: {is_fraud})")
        
        if not os.path.exists(file_path):
            print(f"  ⚠️ File not found: {file_path}")
            continue
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "image/png")}
                response = requests.post(API_URL, files=files)
                
            if response.status_code == 200:
                result = response.json()
                total_processed += 1
                
                # Check Classification
                ai_doc_type = result.get("doc_type_identified", "")
                if ai_doc_type == expected_category:
                    classification_correct += 1
                    print(f"  📋 Classification: ✅ ({ai_doc_type})")
                else:
                    print(f"  📋 Classification: ❌ (AI: {ai_doc_type}, Expected: {expected_category})")
                    
                # Check Decision Correctness
                ai_decision = result.get("final_decision", "")
                if ai_decision in expected_decisions:
                    decision_correct += 1
                    print(f"  🎯 Decision: ✅ ({ai_decision})")
                else:
                    print(f"  🎯 Decision: ❌ (AI: {ai_decision}, Expected: {expected_decisions})")
                    print(f"     Reason: {result.get('justification', 'N/A')}")
            else:
                print(f"  ⚠️ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️ Failed to process: {e}")
            
        time.sleep(1)  # Prevent rate-limiting
        
    ## Calculate Metrics
    print("\n==================================================")
    print("              EVALUATION RESULTS                  ")
    print("==================================================")
    
    if total_processed > 0:
        class_acc = (classification_correct / total_processed) * 100
        dec_acc = (decision_correct / total_processed) * 100
        overall = (class_acc + dec_acc) / 2
        
        print(f"Total Documents Processed: {total_processed}")
        print(f"Classification Accuracy:   {class_acc:.1f}%")
        print(f"Decision Correctness:      {dec_acc:.1f}%")
        print(f"Overall Score:             {overall:.1f}%")
        
        if dec_acc > 60.0:
            print("\n🌟 SUCCESS! You exceeded the >60% Decision Correctness goal! 🌟")
        if overall > 70.0:
            print("🌟 SUCCESS! You exceeded the >70% Overall Score goal! 🌟")
        if dec_acc <= 60.0:
            print("\n⚠️ Decision Correctness is below 60%. Check orchestrator logic.")
    else:
        print("No documents were processed successfully.")

if __name__ == "__main__":
    run_evaluation()
