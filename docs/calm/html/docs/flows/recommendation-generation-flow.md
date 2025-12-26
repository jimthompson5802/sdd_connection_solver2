---
id: recommendation-generation-flow
title: AI Recommendation Generation Process
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | recommendation-generation-flow                   |
| **Name**            | AI Recommendation Generation Process                 |
| **Description**     | User requests AI-powered word grouping recommendations from selected LLM provider          |
</div>

## Sequence Diagram
```mermaid
sequenceDiagram
            Puzzle Player ->> Connection Solver Web Application: Player clicks button to request recommendation
            Connection Solver Web Application ->> Connection Solver Backend API: Frontend requests recommendation from backend with LLM provider selection
            Connection Solver Backend API ->> OpenAI LLM Service: Backend invokes OpenAI API for recommendation (if OpenAI provider selected)
            OpenAI LLM Service -->> Connection Solver Backend API: OpenAI returns recommendation with 4 words and explanation
            Connection Solver Backend API -->> Connection Solver Web Application: Backend returns formatted recommendation to frontend
            Connection Solver Web Application -->> Puzzle Player: Frontend displays recommended words and explanation to player
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
                  Recommendation Generation
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
                  <b>Api Endpoints</b>
              </td>
              <td>
                  GET /api/puzzle/next_recommendation, POST /api/v2/recommendations
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Llm Providers</b>
              </td>
              <td>
                  OpenAI, Ollama, Simple
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Success Criteria</b>
              </td>
              <td>
                  4 words returned with connection explanation
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
