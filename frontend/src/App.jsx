import { useState, useEffect } from "react"
import axios from "axios"
import "./App.css"

const API = "http://127.0.0.1:8000"

function App() {
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [articles, setArticles] = useState([])
  const [tab, setTab] = useState("chat")

  useEffect(() => {
    axios.get(`${API}/stats`).then(r => setStats(r.data))
    axios.get(`${API}/articles?limit=20`).then(r => setArticles(r.data))
  }, [])

  const sendMessage = async () => {
    if (!question.trim()) return
    const userMsg = { role: "user", text: question }
    setMessages(prev => [...prev, userMsg])
    setQuestion("")
    setLoading(true)
    try {
      const res = await axios.post(`${API}/chat`, { question })
      setMessages(prev => [...prev, {
        role: "ai",
        text: res.data.answer,
        sources: res.data.sources
      }])
    } catch {
      setMessages(prev => [...prev, { role: "ai", text: "Greška pri povezivanju sa API-jem." }])
    }
    setLoading(false)
  }

  return (
    <div className="app">
      <header>
        <h1>🌍 Conflict Intel</h1>
        {stats && (
          <div className="stats">
            <span>📰 {stats.total_articles} članaka</span>
            <span>📡 {stats.total_sources} izvora</span>
            <span>🕒 {stats.last_scrape?.slice(0, 16)}</span>
          </div>
        )}
      </header>

      <nav>
        <button className={tab === "chat" ? "active" : ""} onClick={() => setTab("chat")}>Chat</button>
        <button className={tab === "news" ? "active" : ""} onClick={() => setTab("news")}>Vijesti</button>
      </nav>

      {tab === "chat" && (
        <div className="chat">
          <div className="messages">
            {messages.length === 0 && (
              <div className="placeholder">Postavi pitanje o aktualnim konfliktima...</div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role}`}>
                <p>{msg.text}</p>
                {msg.sources && (
                  <div className="sources">
                    {msg.sources.map((s, j) => (
                      <a key={j} href={s.url} target="_blank" rel="noreferrer">
                        {s.source}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && <div className="message ai"><p>⏳ Tražim odgovor...</p></div>}
          </div>
          <div className="input-row">
            <input
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendMessage()}
              placeholder="Npr: Šta se dešava u Maliju?"
            />
            <button onClick={sendMessage} disabled={loading}>Pitaj</button>
          </div>
        </div>
      )}

      {tab === "news" && (
        <div className="news">
          {articles.map((a, i) => (
            <a key={i} href={a.url} target="_blank" rel="noreferrer" className="article">
              <span className="source">{a.source}</span>
              <p>{a.title}</p>
              <span className="date">{a.published_at?.slice(0, 16)}</span>
            </a>
          ))}
        </div>
      )}
    </div>
  )
}

export default App