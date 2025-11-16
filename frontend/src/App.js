// src/App.jsx
import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage = { sender: "user", text: trimmed, ts: Date.now() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/ask-weather", {
        query: trimmed,
      });

      const botMessage = {
        sender: "bot",
        text: res.data.response ?? "No response from server.",
        ts: Date.now(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      const botMessage = {
        sender: "bot",
        text: "⚠️ Could not reach the backend. Is it running on port 8000?",
        ts: Date.now(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="app-title-block">
          <h1 className="app-title">Weather Chat</h1>
          <p className="app-subtitle">
            Ask in plain English. Example: <b>weather in Mumbai tomorrow</b>
          </p>
        </div>
      </header>

      <main className="chat-wrapper">
        <div className="chat-window">
          {messages.map((m) => (
            <div
              key={m.ts}
              className={
                m.sender === "user" ? "chat-bubble user" : "chat-bubble bot"
              }
            >
              {m.text}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble bot">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <form className="chat-input-row" onSubmit={handleSubmit}>
          <input
            className="chat-input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type something... e.g. 'weather in Pune today'"
          />
          <button className="chat-send-btn" disabled={loading}>
            {loading ? "..." : "Send"}
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;
