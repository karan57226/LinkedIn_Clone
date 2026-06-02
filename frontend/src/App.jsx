import { BriefcaseBusiness, Building2, MapPin, RefreshCw, Server } from "lucide-react";
import { useEffect, useState } from "react";

import { getFeed, getJobs, getProfiles } from "./api";

function App() {
  const [feed, setFeed] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [status, setStatus] = useState("loading");

  async function loadData() {
    setStatus("loading");
    try {
      const [feedData, jobData, profileData] = await Promise.all([
        getFeed(),
        getJobs(),
        getProfiles()
      ]);
      setFeed(feedData);
      setJobs(jobData);
      setProfiles(profileData);
      setStatus("ready");
    } catch (error) {
      setStatus(error.message);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Deployment learning app</p>
          <h1>Mini Professional Network</h1>
        </div>
        <button className="iconButton" type="button" onClick={loadData} aria-label="Refresh data">
          <RefreshCw size={18} />
        </button>
      </header>

      <section className="statusBand">
        <Server size={18} />
        <span>
          Frontend calls FastAPI REST endpoints. FastAPI reads from SQLAlchemy models backed by RDS
          PostgreSQL when `DATABASE_URL` points to AWS.
        </span>
      </section>

      {status !== "ready" ? (
        <section className="emptyState">
          {status === "loading" ? "Loading network data..." : `API error: ${status}`}
        </section>
      ) : (
        <div className="layout">
          <aside className="sidebar">
            <section>
              <h2>People</h2>
              <div className="stack">
                {profiles.map((profile) => (
                  <article className="person" key={profile.id}>
                    <img src={profile.avatar_url} alt="" />
                    <div>
                      <strong>{profile.name}</strong>
                      <span>{profile.title}</span>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </aside>

          <section className="feed">
            <h2>Feed</h2>
            <div className="stack">
              {feed.map((post) => (
                <article className="post" key={post.id}>
                  <div className="postHeader">
                    <img src={post.author.avatar_url} alt="" />
                    <div>
                      <strong>{post.author.name}</strong>
                      <span>{post.author.title}</span>
                    </div>
                  </div>
                  <p>{post.body}</p>
                </article>
              ))}
            </div>
          </section>

          <aside className="sidebar">
            <section>
              <h2>Jobs</h2>
              <div className="stack">
                {jobs.map((job) => (
                  <article className="job" key={job.id}>
                    <div className="jobIcon">
                      <BriefcaseBusiness size={18} />
                    </div>
                    <div>
                      <strong>{job.role}</strong>
                      <span>
                        <Building2 size={14} />
                        {job.company.name}
                      </span>
                      <span>
                        <MapPin size={14} />
                        {job.location} · {job.work_mode}
                      </span>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </aside>
        </div>
      )}
    </main>
  );
}

export default App;
