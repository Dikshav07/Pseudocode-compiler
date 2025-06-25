import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [code, setCode] = useState("");
  const [cppCode, setCppCode] = useState("");
  const [output, setOutput] = useState("");
  const [activeTab, setActiveTab] = useState("result");

  const handleCompile = async () => {
    try {
      const res = await axios.post("http://localhost:5000/compile", {
        code: code,
        input: "5", // or use a state for input if needed
      });

      setCppCode(res.data.cpp_code || "C++ code not found");
      setOutput(res.data.output || "No output");
    } catch (err) {
      setOutput("Error: " + err.message);
      setCppCode("");
    }
  };

  const handleCopy = () => {
    const text = activeTab === "result" ? output : cppCode;
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard");
  };

  const handleDownload = () => {
    const blob = new Blob([cppCode], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "generated_code.cpp";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="app-container">
      <h1 className="main-title">Pseudocode to C++ Code</h1>

      <div className="panels">
        <div className="panel">
          <h2>Pseudocode Input</h2>
          <textarea
            placeholder="Paste or type your pseudocode here..."
            value={code}
            onChange={(e) => setCode(e.target.value)}
          ></textarea>
          <button className="glow-btn" onClick={handleCompile}>
            Compile & Generate C++
          </button>
        </div>

        <div className="panel">
          <h2>Output</h2>
          <div className="tabs">
            <button
              className={activeTab === "result" ? "tab active" : "tab"}
              onClick={() => setActiveTab("result")}
            >
              Result
            </button>
            <button
              className={activeTab === "cpp" ? "tab active" : "tab"}
              onClick={() => setActiveTab("cpp")}
            >
              C++ Code
            </button>
          </div>

          <div className="output-box">
            <pre>
              {activeTab === "result"
                ? `Converted to C++\nCompiled with g++\nExecuted\n\nOutput:\n${output}`
                : cppCode}
            </pre>
          </div>

          <div className="btn-group">
            <button className="glow-btn" onClick={handleCopy}>
              Copy to Clipboard
            </button>
            {activeTab === "cpp" && (
              <button className="glow-btn" onClick={handleDownload}>
                Download C++ Code
              </button>
            )}
          </div>
        </div>
      </div>

      <footer>
        <h3>About the Compiler</h3>
        <ul>
          <li>Variable declarations (DECLARE, CONSTANT, ARRAY)</li>
          <li>Input/Output statements (INPUT, OUTPUT)</li>
          <li>Control structures (IF, ELSE, WHILE, REPEAT, FOR)</li>
          <li>Procedures and Functions with parameters</li>
          <li>Logical operators (AND, OR, NOT)</li>
          <li>Assignment with ← or =</li>
        </ul>
        <p>
          The compiled C++ code can be copied and run in any C++ compiler or
          online C++ environment.
        </p>
      </footer>
    </div>
  );
}

export default App;
