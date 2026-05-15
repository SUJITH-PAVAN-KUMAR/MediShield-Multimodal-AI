import os
import re
import json
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

load_dotenv()

PDF_PATH = os.path.join("..", "Assignment2_datagen_scripts", "scripts", "scripts", "dataset", "policies", "medishield_gold_plan.pdf")
DB_DIR = "./qdrant_db"

def ingest():
    print(f"1. Reading PDF with IBM Docling from {PDF_PATH}...")
    converter = DocumentConverter()
    result = converter.convert(PDF_PATH)
    text = result.document.export_to_markdown()
    
    print("2. Parsing specific sections...")
    
    s1_match = re.search(r'## 1\. Schedule of Benefits(.*?)(?=## 2\. Definitions)', text, re.DOTALL)
    section_1_text = s1_match.group(1).strip() if s1_match else ""
    
    s3_match = re.search(r'## 3\. Inclusions(.*?)(?=## 4\. Exclusions)', text, re.DOTALL)
    section_3_text = s3_match.group(1).strip() if s3_match else ""
    
    s4_match = re.search(r'## 4\. Exclusions(.*?)(?=## 4\.1)', text, re.DOTALL)
    section_4_text = s4_match.group(1).strip() if s4_match else ""
    
    s41_match = re.search(r'## 4\.1 Excluded CPT Code Ranges(.*?)(?=## 5\. Optional Riders)', text, re.DOTALL)
    section_41_text = s41_match.group(1).strip() if s41_match else ""
    
    # Save exclusion ranges for rule-based check
    ranges = re.findall(r'(\d{5})-(\d{5})', section_41_text)
    with open("excluded_cpt_ranges.json", "w") as f:
        json.dump(ranges, f)
    print(f"Saved {len(ranges)} excluded ranges to excluded_cpt_ranges.json")

    print("3. Chunking sections...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = []
    
    if section_3_text:
        s3_chunks = text_splitter.create_documents([section_3_text])
        for c in s3_chunks:
            c.metadata = {"section": "inclusions", "schedule_of_benefits": section_1_text}
        docs.extend(s3_chunks)
        
    if section_4_text:
        s4_chunks = text_splitter.create_documents([section_4_text])
        for c in s4_chunks:
            c.metadata = {"section": "exclusions"}
        docs.extend(s4_chunks)
        
    print(f"4. Embedded {len(docs)} chunks. Saving to Qdrant...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    
    qdrant = QdrantVectorStore.from_documents(
        [docs[0]], embeddings, path=DB_DIR, collection_name="medishield_policy", force_recreate=True
    )
    
    for i in range(1, len(docs)):
        qdrant.add_documents([docs[i]])
        
    qdrant.client.close()
    print("Success! Multi-section Policy DB created.")

if __name__ == "__main__":
    ingest()
