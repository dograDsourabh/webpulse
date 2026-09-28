import { useState } from "react";
import {
  ArrowRight,
  Gauge,
  Search,
  ShieldCheck,
  Zap,
} from "lucide-react";

function Home() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    const trimmedUrl = url.trim();

    if (!trimmedUrl) {
      setError("Please enter a website URL.");
      return;
    }

    let parsedUrl;

    try {
      parsedUrl = new URL(trimmedUrl);
    } catch {
      setError("Please enter a valid URL.");
      return;
    }

    if (!["http:", "https:"].includes(parsedUrl.protocol)) {
      setError("Please enter a valid HTTP or HTTPS URL.");
      return;
    }

    setIsAnalyzing(true);

    // Temporary mock request.
    // We will replace this with our FastAPI request later.
    await new Promise((resolve) => setTimeout(resolve, 2000));

    console.log("Website ready for analysis:", parsedUrl.href);

    setIsAnalyzing(false);
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8">
        {/* Navigation */}
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-slate-950">
              <Gauge size={20} />
            </div>

            <span className="text-xl font-semibold tracking-tight">
              WebPulse
            </span>
          </div>

          <span className="hidden text-sm text-slate-400 sm:block">
            Website Health Analyzer
          </span>
        </header>

        {/* Hero */}
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900 px-4 py-2 text-sm text-slate-300">
              <Zap size={16} />
              Simple website insights
            </div>

            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
              Understand your website.
              <span className="block text-slate-400">
                Fix what matters.
              </span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-400">
              Analyze performance, SEO, accessibility, and Core Web Vitals
              without getting buried in technical reports.
            </p>

            {/* URL Form */}
            <form
              onSubmit={handleSubmit}
              className="mx-auto mt-10 max-w-2xl"
            >
              <div className="flex flex-col gap-3 sm:flex-row">
                <div className="relative flex-1">
                  <Search
                    size={20}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
                  />

                  <input
                    type="url"
                    value={url}
                    onChange={(event) => {
                      setUrl(event.target.value);

                      if (error) {
                        setError("");
                      }
                    }}
                    placeholder="https://example.com"
                    disabled={isAnalyzing}
                    className="h-14 w-full rounded-xl border border-slate-700 bg-slate-900 pl-12 pr-4 text-white outline-none transition placeholder:text-slate-600 focus:border-slate-400 disabled:cursor-not-allowed disabled:opacity-60"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isAnalyzing}
                  className="flex h-14 items-center justify-center gap-2 rounded-xl bg-white px-6 font-semibold text-slate-950 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isAnalyzing ? (
                    <>
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-slate-950" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze Website
                      <ArrowRight size={18} />
                    </>
                  )}
                </button>
              </div>

              {/* Error */}
              {error && (
                <p className="mt-3 text-left text-sm text-red-400">
                  {error}
                </p>
              )}
            </form>

            {/* Features */}
            <div className="mt-12 grid gap-4 text-left sm:grid-cols-3">
              <Feature
                icon={<Gauge size={18} />}
                title="Performance"
                description="Understand loading and Core Web Vitals."
              />

              <Feature
                icon={<Search size={18} />}
                title="SEO"
                description="Find important search optimization issues."
              />

              <Feature
                icon={<ShieldCheck size={18} />}
                title="Accessibility"
                description="Discover common accessibility problems."
              />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

function Feature({ icon, title, description }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div className="mb-4 flex h-9 w-9 items-center justify-center rounded-lg bg-slate-800">
        {icon}
      </div>

      <h2 className="font-semibold">{title}</h2>

      <p className="mt-2 text-sm leading-6 text-slate-400">
        {description}
      </p>
    </div>
  );
}

export default Home;