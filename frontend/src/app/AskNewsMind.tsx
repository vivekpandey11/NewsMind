"use client";

import { useState } from "react";

type Source = {
  title: string;
  source: string;
  link: string;
  similarity: number;
};

export default function AskNewsMind() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function askQuestion(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!question.trim() || loading) return;

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not get an answer.");
      }

      setAnswer(data.answer || "No answer was generated.");
      setSources(data.sources || []);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not connect to NewsMind API."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="mt-8 rounded-2xl border border-white/10 bg-slate-900 p-6 text-white">
      <div className="mb-5">
        <p className="text-sm font-medium text-cyan-400">
          YOUR AI NEWS ASSISTANT
        </p>
        <h2 className="mt-1 text-2xl font-bold">Ask NewsMind</h2>
        <p className="mt-2 text-sm text-slate-400">
          Ask a question and get an answer grounded in your available news feed.
        </p>
      </div>

      <form onSubmit={askQuestion} className="flex flex-col gap-3 sm:flex-row">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="e.g. What is happening in Ukraine?"
          className="min-w-0 flex-1 rounded-xl border border-white/10 bg-slate-800 px-4 py-3 text-white outline-none focus:border-cyan-400"
          aria-label="Ask a news question"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded-xl bg-cyan-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Thinking..." : "Ask AI"}
        </button>
      </form>

      {loading && (
        <p className="mt-5 text-sm text-cyan-300">
          Searching articles and generating your answer...
        </p>
      )}

      {error && (
        <p className="mt-5 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
          {error}
        </p>
      )}

      {answer && (
        <div className="mt-6 rounded-xl bg-slate-800/70 p-5">
          <h3 className="mb-3 font-semibold text-cyan-300">AI Answer</h3>
          <p className="whitespace-pre-wrap text-sm leading-7 text-slate-200">
            {answer}
          </p>

          {sources.length > 0 && (
            <div className="mt-6 border-t border-white/10 pt-4">
              <h3 className="mb-3 font-semibold">Sources used</h3>
              <div className="space-y-3">
                {sources.map((source, index) => (
                  <article
                    key={`${source.link}-${index}`}
                    className="rounded-lg border border-white/10 p-3"
                  >
                    <p className="text-xs text-cyan-300">
                      [{index + 1}] {source.source}
                    </p>
                    <a
                      href={source.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 block text-sm font-medium hover:text-cyan-300"
                    >
                      {source.title} ↗
                    </a>
                  </article>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
