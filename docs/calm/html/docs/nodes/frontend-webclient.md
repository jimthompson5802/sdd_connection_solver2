---
id: frontend-webclient
title: Connection Solver Web Application
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | frontend-webclient                   |
| **Node Type**       | webclient             |
| **Name**            | Connection Solver Web Application                 |
| **Description**     | React-based web application providing the user interface for solving NYT Connections puzzles with LLM assistance          |

</div>

## Interfaces
    _No interfaces defined._


## Related Nodes
```mermaid
graph TD;
frontend-webclient[frontend-webclient]:::highlight;
player -- Interacts --> frontend-webclient;
frontend-webclient -- Connects --> backend-api-service;
classDef highlight fill:#f2bbae;

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
                  <b>Technology</b>
              </td>
              <td>
                  React
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Language</b>
              </td>
              <td>
                  TypeScript
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Build Tool</b>
              </td>
              <td>
                  Create React App
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Testing</b>
              </td>
              <td>
                  Jest, React Testing Library
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
