# Revised Hackathon Plan – VeriGreen AI (ESG Audit Platform)

## 🎯 Objective
Build an **autonomous, zero‑cloud‑cost ESG audit platform** that automatically extracts, validates, and scores ESG claims from corporate disclosures (SEBI BRSR, sustainability PDFs, web reports). The solution addresses the challenges highlighted in the referenced ESG video:
- **Data fragmentation & multilingual PDFs** → robust Playwright + OCR pipeline.
- **Green‑washing risk** → evidence‑backed credibility scoring using a local LLM.
- **High verification costs** → 4‑bit quantized Llama‑3 running locally via Ollama.
- **Regulatory compliance & transparency** → full citation trails and downloadable trust‑badge PDFs.

## 🗂️ Repository Layout (updated)
```
verigreen-ai/
├─ .git/                     # git repo (initialized)
├─ README.md                 # high‑level description (already created)
├─ HackathonPlan_v2.md       # this refined plan
├─ CHANGELOG.md              # chronological log of actions
├─ backend/                  # FastAPI service
│   ├─ app/
│   │   ├─ core/
│   │   ├─ models/
│   │   ├─ routes/
│   │   └─ services/
│   ├─ Dockerfile
│   └─ requirements.txt
├─ scraper/                  # Playwright Docker scraper
│   ├─ scripts/
│   │   └─ crawl.py
│   └─ Dockerfile
├─ frontend/                 # React + Vite UI
│   ├─ src/
│   ├─ public/
│   └─ Dockerfile
├─ cli/                      # Typer‑based command line tool
│   └─ main.py
├─ docker-compose.yml        # orchestrates ollama, scraper, api, db, ui
└─ data/                     # .gitignore – runtime data (PDFs, DB files)
```

## 📦 Core Components (with video‑aligned features)
| Component | Technology | Video‑aligned Feature |
|-----------|------------|-----------------------|
| **Scraper** | Playwright (Docker) + proxy rotation | Handles fragmented, multi‑language sources, overcomes anti‑bot blocks. |
| **PDF/Text extraction** | `pdfplumber` + `pytesseract` (OCR) | Extracts tables & scanned text for accurate data. |
| **LLM inference** | Ollama + 4‑bit Llama‑3 (quantized) | Zero‑cloud OPEX, > 70 % token‑cost reduction, fast local inference. |
| **Embedding + retrieval** | `sentence‑transformers` via Ollama → ChromaDB | Semantic search for evidence, solves data‑quality issue. |
| **Claim detection & scoring** | Prompt‑engineered LLM (credibility 1‑5) | Directly mitigates green‑washing risk. |
| **Evidence citation** | PDF page anchor links, auto‑generated PDFs | Provides transparent traceability required by regulators. |
| **Dashboard** | React + Tailwind (i18n) | Multilingual UI for Indian market (Hindi/English). |
| **CLI** | Typer | Quick one‑liner for auditors, generates trust‑badge PDFs. |
| **Packaging** | Docker Compose | One‑command dev & production setup, reproducible for judges. |

## 📅 8‑Week Sprint (aligned with PPT phases)
| Week | Milestone |
|------|-----------|
| **1‑2** | Scaffold repo, Docker‑Compose, Playwright scraper prototype. |
| **3‑4** | Integrate Ollama, implement claim‑detection prompt, expose FastAPI `/audit` endpoint. |
| **5‑6** | Add ChromaDB, evidence retrieval, generate trust‑badge PDFs (Reportlab). |
| **7‑8** | Build React dashboard with i18n, finish CLI, write documentation, record demo video. |

## 📊 Deliverables for Judges
- **Live demo**: Upload a sample BRSR PDF → Dashboard shows claim table with credibility scores and clickable citations.
- **Trust‑badge PDF** for a low‑score claim (visible evidence link).
- **CLI demo**: `verigreen audit sample.pdf --output report.pdf`.
- **Technical write‑up** (README + architecture diagram).
- **Video walkthrough** (< 3 min) covering data flow, UI, and badge generation.

## 🛠️ Immediate Next Steps (to be committed now)
1. **Initialize Git repo** (`git init`).
2. **Add** `README.md`, `HackathonPlan_v2.md`, `CHANGELOG.md`. 
3. **Commit** with message `Init project with refined ESG audit plan`. 
4. **Log** the action in `CHANGELOG.md` (date, author, description).

---
### 📌 How we’ll keep the log
Every meaningful action (file creation, dependency change, Docker configuration) will be appended to `CHANGELOG.md` in standard [Keep a Changelog](https://keepachangelog.com) format. This satisfies the “maintain the log of everything” requirement.

---
**Ready to materialize the plan** – I’ll now:
- Create `HackathonPlan_v2.md` (this file).
- Create `CHANGELOG.md` with the initial entry.
- Initialise the git repository and make the first commit.

Let me know if you need any adjustment before I run those commands.