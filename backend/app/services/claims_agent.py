from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage
from app.services.state import GraphState
from app.services.utils import encode_image, get_gemini_llm

class ClaimsData(BaseModel):
    patient_id: str = Field(description="The Patient ID (e.g., PT_19116)")
    claim_amount: float = Field(description="The total charge or billing amount on the claim form")
    icd_10_codes: List[str] = Field(description="List of diagnosis codes (ICD-10-CM)")
    cpt_codes: List[str] = Field(description="List of procedure or service codes (CPT/HCPCS)")
    provider_npi: str = Field(description="National Provider Identifier (NPI)")

def claims_node(state: GraphState) -> GraphState:
    print(f"--- CLAIMS AGENT RUNNING for {state['case_id']} ---")
    
    base64_image = encode_image(state["file_path"])
    llm = get_gemini_llm()
    
    # Force Gemini to output perfect JSON matching our class!
    structured_llm = llm.with_structured_output(ClaimsData)
    
    prompt = """You are an expert medical billing AI. 
Look at this claim form and extract the Total Charge Amount, ICD-10 Diagnosis Codes, CPT Procedure Codes, and the Provider NPI."""
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ]
    )
    
    try:
        response = structured_llm.invoke([message])
        state["extracted_data"] = response.model_dump()
        print(f"Successfully extracted: {state['extracted_data']}")
    except Exception as e:
        print(f"Extraction failed: {e}")
        state["extracted_data"] = {"error": "Failed to parse claim"}
        
    return state
