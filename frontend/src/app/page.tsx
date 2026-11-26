"use client";

import { useEffect, useState } from "react";
import AskNewsMind from "./AskNewsMind";
import DailyDigest from "./DailyDigest";

type Article = {
  title: string;
  source: string;
  link: string;
  published: string;
  summary: string;
  relevance_score: number;
  matched_interests: string[];
};

const API_URL = "http://127.0.0.1:8000";

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");

  useEffect(() => {
    fetch(`${API_URL}/news?limit=100`)
      .then((response) => {
        if (!response.ok) throw new Error("News API request failed");
        return response.json();
      })
      .then((data) => setArticles(data.articles ?? []))
      .catch(() =>
        setError("News load nahi hui. Check karo ki FastAPI server running hai.")
      )
      .finally(() => setLoading(false));
  }, []);

  const categories = [
    "All",
    ...Array.from(
      new Set(articles.flatMap((article) => article.matched_interests ?? []))
    ),
  ];

  const filtered = articles.filter((article) => {
    const matchesSearch = `${article.title} ${article.summary} ${article.source}`
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchesCategory =
      category === "All" ||
      (article.matched_interests ?? []).includes(category);

    return matchesSearch && matchesCategory;
  });

  return (
    <main className="min-h-screen bg-[#090d16] text-slate-100">
      <header className="border-b border-white/10 bg-[#0d1320]">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              News<span className="text-cyan-400">Mind</span>
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Your world, intelligently filtered.
            </p>
          </div>

          <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">
            AI NEWS FEED
          </span>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-6 py-10">
        <p className="text-sm font-medium text-cyan-400">
          YOUR PERSONAL NEWS BRIEFING
        </p>

        <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
          Stay informed. Skip the noise.
        </h2>

        <p className="mt-3 max-w-2xl text-slate-400">
          News collected from multiple sources and ranked against your interests.
        </p>

        /* Dashboard statistics */
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <p className="text-sm text-slate-400">Articles available</p>
            <p className="mt-2 text-3xl font-semibold">{articles.length}</p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <p className="text-sm text-slate-400">News sources</p>
            <p className="mt-2 text-3xl font-semibold">
              {new Set(articles.map((article) => article.source)).size}
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <p className="text-sm text-slate-400">Matching categories</p>
            <p className="mt-2 text-3xl font-semibold">
              {new Set(
                articles.flatMap((article) => article.matched_interests ?? [])
              ).size}
            </p>
          </div>
        </div>

        /* Personalized Daily Digest */
        <DailyDigest />

        /* AI News Assistant */
        <AskNewsMind />

        /* Search and category filters */
        <div className="mt-10 flex flex-col gap-4 sm:flex-row">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search news, topics or sources..."
            className="min-w-0 flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none placeholder:text-slate-500 focus:border-cyan-400"
          />

          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="rounded-xl border border-white/10 bg-[#111827] px-4 py-3 outline-none focus:border-cyan-400"
          >
            {categories.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>

        {/* News feed */}
        <div className="mb-5 mt-8 flex items-center justify-between">
          <h3 className="text-xl font-semibold">Latest for you</h3>
          <span className="text-sm text-slate-400">
            {filtered.length} articles
          </span>
        </div>

        {loading && (
          <p className="py-10 text-slate-400">Loading your news...</p>
        )}

        {error && (
          <p className="rounded-xl border border-red-400/30 bg-red-400/10 p-4 text-red-300">
            {error}
          </p>
        )}

        {!loading && !error && filtered.length === 0 && (
          <p className="rounded-xl border border-white/10 p-6 text-slate-400">
            No matching articles. Try another search or category.
          </p>
        )}

        <div className="grid gap-5 md:grid-cols-2">
          {filtered.map((article, index) => (
            <article
              key={article.link || index}
              className="rounded-2xl border border-white/10 bg-[#111827]/80 p-6 transition hover:border-cyan-400/40"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
                  {article.source}
                </span>

                <span className="rounded-lg bg-white/5 px-2 py-1 text-xs text-slate-400">
                  Match score: {article.relevance_score}
                </span>
              </div>

              <h4 className="mt-4 text-lg font-semibold leading-7">
                {article.title}
              </h4>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                {article.summary || "No summary available for this article."}
              </p>

              <div className="mt-4 flex flex-wrap gap-2">
                {(article.matched_interests ?? []).map((interest) => (
                  <span
                    key={interest}
                    className="rounded-full border border-cyan-400/20 bg-cyan-400/5 px-3 py-1 text-xs text-cyan-200"
                  >
                    {interest}
                  </span>
                ))}
              </div>

              <div className="mt-6 flex items-center justify-between gap-3 border-t border-white/10 pt-4">
                <span className="text-xs text-slate-500">
                  {article.published}
                </span>

                <a
                  href={article.link}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm font-medium text-cyan-300 hover:text-cyan-200"
                >
                  Read original article ↗
                </a>
              </div>
            </article>
          ))}
        </div>
      </section>

      <footer className="border-t border-white/10 px-6 py-6 text-center text-xs text-slate-500">
        NewsMind · Personalized news, powered by AI
      </footer>
    </main>
  );
}
