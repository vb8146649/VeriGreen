# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-11-23
### Added
- README.md with high‑level project description.
- HackathonPlan_v2.md – refined ESG audit plan (this document).
- Initial repository structure (folders are created later during development).

## [Unreleased]
### Added
- FastAPI application entry point with startup database initialization and dashboard CORS.
- Audit history API and dashboard view, report download, and claim badge download endpoints.
- Unified configurable local data paths for uploads, reports, badges, SQLite, and ChromaDB.
- Persisted evidence snippets and verification verdicts with claim records; scoped retrieval to the current audit.
- README setup steps for the Docker stack, local Ollama models, dashboard, API, and CLI.
- Host Ollama development instructions for running the API and dashboard without Docker.
- Four-page synthetic BRSR-style test disclosure, reproducible generator, and expected discrepancy notes under `sample/`.

### Fixed
- Connected the audit pipeline to the actual database and service function signatures.
- Added uploaded PDF signature validation and URL based PDF acquisition in the audit pipeline.
- Corrected Docker build context paths, and added Tesseract to the backend image for scanned PDF OCR.
- Reduced PDF report table width to fit the page and escaped user supplied text in PDF paragraphs.
- Normalized and bounded LLM generated scores, pillars, claim text, and citations before saving.
