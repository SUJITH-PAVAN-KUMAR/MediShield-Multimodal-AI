# Phase 2: Core LangGraph Setup & Classifier Agent

## Objective
Establish the LangGraph state machine and build the first agent (Classifier) that looks at the incoming document and determines its type.

## 1. Define the Graph State
Create a `State` class (using `TypedDict` from typing). This state will be passed around between all nodes in your graph.

```python
from typing import TypedDict, Dict, Any

class GraphState(TypedDict):
    case_id: str
    file_path: str
    doc_type: str             # populated by Classifier
    extracted_data: Dict[str, Any]
    kyc_result: Dict[str, Any]
    policy_check: Dict[str, Any]
    fraud_score: float
    final_decision: str
    justification: str
```

## 2. Build the Classifier Agent
Create a function `classifier_node(state: GraphState) -> GraphState`.
* **Input:** `state["file_path"]`
* **Action:** Convert the image to base64. Pass it to a Vision LLM (e.g., GPT-4o or Claude 3.5 Sonnet) with a prompt asking it to classify the document into one of the categories: `CLAIM_FORM`, `ID_DOCUMENT`, `DISCHARGE_SUMMARY`, `PRESCRIPTION`, `POLICY_AMENDMENT`, `UNKNOWN`.
* **Output:** Update `state["doc_type"]` and return the state.

*Hint: Use Pydantic and `with_structured_output()` in Langchain to guarantee the LLM returns JSON.*

## 3. Setup Initial LangGraph
In a new file `backend/app/services/graph.py`:
1. Initialize a `StateGraph(GraphState)`.
2. Add the `classifier_node`.
3. Set the entry point to the classifier node.
4. For now, route the output of the classifier to the `END` node.
5. Compile the graph.

## 4. Testing Phase 2
Write a small standalone python script that invokes your compiled graph with a dummy state containing a `file_path` to one of your dataset images, and print the output to ensure the Classifier correctly identifies the doc type.
