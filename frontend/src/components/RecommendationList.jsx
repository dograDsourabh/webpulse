import { useMemo, useState } from "react";
import RecommendationCard from "./RecommendationCard";

const PRIORITIES = ["ALL", "HIGH", "MEDIUM", "LOW"];

function categoryLabel(category) {
  return category.replaceAll("-", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function FilterButton({ active, children, onClick, count, label }) {
  return (
    <button
      type="button"
      aria-pressed={active}
      aria-label={`${label}: ${count}`}
      onClick={onClick}
      className={`inline-flex min-h-10 items-center gap-2 rounded-full border px-4 text-sm font-medium transition ${
        active
          ? "border-slate-300 bg-white text-slate-950"
          : "border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500"
      }`}
    >
      <span>{children}</span>
      <span className={active ? "text-slate-600" : "text-slate-500"}>{count}</span>
    </button>
  );
}

function RecommendationList({ recommendations = [] }) {
  const [category, setCategory] = useState("all");
  const [priority, setPriority] = useState("ALL");

  const categories = useMemo(
    () => [...new Set(recommendations.map((recommendation) => recommendation.category))].sort(),
    [recommendations],
  );

  const filtered = recommendations.filter((recommendation) =>
    (category === "all" || recommendation.category === category) &&
    (priority === "ALL" || recommendation.priority === priority),
  );

  if (recommendations.length === 0) {
    return (
      <div className="rounded-2xl border border-emerald-900/70 bg-emerald-950/30 p-8">
        <h3 className="text-lg font-semibold text-emerald-200">No recommendations found</h3>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          Lighthouse did not flag any issues covered by WebPulse’s current recommendation rules.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-5 space-y-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Category
          </p>
          <div className="flex flex-wrap gap-2" role="group" aria-label="Filter recommendations by category">
            <FilterButton
              active={category === "all"}
              onClick={() => setCategory("all")}
              count={recommendations.length}
              label="All categories"
            >
              All categories
            </FilterButton>
            {categories.map((item) => {
              const count = recommendations.filter((recommendation) => recommendation.category === item).length;
              return (
                <FilterButton
                  key={item}
                  active={category === item}
                  onClick={() => setCategory(item)}
                  count={count}
                  label={categoryLabel(item)}
                >
                  {categoryLabel(item)}
                </FilterButton>
              );
            })}
          </div>
        </div>

        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Priority
          </p>
          <div className="flex flex-wrap gap-2" role="group" aria-label="Filter recommendations by priority">
            {PRIORITIES.map((item) => {
              const count = item === "ALL"
                ? recommendations.length
                : recommendations.filter((recommendation) => recommendation.priority === item).length;
              return (
                <FilterButton
                  key={item}
                  active={priority === item}
                  onClick={() => setPriority(item)}
                  count={count}
                  label={item === "ALL" ? "All priorities" : `${item.toLowerCase()} priority`}
                >
                  {item === "ALL" ? "All priorities" : `${item[0]}${item.slice(1).toLowerCase()}`}
                </FilterButton>
              );
            })}
          </div>
        </div>
      </div>

      <p className="mb-4 text-sm text-slate-400" aria-live="polite">
        Showing {filtered.length} of {recommendations.length} recommendations
      </p>

      {filtered.length > 0 ? (
        <div className="space-y-4">
          {filtered.map((recommendation) => (
            <RecommendationCard key={recommendation.id} recommendation={recommendation} />
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center">
          <h3 className="font-semibold text-white">No matching recommendations</h3>
          <p className="mt-2 text-sm text-slate-400">Change or clear a filter to see other findings.</p>
          <button
            type="button"
            onClick={() => { setCategory("all"); setPriority("ALL"); }}
            className="mt-4 rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:border-slate-500"
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
}

export default RecommendationList;
