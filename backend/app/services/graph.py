from langgraph.graph import StateGraph, END
from app.services.state import GraphState
from app.services.classifier_agent import classifier_node
from app.services.claims_agent import claims_node
from app.services.kyc_agent import kyc_node
from app.services.policy_agent import policy_node
from app.services.fraud_agent import fraud_node
from app.services.orchestrator_agent import orchestrator_node

# Build the LangGraph
workflow = StateGraph(GraphState)
# Add our nodes
workflow.add_node("classifier", classifier_node)
workflow.add_node("claims", claims_node)
workflow.add_node("kyc", kyc_node)
workflow.add_node("policy", policy_node) 
workflow.add_node("fraud", fraud_node)          
workflow.add_node("orchestrator", orchestrator_node) 
workflow.set_entry_point("classifier")
# --- CONDITIONAL ROUTING MAGIC ---
# This function decides which agent gets the document based on the Classifier's decision
def route_document(state: GraphState):
    if state["doc_type"] == "CLAIM_FORM":
        return "claims"
    elif state["doc_type"] == "ID_DOCUMENT":
        return "kyc"
    else:
        # Supporting docs (PRESCRIPTION, DISCHARGE_SUMMARY, etc.) go through fraud check
        return "fraud"
# Connect the router to the classifier
workflow.add_conditional_edges("classifier", route_document)
# After the specialist finishes, end the graph (for now)
workflow.add_edge("claims", "policy")
workflow.add_edge("policy", "fraud")         # Policy goes to Fraud
workflow.add_edge("kyc", "fraud")            # KYC goes to Fraud
workflow.add_edge("fraud", "orchestrator")   # Fraud goes to Orchestrator
workflow.add_edge("orchestrator", END)       # Orchestrator is the final step
# Compile it
graph_app = workflow.compile()
