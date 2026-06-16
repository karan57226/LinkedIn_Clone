import {
  BriefcaseBusiness,
  Building2,
  CheckCircle2,
  Cloud,
  Container,
  Database,
  GitBranch,
  Globe2,
  Layers3,
  Lock,
  MapPin,
  RefreshCw,
  Route,
  Server,
  Shield
} from "lucide-react";
import { useEffect, useState } from "react";

import { getFeed, getJobs, getProfiles } from "./api";

const deploymentSteps = [
  {
    title: "Created the VPC network",
    detail:
      "Built a custom VPC in us-west-1 with public, private app, and private DB subnets across us-west-1a and us-west-1c."
  },
  {
    title: "Added internet routing",
    detail:
      "Attached an Internet Gateway, made the public subnets route 0.0.0.0/0 to it, and kept database subnets private."
  },
  {
    title: "Containerized the app",
    detail:
      "Built Docker images for the React frontend and FastAPI backend, then rebuilt them for linux/amd64 so EC2 could run them."
  },
  {
    title: "Pushed images to ECR",
    detail:
      "Published frontend and backend images to Amazon ECR so EC2 instances could pull the deployment artifacts."
  },
  {
    title: "Launched EC2 instances",
    detail:
      "Created separate EC2 instances for frontend and backend, installed Docker, authenticated to ECR, pulled images, and ran containers."
  },
  {
    title: "Placed services behind an ALB",
    detail:
      "Created an internet-facing Application Load Balancer with target groups for frontend port 80 and backend port 8000."
  },
  {
    title: "Configured routing rules",
    detail:
      "Sent normal web traffic to the frontend target group and /api/* requests to the backend target group."
  },
  {
    title: "Moved data to RDS",
    detail:
      "Created RDS PostgreSQL in private DB subnets and restarted the backend with DATABASE_URL pointing to the RDS endpoint."
  }
];

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
          <p className="eyebrow">Production deployment app</p>
          <h1>SmallScale - Linkedin Production Deployment</h1>
        </div>
        <button className="iconButton" type="button" onClick={loadData} aria-label="Refresh data">
          <RefreshCw size={18} />
        </button>
      </header>

      <section className="statusBand">
        <Server size={18} />
        <span>
          A production-style AWS deployment using Docker, ECR, EC2, an Application Load Balancer,
          and RDS PostgreSQL.
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

      <DeploymentStory />
    </main>
  );
}

function DeploymentStory() {
  return (
    <section className="deployment">
      <div className="sectionIntro">
        <p className="eyebrow">How this was deployed</p>
        <h2>Cloud Architecture Walkthrough</h2>
        <p>
          This app started as a local React and FastAPI project, then moved through Docker, ECR,
          EC2, an Application Load Balancer, and finally RDS PostgreSQL.
        </p>
      </div>

      <div className="architectureGrid">
        <article className="flowPanel">
          <h3>Request Flow</h3>
          <div className="flowLine">
            <FlowNode icon={<Globe2 size={20} />} label="User browser" />
            <FlowNode icon={<Route size={20} />} label="ALB" />
            <FlowNode icon={<Container size={20} />} label="Frontend container" />
            <FlowNode icon={<Server size={20} />} label="FastAPI container" />
            <FlowNode icon={<Database size={20} />} label="RDS PostgreSQL" />
          </div>
        </article>

        <article className="vpcDiagram" aria-label="VPC architecture diagram">
          <div className="diagramHeader">
            <Cloud size={20} />
            <div>
              <h3>VPC in us-west-1</h3>
              <span>Two availability zones: us-west-1a and us-west-1c</span>
            </div>
          </div>

          <div className="vpcBox">
            <div className="azColumn">
              <strong>us-west-1a</strong>
              <DiagramBox tone="public" title="Public subnet" text="ALB + frontend EC2 access" />
              <DiagramBox tone="app" title="Private/app layer" text="Backend EC2 container" />
              <DiagramBox tone="db" title="DB subnet" text="RDS subnet group member" />
            </div>
            <div className="azColumn">
              <strong>us-west-1c</strong>
              <DiagramBox tone="public" title="Public subnet" text="ALB second AZ" />
              <DiagramBox tone="app" title="Private/app layer" text="Scale-out EC2 capacity" />
              <DiagramBox tone="db" title="DB subnet" text="RDS subnet group member" />
            </div>
          </div>
        </article>
      </div>

      <div className="securityPanel">
        <div>
          <Shield size={20} />
          <h3>Security Group Model</h3>
        </div>
        <ul>
          <li>ALB allows HTTP from the internet.</li>
          <li>Frontend EC2 allows HTTP only from the ALB security group.</li>
          <li>Backend EC2 allows port 8000 only from the ALB security group.</li>
          <li>RDS allows PostgreSQL port 5432 only from the backend security group.</li>
        </ul>
      </div>

      <div className="stepsGrid">
        {deploymentSteps.map((step, index) => (
          <article className="stepCard" key={step.title}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <CheckCircle2 size={18} />
            <h3>{step.title}</h3>
            <p>{step.detail}</p>
          </article>
        ))}
      </div>

      <div className="runtimePanel">
        <div>
          <Layers3 size={20} />
          <h3>Runtime Architecture</h3>
        </div>
        <div className="runtimeList">
          <RuntimeItem icon={<GitBranch size={17} />} label="Source" value="React frontend + Python FastAPI backend" />
          <RuntimeItem icon={<Container size={17} />} label="Images" value="Docker images stored in Amazon ECR" />
          <RuntimeItem icon={<Server size={17} />} label="Compute" value="EC2 instances running Docker containers" />
          <RuntimeItem icon={<Route size={17} />} label="Routing" value="ALB sends /api/* to backend and everything else to frontend" />
          <RuntimeItem icon={<Lock size={17} />} label="Data" value="RDS PostgreSQL in private DB subnets" />
        </div>
      </div>
    </section>
  );
}

function FlowNode({ icon, label }) {
  return (
    <div className="flowNode">
      {icon}
      <span>{label}</span>
    </div>
  );
}

function DiagramBox({ tone, title, text }) {
  return (
    <div className={`diagramBox ${tone}`}>
      <span>{title}</span>
      <small>{text}</small>
    </div>
  );
}

function RuntimeItem({ icon, label, value }) {
  return (
    <div className="runtimeItem">
      {icon}
      <strong>{label}</strong>
      <span>{value}</span>
    </div>
  );
}

export default App;
