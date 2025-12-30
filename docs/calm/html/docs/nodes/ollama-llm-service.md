---
id: ollama-llm-service
title: Ollama LLM Service
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | ollama-llm-service                   |
| **Node Type**       | service             |
| **Name**            | Ollama LLM Service                 |
| **Description**     | Local Ollama service providing open-source large language models running on the same system as the backend          |

</div>

## Interfaces
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
                        <b>UniqueId</b>
                    </td>
                    <td>
                        ollama-api-interface
                            </td>
                </tr>
                <tr>
                    <td>
                        <b>AdditionalProperties</b>
                    </td>
                    <td>
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
                                        <b>Hostname</b>
                                    </td>
                                    <td>
                                        localhost
                                            </td>
                                </tr>
                                <tr>
                                    <td>
                                        <b>Port</b>
                                    </td>
                                    <td>
                                        11434
                                            </td>
                                </tr>
                                <tr>
                                    <td>
                                        <b>Protocol</b>
                                    </td>
                                    <td>
                                        HTTP
                                            </td>
                                </tr>
                                </tbody>
                            </table>
                        </div>
                    </td>
                </tr>
                </tbody>
            </table>
        </div>


## Related Nodes
```mermaid
graph TD;
ollama-llm-service[ollama-llm-service]:::highlight;
backend-api-service -- Connects --> ollama-llm-service;
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
                  <b>Authentication</b>
              </td>
              <td>
                  None - local service
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Default Model</b>
              </td>
              <td>
                  qwen2.5:32b
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Supported Models</b>
              </td>
              <td>
                  qwen2.5:32b, llama2, llava (for vision), bakllava
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Deployment</b>
              </td>
              <td>
                  Local service on same host as backend
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Performance</b>
              </td>
              <td>
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
                                  <b>Typical Response Time</b>
                              </td>
                              <td>
                                  10-60 seconds (hardware dependent)
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Timeout</b>
                              </td>
                              <td>
                                  300 seconds (configurable)
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Hardware Requirements</b>
                              </td>
                              <td>
                                  Varies by model (GPU recommended for faster inference)
                                      </td>
                          </tr>
                          </tbody>
                      </table>
                  </div>
              </td>
          </tr>
          <tr>
              <td>
                  <b>Error Handling</b>
              </td>
              <td>
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
                                  <b>Connection Failed</b>
                              </td>
                              <td>
                                  Returns connection error, mapped to HTTP 503 by backend
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Model Not Found</b>
                              </td>
                              <td>
                                  Returns model error, mapped to HTTP 503 by backend
                                      </td>
                          </tr>
                          </tbody>
                      </table>
                  </div>
              </td>
          </tr>
          <tr>
              <td>
                  <b>Service Ownership</b>
              </td>
              <td>
                  Local deployment
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
