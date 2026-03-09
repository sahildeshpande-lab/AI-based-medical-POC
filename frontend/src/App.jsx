import React, { useState } from "react";
import "./App.css";

export default function App() {

  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [finished, setFinished] = useState(false);

  const ask = async () => {

    if (!query.trim()) return;

    setLoading(true);
    setFinished(false);

    try {

      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: query
        })
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("API Error:", err);
        setLoading(false);
        return;
      }

      const json = await res.json();

      setData(json);
      setFinished(true);

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
          <button className="newBtn">✎ New Conversation</button>
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

      {(loading || finished) && (
        <div className="responseSection">

          {finished && (
            <div className="searchEcho">
              {query}
            </div>
          )}

          {loading && (
            <div className="thinkingCard">

              <div className="thinkingHeader">
                <span className="spinner"></span>
                Thinking...
              </div>

              <div className="skeletonLine"></div>
              <div className="skeletonLine"></div>
              <div className="skeletonLine short"></div>

            </div>
          )}

          {finished && !loading && (
            <div className="finishedThinking">

              <svg
                className="checkmark"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>

              Finished thinking

            </div>
          )}

          {data && (
            <div className="answerContainer">

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
              <div className="actions">
                <button className="actionBtn">👍 Helpful</button>
                <button className="actionBtn">👎 Not helpful</button>
                <button className="actionBtn">📋 Copy</button>
              </div>

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
          )}

        </div>
      )}``

    </div>
  );
}