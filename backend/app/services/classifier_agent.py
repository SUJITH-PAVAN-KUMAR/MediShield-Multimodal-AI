from langchain_core.messages import HumanMessage
from app.services.state import GraphState
from app.services.utils import encode_image, get_gemini_llm

def classifier_node(state: GraphState) -> GraphState:
    print(f"--- CLASSIFIER AGENT RUNNING for {state['case_id']} ---")
    
    base64_image = encode_image(state["file_path"])
    llm = get_gemini_llm()
    
    prompt = """You are an expert document classification AI for MediShield Insurance.
Look at the provided document image and classify it into EXACTLY ONE of these categories:
CLAIM_FORM, ID_DOCUMENT, DISCHARGE_SUMMARY, PRESCRIPTION, POLICY_AMENDMENT, UNKNOWN.

Respond ONLY with the exact category name. Do not include any other words, punctuation, or explanations."""
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ]
    )
    
    response = llm.invoke([message])
    
    raw_content = response.content
    text_content = ""
    if isinstance(raw_content, list):
        for item in raw_content:
            if isinstance(item, dict) and "text" in item:
                text_content += item["text"]
    else:
        text_content = str(raw_content)
        
    doc_type = text_content.strip().upper()
    print(f"Decision: {doc_type}")
    
    state["doc_type"] = doc_type
    return state
