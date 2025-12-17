---
id: openai-llm-service
title: OpenAI LLM Service
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | openai-llm-service                   |
| **Node Type**       | service             |
| **Name**            | OpenAI LLM Service                 |
| **Description**     | External OpenAI API service providing large language model capabilities for generating puzzle-solving recommendations          |

</div>

## Interfaces
    _No interfaces defined._


## Related Nodes
```mermaid
graph TD;
openai-llm-service[openai-llm-service]:::highlight;
backend-api-service -- Connects --> openai-llm-service;
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
                  <b>Provider</b>
              </td>
              <td>
                  OpenAI
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Deployment</b>
              </td>
              <td>
                  external
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Api Type</b>
              </td>
              <td>
                  REST API
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Authentication</b>
              </td>
              <td>
                  API Key
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
