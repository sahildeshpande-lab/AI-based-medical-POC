import { useState } from "react";
import "./App.css";


function App() {

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const askQuestion = async () => {
    if (!question) return;

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/query?q=" + encodeURIComponent(question), {
        method: "POST"
      });

      const data = await res.json();
      setResult(data);

    } catch (err) {
      console.error(err);
      alert("Error contacting server");
    }

    setLoading(false);
  };

  const copySummary = () => {

    if (!result) return;

    const text = `
Disease: ${result.disease}

Bottom Line:
${result.bottom_line?.map(b => "- " + b).join("\n")}

Treatment Summary:
${result.treatment_summary}

Drugs:
${result.drugs?.map(d => d.name).join(", ")}

Citations:
${result.citations?.join(", ")}
`;

    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  return (
    <div style={{maxWidth:900, margin:"40px auto", fontFamily:"Arial"}} className="container">

      <h1 className="title"> AI based Assistant</h1>

      <div style={{display:"flex", gap:10}} className="search-box">
        <input
          style={{flex:1, padding:12, fontSize:16}}
          placeholder="Ask a clinical question..."
          value={question}
          onChange={(e)=>setQuestion(e.target.value)}
        />

        <button onClick={askQuestion}>
          Ask
        </button>
      </div>

      {loading && <p>Searching medical evidence...</p>}

      {result && (

        <div style={{marginTop:40}} className="card">

          <h2>Disease Name</h2>
          <p>{result.disease}</p>

          <h3>Disease Summary</h3>
          <p>{result.disease_summary}</p>

          <h3>Bottom Line</h3>
          <ul>
            {result.bottom_line?.map((b,i)=>(
              <li key={i}>{b}</li>
            ))}
          </ul>

          <h3>Treatment Summary</h3>
          <p>{result.treatment_summary}</p>

          <h3>Recommended Drugs</h3>
          <ul>
            {result.drugs?.map((d,i)=>(
              <li key={i}>
                {d.name} (RxNorm: {d.rxnorm})
              </li>
            ))}
          </ul>

          <h3>Sources</h3>
          <ul>
            {result.citations?.map((pmid)=>(
              <li key={pmid}>
                <a
                  href={`https://pubmed.ncbi.nlm.nih.gov/${pmid}/`}
                  target="_blank"
                  rel="noreferrer"
                >
                  PubMed {pmid}
                </a>
              </li>
            ))}
          </ul>

          <h3>What Would Change This Answer</h3>
          <p>{result.contraindications}</p>

          <button onClick={copySummary}>
            Copy Summary with Citations
          </button>

        </div>

      )}

    </div>
  );
}

export default App;