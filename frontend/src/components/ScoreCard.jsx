function ScoreCard({ title, score }) {
  const getStatus = () => {
    if (typeof score !== "number") {
      return {
        label: "Not available",
        className: "text-slate-500",
      };
    }

    if (score >= 90) {
      return {
        label: "Excellent",
        className: "text-green-400",
      };
    }

    if (score >= 50) {
      return {
        label: "Needs Improvement",
        className: "text-yellow-400",
      };
    }

    return {
      label: "Poor",
      className: "text-red-400",
    };
  };

  const status = getStatus();

  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-sm font-medium text-slate-400">
        {title}
      </p>

      <div className="mt-4 flex items-end gap-2">
        <span className="text-5xl font-bold">
          {typeof score === "number" ? score : "—"}
        </span>

        {typeof score === "number" && (
          <span className="mb-2 text-sm text-slate-500">/ 100</span>
        )}
      </div>

      <p className={`mt-3 text-sm font-medium ${status.className}`}>
        {status.label}
      </p>
    </article>
  );
}

export default ScoreCard;
