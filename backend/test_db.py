from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Connect to the SQLite vector database
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    path="./qdrant_db",
    collection_name="medishield_policy"
)

# Let's peek at the data by searching for "MRI"
results = qdrant.similarity_search("cpt code 21120",k=2)

print("--- TOP 2 POLICY CHUNKS FOUND IN DATABASE ---")
for i, doc in enumerate(results):
    print(f"\n[Chunk {i+1}]:")
    print(doc.page_content)

# Explicitly close the database connection before Python shuts down
qdrant.client.close()
