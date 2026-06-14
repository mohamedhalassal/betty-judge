<p align="center">
  <img src="https://wsrv.nl/?url=raw.githubusercontent.com/mohamedhalassal/betty-judge/main/frontend/public/betty-icon.png&mask=circle&w=250" alt="Betty Judge Icon" />
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Betty_Judge-Competitive_Programming_Platform-6C63FF?style=for-the-badge&logo=codeforces&logoColor=white" alt="Betty Judge" />
</p>

<h1 align="center">Betty Judge</h1>

<p align="center">
  <b>A modern, self-hosted competitive programming judge platform — built for speed, security, and scale.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Azure_Queue-Message_Broker-0078D4?style=flat-square&logo=microsoft-azure&logoColor=white" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#1-backend-setup)
  - [Frontend Setup](#2-frontend-setup)
  - [Judge Worker Setup](#3-judge-worker-setup-linux-only)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Judge System](#-judge-system)
- [Database Schema](#-database-schema)
- [CI/CD & Deployment](#-cicd--deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧠 Overview

**Betty Judge** is a full-stack competitive programming platform where users can:

- 📝 **Browse & solve** algorithmic problems with rich problem statements
- 💻 **Write & submit** solutions via an integrated Monaco code editor (C++, Python, Java)
- ⚡ **Get instant verdicts** — submissions are compiled & executed in a sandboxed Docker environment
- 📊 **Track submissions** with detailed execution time & memory metrics
- 🏆 **Compete on leaderboards** and view other users' profiles
- 🔐 **Authenticate securely** with Google OAuth 2.0

The platform follows a **microservice-inspired architecture** with three independent components: a REST API backend, a real-time judge worker, and a modern React frontend.

---

## 🏗 Architecture

```
┌─────────────────┐     HTTPS      ┌─────────────────────┐
│                 │ ◄────────────► │                     │
│    Frontend     │                │      Backend API    │
│   (Next.js)     │                │     (FastAPI)       │
│   Port: 3000    │                │     Port: 8000      │
│                 │                │                     │
└─────────────────┘                └──────────┬──────────┘
                                              │
                                   ┌──────────▼──────────┐
                                   │                     │
                                   │   Azure Queue       │
                                   │   Storage           │
                                   │  (Message Broker)   │
                                   │                     │
                                   └──────────┬──────────┘
                                              │
                                   ┌──────────▼──────────┐
                                   │                     │
                                   │   Judge Worker      │
                                   │  (Docker Container) │
                                   │                     │
                                   │  • Compiles C++ code│
                                   │  • Runs test cases  │
                                   │  • Enforces limits  │
                                   │  • Updates verdicts │
                                   │                     │
                                   └──────────┬──────────┘
                                              │
                                   ┌──────────▼──────────┐
                                   │                     │
                                   │    PostgreSQL       │
                                   │    Database         │
                                   │                     │
                                   └─────────────────────┘
```

### Flow

1. **User** opens the frontend, authenticates via Google OAuth, and submits a solution
2. **Backend API** saves the submission to the database with status `in queue` and pushes the submission ID to **Azure Queue Storage**
3. **Judge Worker** polls the queue, picks up the submission ID, fetches the source code & test cases from the database
4. **Judge Worker** compiles the code (`g++ -std=gnu++20 -O2`), runs it against each test case with CPU/memory/wall-clock limits, and determines the verdict
5. **Judge Worker** updates the submission record in the database with the verdict, execution time, and memory usage
6. **Frontend** displays the updated verdict to the user

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.13** | Runtime |
| **FastAPI** | REST API framework |
| **SQLModel** | ORM (SQLAlchemy + Pydantic) |
| **PostgreSQL** | Production database |
| **SQLite** | Development fallback database |
| **python-jose** | JWT token creation & verification |
| **Google Auth** | OAuth 2.0 authentication |
| **Azure Storage Queue** | Message queue for async judging |
| **uv** | Dependency management & runner |
| **pytest** | Testing framework |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 16** | React framework (App Router) |
| **React 19** | UI library |
| **TypeScript 5** | Type safety |
| **TailwindCSS 4** | Styling |
| **Monaco Editor** | In-browser code editor |
| **TanStack React Query** | Server state management |
| **Zustand** | Client state management |
| **Framer Motion** | Animations |
| **Sonner** | Toast notifications |
| **Lucide React** | Icon library |
| **Axios** | HTTP client |
| **Google OAuth** | Social login |

### Judge Worker
| Technology | Purpose |
|---|---|
| **Python 3.13** | Runtime |
| **Docker** | Sandboxed execution environment |
| **g++ (GNU C++20)** | C++ compiler |
| **Linux resource limits** | CPU/memory sandboxing via `setrlimit` |
| **Azure Queue** | Job queue consumer |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker** | Containerization |
| **GitHub Actions** | CI/CD pipelines |
| **GitHub Container Registry (ghcr.io)** | Docker image hosting |
| **Vercel** | Frontend deployment |
| **Azure** | Database & queue hosting |

---

## 📁 Project Structure

```
betty-judge/
│
├── backend/                    # FastAPI REST API
│   ├── main.py                 # Application entrypoint
│   ├── pyproject.toml          # Python dependencies (uv)
│   ├── .env                    # Environment variables (not committed)
│   ├── src/
│   │   ├── api/                # Route handlers
│   │   │   ├── auth.py         #   POST /login, GET /me, PATCH /me/username
│   │   │   ├── problems.py     #   CRUD /problems
│   │   │   ├── submissions.py  #   POST /submit, GET /submissions, /my-submissions
│   │   │   └── test_cases.py   #   CRUD /test_cases
│   │   ├── core/               # Core utilities
│   │   │   ├── config.py       #   Environment configuration
│   │   │   ├── security.py     #   JWT encode/decode & auth middleware
│   │   │   ├── google_auth.py  #   Google OAuth token verification
│   │   │   └── username.py     #   Auto-generated unique usernames
│   │   ├── models/             # SQLModel database models
│   │   │   ├── user.py         #   User model
│   │   │   ├── problem.py      #   Problem model
│   │   │   ├── submission.py   #   Submission model + verdict enum
│   │   │   └── test_case.py    #   TestCase model
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   │   ├── auth.py, user.py, problem.py, submission.py, test_case.py
│   │   ├── services/           # Business logic services
│   │   │   ├── message_queue.py    # Abstract MessageQueue interface
│   │   │   └── queue_service.py    # Azure Queue implementation
│   │   ├── dependencies/       # FastAPI dependency injection
│   │   │   └── queue.py        #   Queue service provider
│   │   └── database.py         # Engine, session, and table creation
│   └── tests/                  # Backend test suite
│       ├── conftest.py         #   Shared fixtures
│       ├── test_auth.py        #   Authentication tests
│       ├── test_problem_crud.py    # Problem CRUD tests
│       ├── test_submissions.py     # Submission flow tests
│       └── test_test_cases_crud.py # Test case CRUD tests
│
├── frontend/                   # Next.js 16 React application
│   ├── package.json            # Node.js dependencies
│   ├── next.config.ts          # Next.js configuration
│   ├── tsconfig.json           # TypeScript configuration
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   │   ├── layout.tsx      #   Root layout (fonts, metadata, providers)
│   │   │   ├── providers.tsx   #   Google OAuth, React Query, Sonner providers
│   │   │   ├── globals.css     #   Global styles & design tokens
│   │   │   ├── not-found.tsx   #   404 page
│   │   │   ├── (auth)/         #   Auth route group
│   │   │   │   └── login/      #     Login page
│   │   │   └── (main)/         #   Main app route group
│   │   │       ├── page.tsx    #     Home / landing page
│   │   │       ├── problems/   #     Problem list & detail pages
│   │   │       ├── submissions/#     Submission list & detail pages
│   │   │       ├── leaderboard/#     Leaderboard page
│   │   │       └── profile/    #     User profile pages
│   │   ├── components/         # Reusable UI components
│   │   │   ├── editor/         #   Monaco code editor & language selector
│   │   │   ├── layout/         #   Navbar & footer
│   │   │   ├── shared/         #   Empty state, error state, loading, headers
│   │   │   ├── submissions/    #   Submission-specific components
│   │   │   └── ui/             #   Badge, button, card, input, separator, skeleton
│   │   ├── config/             # App configuration
│   │   │   ├── site.ts         #   Site name, URL, API URL
│   │   │   ├── nav.ts          #   Navigation items
│   │   │   └── editor.ts       #   Editor settings & language definitions
│   │   └── lib/                # Shared utilities
│   │       ├── api/            #   API client functions (auth, problems, submissions)
│   │       ├── hooks/          #   React Query hooks
│   │       ├── store/          #   Zustand stores (auth, editor)
│   │       ├── types/          #   TypeScript type definitions
│   │       └── utils.ts        #   Utility functions
│   └── public/                 # Static assets
│
├── judge/                      # Sandboxed code execution worker
│   ├── main.py                 # Worker entrypoint
│   ├── pyproject.toml          # Python dependencies (uv)
│   ├── src/
│   │   ├── compiler.py         # Code compilation logic
│   │   ├── database.py         # DB connection & models
│   │   ├── executor.py         # Program execution logic
│   │   ├── judge.py            # Main judge pipeline orchestration
│   │   ├── queues.py           # Message queue consumer
│   │   ├── repository.py       # DB access layer
│   │   ├── sandbox.py          # Secure execution environment
│   │   ├── verdict.py          # Verdict definitions & evaluation
│   │   └── worker.py           # Worker loop & queue processing
│   └── tests/                  # Judge integration tests
│
├── docker/                     # Production Dockerfiles
│   ├── backend/
│   │   └── Dockerfile          # Backend API container
│   └── judge/
│       └── Dockerfile          # Judge worker container
│
├── .github/
│   └── workflows/              # GitHub Actions CI/CD
│       ├── backend.yaml        #   Build, test, push backend image
│       ├── judge.yaml          #   Build, test, push judge image
│       └── test_backend.yaml   #   Run backend tests on PRs
│
├── test_schema/                # Test data & CLI utilities
│   ├── click_CLI/              #   CLI tools for database population and sync
│   │   ├── compare.py          #   Compare outputs utility
│   │   ├── create_schema_CLI.py#   Initialize DB schema
│   │   ├── producer_CLI.py     #   Push tasks to queue manually
│   │   └── ...                 #   Other CLI sync scripts
│   ├── models/                 #   Test model definitions
│   │   ├── problem.py          #   Problem test model
│   │   ├── submission.py       #   Submission test model
│   │   ├── test_case.py        #   Test case test model
│   │   └── user.py             #   User test model
│   ├── .env                    #   Test environment variables
│   ├── backend_client.py       #   API client for testing
│   └── database.py             #   Test database configuration
│
├── .gitignore
├── .dockerignore
└── README.md                   # ← You are here
```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| **Python** | ≥ 3.13 | [python.org](https://python.org) |
| **uv** | Latest | See below |
| **Node.js** | ≥ 18 | [nodejs.org](https://nodejs.org) |
| **PostgreSQL** | ≥ 15 | [postgresql.org](https://postgresql.org) |
| **Docker** | Latest | [docker.com](https://docker.com) (for judge worker) |
| **g++** | With C++20 | Included in judge Docker image |

#### Install uv (Python package manager)

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
uv sync

# Create .env file (see Environment Variables section)
cp .env.example .env   # or create manually

# Run the development server
uv run fastapi dev main.py
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id" >> .env.local

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

---

### 3. Judge Worker Setup (Linux Only)

> ⚠️ The judge worker uses Linux-specific system calls (`resource.setrlimit`, `os.wait4`, `os.killpg`) and **must run on Linux** — either natively or via Docker.

#### Option A: Run via Docker (Recommended)

```bash
# Build the judge image from the repo root
docker build -f docker/judge/Dockerfile -t betty-judge-worker .

# Run the worker
docker run --rm \
  -e DATABASE_URL="your-database-url" \
  -e AZURE_QUEUE_CONNECTION_STRING="your-connection-string" \
  -e AZURE_QUEUE_NAME="judge" \
  betty-judge-worker
```

#### Option B: Run natively on Linux

```bash
cd judge
# Ensure g++ is installed
sudo apt-get install -y g++

# Run the worker (it polls the Azure Queue continuously)
python main.py
```

---

## 🔐 Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Required | Default |
|---|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | ✅ | `sqlite://./database.db` (dev only) |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 client ID | ✅ | — |
| `JWT_SECRET_KEY` | Secret key for JWT signing (HS256) | ✅ | — |
| `AZURE_QUEUE_NAME` | Azure Storage Queue name | ✅ | `quickstartqueuesample` |
| `AZURE_QUEUE_ACCOUNT_URL` | Azure Queue account URL | ✅ | — |
| `AZURE_QUEUE_CONNECTION_STRING` | Azure Queue connection string | ✅ | — |
| `FRONTEND_URL` | Allowed CORS origin | ❌ | `http://localhost:3000` |
| `ENV` | Environment (`development` / `production`) | ❌ | `development` |
| `POLYGON_API_KEY` | Polygon API key (problem import) | ❌ | — |
| `POLYGON_API_SECRET` | Polygon API secret | ❌ | — |

### Frontend (`frontend/.env.local`)

| Variable | Description | Required | Default |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API URL | ❌ | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_URL` | Frontend public URL | ❌ | `http://localhost:3000` |
| `NEXT_PUBLIC_GOOGLE_CLIENT_ID` | Google OAuth client ID | ✅ | — |

### Judge Worker

The judge worker reads the `backend/.env` file directly. Key variables:

| Variable | Description | Required | Default |
|---|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | ✅ | — |
| `AZURE_QUEUE_CONNECTION_STRING` | Azure Queue connection string | ✅ | — |
| `AZURE_QUEUE_NAME` | Queue name to poll | ❌ | `quickstartqueuesample` |
| `WORKER_NAME` | Identifier for this worker instance | ❌ | hostname |
| `MAX_QUEUE_DEQUEUE_COUNT` | Max retries before moving to poison queue | ❌ | `5` |

---

## 📡 API Reference

Base URL: `http://localhost:8000`

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/login` | Login/register via Google OAuth token | ❌ |
| `GET` | `/me` | Get current user profile | ✅ |
| `PATCH` | `/me/username` | Update username | ✅ |

### Problems

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/problems` | List all problems (supports `?search=`) | ✅ |
| `POST` | `/problems` | Create a new problem | ✅ |
| `GET` | `/problems/{id}` | Get a specific problem | ✅ |
| `PATCH` | `/problems/{id}` | Update a problem (owner only) | ✅ |
| `DELETE` | `/problems/{id}` | Delete a problem (owner only) | ✅ |

### Submissions

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/submit` | Submit a solution | ✅ |
| `GET` | `/submissions` | List all submissions (paginated, filterable) | ❌ |
| `GET` | `/my-submissions` | List current user's submissions | ✅ |
| `GET` | `/my-submissions/{id}` | Get a specific submission | ✅ |

**Query parameters for `/submissions`:**
- `page` (default: 1) — Page number
- `size` (default: 20, max: 100) — Page size
- `problem_id` — Filter by problem
- `username` — Filter by username
- `verdict` — Filter by verdict status

### Test Cases

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/test_cases` | List all test cases | ✅ |
| `POST` | `/test_cases?problem_id={id}` | Create a test case | ✅ |
| `GET` | `/test_cases/{id}` | Get a specific test case | ✅ |
| `PATCH` | `/test_cases/{id}` | Update a test case | ✅ |
| `DELETE` | `/test_cases/{id}` | Delete a test case | ✅ |

> 📖 Full interactive API documentation is auto-generated at `/docs` (Swagger UI) and `/redoc` (ReDoc) when the backend is running.

---

## ⚖️ Judge System

The judge is the core of Betty Judge — it compiles, executes, and evaluates user submissions in a secure sandboxed environment.

### Supported Verdicts

| Verdict | Code | Description |
|---|---|---|
| 🟢 **Accepted** | `AC` | All test cases passed |
| 🔴 **Wrong Answer** | `WA` | Output doesn't match expected output |
| 🟡 **Time Limit Exceeded** | `TLE` | CPU time exceeded the problem's limit |
| 🟠 **Memory Limit Exceeded** | `MLE` | Memory usage exceeded the problem's limit |
| 🔵 **Runtime Error** | `RE` | Program crashed (SIGSEGV, SIGFPE, etc.) |
| ⚪ **Compile Error** | `CE` | Compilation failed |
| 🟣 **Idleness Limit Exceeded** | `ILE` | Wall clock time exceeded (infinite I/O wait) |
| ⏳ **In Queue** | `—` | Submission is waiting to be judged |

### Compilation

- **Compiler:** `g++`
- **Standard:** `GNU C++20` (`-std=gnu++20`)
- **Optimization:** `-O2`
- **Flags:** `-DONLINE_JUDGE`

### Resource Limits

| Resource | Enforcement |
|---|---|
| **CPU Time** | `RLIMIT_CPU` (soft = problem limit, hard = limit + 2s) |
| **Memory** | `RLIMIT_AS` (5× problem memory limit) |
| **Stack** | `RLIMIT_STACK` (256 MB) |
| **Wall Clock** | Threading timer (3× CPU limit + 5s) |

### Execution Flow

```
Source Code
    │
    ▼
┌──────────┐    Fail    ┌────────────────┐
│ Compile  │ ─────────► │ Compile Error  │
│ (g++)    │            └────────────────┘
└────┬─────┘
     │ Success
     ▼
┌────────────────┐
│ For each test: │◄──────────────────┐
│                │                   │
│  1. Run binary │                   │
│  2. Feed input │                   │
│  3. Wait4()    │                   │
│  4. Check:     │                   │
│     - Signals  │                   │
│     - CPU time │                   │
│     - Memory   │                   │
│     - Output   │                   │
└───────┬────────┘                   │
        │                            │
        ├── TLE? ──► Time Limit      │
        ├── MLE? ──► Memory Limit    │
        ├── RE?  ──► Runtime Error   │
        ├── WA?  ──► Wrong Answer    │
        └── OK?  ──► Next test ──────┘
                          │
                    All passed?
                          │
                          ▼
                    ✅ Accepted
```

### Poison Queue

Messages that fail processing more than `MAX_QUEUE_DEQUEUE_COUNT` times (default: 5) are automatically moved to a **poison queue** (`{queue-name}-poison`) for manual investigation.

---

## 🗄 Database Schema

```
┌──────────────┐       ┌────────────────────┐       ┌──────────────┐
│    users     │       │     problems       │       │  test_cases  │
├──────────────┤       ├────────────────────┤       ├──────────────┤
│ id       PK  │◄──┐   │ id            PK   │◄──┐   │ id       PK  │
│ google_id UK │   │   │ name               │   │   │ problem_id FK│──┐
│ email        │   │   │ statement          │   │   │ input_data   │  │
│ username  UK │   ├──►│ created_by     FK  │   │   │ expected_out │  │
│ created_at   │   │   │ solution           │   ├───│              │  │
└──────────────┘   │   │ checker_code       │   │   │ is_sample    │  │
                   │   │ time_limit (ms)    │   │   └──────────────┘  │
                   │   │ memory_limit (MB)  │   │                     │
                   │   │ created_at         │   │                     │
                   │   └────────────────────┘   │                     │
                   │                            │                     │
                   │   ┌────────────────────┐   │                     │
                   │   │   submissions      │   │                     │
                   │   ├────────────────────┤   │                     │
                   │   │ id            PK   │   │                     │
                   ├──►│ user_id       FK   │   │                     │
                   │   │ problem_id    FK   │───┘                     │
                       │ source_code       │                          │
                       │ submitted_at      │                          │
                       │ execution_time    │                          │
                       │ execution_memory  │                          │
                       │ verdict (enum)    │                          │
                       └────────────────────┘                         │
                                                                      │
                       PK = Primary Key                               │
                       FK = Foreign Key ──────────────────────────────┘
                       UK = Unique Key
```

---

## 🔄 CI/CD & Deployment

### GitHub Actions Workflows

| Workflow | Trigger | Description |
|---|---|---|
| `test_backend.yaml` | Push & PR to `main` | Installs deps with `uv`, runs `pytest` |
| `backend.yaml` | Push to `main` | Builds Docker image → runs tests → pushes to `ghcr.io` |
| `judge.yaml` | Push to `main` | Builds Docker image → runs judge tests → pushes to `ghcr.io` |

### Docker Images

```bash
# Backend API
ghcr.io/{owner}/betty-backend:latest

# Judge Worker
ghcr.io/{owner}/judge:latest
```

### Frontend Deployment

The frontend is deployed on **Vercel** and auto-deploys on push to `main`. Configuration is in the `.vercel/` directory.

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
uv run pytest tests
```

Tests cover:
- **Authentication** — Google login flow, JWT creation, `/me` endpoint
- **Problems CRUD** — Create, read, update, delete problems with authorization
- **Submissions** — Submit solutions, query submissions with filters & pagination
- **Test Cases CRUD** — Create, read, update, delete test cases

### Judge Tests

```bash
cd judge
python -m pytest tests
```

Tests cover:
- **Accepted** — Correct solutions pass all test cases
- **Wrong Answer** — Incorrect output detection
- **Compile Error** — Invalid C++ code handling
- **Time Limit Exceeded** — Infinite loops and slow code
- **Memory Limit Exceeded** — Large memory allocations
- **Runtime Error** — Segfaults, division by zero, etc.
- **Idleness Limit Exceeded** — Blocking I/O operations

### Running Tests in Docker

```bash
# Backend
docker build -f docker/backend/Dockerfile -t betty-backend .
docker run --rm -e DATABASE_URL=sqlite:///test.db betty-backend uv run pytest tests

# Judge
docker build -f docker/judge/Dockerfile -t judge .
docker run --rm \
  -e DATABASE_URL=sqlite:///test.db \
  -e AZURE_QUEUE_CONNECTION_STRING="UseDevelopmentStorage=true" \
  judge python -m pytest tests
```

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines

- Backend code follows **PEP 8** conventions
- Frontend uses **TypeScript strict mode** and **ESLint**
- All new features must include tests
- PRs to `main` trigger automated tests

---

## 📄 License

This project is open source. See the repository for license details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/m10090">Mohamed Eltamawey</a>, <a href="https://github.com/Abdo-Saad">Abdelrahman Saad</a>, and <a href="https://github.com/mohamedhalassal">Mohamed Ahmed Alassal</a>
</p>
