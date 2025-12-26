---
id: game-history-retrieval-flow
title: Game History Retrieval Process
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | game-history-retrieval-flow                   |
| **Name**            | Game History Retrieval Process                 |
| **Description**     | User requests and views historical game results with optional CSV export functionality          |
</div>

## Sequence Diagram
```mermaid
sequenceDiagram
            Puzzle Player ->> Connection Solver Web Application: Player navigates to game history view
            Connection Solver Web Application ->> Connection Solver Backend API: Frontend requests game history data
            Connection Solver Backend API ->> Game Results SQLite Database: Backend queries SQLite database for game results
            Game Results SQLite Database -->> Connection Solver Backend API: Database returns game history records
            Connection Solver Backend API -->> Connection Solver Web Application: Backend returns formatted game history to frontend
            Connection Solver Web Application -->> Puzzle Player: Frontend displays game history with statistics and details
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
                  Game History Analysis
                      </td>
          </tr>
          <tr>
              <td>
                  <b>User Journey Step</b>
              </td>
              <td>
                  5-Review-History
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Api Endpoint</b>
              </td>
              <td>
                  GET /api/v2/game_results
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Export Format</b>
              </td>
              <td>
                  JSON, CSV (via ?format&#x3D;csv query parameter)
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Display Features</b>
              </td>
              <td>
                  Pagination, filtering, sorting, CSV download
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
