# Mini Professional Network

A small LinkedIn-style teaching project for learning cloud deployment.

- Frontend: React + Vite
- Backend: Python + FastAPI
- Database: PostgreSQL for AWS RDS, with SQLite fallback for local development

## Project Shape

```text
.
├── backend
│   ├── app
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── seed.py
│   ├── .env.example
│   └── requirements.txt
└── frontend
    ├── src
    │   ├── App.jsx
    │   ├── api.js
    │   ├── main.jsx
    │   └── styles.css
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Run Locally

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The backend will create and seed a local SQLite database if `DATABASE_URL` is not set.

For RDS PostgreSQL later, set:

```bash
DATABASE_URL=postgresql+psycopg://app_user:password@your-rds-endpoint:5432/professional_network
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL. The frontend calls the backend at `http://localhost:8000` unless you set `VITE_API_BASE_URL`.

## Run With Docker

```bash
docker compose up --build
```

Then open:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000/health
```

The Docker setup runs PostgreSQL locally so the app behaves more like the future AWS RDS deployment.

See [docs/dockerisation.md](docs/dockerisation.md) for the deployment mapping.

## CI/CD Pipeline

GitHub Actions workflow:

```text
.github/workflows/ci-cd.yml
```

The pipeline runs backend unit tests, builds the frontend, and pushes Docker images to ECR on pushes to `main`.

See [docs/devops-pipeline.md](docs/devops-pipeline.md) for setup details.

## API

- `GET /health`
- `GET /api/feed`
- `GET /api/profiles`
- `GET /api/companies`
- `GET /api/jobs`

## First Infrastructure Step

The first infrastructure step is to design and create the network foundation:

1. Create a VPC.
2. Add public subnets for internet-facing services like a load balancer.
3. Add private subnets for the backend service and RDS database.
4. Add routing, NAT access for private workloads, and security groups.

RDS should not be created as a public database. The frontend, backend, and RDS all depend on the network boundaries, so the VPC layout comes first.
