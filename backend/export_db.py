import csv
from qdrant_client import QdrantClient

def export_to_csv():
    print("Connecting to local Qdrant Database...")
    client = QdrantClient(path="./qdrant_db")
    
    # Scroll through the database to get all records (without the giant vector math arrays)
    records, _ = client.scroll(
        collection_name="medishield_policy",
        limit=1000,
        with_payload=True,
        with_vectors=False 
    )
    
    print(f"Found {len(records)} chunks. Exporting to Excel CSV...")
    
    with open("medishield_database.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Chunk ID", "Section Label", "Policy Content", "Section 1 Metadata (Schedule of Benefits)"])
        
        for r in records:
            content = r.payload.get("page_content", "")
            metadata = r.payload.get("metadata", {})
            section_label = metadata.get("section", "unknown")
            sec1_metadata = metadata.get("schedule_of_benefits", "")
            writer.writerow([r.id, section_label, content, sec1_metadata])
            
    print("Export Complete! You can now open 'backend/medishield_database.csv' in Excel.")

if __name__ == "__main__":
    export_to_csv()
