# NYT Connections Puzzle Solver Architecture

This document provides a visual representation of the system architecture based on the CALM specification, including detailed views of nodes, interfaces, and the LLM provider architecture.

## System Architecture Overview

```mermaid
graph TB
    %% Actors
    Player["Puzzle Player<br/>(Actor)"]

    %% Frontend
    Frontend["Connection Solver<br/>Web Application<br/>(React/TypeScript)<br/>localhost:3000"]

    %% Backend
    Backend["Connection Solver<br/>Backend API<br/>(FastAPI/Python)<br/>localhost:8000"]

    %% External Services
    OpenAI["OpenAI LLM Service<br/>(External API)<br/>api.openai.com"]
    Ollama["Ollama LLM Service<br/>(Local Service)<br/>localhost:11434"]

    %% Database
    Database[("Game Results<br/>SQLite Database<br/>puzzle_results.db")]

    %% LLM Providers in Backend
    SimpleProvider["Simple Provider<br/>(Internal)<br/>Rule-based, &lt;100ms"]
    OpenAIProvider["OpenAI Provider<br/>(External Integration)<br/>2-5 seconds"]
    OllamaProvider["Ollama Provider<br/>(Local Integration)<br/>10-60 seconds"]

    %% Connections
    Player -->|"HTTP<br/>Browser"| Frontend
    Frontend -->|"HTTP<br/>REST API<br/>Timeout: 5min"| Backend

    %% Backend to LLM Providers (internal)
    Backend -.->|"Factory Pattern"| SimpleProvider
    Backend -.->|"Factory Pattern"| OpenAIProvider
    Backend -.->|"Factory Pattern"| OllamaProvider

    %% Provider to External Services
    OpenAIProvider -->|"HTTPS<br/>OpenAI API v1"| OpenAI
    OllamaProvider -->|"HTTP"| Ollama

    %% Backend to Database
    Backend -->|"JDBC<br/>SQLite"| Database

    %% Styling
    classDef actor fill:lightskyblue,stroke:darkblue,stroke-width:3px
    classDef frontend fill:lavender,stroke:purple,stroke-width:2px
    classDef backend fill:wheat,stroke:darkorange,stroke-width:2px
    classDef external fill:lightgreen,stroke:darkgreen,stroke-width:2px
    classDef database fill:pink,stroke:crimson,stroke-width:2px
    classDef provider fill:lightyellow,stroke:gold,stroke-width:1px,stroke-dasharray: 5 5

    class Player actor
    class Frontend frontend
    class Backend backend
    class OpenAI,Ollama external
    class Database database
    class SimpleProvider,OpenAIProvider,OllamaProvider provider
```

## LLM Provider Architecture

```mermaid
graph LR
    subgraph "Backend API Service"
        Factory["LLMProviderFactory<br/>(backend/src/services/<br/>llm_provider_factory.py)"]

        subgraph "Provider Implementations"
            Simple["SimpleLLMProvider<br/>Type: internal<br/>Response: &lt;100ms<br/>No external deps"]
            OpenAIImpl["OpenAILLMProvider<br/>Type: external<br/>Response: 2-5s<br/>Requires: API Key"]
            OllamaImpl["OllamaLLMProvider<br/>Type: local-service<br/>Response: 10-60s<br/>No API Key needed"]
        end

        Factory -->|"Instantiates"| Simple
        Factory -->|"Instantiates"| OpenAIImpl
        Factory -->|"Instantiates"| OllamaImpl
    end

    OpenAIImpl -->|"HTTPS"| ExtOpenAI["OpenAI API<br/>api.openai.com"]
    OllamaImpl -->|"HTTP"| ExtOllama["Ollama Service<br/>localhost:11434"]

    classDef factory fill:#ffe0b2,stroke:#e65100,stroke-width:2px
    classDef internal fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef external fill:#ffccbc,stroke:#bf360c,stroke-width:2px
    classDef service fill:#b2dfdb,stroke:#00695c,stroke-width:2px
    classDef externalNode fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px

    class Factory factory
    class Simple internal
    class OpenAIImpl external
    class OllamaImpl service
    class ExtOpenAI,ExtOllama externalNode
```

## Provider Characteristics

