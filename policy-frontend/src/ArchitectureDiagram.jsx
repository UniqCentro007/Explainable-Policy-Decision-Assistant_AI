import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  themeVariables: {
    fontFamily: 'Inter, system-ui, sans-serif',
    mainBkg: '#0f172a',
    lineColor: '#334155',
    nodeBorder: '#334155',
    clusterBkg: 'rgba(255, 255, 255, 0.02)',
    clusterBorder: '#1e293b',
  }
});

const ArchitectureDiagram = () => {
  const mermaidRef = useRef(null);

  useEffect(() => {
    if (mermaidRef.current) {
      mermaid.run({
        nodes: [mermaidRef.current],
      });
    }
  }, []);

  // Professional Left-to-Right Layout with Subgraphs
  const chart = `
    graph LR
      %% Global Styles
      classDef client fill:#0ea5e9,stroke:#0284c7,stroke-width:2px,color:#fff;
      classDef service fill:#1e293b,stroke:#38bdf8,stroke-width:1px,color:#e2e8f0;
      classDef storage fill:#0f172a,stroke:#0891b2,stroke-width:2px,stroke-dasharray: 5 5,color:#22d3ee;
      classDef engine fill:#7c3aed,stroke:#020617,stroke-width:1px,color:#fff;

      subgraph UI [User Interface Layer]
        U[fa:fa-user User]:::client
        Dash[fa:fa-desktop Dashboard UI]:::service
        Login[fa:fa-lock Login Screen]:::service
      end

      subgraph Middle [Application Logic]
        Auth[fa:fa-shield-halved Auth Gate]:::service
        RAG[fa:fa-gears RAG Engine]:::service
      end

      subgraph Intelligence [Intelligence & Data]
        MySQL[(fa:fa-database MySQL DB)]:::storage
        Chroma[(fa:fa-microchip ChromaDB)]:::storage
        Groq{{fa:fa-brain Groq LLM}}:::engine
      end

      %% Flows
      U --> Login
      Login --> Auth
      Auth <--> MySQL
      
      U --> Dash
      Dash --> RAG
      RAG <--> Chroma
      RAG --> Groq
      RAG -. Audit Logs .-> MySQL
      
      %% Styling the subgraphs
      style UI fill:transparent,stroke:#334155,stroke-dasharray: 5 5
      style Middle fill:transparent,stroke:#334155,stroke-dasharray: 5 5
      style Intelligence fill:transparent,stroke:#334155,stroke-dasharray: 5 5
  `;

  return (
    <div className="bg-slate-900/40 backdrop-blur-md p-12 rounded-[2.5rem] border border-white/10 shadow-2xl mt-12">
      <div className="flex flex-col items-center mb-10">
        <h3 className="text-[11px] font-black text-cyan-500 uppercase tracking-[0.5em]">
          System Infrastructure Flow
        </h3>
        <div className="h-1 w-20 bg-gradient-to-r from-transparent via-cyan-500 to-transparent mt-4 opacity-50"></div>
      </div>
      
      <div 
        ref={mermaidRef} 
        className="mermaid flex justify-center opacity-90 hover:opacity-100 transition-opacity duration-500"
        id="mermaid-diagram"
      >
        {chart}
      </div>
    </div>
  );
};

export default ArchitectureDiagram;