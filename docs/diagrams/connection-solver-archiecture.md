# High-level Architechure
After adding CALM Architecture JSON File to its context GHCP (gpt-5-mini) generated diagram with this prompt:

```text
generate mermaid diagram that shows the nodes and interfaces
```

Manually edited to remove extraneous items for visual clarity.

```mermaid
flowchart TD
  %% Player
  subgraph Player["Puzzle Player (actor)"]
    player_browser["player-browser-interface\n(hostname: localhost)"]
  end

  %% Frontend
  subgraph Frontend["Connection Solver Web Application (webclient)"]
    frontend_http["frontend-http-interface\n(host: localhost:3000)"]
    frontend_api_client["frontend-api-client\n(url: http://localhost:8000)"]
  end

  %% Backend
  subgraph Backend["Connection Solver Backend API (service)"]
    backend_rest["backend-rest-api\n(host: localhost:8000)"]
  end

  %% OpenAI LLM
  subgraph OpenAI["OpenAI LLM Service (external)"]
    openai_api["openai-api-interface\n(https://api.openai.com/v1)"]
  end

  %% Ollama LLM
  subgraph Ollama["Ollama LLM Service (local)"]
    ollama_api["ollama-api-interface\n(host: localhost:11434)"]
  end

  %% Database
  subgraph DB["Game Results SQLite Database"]
    sqlite["sqlite-db-interface\n(database: puzzle_results.db)"]
  end

  %% Relationships / connections
  player_browser -->|Uses UI| frontend_http
  frontend_http -->|API client| frontend_api_client
  frontend_api_client -->|HTTP| backend_rest

  backend_rest -->|HTTPS| openai_api
  backend_rest -->|HTTP| ollama_api
  backend_rest -->|DB API| sqlite


```