| Provider | Type | Response Time | External Service | API Key | Use Case |
|----------|------|---------------|------------------|---------|----------|
| **Simple** | Internal | < 100ms | ❌ No | ❌ No | Testing, development, baseline |
| **OpenAI** | External API | 2-5 seconds | ✅ Yes | ✅ Yes | Production AI recommendations |
| **Ollama** | Local Service | 10-60 seconds | ✅ Yes (local) | ❌ No | Privacy-focused, no API costs |

### Simple Provider Details
- **Implementation**: LangChain FakeListLLM with hardcoded responses
- **Capabilities**: Basic recommendations only (no AI, no explanations)
- **Predefined Responses**:
  1. BASS, FLOUNDER, SALMON, TROUT
  2. PIANO, GUITAR, VIOLIN, DRUMS
  3. RED, BLUE, GREEN, YELLOW
  4. APPLE, BANANA, ORANGE, GRAPE


## Key API Endpoints

### Backend Service Endpoints (localhost:8000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/puzzle/setup_puzzle` | POST | Initialize puzzle with 16 words |
| `/api/puzzle/next_recommendation` | GET | Get next recommendation (legacy) |
| `/api/puzzle/record_response` | POST | Record player response |
| `/api/v2/recommendations` | POST | Get AI recommendation |
| `/api/v2/providers` | GET | List available providers |
| `/api/v2/providers/validate` | POST | Validate provider configuration |
| `/api/v2/providers/status` | GET | Get provider status |
| `/api/v2/setup_puzzle_from_image` | POST | Setup puzzle from image |
| `/api/v2/game_results` | POST/GET | Store/retrieve game history |


## Database Schema

### Game Results Table

```mermaid
erDiagram
    GAME_RESULTS {
        string session_id PK
        date puzzle_date
        json words
        json recommendations
        json responses
        string final_status
        timestamp created_at
        timestamp updated_at
    }
```

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | React | 18.x |
| | TypeScript | - |
| | Create React App | - |
| **Backend** | Python | 3.11+ |
| | FastAPI | - |
| | LangChain | - |
| | Uvicorn | - |
| **LLM** | OpenAI API | v1 (gpt-4o-mini) |
| | Ollama | - (qwen2.5:32b) |
| **Database** | SQLite | 3.x |

## Environment Configuration

### Required Environment Variables

```bash
# OpenAI Provider (required for OpenAI)
OPENAI_API_KEY=sk-...           # Required
OPENAI_MODEL_NAME=gpt-4o-mini   # Optional (default shown)
OPENAI_TIMEOUT=300              # Optional (seconds)

# Ollama Provider (optional)
OLLAMA_BASE_URL=http://localhost:11434  # Optional (default shown)

# Backend Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Simple Provider
No configuration required - works out of the box for testing and development.

## Performance Targets

| Operation | Target Time |
|-----------|-------------|
| Non-LLM API Response | < 100ms |
| Simple Provider Response | < 100ms |
| OpenAI Response (typical) | 2-5 seconds |
| Ollama Response (typical) | 10-60 seconds |
| Database Insert | < 10ms |
| Database Query | < 50ms |

## Error Handling

| Error Type | HTTP Status | Description |
|------------|-------------|-------------|
| Validation Errors | 400 | Invalid request data |
| LLM Provider Errors | 503 | Provider-specific failures |
| Timeout Errors | 504 | Request timeout |
| Configuration Errors | 500 | Server configuration issues |

### Provider-Specific Errors
- **SimpleProviderError**: Internal rule-based logic failure
- **OpenAIAPIError**: OpenAI API failures (401/429/503)
- **OllamaConnectionError**: Ollama service connectivity issues

## Deployment Model

- **Type**: Full-stack web application
- **Environment**: Single-user local deployment
- **Authentication**: None required
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Database**: Local SQLite file (puzzle_results.db)
- **Ollama**: Local service on http://localhost:11434 (optional)
- **OpenAI**: External cloud service (optional)

---

## User Flows

This section details all the key user flows through the system, mapped from the CALM architecture specification.

### Flow 1: Puzzle Setup Process (CSV Upload)

**Business Process**: Puzzle Initialization
**API Endpoint**: `POST /api/puzzle/setup_puzzle`
**Success Criteria**: Session created with 16 validated words

```mermaid
sequenceDiagram
    actor Player
    participant Frontend as Web App
    participant Backend as Backend API

    Note over Player,Backend: User Journey Step 1: Setup

    Player->>Frontend: Upload CSV file (16 words)
    activate Frontend
    Frontend->>Backend: POST /api/puzzle/setup_puzzle<br/>{csv_content}
    activate Backend
    Backend->>Backend: Validate 16 words
    Backend->>Backend: Create session
    Backend-->>Frontend: {session_id, words}
    deactivate Backend
    Frontend->>Frontend: Initialize puzzle interface
    Frontend-->>Player: Display 16 word grid
    deactivate Frontend
