# VeriGreen AI – Agentic ESG Audit

**Hackathon project** built to automatically verify ESG claims from corporate disclosures using a **local, zero‑cloud‑cost LLM**.

- Scrapes PDFs (SEBI BRSR, sustainability reports) via Playwright.
- Performs **claim detection**, **pillar classification**, and **evidence‑backed credibility scoring** with a 4‑bit quantized Llama‑3 (Ollama).
- Stores semantic vectors in **ChromaDB** for fast retrieval.
- Generates **trust‑badge PDFs** and a full audit report (HTML/PDF/CSV).
- Provides a **React dashboard** and a **Typer CLI**.
- Multilingual UI & zero OPEX – ideal for civic watchdogs, investors, regulators, and corporate ESG teams.
