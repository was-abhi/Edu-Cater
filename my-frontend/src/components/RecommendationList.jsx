function formatProbability(value) {
  return typeof value === "number"
    ? `${Math.round(value * 100)}%`
    : "N/A";
}

function formatPercentage(value) {
  return value != null ? `${value}%` : "N/A";
}

export default function RecommendationList({ recommendations }) {
  if (recommendations.length === 0) {
    return (
      <div className="empty-state">
        <h3>No recommendations returned</h3>
        <p>Try changing your preferences and searching again.</p>
      </div>
    );
  }

  return (
    <div className="recommendation-list">
      {recommendations.map((college, index) => (
        <article
          className="recommendation-card"
          key={`${college.college_id}-${college.course_code}`}
        >
          <div className="recommendation-top">
            <span className="recommendation-number">#{index + 1}</span>

            <span
              className={`recommendation-badge ${String(
                college.recommendation_category ?? ""
              ).toLowerCase()}`}
            >
              {college.recommendation_category ?? "Unclassified"}
            </span>
          </div>

          <h3>{college.college_name}</h3>

          <p className="recommendation-meta">
            {college.college_code} · {college.district}
          </p>

          <p className="recommendation-course">
            {college.course_name || college.course_code}
          </p>

          <div className="recommendation-stats">
            <div>
              <span>Admission probability</span>
              <strong>
                {formatProbability(college.admission_probability)}
              </strong>
            </div>

            <div>
              <span>Opening rank</span>
              <strong>{college.category_opening_rank ?? "N/A"}</strong>
            </div>

            <div>
              <span>Closing rank</span>
              <strong>{college.category_closing_rank ?? "N/A"}</strong>
            </div>

            <div>
              <span>Pass percentage</span>
              <strong>{formatPercentage(college.pass_percentage)}</strong>
            </div>
          </div>

          <div className="recommendation-footer">
            <span>
              NBA: {college.nba_accredited ? "Accredited" : "Not accredited"}
            </span>

            <span>
              NAAC: {college.naac_accredited ? "Accredited" : "Not accredited"}
            </span>
          </div>
        </article>
      ))}
    </div>
  );
}