```

### Flow 2: AI Recommendation Generation Process

**Business Process**: Recommendation Generation
**API Endpoints**: `GET /api/puzzle/next_recommendation`, `POST /api/v2/recommendations`
**LLM Providers**: OpenAI, Ollama, Simple
**Success Criteria**: 4 words returned with connection explanation

```mermaid
sequenceDiagram
    actor Player
    participant Frontend as Web App
    participant Backend as Backend API
    participant OpenAI as OpenAI Service

    Note over Player,OpenAI: User Journey Step 2: Get Recommendation

    Player->>Frontend: Click "Get Recommendation" button
    activate Frontend
    Frontend->>Backend: POST /api/v2/recommendations<br/>{provider: "openai", remaining_words, previous_guesses}
    activate Backend

    Note over Backend,OpenAI: Example shows OpenAI provider
    Backend->>OpenAI: Request recommendation with puzzle context
    activate OpenAI
    OpenAI->>OpenAI: Generate 4-word grouping
    OpenAI-->>Backend: {words: [w1,w2,w3,w4], explanation}
    deactivate OpenAI

    Backend->>Backend: Format response
    Backend-->>Frontend: {recommended_words, connection_explanation, provider_used, generation_time_ms}
    deactivate Backend

    Frontend->>Frontend: Display words & explanation
    Frontend-->>Player: Show recommended group with explanation
    deactivate Frontend
```

### Flow 3: Local LLM Recommendation Process (Ollama)

**Business Process**: Local LLM Recommendation
**API Endpoint**: `POST /api/v2/recommendations`
**LLM Provider**: Ollama
**Deployment**: Local service on same host

```mermaid
sequenceDiagram
    actor Player
    participant Frontend as Web App
    participant Backend as Backend API
    participant Ollama as Ollama Service<br/>(localhost:11434)

    Note over Player,Ollama: User Journey Step 2: Get Recommendation (Ollama)

    Player->>Frontend: Select Ollama provider
    Player->>Frontend: Click "Get Recommendation"
    activate Frontend
    Frontend->>Backend: POST /api/v2/recommendations<br/>{provider: "ollama", model: "qwen2.5:32b"}
    activate Backend

    Backend->>Ollama: HTTP request with prompt
    activate Ollama
    Note over Ollama: Local LLM inference<br/>(10-60 seconds)
    Ollama-->>Backend: Recommendation response
    deactivate Ollama

    Backend->>Backend: Process & validate response
    Backend-->>Frontend: Formatted recommendation
    deactivate Backend

    Frontend-->>Player: Display Ollama recommendation
    deactivate Frontend
