from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

client = PersistentClient(path="./chroma_db") #This is used to store the data even after app shuts down
collection = client.get_or_create_collection("invoices") #This creates a logical collection in vector db

model = SentenceTransformer('all-MiniLM-L6-v2')

def store(id, employee_name, date, text, status, reason):
    '''This function is used to convert text into vector which is coverted to normal python list
    from numpy array to be stored in chromadb. Metadata is also stored along with vector.'''
    text_embeding = text + " " + status + " " + reason
    embeding = model.encode(text_embeding).tolist()

    metadata = {
        "invoice_id": id,
        "employee_name": employee_name,
        "date": date,
        "status": status,
        "reason": reason
    }

    collection.add(
        documents=[text],
        embeddings=[embeding],
        metadatas=[metadata],
        ids=[id]
    )

    print(f"Invoice {id} is stored as {status} for {employee_name}.")