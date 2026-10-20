
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/v1/cutoffs";

const categories = [
  "GN", "SC", "ST", "EZ", "MU", "BH", "BX", "EW",
];

const courses = [
  "CS", "ME", "EC", "CE", "EE", "AD", "CY", "AH",
];

const collegeTypes = [
  "Government",
  "Private",
  "Semi-Govt / Autonomous",
];

function App() {
  const [rank, setRank] = useState("");
  const [category, setCategory] = useState("GN");
  const [selectedCourses, setSelectedCourses] = useState(["CS"]);
  const [selectedTypes, setSelectedTypes] = useState([...collegeTypes]);

  const [cutoffs, setCutoffs] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function toggleSelection(value, selected, setSelected) {
    setSelected(
      selected.includes(value)
        ? selected.filter((item) => item !== value)
        : [...selected, value]
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSearched(false);
    setCutoffs([]);

    if (!rank || Number(rank) <= 0 || !Number.isInteger(Number(rank))) {
      setError("Enter a valid positive whole-number KEAM rank.");
      return;
    }

    if (selectedCourses.length === 0) {
      setError("Select at least one course.");
      return;
    }

    if (selectedTypes.length === 0) {
      setError("Select at least one college type.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          keam_rank: Number(rank),
          category,
          courses: selectedCourses,
          types: selectedTypes,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to retrieve cutoff data."
        );
      }

      setCutoffs(data.cutoffs ?? []);
      setSearched(true);
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Cannot connect to the backend. Check that FastAPI is running."
          : err.message || "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  function resetForm() {
    setRank("");
    setCategory("GN");
    setSelectedCourses(["CS"]);
    setSelectedTypes([...collegeTypes]);
    setCutoffs([]);
    setSearched(false);
    setError("");
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">E</span>
          <span>Edu-Cater</span>
        </a>
        <span className="topbar-label">KEAM College Explorer</span>
      </header>

      <section className="hero">
        <span className="eyebrow">YOUR ADMISSION JOURNEY</span>
        <h1>Find colleges that fit your rank.</h1>
        <p>
          Explore colleges using KEAM cutoff data. Choose your preferences
          to find matching courses and institutions.
        </p>
      </section>

      <section className="finder-layout">
        <form className="filter-panel" onSubmit={handleSubmit}>
          <div className="panel-heading">
            <div>
              <span className="section-kicker">STEP 01</span>
              <h2>Your preferences</h2>
            </div>
            <button
              className="text-button"
              type="button"
              onClick={resetForm}
            >
              Reset
            </button>
          </div>

          <div className="field-group">
            <label htmlFor="rank">KEAM rank</label>
            <input
              id="rank"
              type="number"
              min="1"
              step="1"
              placeholder="e.g. 15000"
              value={rank}
              onChange={(event) => setRank(event.target.value)}
              required
            />
            <span className="field-hint">
              Enter your overall rank.
            </span>
          </div>

          <div className="field-group">
            <label htmlFor="category">Admission category</label>
            <select
              id="category"
              value={category}
              onChange={(event) => setCategory(event.target.value)}
            >
              {categories.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <span className="field-hint">
              Select the category used for cutoff matching.
            </span>
          </div>

          <fieldset className="field-group">
            <legend>Preferred courses</legend>
            <p className="field-hint group-hint">
              Select one or more courses.
            </p>
            <div className="choice-grid">
              {courses.map((course) => (
                <label className="choice" key={course}>
                  <input
                    type="checkbox"
                    checked={selectedCourses.includes(course)}
                    onChange={() =>
                      toggleSelection(
                        course,
                        selectedCourses,
                        setSelectedCourses
                      )
                    }
                  />
                  <span>{course}</span>
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset className="field-group">
            <legend>College type</legend>
            <p className="field-hint group-hint">
              Choose the institutions to include.
            </p>
            <div className="type-options">
              {collegeTypes.map((type) => (
                <label className="type-choice" key={type}>
                  <input
                    type="checkbox"
                    checked={selectedTypes.includes(type)}
                    onChange={() =>
                      toggleSelection(type, selectedTypes, setSelectedTypes)
                    }
                  />
                  <span>{type}</span>
                </label>
              ))}
            </div>
          </fieldset>

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          <button className="submit-button" type="submit" disabled={loading}>
            {loading ? "Searching..." : "Find matching colleges"}
            {!loading && <span aria-hidden="true">→</span>}
          </button>

          <p className="privacy-note">
            Results are based on available cutoff records, not a guarantee
            of admission.
          </p>
        </form>

        <section className="results-panel" aria-live="polite">
          <div className="results-heading">
            <div>
              <span className="section-kicker">STEP 02</span>
              <h2>Matching colleges</h2>
            </div>
            {searched && (
              <span className="result-count">
                {cutoffs.length} {cutoffs.length === 1 ? "result" : "results"}
              </span>
            )}
          </div>

          {!searched && !loading && (
            <div className="empty-state">
              <div className="empty-icon" aria-hidden="true">
                <svg
                  viewBox="0 0 48 48"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <rect
                    x="7"
                    y="14"
                    width="34"
                    height="27"
                    rx="3"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  />
                  <path
                    d="M17 14V9h14v5M17 23h14M17 30h9"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />
                </svg>
              </div>
              <h3>Your results will appear here</h3>
              <p>
                Enter your rank, select your preferences, and run a search
                to explore matching colleges.
              </p>
            </div>
          )}

          {loading && (
            <div className="empty-state">
              <div className="loader" />
              <h3>Finding matching colleges</h3>
              <p>Retrieving cutoff records from the database.</p>
            </div>
          )}

          {searched && cutoffs.length === 0 && !loading && (
            <div className="empty-state">
              <div className="empty-icon" aria-hidden="true">!</div>
              <h3>No matching colleges found</h3>
              <p>
                No records matched these filters. Try different preferences
                or check again after the cutoff data has been updated.
              </p>
            </div>
          )}

          {searched && cutoffs.length > 0 && (
            <div className="table-wrapper">
              <table className="results-table">
                <thead>
                  <tr>
                    <th>College</th>
                    <th>Course</th>
                    <th>Opening rank</th>
                    <th>Cutoff rank</th>
                  </tr>
                </thead>
                <tbody>
                  {cutoffs.map((college, index) => (
                    <tr
                      key={[
                        college.college_id,
                        college.course_code,
                        college.category,
                        index,
                      ].join("-")}
                    >
                      <td>
                        <div className="college-name">
                          {college.college_name}
                        </div>
                        <div className="college-meta">
                          {college.college_code}
                          {college.district
                            ? ` · ${college.district}`
                            : ""}
                        </div>
                        <span className="college-type-badge">
                          {college.college_type}
                        </span>
                      </td>
                      <td>{college.course_code}</td>
                      <td>{college.opening_rank ?? "N/A"}</td>
                      <td className="cutoff-value">
                        {college.cutoff_rank ?? "N/A"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="results-footnote">
                Cutoff ranks are based on the records currently available
                in the database.
              </p>
            </div>
          )}
        </section>
      </section>

      <footer className="app-footer">
        <span>Edu-Cater</span>
        <span>KEAM Cutoff Finder</span>
      </footer>
    </main>
  );
}

export default App;
