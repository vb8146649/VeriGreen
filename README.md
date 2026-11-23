# VeriGreen AI – Agentic ESG Audit

**Hackathon project** built to automatically verify ESG claims from corporate disclosures using a **local, zero‑cloud‑cost LLM**.

- Scrapes PDFs (SEBI BRSR, sustainability reports) via Playwright.
- Performs **claim detection**, **pillar classification**, and **evidence‑backed credibility scoring** with a 4‑bit quantized Llama‑3 (Ollama).
- Stores semantic vectors in **ChromaDB** for fast retrieval.
- Generates **trust‑badge PDFs** and a full audit report (HTML/PDF/CSV).
- Provides a **React dashboard** and a **Typer CLI**.
- Multilingual UI & zero OPEX – ideal for civic watchdogs, investors, regulators, and corporate ESG teams.

---

## System Design

### High‑Level Architecture

```mermaid
flowchart TB
    subgraph USER_LAYER["👤 User Layer"]
        UI["React Dashboard\n(Vite + Tailwind + i18n)"]
        CLI["Typer CLI\n(verigreen audit / badge)"]
    end

    subgraph API_LAYER["⚡ API Layer"]
        API["FastAPI Backend\n(/audit  /report  /badge)"]
    end

    subgraph INTELLIGENCE_LAYER["🧠 Intelligence Layer"]
        CLAIM["Claim Detector\n(Prompt Engine)"]
        SCORER["Credibility Scorer\n(1‑5 Scale)"]
        RETRIEVER["Evidence Retriever\n(Semantic Search)"]
    end

    subgraph INFERENCE_LAYER["🔧 Local Inference Layer"]
        OLLAMA["Ollama Server\n(4‑bit Quantized Llama‑3)"]
        EMBED["Embedding Model\n(all‑MiniLM / nomic‑embed)"]
    end

    subgraph DATA_LAYER["💾 Data Layer"]
        CHROMA["ChromaDB\n(Vector Store)"]
        FILESTORE["Local File Store\n(PDFs, Reports, Badges)"]
    end

    subgraph INGESTION_LAYER["📥 Ingestion Layer"]
        SCRAPER["Playwright Scraper\n(Dockerized + Proxy Rotation)"]
        PARSER["PDF Parser\n(pdfplumber + pytesseract OCR)"]
        CHUNKER["Text Chunker\n(~200 word sections)"]
    end

    subgraph EXTERNAL["🌐 External Sources"]
        BRSR["SEBI BRSR Filings"]
        CSR["Corporate Sustainability\nReports (Websites)"]
        GOV["Government Portals\n(MCA, Stock Exchanges)"]
    end

    %% External → Ingestion
    BRSR --> SCRAPER
    CSR --> SCRAPER
    GOV --> SCRAPER

    %% Ingestion pipeline
    SCRAPER --> PARSER
    PARSER --> CHUNKER
    CHUNKER -->|"text chunks"| EMBED
    EMBED -->|"vectors"| CHROMA
    CHUNKER -->|"raw text"| FILESTORE

    %% User → API
    UI -->|"HTTP / WebSocket"| API
    CLI -->|"HTTP"| API

    %% API → Intelligence
    API --> CLAIM
    API --> SCORER
    API --> RETRIEVER

    %% Intelligence → Inference
    CLAIM -->|"prompt"| OLLAMA
    SCORER -->|"prompt"| OLLAMA
    RETRIEVER -->|"query vector"| EMBED

    %% Intelligence → Data
    RETRIEVER -->|"semantic search"| CHROMA
    SCORER -->|"fetch evidence"| CHROMA

    %% Output
    API -->|"PDF / JSON"| FILESTORE
```

### Request Flow (Single Audit)

```mermaid
sequenceDiagram
    actor User
    participant UI as React / CLI
    participant API as FastAPI
    participant Scraper as Playwright Scraper
    participant Parser as PDF Parser + OCR
    participant LLM as Ollama (Llama‑3 4‑bit)
    participant VDB as ChromaDB
    participant Badge as Badge Generator

    User->>UI: Upload PDF / paste URL
    UI->>API: POST /audit {file | url}

    alt URL provided
        API->>Scraper: download(url)
        Scraper-->>API: raw PDF bytes
    end

    API->>Parser: extract_text(pdf)
    Parser-->>API: text chunks + tables

    API->>LLM: embed(chunks)
    LLM-->>API: vectors
    API->>VDB: store(vectors, metadata)

    loop For each chunk
        API->>LLM: detect_claim(chunk)
        LLM-->>API: {claim, pillar, score, reason}
    end

    loop For each low‑score claim (≤ 3)
        API->>VDB: semantic_search(claim_text)
        VDB-->>API: top‑k evidence snippets
        API->>LLM: re‑score(claim + evidence)
        LLM-->>API: updated score + citations
    end

    API->>Badge: generate(claims, citations)
    Badge-->>API: badge PDFs + report PDF

    API-->>UI: JSON response + download links
    UI-->>User: Dashboard view + downloadable badges
```

### Component Interaction Map

```mermaid
graph LR
    subgraph Input
        A["📄 PDF Upload"]
        B["🔗 URL Input"]
    end

    subgraph Processing
        C["🕷️ Scraper"]
        D["📝 Parser + OCR"]
        E["✂️ Chunker"]
        F["🧠 LLM Claim Detection"]
        G["🔍 Evidence Retrieval"]
        H["⭐ Credibility Scoring"]
    end

    subgraph Storage
        I["💾 ChromaDB"]
        J["📁 File Store"]
    end

    subgraph Output
        K["📊 ESG Report PDF"]
        L["🏷️ Trust Badge PDF"]
        M["📈 Dashboard View"]
        N["📋 CSV Export"]
    end

    A --> D
    B --> C --> D
    D --> E --> F
    E -->|"embed"| I
    F --> G
    G -->|"query"| I
    G --> H
    H --> K
    H --> L
    H --> M
    H --> N
    K --> J
    L --> J
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Scraper** | Playwright (Docker) | Headless browsing, proxy rotation, anti‑bot evasion |
| **PDF Extraction** | pdfplumber + pytesseract | Tables, scanned text, multilingual OCR |
| **LLM** | Ollama + 4‑bit Llama‑3 | Local inference, zero cloud cost |
| **Embeddings** | all‑MiniLM / nomic‑embed via Ollama | Fast semantic vectors |
| **Vector Store** | ChromaDB (SQLite) | Embeddable, Docker‑friendly |
| **API** | FastAPI (Python) | Async, auto‑docs (Swagger) |
| **CLI** | Typer | One‑liner audit commands |
| **Frontend** | React + Vite + Tailwind CSS | Responsive, i18n‑ready dashboard |
| **Badge/Report** | ReportLab | PDF generation with citation links |
| **Orchestration** | Docker Compose | Single‑command dev/prod environment |

---

## Quick Start (coming soon)
```bash
docker compose up --build
# Dashboard  → http://localhost:3000
# API docs   → http://localhost:8000/docs
# CLI        → verigreen audit sample.pdf
```
