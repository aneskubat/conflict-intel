🌍 Conflict Intel — AI-Powered News Intelligence System

A real-time conflict and geopolitical news intelligence system that lets you chat with today's news using AI. Built with a RAG (Retrieval-Augmented Generation) architecture to solve a real problem: AI models have outdated knowledge, this system always has today's data.

## 🎯 Problem This Solves

Most AI assistants (ChatGPT, Claude, etc.) have a knowledge cutoff date and can't answer questions about current events. Conflict Intel solves this by continuously scraping live news sources and using RAG to give the AI access to real-time information.

## 🏗️ Architecture
News Sources (BBC, Al Jazeera, Reuters, etc.)
↓
Python Scraper (feedparser, BeautifulSoup)
↓
SQLite Database + ChromaDB Vector Store
↓
RAG Engine (semantic search + context injection)
↓
Groq LLM (Llama 3.3 70B)
↓
Chat Interface

## ⚙️ Tech Stack

- **Backend:** Python, FastAPI
- **AI/ML:** Groq API (Llama 3.3 70B), Sentence Transformers
- **Vector Database:** ChromaDB
- **Database:** SQLite
- **Scraping:** feedparser, BeautifulSoup4
- **Scheduling:** APScheduler

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Groq API key (free at console.groq.com)

### Installation

```bash
git clone https://github.com/aneskubat/conflict-intel.git
cd conflict-intel
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:
GROQ_API_KEY=your_groq_api_key_here

### Usage

```bash
# 1. Scrape latest news
python scraper.py

# 2. Generate embeddings
python embedder.py

# 3. Start chatting
python chat.py
```

## 📰 News Sources

| Source | Coverage |
|--------|----------|
| BBC World | Global news |
| Al Jazeera | Middle East, Global |
| France 24 | Europe, Africa |
| Kyiv Independent | Ukraine conflict |
| Middle East Eye | Middle East |
| DW News | Europe, Global |
| Sky News | Global |
| ReliefWeb | Humanitarian crises |

## 🗺️ Roadmap

- [x] RSS scraper with multiple sources
- [x] Vector database with semantic search
- [x] RAG-powered chat interface
- [ ] FastAPI REST backend
- [ ] React web dashboard
- [ ] Live conflict map (Leaflet.js)
- [ ] Automated scheduling
- [ ] Docker deployment

## 📄 License

MIT