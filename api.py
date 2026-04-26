from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Conflict Intel API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("conflict_articles")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatRequest(BaseModel):
    question: str

def get_db():
    return sqlite3.connect("conflict_intel.db")

@app.get("/")
def root():
    return {"status": "online", "name": "Conflict Intel API"}

@app.get("/stats")
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM articles")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT source) FROM articles")
    sources = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(created_at) FROM articles")
    last_scrape = cursor.fetchone()[0]
    conn.close()
    return {
        "total_articles": total,
        "total_sources": sources,
        "last_scrape": last_scrape,
        "vector_db_count": collection.count()
    }

@app.get("/articles")
def get_articles(limit: int = 20, source: str = None):
    conn = get_db()
    cursor = conn.cursor()
    if source:
        cursor.execute(
            "SELECT title, source, published_at, url FROM articles WHERE source LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f"%{source}%", limit)
        )
    else:
        cursor.execute(
            "SELECT title, source, published_at, url FROM articles ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"title": r[0], "source": r[1], "published_at": r[2], "url": r[3]}
        for r in rows
    ]

@app.post("/chat")
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Pitanje ne može biti prazno")

    query_embedding = model.encode(request.question).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=5)

    context = ""
    sources = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context += f"\n- {doc}\n  Izvor: {meta['source']} | {meta['published_at']}\n"
        sources.append({
            "title": meta["title"],
            "source": meta["source"],
            "url": meta["url"]
        })

    prompt = f"""Ti si ekspert za međunarodne konflikte i geopolitiku.
Odgovaraj na osnovu sljedećih vijesti, isključivo na bosanskom jeziku.
Ako informacija nije u vijestima, reci to jasno.

VIJESTI:
{context}

PITANJE: {request.question}"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": sources
    }