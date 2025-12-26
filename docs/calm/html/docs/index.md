---
id: index
title: Welcome to CALM Documentation
sidebar_position: 1
slug: /
---

# Welcome to CALM Documentation

This documentation is generated from the **CALM Architecture-as-Code** model.

## High Level Architecture
```mermaid
C4Deployment

    Deployment_Node(deployment, "Architecture", ""){
        Person(player, "Puzzle Player", "End user who interacts with the web application to solve NYT Connections puzzles with AI assistance")
        Container(frontend-webclient, "Connection Solver Web Application", "", "React-based web application providing the user interface for solving NYT Connections puzzles with LLM assistance")
        Container(backend-api-service, "Connection Solver Backend API", "", "FastAPI-based REST API service that orchestrates puzzle solving, manages game sessions, integrates with LLM providers for generating recommendations, and persists game results to SQLite database")
        Container(openai-llm-service, "OpenAI LLM Service", "", "External OpenAI API service providing large language model capabilities for generating puzzle-solving recommendations")
        Container(ollama-llm-service, "Ollama LLM Service", "", "Local Ollama service providing open-source large language models running on the same system as the backend")
        Container(game-results-database, "Game Results SQLite Database", "", "SQLite database that persists completed game sessions, including puzzle details, recommendations, player responses, and final outcomes for historical analysis")
    }

    Rel(player,frontend-webclient,"Interacts With")
    Rel(frontend-webclient,backend-api-service,"Connects To")
    Rel(backend-api-service,openai-llm-service,"Connects To")
    Rel(backend-api-service,ollama-llm-service,"Connects To")
    Rel(backend-api-service,game-results-database,"Connects To")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
```
## Nodes
    - [Puzzle Player](nodes/player)
    - [Connection Solver Web Application](nodes/frontend-webclient)
    - [Connection Solver Backend API](nodes/backend-api-service)
    - [OpenAI LLM Service](nodes/openai-llm-service)
    - [Ollama LLM Service](nodes/ollama-llm-service)
    - [Game Results SQLite Database](nodes/game-results-database)

## Relationships
    - [Player Interaction](relationships/player-interaction)
    - [Frontend To Backend Connection](relationships/frontend-to-backend-connection)
    - [Backend To Openai Connection](relationships/backend-to-openai-connection)
    - [Backend To Ollama Connection](relationships/backend-to-ollama-connection)
    - [Backend To Database Connection](relationships/backend-to-database-connection)


## Flows
    - [Puzzle Setup Process](flows/puzzle-setup-flow)
    - [AI Recommendation Generation Process](flows/recommendation-generation-flow)
    - [Local LLM Recommendation Process](flows/ollama-recommendation-flow)
    - [User Response Recording Process](flows/response-recording-flow)
    - [LLM Provider Validation Process](flows/provider-validation-flow)
    - [Image-Based Puzzle Setup Process](flows/image-puzzle-setup-flow)
    - [Game Results Recording Process](flows/game-results-recording-flow)
    - [Game History Retrieval Process](flows/game-history-retrieval-flow)

## Controls
  _No Controls defined._

## Metadata
  <div className="table-container">
      <table>
          <thead>
          <tr>
              <th>Key</th>
              <th>Value</th>
          </tr>
          </thead>
          <tbody>
          <tr>
              <td>
                  <b>Version</b>
              </td>
              <td>
                  2.0.0
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Created By</b>
              </td>
              <td>
                  Architecture Team
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Created Date</b>
              </td>
              <td>
                  2025-12-18
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Updated Date</b>
              </td>
              <td>
                  2025-12-25
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Environment</b>
              </td>
              <td>
                  production
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Tech Stack</b>
              </td>
              <td>
                  React, TypeScript, FastAPI, Python 3.11+, LangChain, SQLite
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Deployment Model</b>
              </td>
              <td>
                  Full-stack web application with frontend and backend services
                      </td>
          </tr>
          </tbody>
      </table>
  </div>

## Adrs
  _No Adrs defined._
