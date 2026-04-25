import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime

print("⏳ Učitavam model za embedinge...")
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("conflict_articles")

def embed_articles():
    conn = sqlite3.connect("conflict_intel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, source, published_at, url FROM articles")
    articles = cursor.fetchall()
    conn.close()

    existing_ids = set(collection.get()["ids"])
    new_articles = [a for a in articles if str(a[0]) not in existing_ids]

    if not new_articles:
        print("✅ Svi članci već su u ChromaDB")
        return

    print(f"📊 Dodajem {len(new_articles)} novih članaka u ChromaDB...")

    for article in new_articles:
        id_, title, content, source, published_at, url = article
        text = f"{title}. {content or ''}"
        embedding = model.encode(text).tolist()

        collection.add(
            ids=[str(id_)],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "title": title,
                "source": source or "",
                "published_at": published_at or "",
                "url": url or ""
            }]
        )

    print(f"✅ Gotovo! {len(new_articles)} članaka dodano u ChromaDB\n")

if __name__ == "__main__":
    embed_articles()