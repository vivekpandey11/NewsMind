"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

const API_URL = "http://127.0.0.1:8000";

type DigestArticle = {
  title: string;
  source: string;
  link: string;
  summary: string;
  relevance_score: number;
  matched_interests: string[];
};

type DigestData = {
  status: string;
  digest_date?: string;
  generated_at?: string;
  article_count: number;
  digest: string;
  articles: DigestArticle[];
  message?: string;
};

export default function DailyDigest() {
  const [data, setData] = useState<DigestData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchDigest() {
      try {
        const response = await fetch(`${API_URL}/digest`);

        const result = await response.json();

        if (!response.ok) {
          throw new Error(
            result.detail || "Could not load your daily digest."
          );
        }

        setData(result);
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

    fetchDigest();
  }, []);

  return (
    <section className="mt-10 rounded-2xl border border-cyan-400/20 bg-[#101a2a] p-6 sm:p-8">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <p className="text-sm font-semibold tracking-wider text-cyan-400">
            PERSONALIZED AI BRIEFING
          </p>
          <h2 className="mt-2 text-2xl font-bold sm:text-3xl">
            Your Daily Digest
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Your important stories, summarized and explained by AI.
          </p>
        </div>

        <span className="w-fit rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1.5 text-xs text-cyan-300">
          NEWSMIND AI
        </span>
      </div>

      {loading && (
        <div className="mt-8 rounded-xl bg-white/[0.03] p-6 text-sm text-cyan-300">
          Loading your personalized digest...
        </div>
      )}

      {error && (
        <div className="mt-8 rounded-xl border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {!loading && !error && data?.status === "empty" && (
        <div className="mt-8 rounded-xl bg-white/[0.03] p-6 text-sm text-slate-400">
          {data.message || "No relevant news is available right now."}
        </div>
      )}

      {!loading && !error && data?.status === "success" && (
        <>
          <div className="mt-6 flex flex-wrap items-center gap-3 text-xs text-slate-400">
            <span>{data.article_count} selected stories</span>
            {data.digest_date && (
              <>
                <span>•</span>
                <span>{data.digest_date}</span>
              </>
            )}
            <span>•</span>
            <span>Personalized to your interests</span>
          </div>

          <div className="prose prose-invert prose-sm mt-6 max-w-none prose-headings:text-cyan-300 prose-p:leading-7 prose-a:text-cyan-300 prose-strong:text-slate-100 prose-li:my-1">
            <ReactMarkdown>
              {data.digest || "No digest content was generated."}
            </ReactMarkdown>
          </div>

          {data.articles?.length > 0 && (
            <div className="mt-8 border-t border-white/10 pt-6">
              <h3 className="mb-4 text-lg font-semibold">
                Articles included in this digest
              </h3>

              <div className="grid gap-4 md:grid-cols-2">
                {data.articles.map((article, index) => (
                  <article
                    key={`${article.link}-${index}`}
                    className="rounded-xl border border-white/10 bg-white/[0.03] p-4"
                  >
                    <p className="text-xs font-semibold text-cyan-300">
                      {article.source}
                    </p>

                    <h4 className="mt-2 font-semibold leading-6">
                      {article.title}
                    </h4>

                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      {article.summary || "No article summary available."}
                    </p>

                    <div className="mt-3 flex flex-wrap gap-2">
                      {article.matched_interests.map((interest) => (
                        <span
                          key={interest}
                          className="rounded-full border border-cyan-400/20 px-2.5 py-1 text-xs text-cyan-200"
                        >
                          {interest}
                        </span>
                      ))}
                    </div>

                    <a
                      href={article.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-4 inline-block text-sm font-medium text-cyan-300 hover:text-cyan-200"
                    >
                      Read original article ↗
                    </a>
                  </article>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
