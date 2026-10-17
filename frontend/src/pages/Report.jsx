import { useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft, Gauge } from "lucide-react";
import ScoreCard from "../components/ScoreCard";
import MetricCard from "../components/MetricCard";
import RecommendationList from "../components/RecommendationList";

const SCORE_CATEGORIES = [
  ["Performance", "performance"],
  ["SEO", "seo"],
  ["Accessibility", "accessibility"],
  ["Best practices", "bestPractices"],
];

function Report() {
  const location = useLocation();
  const navigate = useNavigate();
  const audit = location.state?.audit;

  if (!audit) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
        <div className="max-w-md text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-800 text-slate-200">
            <Gauge size={22} aria-hidden="true" />
          </div>
          <h1 className="mt-5 text-2xl font-semibold">No report to show</h1>
          <p className="mt-3 text-sm leading-6 text-slate-400">
            Audit a website first. Report data is kept for this browser session.
          </p>
          <button
            type="button"
            onClick={() => navigate("/")}
            className="mt-6 rounded-lg bg-white px-5 py-3 font-medium text-slate-950 hover:bg-slate-200"
          >
            Analyze a website
          </button>
        </div>
      </main>
    );
  }

  const scores = audit.scores || {};
  const vitals = audit.coreWebVitals || {};
  const metrics = audit.metrics || {};
  const recommendations = Array.isArray(audit.recommendations) ? audit.recommendations : [];

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-white sm:px-6 sm:py-12">
      <div className="mx-auto max-w-6xl">
        <button
          type="button"
          onClick={() => navigate("/")}
          className="inline-flex min-h-10 items-center gap-2 text-sm font-medium text-slate-400 transition hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-slate-300"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          Analyze another website
        </button>

        <header className="mt-7 border-b border-slate-800 pb-7">
          <p className="text-sm font-medium text-sky-300">WebPulse website report</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">Website health</h1>
          <p className="mt-3 break-all text-sm text-slate-400">{audit.url}</p>
          <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-sm text-slate-400">
            <span>{recommendations.length} {recommendations.length === 1 ? "recommendation" : "recommendations"}</span>
            <span>Mobile Lighthouse analysis</span>
          </div>
        </header>

        <section className="mt-9" aria-labelledby="category-scores-heading">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 id="category-scores-heading" className="text-xl font-semibold">Category scores</h2>
              <p className="mt-1 text-sm text-slate-400">Lighthouse scores out of 100.</p>
            </div>
          </div>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {SCORE_CATEGORIES.map(([title, key]) => (
              <ScoreCard key={key} title={title} score={scores[key]} />
            ))}
          </div>
        </section>

        <section className="mt-12" aria-labelledby="vitals-heading">
          <div>
            <h2 id="vitals-heading" className="text-xl font-semibold">Core Web Vitals</h2>
            <p className="mt-1 text-sm text-slate-400">Key metrics for loading, responsiveness, and visual stability.</p>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <MetricCard label="Largest Contentful Paint (LCP)" metric={vitals.lcp} />
            <MetricCard label="Interaction to Next Paint (INP)" metric={vitals.inp} />
            <MetricCard label="Cumulative Layout Shift (CLS)" metric={vitals.cls} />
          </div>
        </section>

        <section className="mt-12" aria-labelledby="metrics-heading">
          <div>
            <h2 id="metrics-heading" className="text-xl font-semibold">Additional performance metrics</h2>
            <p className="mt-1 text-sm text-slate-400">More detail to help explain how the page loads.</p>
          </div>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label="First Contentful Paint (FCP)" metric={metrics.fcp} />
            <MetricCard label="Total Blocking Time (TBT)" metric={metrics.tbt} />
            <MetricCard label="Speed Index" metric={metrics.speedIndex} />
            <MetricCard label="Time to First Byte (TTFB)" metric={metrics.ttfb} />
          </div>
        </section>

        <section className="mt-12 pb-12" aria-labelledby="recommendations-heading">
          <div>
            <h2 id="recommendations-heading" className="text-xl font-semibold">Recommendations</h2>
            <p className="mt-1 text-sm text-slate-400">Prioritized actions, supporting evidence, and implementation examples.</p>
          </div>
          <div className="mt-5">
            <RecommendationList recommendations={recommendations} />
          </div>
        </section>

        <footer className="border-t border-slate-800 py-5 text-xs leading-5 text-slate-500">
          Scores and opportunities can vary between Lighthouse runs. Use these findings as guidance and validate changes on your own site.
        </footer>
      </div>
    </main>
  );
}

export default Report;
