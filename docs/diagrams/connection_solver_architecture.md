# NYT Connections Puzzle Solver Architecture

This document provides a visual representation of the system architecture based on the CALM specification, including detailed views of nodes, interfaces, and the LLM provider architecture.

## System Architecture Overview

```mermaid
graph TB
    %% Actors
    Player[("Puzzle Player<br/>(Actor)")]

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
    classDef actor fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef frontend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef backend fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef external fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef database fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef provider fill:#fff9c4,stroke:#f57f17,stroke-width:1px,stroke-dasharray: 5 5

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

## Data Flow: Recommendation Generation

```mermaid
sequenceDiagram
    actor Player
    participant Frontend as Web App<br/>(React)
    participant Backend as Backend API<br/>(FastAPI)
    participant Factory as Provider<br/>Factory
    participant Provider as LLM Provider<br/>(Simple/OpenAI/Ollama)
    participant External as External LLM<br/>(if applicable)

    Player->>Frontend: Click "Get Recommendation"
    Frontend->>Backend: POST /api/v2/recommendations<br/>{provider_type, remaining_words}
    Backend->>Factory: create_provider(provider_type)
    Factory->>Provider: Instantiate provider
    Factory-->>Backend: Return provider instance
    Backend->>Provider: generate_recommendation(prompt)

    alt External Provider (OpenAI/Ollama)
        Provider->>External: Send LLM request
        External-->>Provider: Return response
    else Internal Provider (Simple)
        Provider->>Provider: Return hardcoded response
    end

    Provider-->>Backend: LLMRecommendationResponse
    Backend-->>Frontend: {words, explanation, metadata}
    Frontend-->>Player: Display recommendation
```

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
