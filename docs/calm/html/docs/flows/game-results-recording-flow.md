---
id: game-results-recording-flow
title: Game Results Recording Process
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | game-results-recording-flow                   |
| **Name**            | Game Results Recording Process                 |
| **Description**     | System persists completed game session data to database for historical tracking and analysis          |
</div>

## Sequence Diagram
```mermaid
sequenceDiagram
            Puzzle Player ->> Connection Solver Web Application: Player completes a puzzle session (win/loss)
            Connection Solver Web Application ->> Connection Solver Backend API: Frontend sends game results with puzzle details, recommendations, and outcomes
            Connection Solver Backend API ->> Game Results SQLite Database: Backend writes game session data to SQLite database
            Game Results SQLite Database -->> Connection Solver Backend API: Database confirms successful write operation
            Connection Solver Backend API -->> Connection Solver Web Application: Backend returns confirmation to frontend
            Connection Solver Web Application -->> Puzzle Player: Frontend displays confirmation message
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
                  Game Results Persistence
                      </td>
          </tr>
          <tr>
              <td>
                  <b>User Journey Step</b>
              </td>
              <td>
                  4-Complete-Game
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Api Endpoint</b>
              </td>
              <td>
                  POST /api/v2/game_results
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Database Table</b>
              </td>
              <td>
                  game_results
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Stored Data</b>
              </td>
              <td>
                  session_id, puzzle_date, words, recommendations, responses, final_status, timestamps
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
