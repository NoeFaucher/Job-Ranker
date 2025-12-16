# Job Ranker

> 🚀 AI-powered job ranking using local NLP and embeddings

## Overview

Job Ranker is a local-first, AI-powered job aggregation and ranking system designed to optimize the job search process.

It collects job offers from multiple platforms, extracts required skills using a small language model, and ranks job postings based on their relevance to a candidate profile using multilingual embeddings.

The project was born from a real-world problem: job searching is time-consuming and often involves browsing through many irrelevant offers. Job Ranker aims to reduce this friction by surfacing the most relevant opportunities first.

---

## Key Features

* 🔎 **Multi-source job scraping** (LinkedIn, Indeed – more to come)
* 🧠 **Skill extraction using a Small Language Model (SLM)**
* 📐 **Semantic job ranking using embeddings and cosine similarity**
* ⚡ **Fully local execution** (no GPU required)
* 🗂️ **Centralized job storage** with SQLite
* 🌐 **Web interface** for browsing and ranking job offers

---

## Architecture (High Level)

1. **Data Collection**

   * Job scraping from multiple platforms using `jobspy`
   * Data stored in a Pandas DataFrame and persisted in a SQLite database

2. **AI Processing & Ranking**

   * Skill extraction from job descriptions using **Gemma 3 (1B)**

     * Chosen for its multilingual capabilities and efficiency on CPU
   * Skill representation using **bge-m3 embeddings**

     * Lightweight, multilingual, and among the best-performing embedding models
   * Job relevance computed via **cosine similarity**
   * Offers are ranked according to their semantic alignment with the candidate profile

3. **Visualization**

   * Web-based interface to explore, filter, and prioritize job offers

---

## Tech Stack

* **Language**: Python
* **Scraping**: jobspy
* **NLP / AI**:

  * Gemma 3 (1B) – skill extraction
  * bge-m3 – multilingual embeddings
* **Data**: Pandas, SQLite
* **Similarity**: Cosine similarity
* **Web**: [Web interface documentation](web_app/README.md)

---

## Requirements

* Python **3.11+**
* CPU-only machine (tested on 8 cores / 16 GB RAM)
* No GPU required

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

### Run full pipeline (scraping + ranking)

```bash
python job_scrapper.py -c example_config.yaml
```

### Run ranking only (skip scraping)

```bash
python job_scrapper.py -c example_config.yaml --process-only
```

The configuration file allows you to define:

* Job sources
* Search keywords
* Target skills
* Language preferences

---

## Project Status & Roadmap

🚧 **Work in progress**

Planned improvements:

* Support for additional job platforms

If you are reading this, feel free to contribute.

---

## Motivation

Job Ranker was developed alongside my own job search as a Data Scientist.

Beyond its practical use, the project serves as a real-world application of:

* NLP for unstructured text
* Efficient AI pipelines under hardware constraints
* End-to-end data and AI system design

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.