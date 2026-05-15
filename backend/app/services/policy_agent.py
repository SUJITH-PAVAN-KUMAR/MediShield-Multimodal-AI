import json
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.services.state import GraphState
from app.services.utils import get_gemini_llm

_qdrant_store = None

def get_qdrant_store():
    global _qdrant_store
    if _qdrant_store is None:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
        _qdrant_store = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            path="./qdrant_db",
            collection_name="medishield_policy"
        )
    return _qdrant_store

class PolicyDecision(BaseModel):
    covered: str = Field(description="Must be 'true', 'false', or 'pending_review'")
    coverage_percentage: str = Field(description="The percentage covered (e.g. '80', '100') or null if not found. Extract from schedule of benefits.")
    policy_clause: str = Field(description="The exact text or clause from the policy rulebook justifying the decision.")
    exclusions: list[str] = Field(description="List of specific exclusions or conditions mentioned.")
    conditions: list[str] = Field(description="List of conditions, e.g. 'Subject to $1,500 individual deductible'.")

def policy_node(state: GraphState) -> GraphState:
    print(f"--- POLICY AGENT RUNNING for {state['case_id']} ---")
    
    extracted_data = state.get("extracted_data", {})
    cpt_codes = extracted_data.get("cpt_codes", [])
    
    if not cpt_codes:
        state["policy_check"] = {"status": "SKIPPED", "reason": "No CPT codes found"}
        return state
        
    llm = get_gemini_llm()
    structured_llm = llm.with_structured_output(PolicyDecision)
    
    # Variables to hold our aggregated results
    overall_covered = "true"
    all_clauses = []
    all_exclusions = []
    all_conditions = []
    individual_decisions = []

    # Loop through EVERY extracted CPT code
    for target_cpt in cpt_codes:
        print(f"\nEvaluating CPT Code: {target_cpt}...")
        decision_dict = None
        
        # STEP 1 - Rule-based Exclusion Check
        try:
            with open("excluded_cpt_ranges.json", "r") as f:
                excluded_ranges = json.load(f)
                
            cpt_int = int(target_cpt)
            for start, end in excluded_ranges:
                if int(start) <= cpt_int <= int(end):
                    print(f"REJECTED IN STEP 1: {target_cpt} falls in excluded range {start}-{end}")
                    decision_dict = {
                        "covered": "false",
                        "coverage_percentage": "null",
                        "policy_clause": f"Automatically excluded under Section 4.1 rule-based check.",
                        "exclusions": [f"CPT {target_cpt} is explicitly excluded in Section 4.1."],
                        "conditions": []
                    }
                    break # Break out of the exclusion range loop
        except Exception as e:
            pass

        # If not rejected in Step 1, run LLM Retrieval
        if not decision_dict:
            # STEP 2 - CPT Code to Description Lookup
            translation_prompt = f"What is the short medical name for CPT code {target_cpt}? Reply with JUST the 1-3 word procedure name (e.g., 'CT Scan') and nothing else."
            
            procedure_name = target_cpt
            try:
                response_msg = llm.invoke([HumanMessage(content=translation_prompt)])
                content = response_msg.content
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            procedure_name = block.get("text", "").strip()
                            break
                else:
                    procedure_name = str(content).strip()
            except Exception as e:
                print(f"STEP 2 Translation failed, falling back to raw CPT: {e}")
                
            print(f"STEP 2: Translated CPT {target_cpt} -> {procedure_name}")

            # STEP 3 & 4 - Semantic Search
            from qdrant_client.http import models
            qdrant_store = get_qdrant_store()
            retriever_inc = qdrant_store.as_retriever(search_kwargs={"k": 2, "filter": models.Filter(must=[models.FieldCondition(key="metadata.section", match=models.MatchValue(value="inclusions"))])})
            retriever_exc = qdrant_store.as_retriever(search_kwargs={"k": 2, "filter": models.Filter(must=[models.FieldCondition(key="metadata.section", match=models.MatchValue(value="exclusions"))])})
            
            docs_inc = retriever_inc.invoke(procedure_name)
            docs_exc = retriever_exc.invoke(procedure_name)
            
            cost_details = docs_inc[0].metadata.get("schedule_of_benefits", "") if docs_inc else ""
            context_inc = "\n\n".join([d.page_content for d in docs_inc])
            context_exc = "\n\n".join([d.page_content for d in docs_exc])

            # STEP 5 - LLM Decision
            prompt = f"""You are a strict insurance claims adjuster for MediShield. Evaluate if '{procedure_name}' (CPT {target_cpt}) is covered.
            Step 3 (Inclusions): {context_inc}
            Step 4 (Exclusions): {context_exc}
            Cost Sharing Details: {cost_details}
            RULES: 
            1. If found in Exclusions -> output covered: "false".
            2. If found in Inclusions -> output covered: "true". Extract coverage_percentage.
            3. If not found in either -> output covered: "pending_review".
            Respond strictly using the JSON format provided."""

            try:
                response = structured_llm.invoke([HumanMessage(content=prompt)])
                decision_dict = response.model_dump()
            except Exception as e:
                print(f"Policy check failed: {e}")
                decision_dict = {"covered": "pending_review", "coverage_percentage": "null", "policy_clause": f"Error: {str(e)}", "exclusions": [], "conditions": []}

        # --- AGGREGATION LOGIC ---
        individual_decisions.append(decision_dict)
        all_clauses.append(f"[{target_cpt}]: {decision_dict.get('policy_clause', '')}")
        all_exclusions.extend(decision_dict.get("exclusions", []))
        all_conditions.extend(decision_dict.get("conditions", []))
        
        # If any procedure is denied, the whole claim is denied
        if decision_dict.get("covered") == "false":
            overall_covered = "false"
        elif decision_dict.get("covered") == "pending_review" and overall_covered != "false":
            overall_covered = "pending_review"

    # Final Aggregated State Update
    state["policy_check"] = {
        "covered": overall_covered,
        "coverage_percentage": individual_decisions[0].get("coverage_percentage", "null") if individual_decisions else "null",
        "policy_clause": " | ".join(all_clauses),
        "exclusions": list(set(all_exclusions)),
        "conditions": list(set(all_conditions)),
        "details": individual_decisions
    }
    
    print(f"\nFinal Aggregated Policy Decision: {state['policy_check']['covered']}")
    return state

