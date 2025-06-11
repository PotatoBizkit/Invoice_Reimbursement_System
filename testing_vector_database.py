from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

client = PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("invoices")
model = SentenceTransformer('all-MiniLM-L6-v2')

query_text = "cab ride reimbursement"  
filters = {
    # "employee_name": "Denji",
    # "status": "Partially Reimbursed"
}
results = collection.get(include=["documents", "metadatas"])

print(f"\nTotal invoices stored: {len(results['ids'])}\n")

for i, meta in enumerate(results["metadatas"]):
    try:
        print(f"--- Invoice {i+1} ---")
        print(f"ID: {results['ids'][i]}")
        print(f"Employee: {meta.get('employee_name')}")
        print(f"Date: {meta.get('date')}")
        print(f"Status: {meta.get('status')}")
        reason = meta.get('reason')
        safe_reason = reason.encode('ascii', 'ignore').decode('ascii') if reason else "None"
        print(f"Reason: {safe_reason}")
        print(f"Text preview: {results['documents'][i][:200]}...")
        print("------------------------\n")
    except Exception as e:
        print(f"Error printing invoice {i+1}: {e}")

print(f"\n=== Performing vector search for query: '{query_text}' with filters: {filters} ===\n")

query_embedding = model.encode(query_text).tolist()

search_results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where=filters if filters else {}
)

retrieved_texts = search_results.get("documents", [[]])[0]
retrieved_metadatas = search_results.get("metadatas", [[]])[0]

if not retrieved_texts:
    print("No results found.\n")
else:
    for i, (text, meta) in enumerate(zip(retrieved_texts, retrieved_metadatas)):
        try:
            print(f"Result {i+1}:")
            print(f"Invoice ID: {meta.get('invoice_id')}")
            print(f"Employee: {meta.get('employee_name')}")
            print(f"Date: {meta.get('date')}")
            print(f"Status: {meta.get('status')}")
            reason = meta.get('reason')
            safe_reason = reason.encode('ascii', 'ignore').decode('ascii') if reason else "None"
            print(f"Reason: {safe_reason}")
            print(f"--- Invoice Text Preview ---")
            safe_text = text.encode('ascii', 'ignore').decode('ascii')
            print(safe_text[:300], "...")
        except Exception as e:
            print(f"Error printing search result {i+1}: {e}")