```

### Flow 4: User Response Recording Process

**Business Process**: Response Recording
**API Endpoint**: `POST /api/puzzle/record_response`
**State Updates**: `remaining_words`, `mistake_count`, `game_status`
**Game Rules**: Max 4 mistakes allowed

```mermaid
sequenceDiagram
    actor Player
    participant Frontend as Web App
    participant Backend as Backend API

    Note over Player,Backend: User Journey Step 3: Record Response

    Player->>Frontend: Indicate result:<br/>✓ Correct / ✗ Incorrect / ≈ One-Away
    activate Frontend

    alt Correct
        Frontend->>Backend: POST /api/puzzle/record_response<br/>{result: "correct", words: [w1,w2,w3,w4]}
        activate Backend
        Backend->>Backend: Remove words from remaining
        Backend->>Backend: Increment correct count
        Backend-->>Frontend: {remaining_words, game_status: "in_progress"}
        deactivate Backend
        Frontend-->>Player: ✅ Show success, update grid
    else Incorrect
        Frontend->>Backend: POST /api/puzzle/record_response<br/>{result: "incorrect"}
        activate Backend
        Backend->>Backend: Increment mistake_count
        Backend->>Backend: Check if mistake_count >= 4
        alt Game Over
            Backend-->>Frontend: {game_status: "lost", mistakes: 4}
            Frontend-->>Player: ❌ Game Over - Max mistakes reached
        else Continue
            Backend-->>Frontend: {mistakes: n, game_status: "in_progress"}
            Frontend-->>Player: ⚠️ Mistake recorded (n/4)
        end
        deactivate Backend
    else One-Away
        Frontend->>Backend: POST /api/puzzle/record_response<br/>{result: "one_away"}
        activate Backend
        Backend->>Backend: Increment mistake_count
        Backend-->>Frontend: {mistakes: n, hint: "one away"}
        deactivate Backend
        Frontend-->>Player: ⚠️ One word away! (n/4 mistakes)
    end

    deactivate Frontend
```

### Flow 5: LLM Provider Validation Process

**Business Process**: Provider Configuration
**API Endpoint**: `POST /api/v2/providers/validate`
**Validation Checks**: API key, connectivity, model availability

```mermaid
sequenceDiagram
    actor Player
    participant Frontend as Web App
    participant Backend as Backend API
    participant OpenAI as OpenAI Service

    Note over Player,OpenAI: User Journey Step 0: Setup/Configuration

    Player->>Frontend: Configure LLM provider settings<br/>(e.g., enter API key)
    activate Frontend
    Frontend->>Backend: POST /api/v2/providers/validate<br/>{provider: "openai", api_key: "sk-..."}
    activate Backend

    Backend->>OpenAI: Test API connectivity<br/>(lightweight health check)
    activate OpenAI

    alt Valid Configuration
        OpenAI-->>Backend: HTTP 200 - Success
        Backend->>Backend: Mark provider as available
        Backend-->>Frontend: {valid: true, status: "available"}
        Frontend-->>Player: ✅ OpenAI provider configured successfully
    else Invalid API Key
        OpenAI-->>Backend: HTTP 401 - Unauthorized
        Backend-->>Frontend: {valid: false, error: "Invalid API key"}
        Frontend-->>Player: ❌ Invalid API key - check configuration
    else Connection Error
        Note over Backend,OpenAI: Connection times out
        Backend-->>Frontend: {valid: false, error: "Connection failed"}
        Frontend-->>Player: ❌ Cannot reach OpenAI - check network
    end

    deactivate OpenAI
    deactivate Backend
    deactivate Frontend
```

### Flow 6: Image-Based Puzzle Setup Process

**Business Process**: Image-Based Setup
**API Endpoint**: `POST /api/v2/setup_puzzle_from_image`
**LLM Capability**: Vision API
**Image Format**: base64-encoded, JPEG/PNG
**Success Criteria**: 16 words extracted from 4x4 grid

```mermaid
sequenceDiagram
    actor Player
    participant Frontend as Web App
    participant Backend as Backend API
    participant OpenAI as OpenAI Vision API

    Note over Player,OpenAI: User Journey Step 1: Setup (Alternative - Image Upload)

    Player->>Frontend: Upload puzzle image (4x4 grid)
    activate Frontend
    Frontend->>Frontend: Convert image to base64
    Frontend->>Backend: POST /api/v2/setup_puzzle_from_image<br/>{image_data: "base64...", provider: "openai"}
    activate Backend

    Backend->>OpenAI: Vision API request<br/>(extract 16 words from grid)
    activate OpenAI
    Note over OpenAI: GPT-4 Vision processes image<br/>Identifies 16 words in 4x4 layout
    OpenAI-->>Backend: {words: [w1, w2, ..., w16]}
    deactivate OpenAI

    Backend->>Backend: Validate 16 words extracted
    Backend->>Backend: Create puzzle session
    Backend-->>Frontend: {session_id, words: [16 words]}
    deactivate Backend

    Frontend->>Frontend: Initialize puzzle interface
    Frontend-->>Player: Display extracted words<br/>with editable grid
    deactivate Frontend
