from fastapi import FastAPI, Form
from pydantic import BaseModel
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from groq import Groq

app = FastAPI()
client = PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("invoices")
model = SentenceTransformer('all-MiniLM-L6-v2')
groq_client = Groq(api_key="")
chat_history = []

class ChatQuery(BaseModel): #creates a new class ChatQuery that inherits from BaseModel
    query: str #this ensures any instance of ChatQuery must have query field containing a string

@app.post("/ragbot")
def ragbot(cquery: ChatQuery):
    global chat_history
    user_query = cquery.query #this gets user's query
    print(f"\nUser query: {user_query}")
    query_embedding = model.encode(user_query).tolist() #converts users query into vector

    search_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    retrieved_texts = search_results.get("documents", [[]])[0]
    retrieved_metadatas = search_results.get("metadatas", [[]])[0]
    context = ""
    for i, (text, meta) in enumerate(zip(retrieved_texts, retrieved_metadatas)): #creates a string of top 5 responses for LLM
        context += f"""
        Invoice - {i+1}:
        - Employee: {meta.get('employee_name')}
        - Date: {meta.get('date')}
        - Status: {meta.get('status')}
        - Reason: {meta.get('reason')}
        - Invoice Text (partial): {text[:300]}...

        """

    messages = [
        {"role": "system", "content": "You are an intelligent assistant helping the HR department understand invoice reimbursements. You answer using the given context of invoices."},
        {"role": "user", "content": f"Here is the context of the invoices:\n{context}\n\nNow answer this question: {user_query}"}
    ]

    for entry in chat_history[-5:]: #adds last 5 chats from chat_history list
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["assistant"]})

    completion = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        temperature=0.7, #for balanced creativity and randomness in response
        max_completion_tokens=1024 #sets max response length
    )
    reply = completion.choices[0].message.content.strip() #get first response stripping extra spaces

    chat_history.append({ #store in chat_history
        "user": user_query,
        "assistant": reply
    })

    return { #result in markdown format
        "response_markdown": f"### Chatbot Response:\n\n{reply}"
    }