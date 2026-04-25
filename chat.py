import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("conflict_articles")


def search_articles(query, n=5):
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n
    )
    return results

def ask_ai(question):
    results = search_articles(question)
    
    context = ""
    sources = []
    for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        context += f"\n[{i+1}] {doc}\nIzvor: {meta['source']} | {meta['published_at']}\n"
        sources.append(meta)

    prompt = f"""Ti si ekspert za međunarodne konflikte i geopolitiku. 
Odgovaraj na osnovu sljedećih vijesti, isključivo na bosanskom jeziku.
Ako informacija nije u vijestima, reci to jasno.

VIJESTI:
{context}

PITANJE: {question}

Odgovori detaljno i navedi koji članci su ti bili korisni."""

    client_groq = Groq(api_key=GROQ_API_KEY)
    response = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    
    return response.choices[0].message.content, sources

if __name__ == "__main__":
    print("🌍 Conflict Intel Chat — ukucaj 'exit' za izlaz\n")
    while True:
        question = input("Ti: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue
        print("\n⏳ Tražim relevantne vijesti...\n")
        answer, sources = ask_ai(question)
        print(f"AI: {answer}\n")
        print("📰 Izvori:")
        for s in sources:
            print(f"  - {s['title']} ({s['source']})")
        print()