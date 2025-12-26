---
id: ollama-recommendation-flow
title: Local LLM Recommendation Process
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | ollama-recommendation-flow                   |
| **Name**            | Local LLM Recommendation Process                 |
| **Description**     | User requests recommendations using local Ollama LLM service          |
</div>

## Sequence Diagram
```mermaid
sequenceDiagram
            Puzzle Player ->> Connection Solver Web Application: Player selects Ollama provider and requests recommendation
            Connection Solver Web Application ->> Connection Solver Backend API: Frontend sends recommendation request with Ollama provider
            Connection Solver Backend API ->> Ollama LLM Service: Backend calls local Ollama service for recommendation
            Ollama LLM Service -->> Connection Solver Backend API: Ollama returns recommendation response
            Connection Solver Backend API -->> Connection Solver Web Application: Backend processes and returns recommendation to frontend
            Connection Solver Web Application -->> Puzzle Player: Frontend displays Ollama recommendation to player
```
## Controls
    _No controls defined._

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
                  <b>Business Process</b>
              </td>
              <td>
                  Local LLM Recommendation
                      </td>
          </tr>
          <tr>
              <td>
                  <b>User Journey Step</b>
              </td>
              <td>
                  2-Get-Recommendation
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Api Endpoint</b>
              </td>
              <td>
                  POST /api/v2/recommendations
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Llm Provider</b>
              </td>
              <td>
                  Ollama
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Deployment</b>
              </td>
              <td>
                  Local service on same host
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
