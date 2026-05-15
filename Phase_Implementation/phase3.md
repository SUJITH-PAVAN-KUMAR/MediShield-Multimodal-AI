# Phase 3: The Specialist Agents

## Objective
Build the specific processing nodes for different document types. These nodes will operate in parallel in the final graph.

## 1. KYC Agent (`kyc_node`)
* **Triggered by:** `ID_DOCUMENT`
* **Task:** Extract Name, DOB, and Expiry Date. 
* **Logic:** Check if the expiry date is in the past. If yes, fail KYC. You can also prompt the Vision LLM to look for visual tampering (mismatched fonts, blurry text).
* **Updates:** `state["kyc_result"]`

## 2. Claims Agent (`claims_node`)
* **Triggered by:** `CLAIM_FORM`
* **Task:** Extract specific structured data.
* **Logic:** Use a Vision LLM to extract `claim_amount`, `icd_10_codes`, `cpt_codes`, `provider_npi`. Define a strict Pydantic model for this extraction.
* **Updates:** `state["extracted_data"]`

## 3. Policy Agent (RAG) (`policy_node`)
* **Triggered by:** Successful Claims extraction.
* **Setup:** 
  1. Write a script to ingest `medishield_gold_plan.pdf` using **Docling**.
  2. Chunk the text and embed it into a local vector store (like **ChromaDB**).
* **Task:** Retrieve policy rules.
* **Logic:** Take the `cpt_codes` from the `extracted_data` and query the vector store to see if that procedure is covered. Return a boolean and the relevant policy text.
* **Updates:** `state["policy_check"]`

## 4. Fraud Detection Agent (`fraud_node`)
* **Task:** Evaluate risk.
* **Logic:** This can be an LLM call or pure python logic. Look at the `extracted_data`. If the claim amount is extremely high, or if dates conflict, assign a high fraud score (>0.5).
* **Updates:** `state["fraud_score"]`

## 5. Testing Phase 3
Test each node function individually by passing it a mocked `GraphState` dictionary to ensure they output the expected data formats before wiring them into the main graph.
