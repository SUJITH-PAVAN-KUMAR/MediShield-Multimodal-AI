from app.services.state import GraphState

def orchestrator_node(state: GraphState) -> GraphState:
    print(f"--- ORCHESTRATOR AGENT RUNNING for {state['case_id']} ---")
    
    doc_type = state.get("doc_type", "UNKNOWN")
    fraud_score = state.get("fraud_score", 0.0)
    
    # 1. Handle ID Documents (KYC Path)
    if doc_type == "ID_DOCUMENT":
        kyc = state.get("kyc_result", {})
        if kyc.get("overall_pass") is True and fraud_score < 0.4:
            state["final_decision"] = "APPROVE"
            state["justification"] = "Identity verified successfully. Low fraud risk."
        elif fraud_score >= 0.7:
            state["final_decision"] = "ESCALATE"
            state["justification"] = "Identity flagged for high fraud risk. Requires human investigation."
        else:
            state["final_decision"] = "REJECT"
            state["justification"] = "Identity verification failed or high fraud risk."
        print(f"Final Decision: {state['final_decision']}")
        return state

    # 2. Handle Claim Forms (Claims -> Policy -> Fraud Path)
    if doc_type == "CLAIM_FORM":
        policy = state.get("policy_check", {})
        is_covered = policy.get("covered", "false").lower() == "true"
        
        if fraud_score >= 0.7:
            state["final_decision"] = "ESCALATE"
            state["justification"] = "High fraud score detected. Requires human investigation."
        elif not is_covered:
            state["final_decision"] = "REJECT"
            state["justification"] = f"Procedure not covered by policy. Reason: {policy.get('policy_clause', 'N/A')}"
        elif is_covered and fraud_score < 0.7:
            state["final_decision"] = "APPROVE"
            state["justification"] = "Claim is covered and fraud risk is acceptable."
        else:
            state["final_decision"] = "ESCALATE"
            state["justification"] = "Edge case detected. Escalating to human reviewer."
            
        print(f"Final Decision: {state['final_decision']}")
        return state

    # 3. Handle Supporting Documents (Prescriptions, Discharge Summaries, Amendments)
    #    These are valid medical/policy documents. Approve if no fraud, escalate if suspicious.
    if doc_type in ["PRESCRIPTION", "DISCHARGE_SUMMARY", "POLICY_AMENDMENT"]:
        if fraud_score >= 0.7:
            state["final_decision"] = "ESCALATE"
            state["justification"] = f"Supporting document '{doc_type}' flagged for high fraud risk."
        else:
            state["final_decision"] = "APPROVE"
            state["justification"] = f"Supporting document '{doc_type}' accepted. No fraud indicators detected."
        print(f"Final Decision: {state['final_decision']}")
        return state

    # 4. Truly unknown documents get escalated
    state["final_decision"] = "ESCALATE"
    state["justification"] = f"Document type '{doc_type}' is unrecognized. Requires human review."
    print(f"Final Decision: {state['final_decision']}")
    return state
