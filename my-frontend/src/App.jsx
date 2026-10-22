
import { useState } from "react";
import "./App.css";

import FeatureSelector from "./components/FeatureSelector";
import RecommendationList from "./components/RecommendationList";
import {
  fetchCutoffs,
  fetchRecommendations,
} from "./services/api";

const categories = ["GN", "SC", "ST", "EZ", "MU", "BH", "BX", "EW"];

const courses = ["CS", "ME", "EC", "CE", "EE", "AD", "CY", "AH"];

const collegeTypes = [
  { label: "Government", value: "government" },
  { label: "Private", value: "private" },
  { label: "Semi-Govt / Autonomous", value: "autonomous" },
];

function App() {
  const [rank, setRank] = useState("");
  const [category, setCategory] = useState("GN");

  const [selectedCourses, setSelectedCourses] = useState(["CS"]);

  const [selectedTypes, setSelectedTypes] = useState(
    collegeTypes.map((type) => type.value)
  );

  const [mode, setMode] = useState("cutoffs");
  const [cutoffs, setCutoffs] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function toggleCourse(course) {
    setSelectedCourses((previous) =>
      previous.includes(course)
        ? previous.filter((item) => item !== course)
        : [...previous, course]
    );
  }

  function toggleType(type) {
    setSelectedTypes((previous) =>
      previous.includes(type)
        ? previous.filter((item) => item !== type)
        : [...previous, type]
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSearched(false);
    setCutoffs([]);
    setRecommendations([]);

    if (
      !rank ||
      !Number.isInteger(Number(rank)) ||
      Number(rank) <= 0
    ) {
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

    const payload = {
      keam_rank: Number(rank),
      category,
      courses: selectedCourses,
      types: selectedTypes,
    };

    setLoading(true);

    try {
      if (mode === "cutoffs") {
        const data = await fetchCutoffs(payload);
        setCutoffs(data.cutoffs ?? []);
      } else {
        const data = await fetchRecommendations(payload);
        setRecommendations(data.recommendations ?? []);
      }

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
    setSelectedTypes(collegeTypes.map((type) => type.value));

    setCutoffs([]);
    setRecommendations([]);
    setSearched(false);
    setLoading(false);
    setError("");
  }

  function changeMode(nextMode) {
    setMode(nextMode);
    setCutoffs([]);
    setRecommendations([]);
    setSearched(false);
    setError("");
  }

  const resultCount =
    mode === "cutoffs" ? cutoffs.length : recommendations.length;

  return (
    <main className="app-container">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark">E</div>
          <div>
            <h1>Edu-Cater</h1>
            <p>KEAM College Selection Assistant</p>
          </div>
        </div>
      </header>

      <section className="hero">
        <p className="eyebrow">YOUR ADMISSION, SIMPLIFIED</p>
        <h1>Find the right college for your rank.</h1>
        <p>
          Explore historical cutoff data or get AI-powered college
          recommendations based on your KEAM rank, category, and preferences.
        </p>
      </section>

      <FeatureSelector mode={mode} onChange={changeMode} />

      <section className="finder-layout">
        <form className="finder-form" onSubmit={handleSubmit}>
          <div className="section-heading">
            <h2>Admission preferences</h2>
            <p>Enter your details to get started.</p>
          </div>

          <div className="form-group">
            <label htmlFor="rank">KEAM rank</label>
            <input
              id="rank"
              type="number"
              min="1"
              step="1"
              placeholder="e.g. 4500"
              value={rank}
              onChange={(event) => setRank(event.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="category">Reservation category</label>
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
          </div>

          <fieldset className="form-group">
            <legend>Preferred courses</legend>
            <div className="checkbox-grid">
              {courses.map((course) => (
                <label className="checkbox-option" key={course}>
                  <input
                    type="checkbox"
                    checked={selectedCourses.includes(course)}
                    onChange={() => toggleCourse(course)}
                  />
                  <span>{course}</span>
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset className="form-group">
            <legend>College types</legend>
            <div className="checkbox-list">
              {collegeTypes.map((type) => (
                <label className="checkbox-option" key={type.value}>
                  <input
                    type="checkbox"
                    checked={selectedTypes.includes(type.value)}
                    onChange={() => toggleType(type.value)}
                  />
                  <span>{type.label}</span>
                </label>
              ))}
            </div>
          </fieldset>

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          <div className="form-actions">
            <button
              className="primary-button"
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Processing..."
                : mode === "cutoffs"
                  ? "Find colleges"
                  : "Get recommendations"}
            </button>

            <button
              className="secondary-button"
              type="button"
              onClick={resetForm}
              disabled={loading}
            >
              Reset
            </button>
          </div>
        </form>

        <section className="results-panel">
          <div className="results-header">
            <div>
              <h2>
                {mode === "cutoffs"
                  ? "Matching colleges"
                  : "AI recommendations"}
              </h2>
              <p>
                {loading
                  ? "Finding suitable colleges..."
                  : searched
                    ? `${resultCount} result${resultCount === 1 ? "" : "s"} found`
                    : "Your results will appear here."}
              </p>
            </div>
          </div>

          {loading && (
            <div className="empty-state">
              <p>
                {mode === "cutoffs"
                  ? "Searching historical cutoff data..."
                  : "Generating college recommendations..."}
              </p>
            </div>
          )}

          {!loading && !searched && (
            <div className="empty-state">
              <h3>Ready when you are</h3>
              <p>
                Enter your KEAM rank, choose your preferences, and submit
                the form to see your results.
              </p>
            </div>
          )}

          {!loading && searched && mode === "cutoffs" &&
            cutoffs.length === 0 && (
              <div className="empty-state">
                <h3>No matching colleges</h3>
                <p>
                  Try a different category, course, or college type.
                </p>
              </div>
            )}

          {!loading && searched && mode === "cutoffs" &&
            cutoffs.length > 0 && (
              <div className="table-wrapper">
                <table className="cutoff-table">
                  <thead>
                    <tr>
                      <th>College</th>
                      <th>Course</th>
                      <th>Category</th>
                      <th>Closing rank</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cutoffs.map((college, index) => (
                      <tr
                        key={
                          college.id ??
                          `${college.college_code}-${college.course_code}-${index}`
                        }
                      >
                        <td>
                          <strong>
                            {college.college_name ??
                              college.name ??
                              "Unknown college"}
                          </strong>
                          <span className="table-subtext">
                            {college.college_code ?? ""}
                          </span>
                        </td>
                        <td>
                          {college.course_name ??
                            college.course_code ??
                            "N/A"}
                        </td>
                        <td>
                          {college.category ??
                            college.applied_category ??
                            category}
                        </td>
                        <td>
                          {college.closing_rank ??
                            college.category_closing_rank ??
                            "N/A"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

          {!loading && searched && mode === "recommendations" && (
            <RecommendationList recommendations={recommendations} />
          )}
        </section>
      </section>
    </main>
  );
}

export default App;
