
# 📰 NewsMind – Personalized AI News Agent

An AI-powered personalized news platform that delivers relevant news, AI-generated summaries, and intelligent answers based on your interests.

## 🚀 Live Demo

🌐 **[Open NewsMind Live](YOUR_LIVE_VERCEL_URL)**

> Explore the live interface and experience personalized news, AI-powered Q&A, and daily news digests.

## ✨ Features

- 📰 Latest News Feed
- 🎯 Personalized News Recommendations
- 🤖 Ask NewsMind – AI-powered news Q&A
- 📑 AI-Generated Daily News Digest
- 🔍 Semantic Search and Retrieval
- 🔗 Source Links for News Verification

## 🛠️ Tech Stack

**Frontend:** Next.js, React, TypeScript  
**Backend:** Python, FastAPI  
**AI/LLM:** Google Gemini API  
**Semantic Search:** Sentence Transformers  
**Model:** all-MiniLM-L6-v2

## 🖥️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/vivekpandey11/NewsMind.git
cd NewsMind
```

### 2. Backend Setup

```bash
python -m venv .venv
```

Activate the environment and install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_api_key_here
```

Start the backend:

```bash
uvicorn backend.app.main:app --reload
```

Backend: http://127.0.0.1:8000

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

## 📁 Project Structure

```text
NewsMind/
├── backend/
│   ├── app/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── data/
│   └── processed/
├── .gitignore
└── README.md
```

## 🔐 Environment Variables

Add your Gemini API key to `.env`. Never commit your API key to GitHub.

## 👨‍💻 Author

**Vivek Pandey**

GitHub: https://github.com/vivekpandey11
