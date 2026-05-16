"use client";

import { useState, useEffect, useRef, FormEvent } from "react";

type FeedItem = {
  id: string;
  type: "call" | "result" | "error";
  title: string;
  body: string;
  time: string;
};

type ChatMessage = {
  id: string;
  role: "user" | "agent" | "system";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("Connecting...");
  const wsRef = useRef<WebSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const feedEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Scroll to bottom when items change
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    feedEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [feed]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      wsRef.current?.close();
    };
  }, []);

  const connectWebSocket = () => {
    const productionUrl = "wss://countybudgetwatchdog-81214252020.europe-west1.run.app/ws/chat";
    const ws = new WebSocket(productionUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus("Connected");
      setMessages((prev) => [
        ...prev,
        { id: Date.now().toString(), role: "system", content: "Connected to Watchdog backend." },
      ]);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const time = new Date().toLocaleTimeString();

      switch (data.type) {
        case "message":
          setStatus("Connected");
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString() + Math.random(), role: data.role, content: data.content },
          ]);
          break;
        case "status":
          setStatus(data.content);
          break;
        case "tool_call":
          setFeed((prev) => [
            ...prev,
            {
              id: Date.now().toString() + Math.random(),
              type: "call",
              title: `Execute: ${data.tool}()`,
              body: JSON.stringify(data.args, null, 2),
              time,
            },
          ]);
          break;
        case "tool_result":
          setFeed((prev) => [
            ...prev,
            {
              id: Date.now().toString() + Math.random(),
              type: "result",
              title: `Result: ${data.tool}()`,
              body: data.result,
              time,
            },
          ]);
          break;
        case "error":
          setStatus("Error");
          setMessages((prev) => [
            ...prev,
            { id: Date.now().toString(), role: "system", content: `Error: ${data.content}` },
          ]);
          break;
      }
    };

    ws.onclose = () => {
      setStatus("Disconnected. Reconnecting in 3s...");
      setTimeout(connectWebSocket, 3000);
    };
  };

  const sendMessage = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    wsRef.current.send(JSON.stringify({ message: input }));
    setMessages((prev) => [
      ...prev,
      { id: Date.now().toString(), role: "user", content: input },
    ]);
    setInput("");
  };

  return (
    <div className="dashboard-container">
      {/* Left Pane: Live Feed */}
      <div className="left-pane">
        <h2 className="pane-title">Live Dashboard Monitoring Feed</h2>
        <p className="pane-subtitle">Real-time internal agent activity and system operations.</p>
        
        <div className="feed-container">
          {feed.length === 0 ? (
            <div style={{ color: "#666", fontStyle: "italic", textAlign: "center", marginTop: "2rem" }}>
              Awaiting agent activity...
            </div>
          ) : (
            feed.map((item) => (
              <div key={item.id} className={`feed-item ${item.type}`}>
                <div className="feed-item-header">
                  <span className="feed-item-title">{item.title}</span>
                  <span className="feed-item-time">{item.time}</span>
                </div>
                <div className="feed-item-body">{item.body}</div>
              </div>
            ))
          )}
          <div ref={feedEndRef} />
        </div>
      </div>

      {/* Right Pane: Chat Box */}
      <div className="right-pane">
        <h2 className="pane-title">Watchdog Interaction Terminal</h2>
        <p className="pane-subtitle">System Status: <span className={status === "Connected" ? "" : "pulse"} style={{ color: status === "Connected" ? "var(--primary)" : "#aaa" }}>{status}</span></p>

        <div className="chat-container">
          <div className="chat-messages">
            {messages.length === 0 ? (
              <div style={{ color: "#666", fontStyle: "italic", textAlign: "center", marginTop: "auto", marginBottom: "auto" }}>
                Send a message to start monitoring public finance.
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`chat-message ${msg.role}`}>
                  {msg.content}
                </div>
              ))
            )}
            <div ref={chatEndRef} />
          </div>
          
          <form onSubmit={sendMessage} className="chat-input-area">
            <input
              type="text"
              className="chat-input"
              placeholder="E.g., Check budget for Westlands, Nairobi and send SMS alert..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={status.includes("Disconnected")}
            />
            <button 
              type="submit" 
              className="chat-send-btn"
              disabled={!input.trim() || status.includes("Disconnected")}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
