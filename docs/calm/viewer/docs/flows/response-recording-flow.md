---
id: response-recording-flow
title: User Response Recording Process
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | response-recording-flow                   |
| **Name**            | User Response Recording Process                 |
| **Description**     | User provides feedback on recommendation correctness and system updates game state          |
</div>

## Sequence Diagram
```mermaid
sequenceDiagram
            Puzzle Player ->> Connection Solver Web Application: Player indicates if recommendation was correct, incorrect, or one-away
            Connection Solver Web Application ->> Connection Solver Backend API: Frontend sends response recording request with result type
            Connection Solver Backend API -->> Connection Solver Web Application: Backend updates session state and returns updated game status
            Connection Solver Web Application -->> Puzzle Player: Frontend displays updated puzzle state with remaining words and mistake count
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
                  Response Recording
                      </td>
          </tr>
          <tr>
              <td>
                  <b>User Journey Step</b>
              </td>
              <td>
                  3-Record-Response
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Api Endpoint</b>
              </td>
              <td>
                  POST /api/puzzle/record_response
                      </td>
          </tr>
          <tr>
              <td>
                  <b>State Updates</b>
              </td>
              <td>
                  remaining_words, mistake_count, game_status
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Game Rules</b>
              </td>
              <td>
                  Max 4 mistakes allowed
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
