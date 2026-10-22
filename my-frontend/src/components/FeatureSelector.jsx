export default function FeatureSelector({ mode, onChange }) {
  return (
    <div className="mode-selector">
      <button
        type="button"
        className={`mode-option ${mode === "cutoffs" ? "active" : ""}`}
        onClick={() => onChange("cutoffs")}
      >
        Cutoff Finder
        <span>Explore historical cutoff data</span>
      </button>

      <button
        type="button"
        className={`mode-option ${
          mode === "recommendations" ? "active" : ""
        }`}
        onClick={() => onChange("recommendations")}
      >
        AI Recommendations
        <span>Get ranked college suggestions</span>
      </button>
    </div>
  );
}