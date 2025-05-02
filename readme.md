# QwikNews Backend

This is the backend service for **QwikNews**, a personal project built to showcase my skills in backend development, machine learning integration, and API design. It powers the data processing and summarization behind a sample frontend at [qwiknews.netlify.app](https://qwiknews.netlify.app).

⚠️ **Note**: This API is not intended for public or production use. It is a demonstration project.

---

## 🔧 Technologies Used

- **FastAPI** – High-performance framework for building web APIs.
- **FLAN-T5-Small & DistilBART** – Lightweight transformer models used for abstractive news summarization.
- **BeautifulSoup / Requests** – For scraping news data from multiple online sources.
- **SQLite / PostgreSQL (Configurable)** – Database to store news articles and summaries.

---

## 🎯 Project Goals

- Demonstrate full-stack backend development skills.
- Showcase integration of NLP models for real-world tasks.
- Highlight scraping, cleaning, and summarization techniques for large text data.
- Build a working API layer to serve processed data to a frontend interface.

---

## 🧠 Summarization Pipeline

1. **Scraping**: News articles are scraped from select websites and cleaned.
2. **Initial Summarization**: Text is summarized using `FLAN-T5-Small`.
3. **Refinement**: `DistilBART` optionally improves the clarity of the summaries.
4. **Storage**: Cleaned content and summaries are stored in a structured database.

---

## 📦 API Features (Showcase Only)

| Endpoint             | Method | Description                         |
|----------------------|--------|-------------------------------------|
| `/news/latest`       | GET    | Retrieve latest summarized articles |
| `/news/{id}`         | GET    | Retrieve a single news article      |
| `/news/category/{}`  | GET    | Filter news by category             |
| `/scrape/update`     | POST   | Trigger scraping (restricted use)   |

🔐 **Access Note**: These endpoints are for demonstration purposes and are not secured or optimized for public access.

---

## 🗃️ Simplified Database Schema

```sql
Table: news_articles
- id (UUID)
- title (TEXT)
- summary (TEXT)
- content (TEXT)
- source_url (TEXT)
- category (TEXT)
- published_at (TIMESTAMP)
