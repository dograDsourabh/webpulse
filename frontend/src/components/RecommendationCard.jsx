const PRIORITY_STYLES = {
  HIGH: "border-rose-500/30 bg-rose-500/10 text-rose-200",
  MEDIUM: "border-amber-500/30 bg-amber-500/10 text-amber-200",
  LOW: "border-sky-500/30 bg-sky-500/10 text-sky-200",
};

function formatBytes(bytes) {
  if (typeof bytes !== "number") return null;
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatMilliseconds(milliseconds) {
  if (typeof milliseconds !== "number") return null;
  if (milliseconds < 1000) return `${Math.round(milliseconds)} ms`;
  return `${(milliseconds / 1000).toFixed(2)} s`;
}

function EvidenceSection({ evidence = {} }) {
  const resources = evidence.affectedResources || [];
  const elements = evidence.affectedElements || [];
  const errors = evidence.errors || [];
  const affectedItems = evidence.affectedItems || [];
  const hasDetails = resources.length || elements.length || errors.length || affectedItems.length;

  return (
    <section className="mt-6" aria-label="Audit evidence">
      <h4 className="text-sm font-semibold text-white">Evidence</h4>
      {(typeof evidence.score === "number" || evidence.displayValue) && (
        <div className="mt-3 grid gap-3 rounded-xl border border-slate-800 bg-slate-950 p-4 sm:grid-cols-2">
          {typeof evidence.score === "number" && (
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Lighthouse score</p>
              <p className="mt-1 font-semibold text-white">{Math.round(evidence.score * 100)}%</p>
            </div>
          )}
          {evidence.displayValue && (
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Audit result</p>
              <p className="mt-1 text-sm text-slate-300">{evidence.displayValue}</p>
            </div>
          )}
        </div>
      )}

      {resources.length > 0 && (
        <div className="mt-3 rounded-xl border border-slate-800 bg-slate-950 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h5 className="text-sm font-semibold text-white">Affected resources</h5>
            {evidence.totalAffectedResources > resources.length && (
              <span className="text-xs text-slate-500">Showing {resources.length} of {evidence.totalAffectedResources}</span>
            )}
          </div>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full min-w-[34rem] text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-xs uppercase tracking-wide text-slate-500">
                  <th className="pb-3 pr-4 font-medium">Resource</th>
                  <th className="pb-3 pr-4 font-medium">Size</th>
                  <th className="pb-3 pr-4 font-medium">Potential saving</th>
                  <th className="pb-3 font-medium">Occurrences / delay</th>
                </tr>
              </thead>
              <tbody>
                {resources.map((resource, index) => (
                  <tr key={`${resource.url || "resource"}-${index}`} className="border-b border-slate-900 last:border-0">
                    <td className="max-w-md break-all py-3 pr-4 text-slate-300">{resource.url || "Unknown resource"}</td>
                    <td className="whitespace-nowrap py-3 pr-4 text-slate-400">{formatBytes(resource.totalBytes) || "—"}</td>
                    <td className="whitespace-nowrap py-3 pr-4 text-slate-400">{formatBytes(resource.wastedBytes) || "—"}</td>
                    <td className="whitespace-nowrap py-3 text-slate-400">
                      {resource.occurrences ? `${resource.occurrences}×` : formatMilliseconds(resource.wastedMs) || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {elements.length > 0 && (
        <div className="mt-3 rounded-xl border border-slate-800 bg-slate-950 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h5 className="text-sm font-semibold text-white">Affected elements</h5>
            {evidence.totalAffectedElements > elements.length && (
              <span className="text-xs text-slate-500">Showing {elements.length} of {evidence.totalAffectedElements}</span>
            )}
          </div>
          <div className="mt-3 space-y-3">
            {elements.map((element, index) => (
              <div key={`${element.selector || "element"}-${index}`} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
                {element.selector && <p className="break-all font-mono text-xs text-slate-300">{element.selector}</p>}
                {element.snippet && <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-all rounded bg-slate-950 p-3 font-mono text-xs leading-5 text-slate-400">{element.snippet}</pre>}
                {element.explanation && <p className="mt-2 text-xs leading-5 text-slate-400">{element.explanation}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {errors.length > 0 && (
        <div className="mt-3 rounded-xl border border-slate-800 bg-slate-950 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h5 className="text-sm font-semibold text-white">Console errors</h5>
            {evidence.totalErrors > errors.length && (
              <span className="text-xs text-slate-500">Showing {errors.length} of {evidence.totalErrors}</span>
            )}
          </div>
          <ul className="mt-3 space-y-3">
            {errors.map((error, index) => (
              <li key={`${error.url || error.source || "error"}-${index}`} className="rounded-lg border border-slate-800 bg-slate-900 p-3">
                <p className="break-words text-sm leading-6 text-slate-200">{error.message || "Browser error reported"}</p>
                {(error.url || error.source || error.line != null) && (
                  <p className="mt-2 break-all font-mono text-xs leading-5 text-slate-500">
                    {error.source && <span>{error.source} · </span>}
                    {error.url && <span>{error.url}</span>}
                    {error.line != null && <span>:{error.line}{error.column != null ? `:${error.column}` : ""}</span>}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {affectedItems.length > 0 && (
        <div className="mt-3 rounded-xl border border-slate-800 bg-slate-950 p-4">
          <h5 className="text-sm font-semibold text-white">Reported issues</h5>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-slate-300">
            {affectedItems.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}
          </ul>
        </div>
      )}

      {!hasDetails && !evidence.displayValue && (
        <p className="mt-3 rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm text-slate-400">
          Lighthouse did not return additional resource-level evidence for this finding.
        </p>
      )}

    </section>
  );
}

function RecommendationCard({ recommendation }) {
  const priorityClass = PRIORITY_STYLES[recommendation.priority] || PRIORITY_STYLES.MEDIUM;
  const category = recommendation.category.replaceAll("-", " ");
  const impact = recommendation.estimatedImpact;

  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm capitalize text-slate-500">{category}</p>
          <h3 className="mt-1 text-lg font-semibold text-white">{recommendation.title}</h3>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${priorityClass}`}>
          {recommendation.priority}
        </span>
      </div>

      <p className="mt-4 text-sm leading-6 text-slate-300">{recommendation.summary}</p>
      <EvidenceSection evidence={recommendation.evidence} />

      <section className="mt-6" aria-label="Where to fix">
        <h4 className="text-sm font-semibold text-white">Where to fix</h4>
        <div className="mt-2 rounded-xl border border-slate-800 bg-slate-950 p-4">
          {recommendation.where.location && <p className="text-sm text-slate-300"><span className="font-medium text-white">Location:</span> {recommendation.where.location}</p>}
          <p className="text-sm leading-6 text-slate-400">{recommendation.where.description}</p>
        </div>
      </section>

      <section className="mt-6" aria-label="Why this matters">
        <h4 className="text-sm font-semibold text-white">Why this matters</h4>
        <p className="mt-2 text-sm leading-6 text-slate-400">{recommendation.whyItMatters}</p>
      </section>

      {recommendation.recommendedActions.length > 0 && (
        <section className="mt-6" aria-label="Recommended actions">
          <h4 className="text-sm font-semibold text-white">How to fix</h4>
          <ol className="mt-3 space-y-3">
            {recommendation.recommendedActions.map((action, index) => (
              <li key={`${action}-${index}`} className="flex gap-3 text-sm text-slate-300">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-800 text-xs font-medium text-slate-300">{index + 1}</span>
                <span className="leading-6">{action}</span>
              </li>
            ))}
          </ol>
        </section>
      )}

      {recommendation.example?.code && (
        <section className="mt-6" aria-label="Example fix">
          <h4 className="text-sm font-semibold text-white">Example</h4>
          <pre className="mt-3 overflow-x-auto rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm leading-6 text-slate-300"><code>{recommendation.example.code}</code></pre>
        </section>
      )}

      {impact && (impact.description || impact.potentialSavingsBytes != null || impact.potentialSavingsMs != null || impact.displayValue) && (
        <section className="mt-6" aria-label="Estimated impact">
          <h4 className="text-sm font-semibold text-white">Estimated impact</h4>
          <div className="mt-2 text-sm leading-6 text-slate-400">
            {impact.description && <p>{impact.description}</p>}
            {impact.potentialSavingsBytes != null && <p className="mt-1">Potential data savings: {formatBytes(impact.potentialSavingsBytes)}</p>}
            {impact.potentialSavingsMs != null && <p className="mt-1">Potential time savings: {formatMilliseconds(impact.potentialSavingsMs)}</p>}
            {impact.displayValue && <p className="mt-1">Lighthouse estimate: {impact.displayValue}</p>}
          </div>
        </section>
      )}
    </article>
  );
}

export default RecommendationCard;
