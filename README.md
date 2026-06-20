# 📈 Autonomous Quantitative Edge Pipeline (CS2 Esports)

## Overview
This repository contains the frontend visualization and the backend architecture documentation for a fully autonomous, self-healing Data Engineering and Quantitative Analytics pipeline. 

The system continuously extracts live esports odds, dynamically strips bookmaker vig to compute true implied probabilities, and cross-references them against historical match outcomes to detect mathematical market inefficiencies.

> **Note on the Live Demo:** The live Streamlit dashboard running on GitHub/Streamlit Cloud operates using a static snapshot of the production database. The production PostgreSQL instance runs on a secure, bare-metal Proxmox LXC container. A fallback mechanism natively catches offline database connections and loads pre-computed CSV extracts to ensure this showcase remains 100% online.

## 🏗️ System Architecture & ETL Orchestration

The backend operates entirely without manual intervention, utilizing **n8n** to orchestrate two asynchronous ETL cycles. 

### 1. The 2-Hour Odds Ingestion Cycle (AI Parsing Layer)
Traditional CSS scraping is brittle and fails against dynamic web elements. This pipeline bypasses standard scrapers by deploying an autonomous LLM parsing layer.
*   **Anti-Bot Evasion:** Integrates FlareSolverr to autonomously bypass Cloudflare protections.
*   **LLM Extraction:** Routes raw HTML to a local **Qwen 2.5 LLM** (via Ollama) to dynamically parse unstructured odds data into standardized JSON.
*   **Database:** Upserts validated data into a normalized PostgreSQL database.

![Odds Ingestion Pipeline](Screenshot%202026-06-17%20183546.png)

### 2. The Nightly Results Logger
Executes a nightly HTTP request cycle to extract resolved match outcomes, utilizing programmatic entity resolution to reconcile inconsistent team name variants across different data providers.

![Results Logger Pipeline](Screenshot%202026-06-17%20183621.png)

## 📊 Quantitative Analytics & Edge Detection
The pipeline does not just log data; it processes it to find actionable intelligence.
*   **Vig-Stripping:** Implements probability calibration algorithms to strip the built-in bookmaker margins from raw odds.
*   **True Implied Probability:** Calculates the actual mathematical win probability assigned by the market.
*   **Market Calibration Testing:** Cross-references true probabilities against actual match results (using complex SQL `JOIN` and anti-join logic) to visualize where the bookmakers are systematically overvaluing or undervaluing specific outcomes.

## 🛠️ Tech Stack
*   **Data Engineering & Orchestration:** n8n, PostgreSQL (pgvector)
*   **AI & Automation:** Local LLMs (Qwen 2.5), Ollama, FlareSolverr, OpenCV
*   **Frontend UI & Analytics:** Python, Streamlit, Pandas
*   **Infrastructure:** Proxmox, LXC Containers, Docker, Linux (Xubuntu)
