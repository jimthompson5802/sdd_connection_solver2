%% Mermaid architecture diagram for sdd_connection_solver2
%% Render with a Mermaid-aware previewer (e.g., VS Code Mermaid preview)

```mermaid
flowchart TD
  subgraph Browser[User Browser]
    U[User]
  end

  subgraph Frontend["Frontend (frontend/)"]
    FEApp[React / TypeScript App]
    FEBuild[Build / Static Assets]
    FEComponents[UI Components]
    FEServices["API Client & State"]
    FETests[Frontend Tests]
  end

  subgraph Backend["Backend (backend/)"]
    API["API Layer (v1 endpoints)"]
    Main["App Entrypoint / FastAPI (or similar)"]
    Reco[Recommendation Engine]
    Models[Domain Models / Pydantic]
    Exceptions[Error Handling]
    Health[Health & Config Services]
    BETests[Backend Tests]
  end

  subgraph Data["Data & Storage"]
    CSV["CSV files in `/data`"]
    DB[(Optional DB)]
    Cache[(Optional Cache/Redis)]
  end

  subgraph External["External Services"]
    LLM["LLM Provider (OpenAI / Ollama / other)"]
    CDN["CDN / Static Hosting"]
  end

  %% Relationships
  U -->|Interacts with| FEApp
  FEApp -->|uses| FEComponents
  FEApp -->|fetch POST/GET JSON| FEServices
  FEServices -->|"HTTPS REST (JSON)"| API
  FEBuild -->|deployed to| CDN
  API -->|routes requests to| Main
  Main -->|calls| Reco
  Reco -->|uses| Models
  Main -->|reads/writes| CSV
  Main -->|may persist| DB
  Main -->|may use| Cache
  Main -->|calls LLM via HTTP/gRPC| LLM
  API -->|exposes health/config endpoints| Health

  %% Testing & CI
  FETests -.-> FEApp
  BETests -.-> API

  %% Deployment notes
  CDN -->|serves| U
  LLM -->|external API| External

  style Frontend fill:#f9f,stroke:#333,stroke-width:1px
  style Backend fill:#bbf,stroke:#333,stroke-width:1px
  style Data fill:#efe,stroke:#333,stroke-width:1px
  style External fill:#fdd,stroke:#333,stroke-width:1px

  classDef small font-size:12px;
  class FEBuild,FETests,BETests small;
```

Legend:
- `Frontend` — code in `frontend/` (React/TS). Communicates with backend via REST JSON endpoints (e.g., `/api/v1/*`).
- `Backend` — code in `backend/` (Python). Implements API routes, recommendation engine, model validation, health and config services.
- `Data` — local CSVs in `data/` or an optional DB/cache for persistent/session state.
- `External` — third-party LLMs and hosting/CDN used for static assets.

Notes & Integration Points:
- Frontend builds static assets (`frontend/build`) which can be served by a CDN or the backend's static file server.
- The front-end API client in `frontend/src` talks to the backend API (`/api/v1`) using JSON.
- Backend may call external LLM providers via `llm_provider_factory` or similar modules; treat those calls as network-external and mock in tests.
- Tests live under `frontend/tests` and `backend/tests`; maintain CI steps to run both.
