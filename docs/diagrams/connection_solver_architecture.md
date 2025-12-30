# Connection Solver Architecture Diagram

This document contains a Mermaid diagram depicting the architecture of the NYT Connections Puzzle Solver application, based on the CALM architecture specification.


## System Architecture

```mermaid
graph TB
    %% Actors
    Player[["Puzzle Player<br/>(Actor)"]]

    %% Frontend
    Frontend["Connection Solver Web Application<br/>(WebClient)<br/>localhost:3000"]

    %% Backend
    Backend["Connection Solver Backend API<br/>(Service)<br/>localhost:8000"]

    %% External Services
    OpenAI["OpenAI LLM Service<br/>(Service)<br/>api.openai.com"]
    Ollama["Ollama LLM Service<br/>(Service)<br/>localhost:11434"]

    %% Database
    DB[("Game Results SQLite Database<br/>(Database)<br/>puzzle_results.db")]

    %% Relationships
    Player -->|"Interacts via Browser"| Frontend
    Frontend -->|"HTTP API Calls<br/>Port 3000 → 8000"| Backend
    Backend -->|"HTTPS<br/>OpenAI API v1"| OpenAI
    Backend -->|"HTTP<br/>Local LLM"| Ollama
    Backend -->|"JDBC<br/>Read/Write Game Results"| DB

    %% Styling
    classDef actor fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef webclient fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef service fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef external fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef database fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class Player actor
    class Frontend webclient
    class Backend service
    class OpenAI,Ollama external
    class DB database
```

## Backend API Endpoints

The backend service exposes the following key endpoints:

### Health & Status
- `GET /health` - Service health check
- `GET /` - Root endpoint
- `GET /api/v2/recommendations/health` - Recommendations service health
- `GET /api/v2/providers/status` - Provider status check

### Puzzle Operations
- `POST /api/puzzle/setup_puzzle` - Initialize puzzle from CSV
- `GET /api/puzzle/next_recommendation` - Get AI recommendation (v1)
- `POST /api/puzzle/record_response` - Record player response
- `POST /api/v2/setup_puzzle_from_image` - Initialize puzzle from image

### Recommendations (v2)
- `POST /api/v2/recommendations` - Generate AI recommendation
- `GET /api/v2/recommendations/providers` - List available providers

### Provider Management (v2)
- `GET /api/v2/providers` - List LLM providers
- `POST /api/v2/providers/validate` - Validate provider configuration

### Game Results (v2)
- `POST /api/v2/game_results` - Save completed game results
- `GET /api/v2/game_results` - Retrieve game history (JSON/CSV)

## Key Flows

```mermaid
sequenceDiagram
    participant P as Player
    participant F as Frontend
    participant B as Backend
    participant L as LLM Service
    participant D as Database

    %% Puzzle Setup Flow
    rect rgb(230, 245, 255)
        note right of P: Puzzle Setup Flow
        P->>F: Upload CSV file (16 words)
        F->>B: POST /api/puzzle/setup_puzzle
        B-->>F: Session created
        F-->>P: Display puzzle interface
    end

    %% Recommendation Flow
    rect rgb(245, 255, 230)
        note right of P: Recommendation Generation Flow
        P->>F: Click "Get Recommendation"
        F->>B: POST /api/v2/recommendations
        B->>L: Request recommendation (with context)
        L-->>B: Return 4 words + explanation
        B-->>F: Formatted recommendation
        F-->>P: Display recommendation
    end

    %% Response Recording Flow
    rect rgb(255, 245, 230)
        note right of P: Response Recording Flow
        P->>F: Indicate correct/incorrect/one-away
        F->>B: POST /api/puzzle/record_response
        B-->>F: Updated game state
        F-->>P: Display updated puzzle
    end

    %% Game Results Flow
    rect rgb(255, 230, 245)
        note right of P: Game Results Recording Flow
        P->>F: Complete puzzle (win/loss)
        F->>B: POST /api/v2/game_results
        B->>D: Write game session data
        D-->>B: Confirm write
        B-->>F: Confirmation
        F-->>P: Display completion message
    end
```

## Technology Stack

- **Frontend**: React 18.x, TypeScript, Create React App
- **Backend**: FastAPI, Python 3.11+, Pydantic, Uvicorn
- **LLM Integration**: LangChain, OpenAI API v1, Ollama
- **Database**: SQLite 3.x
- **Default Models**:
  - OpenAI: `gpt-4o-mini`
  - Ollama: `qwen2.5:32b`

## Performance Targets

| Operation | Target |
|-----------|--------|
| Non-LLM API Response | < 100ms |
| Simple Provider Response | < 100ms |
| OpenAI Response | 2-5 seconds |
| Ollama Response | 10-60 seconds (hardware dependent) |
| Database Insert | < 10ms |
| Database Query | < 50ms |

## Authentication & Security

- **No authentication required** - Single-user local deployment
- **API Keys**: Configured via environment variables (`OPENAI_API_KEY`)
- **CORS**: Configured for `http://localhost:3000` and `http://127.0.0.1:3000`
- **Local Access Only**: All services run on localhost

## Error Handling

- **No automatic retry** - User-initiated retry only
- **No timeout** for LLM requests - Indefinite loading indicator
- **No automatic fallback** between providers
- **All LLM failures** return HTTP 503 with error details
- **Validation errors** return HTTP 400
- **Configuration errors** return HTTP 500
