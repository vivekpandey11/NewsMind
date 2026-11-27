# 📰 NewsMind – Personalized AI News Agent

**Your world, intelligently filtered.**

NewsMind is an AI-powered personalized news platform designed to help users stay informed without getting overwhelmed by information.

It collects news from multiple sources, organizes articles around user interests, provides intelligent news retrieval, and uses Google's Gemini API to generate AI-powered answers and daily news briefings.

## 🌐 Live Demo

**[🚀 Open NewsMind Live](https://news-mind-pi.vercel.app/)**

- **Frontend:** Deployed on Vercel
- **Backend API:** Deployed on Render
- **API Base URL:** https://newsmind-1.onrender.com

Explore the live interface to discover personalized news, ask questions about current stories, and access AI-generated daily digests.

## ✨ Key Features

### 📰 Personalized News Feed
- Displays the latest available news articles.
- Organizes news based on user interests.
- Supports keyword-based search and category filtering.
- Provides links to original news sources for verification.

### 🎯 Intelligent News Ranking
- Matches articles against predefined user-interest categories.
- Uses lightweight TF-IDF-based ranking to identify relevant content.
- Uses BM25-style keyword retrieval for query-based news search.
- Compares keyword and interest-based ranking results.

### 🤖 Ask NewsMind
- AI-powered question-answering interface.
- Retrieves relevant news articles before generating answers.
- Uses Google Gemini API to produce contextual responses.
- Helps users understand news topics through conversational interaction.

### 📑 Personalized Daily Digest
- Generates AI-powered summaries of important news.
- Selects relevant articles from the available news collection.
- Presents important stories in a concise briefing format.
- Uses caching to avoid unnecessary repeated generation.

## 🛠️ Technology Stack

| Component | Technologies |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | Python, FastAPI |
| AI / LLM | Google Gemini API |
| News Retrieval | BM25-style keyword retrieval |
| News Ranking | TF-IDF and cosine similarity |
| Data Processing | Python, JSON |
| Deployment | Vercel, Render |
| Version Control | Git, GitHub |

**Performance optimization:** The original Sentence Transformers-based implementation was replaced with lightweight Python-based retrieval and ranking methods to reduce memory consumption and make backend deployment more practical on limited resources.

## 🏗️ Project Architecture

```text
                    USER
                      |
                      v
             Next.js Frontend
                (Vercel)
                      |
                      v
              FastAPI Backend
                (Render)
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
      News Feed   News Search   AI Services
          |           |           |
          v           v           v
       Ranking    BM25-style   Gemini API
       TF-IDF     Retrieval    Integration
          |                       |
          +-----------+-----------+
                      |
                      v
              Personalized News
                & Daily Digest
```

## 📁 Project Structure

```text
NewsMind/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── news_retrieval.py
│       ├── semantic_ranking.py
│       ├── digest_generator.py
│       ├── relevance_ranking.py
│       ├── compare_rankings.py
│       ├── evaluate_rankings.py
│       └── news_ingestion.py
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   └── components/
│   ├── package.json
│   └── ...
│
├── data/
│   └── processed/
│       ├── news_articles.json
│       ├── ranked_news.json
│       ├── semantic_ranked_news.json
│       └── ...
│
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/vivekpandey11/NewsMind.git
cd NewsMind
```

### 2. Backend Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Start the FastAPI backend:

```bash
uvicorn backend.app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend Setup

Open a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:3000
```

## 🔐 Environment Variables

The backend requires a Google Gemini API key.

```env
GEMINI_API_KEY=your_gemini_api_key
```

For production deployment, configure the frontend API base URL to point to the deployed Render backend:

```text
https://newsmind-1.onrender.com
```

Configure the frontend's API URL using the environment variable expected by the frontend code in Vercel Project Settings.

**Security:** Never commit API keys, `.env` files, or other sensitive credentials to GitHub.

## 🚀 Deployment

### Frontend – Vercel
- Connected to the GitHub repository.
- Root directory: `frontend`.
- Production URL: https://news-mind-pi.vercel.app/

### Backend – Render
- FastAPI application deployed as a Web Service.
- Start command:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

- Backend URL: https://newsmind-1.onrender.com

## 📊 Ranking and Evaluation

NewsMind includes scripts for comparing and evaluating its ranking approaches.

```bash
python -m backend.app.semantic_ranking
python -m backend.app.compare_rankings
python -m backend.app.evaluate_rankings
```

The evaluation workflow compares the top-ranked articles from keyword-based and TF-IDF-based ranking and calculates their Top-5 Jaccard overlap.

This helps analyze how different ranking strategies prioritize available news articles.

## 🔮 Future Improvements

- Real-time news ingestion and refresh scheduling.
- More advanced personalization based on reading preferences.
- Improved relevance evaluation using larger news datasets.
- Better retrieval and ranking optimization.
- User authentication and saved interests.
- Expanded news source coverage.
- Improved monitoring and production performance.

## 👨‍💻 Author

**Vivek Pandey**

- GitHub: [vivekpandey11](https://github.com/vivekpandey11)
- Project Repository: [NewsMind](https://github.com/vivekpandey11/NewsMind)

---

**NewsMind – Your world, intelligently filtered.**
