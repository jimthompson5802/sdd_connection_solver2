# CALM Architecture Documentation

This directory contains the FINOS CALM (Common Architecture Language Model) architecture definition for the NYT Connections Puzzle Solver application.

## Files

- `connection-solver.architecture.json` - Complete CALM architecture definition

## Architecture Overview

The architecture models a full-stack web application that assists users in solving NYT Connections puzzles using AI-powered recommendations.

### Nodes (5)

1. **player** (actor) - End user who interacts with the web application
2. **frontend-webclient** (webclient) - React-based web application (localhost:3000)
3. **backend-api-service** (service) - FastAPI backend API (localhost:8000)
4. **openai-llm-service** (service) - External OpenAI API for LLM capabilities
5. **ollama-llm-service** (service) - Local Ollama service for open-source LLMs (localhost:11434)

### Interfaces (16)

The architecture defines detailed interfaces for:
- Player browser interface
- Frontend HTTP server (port 3000)
- Frontend API client
- Backend REST API (port 8000)
- Backend API endpoints:
  - `POST /api/puzzle/setup_puzzle`
  - `GET /api/puzzle/next_recommendation`
  - `POST /api/puzzle/record_response`
  - `POST /api/v2/recommendations`
  - `POST /api/v2/providers/validate`
  - `GET /api/v2/providers/status`
  - `POST /api/v2/setup_puzzle_from_image`
- OpenAI API interface (https://api.openai.com/v1)
- Ollama API interface (localhost:11434)

### Relationships (4)

1. **player-interaction** - Player interacts with frontend through browser
2. **frontend-to-backend-connection** - Frontend connects to backend via HTTP REST API
3. **backend-to-openai-connection** - Backend connects to OpenAI API via HTTPS
4. **backend-to-ollama-connection** - Backend connects to Ollama service via HTTP

### Flows (6)

Complete business process flows documented:

1. **puzzle-setup-flow** - CSV file upload and puzzle initialization
2. **recommendation-generation-flow** - AI-powered recommendation using OpenAI
3. **ollama-recommendation-flow** - Local LLM recommendation using Ollama
4. **response-recording-flow** - User feedback and game state updates
5. **provider-validation-flow** - LLM provider configuration validation
6. **image-puzzle-setup-flow** - Image-based puzzle setup using Vision API

Each flow includes:
- Detailed transitions showing data flow through the architecture
- Metadata with business context, API endpoints, and success criteria
- Directional information (source-to-destination or destination-to-source)

## Validation

The architecture has been validated against FINOS CALM v1.1 schema:

```bash
calm validate -a connection-solver.architecture.json
```

**Result**: ✅ No errors, no warnings

## Viewing the Architecture

You can visualize and explore this architecture using:

1. **CALM Viewer** - Visual exploration of nodes, relationships, and flows
2. **Generated Documentation** - See `docs/calm/html/` for Docusaurus-based documentation
3. **JSON Analysis** - Direct inspection of the architecture JSON file

## Architecture Characteristics

- **Technology Stack**: React, TypeScript, FastAPI, Python 3.11+, LangChain
- **Deployment Model**: Full-stack web application with local development servers
- **LLM Integration**: Multi-provider support (OpenAI, Ollama, Simple fallback)
- **API Versioning**: v1 and v2 API endpoints for backward compatibility
- **Session Management**: In-memory session management in backend
- **Image Processing**: Vision API integration for image-based puzzle setup

## Key Design Decisions

1. **Multi-Provider LLM Support**: Architecture supports multiple LLM providers with runtime selection
2. **API Versioning**: Maintains v1 (legacy) and v2 (enhanced) endpoints
3. **Local + Cloud**: Supports both local (Ollama) and cloud (OpenAI) LLM services
4. **RESTful Design**: All communication via HTTP/HTTPS REST APIs
5. **Image Support**: Vision API capabilities for image-based puzzle extraction
6. **Stateful Sessions**: Backend maintains game state with session IDs

## Business Processes

The architecture captures 6 complete user journeys:
1. Puzzle initialization from CSV
2. AI recommendation generation
3. Local LLM processing
4. Response recording and validation
5. Provider configuration
6. Image-based puzzle setup

Each process is mapped to specific API endpoints and shows the complete request/response flow through the system.
