import React, { useState, useRef, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Legend,
  Tooltip,
} from "chart.js";
import "./index.css";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Legend, Tooltip);

// API URL (LOCAL DJANGO SERVER)
const API_URL = "https://real-estate-chatbot-5gi5.onrender.com";

function App() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "👋 Hi! I'm your Real Estate Assistant. Ask something like: Analyze Wakad",
    },
  ]);

  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const chatEndRef = useRef(null);

  // auto scroll
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

    // show typing
    setMessages((prev) => [...prev, { sender: "bot", text: "typing...", loading: true }]);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!res.ok) {
        throw new Error("Server error");
      }

      const data = await res.json();

      // replace typing message
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          sender: "bot",
          text: data.summary,
        };
        return updated;
      });

      setResult(data);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "❌ Server not responding. Please start Django backend." },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="app-container">
      {/* CHAT PANEL */}
      <div className="chat-panel shadow-lg">
        <div className="chat-header">🏙️ Real Estate Chatbot</div>

        <div className="chat-body">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`chat-bubble ${msg.sender === "user" ? "user" : "bot"}`}
            >
              {msg.loading ? (
                <div className="typing">
                  <span></span>
                  <span></span>
                  <span></span>
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

      {/* RESULT PANEL */}
      <div className="result-panel shadow-lg">
        {result ? (
          <>
            <h4 className="section-title">📄 Summary</h4>
            <div className="summary-box">{result.summary}</div>

            {/* DOWNLOAD BUTTON */}
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
                  datasets: result.chartData.datasets?.map((ds) => ({
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
                      {Object.values(row).map((val, j) => (
                        <td key={j}>{val}</td>
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