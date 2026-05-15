from typing import TypedDict, Dict, Any

class GraphState(TypedDict):
    case_id: str
    file_path: str
    doc_type: str
    extracted_data: Dict[str, Any]
    kyc_result: Dict[str, Any]
    policy_check: Dict[str, Any]
    fraud_score: float
    final_decision: str
    justification: str
