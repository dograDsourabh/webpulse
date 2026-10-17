const STATUS_STYLES = {
  good: { label: "Good", className: "text-emerald-400" },
  "needs-improvement": { label: "Needs improvement", className: "text-amber-300" },
  poor: { label: "Poor", className: "text-rose-300" },
  measured: { label: "Measured", className: "text-slate-400" },
};

function MetricCard({ label, metric = {} }) {
  const status = STATUS_STYLES[metric.status] || {
    label: "Not available",
    className: "text-slate-500",
  };

  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-sm font-medium text-slate-400">{label}</p>
      <div className="mt-4">
        <span className="text-3xl font-bold">
          {metric.displayValue || "—"}
        </span>
      </div>
      <p className={`mt-3 text-sm font-medium ${status.className}`}>
        {status.label}
      </p>
    </article>
  );
}

export default MetricCard;
