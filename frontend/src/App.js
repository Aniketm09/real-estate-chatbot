import React, { useState, useRef, useEffect } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Legend,
  Tooltip
} from "chart.js";
import "./index.css";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Legend, Tooltip);

const API_URL = "http://127.0.0.1:8000/api/analyze/";

function App() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "👋 Hi! I'm your Real Estate Assistant. Ask me something like: “Analyze Wakad”" }
  ]);
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const chatEndRef = useRef(null);

  // auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setInput("");
    setLoading(true);

    // add bot "typing..."
    setMessages((prev) => [...prev, { sender: "bot", text: "typing...", loading: true }]);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!res.ok) throw new Error("Network error");

      const data = await res.json();

      // replace typing bubble
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { sender: "bot", text: data.summary };
        return updated;
      });

      setResult(data);

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "❌ Error: Unable to reach server." }
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="app-container">
      {/* LEFT CHAT PANEL */}
      <div className="chat-panel shadow-lg">
        <div className="chat-header">
          🏙️ Real Estate Chatbot
        </div>

        <div className="chat-body">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`chat-bubble ${msg.sender === "user" ? "user" : "bot"}`}
            >
              {msg.loading ? (
                <div className="typing">
                  <span></span><span></span><span></span>
                </div>
              ) : (
                msg.text
              )}
            </div>
          ))}
          <div ref={chatEndRef}></div>
        </div>

        <form className="input-bar" onSubmit={handleSubmit}>
          <input
            className="form-control chat-input"
            placeholder="Type your query..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button className="btn btn-primary send-btn" disabled={loading}>
            {loading ? "..." : "Send"}
          </button>
        </form>
      </div>

      {/* RIGHT RESULT PANEL */}
      <div className="result-panel shadow-lg">
        {result ? (
          <>
            <h4 className="section-title">📄 Summary</h4>
            <div className="summary-box">{result.summary}</div>

            {/* Download CSV button */}
            {result.locations?.length > 0 && (
              <a
                href={`http://127.0.0.1:8000/api/download/?area=${result.locations[0]}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline-success download-btn"
              >
                ⬇ Download CSV Data
              </a>
            )}

            <h4 className="section-title mt-4">📈 Trend Chart</h4>
            {result.chartData && (
              <Line
                data={{
                  labels: result.chartData.labels,
                  datasets: result.chartData.datasets.map((ds) => ({
                    ...ds,
                    borderColor: "#007bff",
                    backgroundColor: "rgba(0,123,255,0.2)",
                    tension: 0.3,
                  })),
                }}
              />
            )}

            <h4 className="section-title mt-4">📊 Data Table</h4>
            {result.tableData?.length > 0 ? (
              <table className="table table-striped table-bordered">
                <thead>
                  <tr>
                    {Object.keys(result.tableData[0]).map((col) => (
                      <th key={col}>{col.toUpperCase()}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.tableData.map((row, i) => (
                    <tr key={i}>
                      {Object.entries(row).map(([key, value]) => (
                        <td key={key}>{value}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>No table data available.</p>
            )}
          </>
        ) : (
          <div className="empty-box">Ask something to show results!</div>
        )}
      </div>
    </div>
  );
}

export default App;