```

### Flow 7: Game Results Recording Process

**Business Process**: Game Results Persistence
**API Endpoint**: `POST /api/v2/game_results`
**Database Table**: `game_results`
**Stored Data**: session_id, puzzle_date, words, recommendations, responses, final_status, timestamps

```mermaid
sequenceDiagram
    actor Player
    participant Frontend as Web App
    participant Backend as Backend API
    participant Database as SQLite DB

    Note over Player,Database: User Journey Step 4: Complete Game

    Note over Player: Player completes puzzle<br/>(Win: all correct OR Loss: 4 mistakes)

    Player->>Frontend: Game ends (win/loss)
    activate Frontend
    Frontend->>Frontend: Compile game session data
    Frontend->>Backend: POST /api/v2/game_results<br/>{session_id, puzzle_date, words, recommendations,<br/>responses, final_status, started_at, completed_at}
    activate Backend

    Backend->>Database: INSERT INTO game_results<br/>(session data)
    activate Database
    Database->>Database: Write to puzzle_results.db
    Database-->>Backend: Confirm write (< 10ms)
    deactivate Database

    Backend-->>Frontend: {success: true, result_id}
    deactivate Backend

    Frontend->>Frontend: Show completion screen
    Frontend-->>Player: Display final results<br/>with statistics
    deactivate Frontend
```

### Flow 8: Game History Retrieval Process

**Business Process**: Game History Analysis
**API Endpoint**: `GET /api/v2/game_results`
**Export Format**: JSON, CSV (via `?format=csv` query parameter)
**Display Features**: Pagination, filtering, sorting, CSV download

```mermaid
sequenceDiagram
    actor Player
    participant Frontend as Web App
    participant Backend as Backend API
    participant Database as SQLite DB

    Note over Player,Database: User Journey Step 5: Review History

    Player->>Frontend: Navigate to "Game History" view
    activate Frontend
    Frontend->>Backend: GET /api/v2/game_results<br/>(optional: ?limit=50&offset=0)
    activate Backend

    Backend->>Database: SELECT * FROM game_results<br/>ORDER BY completed_at DESC
    activate Database
    Database-->>Backend: Game records (< 50ms)
    deactivate Database

    Backend->>Backend: Format results
    Backend-->>Frontend: {total: N, games: [{...}, {...}]}
    deactivate Backend

    Frontend->>Frontend: Render game history table
    Frontend-->>Player: Display games with:<br/>- Date<br/>- Result (Win/Loss)<br/>- Mistakes<br/>- Provider used<br/>- Duration

    opt Player requests CSV export
        Player->>Frontend: Click "Export CSV"
        Frontend->>Backend: GET /api/v2/game_results?format=csv
        activate Backend
        Backend->>Database: SELECT * FROM game_results
        activate Database
        Database-->>Backend: All records
        deactivate Database
        Backend->>Backend: Generate CSV (< 100ms)
        Backend-->>Frontend: CSV file download
        deactivate Backend
        Frontend-->>Player: Download game_history.csv
    end

    deactivate Frontend
```

## Flow Summary Table

| Flow # | Name | Primary Endpoint | User Journey Step | Key LLM Integration |
|--------|------|-----------------|-------------------|---------------------|
| 1 | Puzzle Setup (CSV) | POST /api/puzzle/setup_puzzle | 1-Setup | None |
| 2 | AI Recommendation (OpenAI) | POST /api/v2/recommendations | 2-Get-Recommendation | OpenAI API |
| 3 | AI Recommendation (Ollama) | POST /api/v2/recommendations | 2-Get-Recommendation | Ollama Local |
| 4 | Response Recording | POST /api/puzzle/record_response | 3-Record-Response | None |
| 5 | Provider Validation | POST /api/v2/providers/validate | 0-Setup | OpenAI/Ollama Health Check |
| 6 | Image-Based Setup | POST /api/v2/setup_puzzle_from_image | 1-Setup-Alternative | OpenAI Vision API |
| 7 | Game Results Recording | POST /api/v2/game_results | 4-Complete-Game | None |
| 8 | Game History Retrieval | GET /api/v2/game_results | 5-Review-History | None |
