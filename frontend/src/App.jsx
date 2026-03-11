import React, { useState } from "react";
import "./App.css";

export default function App() {

  const [query, setQuery] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const ask = async () => {

    if (!query.trim()) return;

    setLoading(true);
    const currentQuery = query;

    try {

      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: currentQuery
        })
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("API Error:", err);
        setLoading(false);
        return;
      }

      const json = await res.json();

      setHistory(prev => [
        ...prev,
        {
          question: currentQuery,
          data: json
        }
      ]);

      setQuery("");

    } catch (err) {
      console.error("Network error:", err);
    }

    setLoading(false);
  };

  return (
    <div className="page">

      <div className="navbar">
        <div className="logo">
          PubMed Based Retriever<span className="reg">®</span>
        </div>

        <div className="navButtons">
          <button className="shareBtn">Share</button>
          <button
            className="newBtn"
            onClick={() => setHistory([])}
          >
            ✎ New Conversation
          </button>
          <div className="menu">☰</div>
        </div>
      </div>

      <div className="searchArea">

        <div className="orangeCircle"></div>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a medical question..."
          onKeyDown={(e) => e.key === "Enter" && ask()}
          autoFocus
        />

        

      </div>

        {loading && (
                <div className="thinkingCard">
                  <div className="thinkingHeader">
                    <span className="spinner"></span>
                    Thinking...
                  </div>
                </div>
              )}

      <div className="responseSection">

        {history.map((item, idx) => {

          const data = item.data;

          return (
            <div key={idx} className="answerContainer">
              

              <div className="searchEcho">
                {item.question}
              </div>

              <p className="diseaseIntro">
                A <b>{data.disease}</b> {data.disease_summary}
              </p>

              <p className="treatmentIntro">
                {data.treatment_summary}
              </p>

              {data.drugs?.length > 0 && (
                <>
                  <h3 className="sectionTitle">Drugs</h3>

                  <div className="drugGrid">
                    {data.drugs.map((d, i) => (
                      <div key={i} className="drugCard">

                        <div className="drugName">
                          {d.name}
                        </div>

                        {d.rxnorm &&
                          <div className="drugMeta">
                            RxNorm: {d.rxnorm}
                          </div>
                        }

                        {d.dosage &&
                          <div className="drugMeta">
                            {d.dosage.label}
                          </div>
                        }

                      </div>
                    ))}
                  </div>
                </>
              )}

              {data.citations?.length > 0 && (
                <div className="references">

                  <h3 className="sectionTitle">
                    References
                  </h3>

                  {data.citations.map((c, i) => (
                    <div key={i} className="referenceCard">

                      <div className="refNumber">
                        {i + 1}
                      </div>

                      <a
                        href={`https://pubmed.ncbi.nlm.nih.gov/${c}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        PubMed Article {c}
                      </a>

                    </div>
                  ))}

                </div>
              )}

            </div>
          );

        })}



      </div>

    </div>
  );
}