---
id: backend-api-service
title: Connection Solver Backend API
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | backend-api-service                   |
| **Node Type**       | service             |
| **Name**            | Connection Solver Backend API                 |
| **Description**     | FastAPI-based REST API service that orchestrates puzzle solving, manages game sessions, integrates with LLM providers for generating recommendations, and persists game results to SQLite database          |

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
                        backend-rest-api
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
                                        8000
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
                                <tr>
                                    <td>
                                        <b>Cors Origins</b>
                                    </td>
                                    <td>
                                        http://localhost:3000, http://127.0.0.1:3000
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
                        health-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/health
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
                        root-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/
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
                        puzzle-setup-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/puzzle/setup_puzzle
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
                        next-recommendation-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/puzzle/next_recommendation
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
                        record-response-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/puzzle/record_response
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
                        v2-recommendations-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/v2/recommendations
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
                        v2-recommendations-health-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/v2/recommendations/health
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
                        v2-recommendations-providers-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/v2/recommendations/providers
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
                        v2-providers-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/v2/providers
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
                        v2-provider-validate-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/v2/providers/validate
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
                        v2-provider-status-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/v2/providers/status
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
                        v2-image-setup-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/v2/setup_puzzle_from_image
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
                        v2-game-results-post-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/v2/game_results
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
                        v2-game-results-get-endpoint
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
                                        <b>Url</b>
                                    </td>
                                    <td>
                                        http://localhost:8000/api/v2/game_results
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
backend-api-service[backend-api-service]:::highlight;
frontend-webclient -- Connects --> backend-api-service;
backend-api-service -- Connects --> openai-llm-service;
backend-api-service -- Connects --> ollama-llm-service;
backend-api-service -- Connects --> game-results-database;
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
                  None - API keys for LLM providers configured via environment variables only
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Environment Variables</b>
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
                                  <b>OPENAI_API_KEY</b>
                              </td>
                              <td>
                                  Required for OpenAI provider (format: sk-*)
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>OPENAI_MODEL_NAME</b>
                              </td>
                              <td>
                                  Optional, default: gpt-4o-mini
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>OPENAI_TIMEOUT</b>
                              </td>
                              <td>
                                  Optional, default: 300s
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>OLLAMA_BASE_URL</b>
                              </td>
                              <td>
                                  Optional, default: http://localhost:11434
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>BACKEND_CORS_ORIGINS</b>
                              </td>
                              <td>
                                  Optional, comma-separated origins
                                      </td>
                          </tr>
                          </tbody>
                      </table>
                  </div>
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
                                  <b>Non Llm Api Response</b>
                              </td>
                              <td>
                                  &lt; 100ms
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Simple Provider</b>
                              </td>
                              <td>
                                  &lt; 100ms
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Database Insert</b>
                              </td>
                              <td>
                                  &lt; 10ms
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Database Query</b>
                              </td>
                              <td>
                                  &lt; 50ms
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
                                  <b>Validation Errors</b>
                              </td>
                              <td>
                                  HTTP 400 with error details
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Llm Provider Errors</b>
                              </td>
                              <td>
                                  HTTP 503 with provider-specific error code
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Timeout Errors</b>
                              </td>
                              <td>
                                  HTTP 504
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Configuration Errors</b>
                              </td>
                              <td>
                                  HTTP 500
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Retry Policy</b>
                              </td>
                              <td>
                                  No automatic retry - error returned to client
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Fallback Policy</b>
                              </td>
                              <td>
                                  No automatic fallback between providers
                                      </td>
                          </tr>
                          </tbody>
                      </table>
                  </div>
              </td>
          </tr>
          <tr>
              <td>
                  <b>Llm Providers</b>
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
                                  <b>Supported Types</b>
                              </td>
                              <td>
                                  <ul>
                                      <li>simple</li>
                                      <li>openai</li>
                                      <li>ollama</li>
                                  </ul>
                              </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Provider Architecture</b>
                              </td>
                              <td>
                                  Factory pattern with BaseLLMProvider abstract base class
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Provider Factory</b>
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
                                                  <b>Class</b>
                                              </td>
                                              <td>
                                                  LLMProviderFactory
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Location</b>
                                              </td>
                                              <td>
                                                  backend/src/services/llm_provider_factory.py
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Responsibilities</b>
                                              </td>
                                              <td>
                                                  Provider instantiation, configuration management, validation
                                                      </td>
                                          </tr>
                                          </tbody>
                                      </table>
                                  </div>
                              </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Simple</b>
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
                                                  <b>Type</b>
                                              </td>
                                              <td>
                                                  internal
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Class</b>
                                              </td>
                                              <td>
                                                  SimpleLLMProvider
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Description</b>
                                              </td>
                                              <td>
                                                  Built-in rule-based provider using LangChain FakeListLLM with predefined word groups for testing and development
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Implementation</b>
                                              </td>
                                              <td>
                                                  backend/src/services/llm_provider_factory.py
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Requires External Service</b>
                                              </td>
                                              <td>
                                                  false
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Requires Api Key</b>
                                              </td>
                                              <td>
                                                  false
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Requires Configuration</b>
                                              </td>
                                              <td>
                                                  false
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Configuration Keys</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Use Cases</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>Testing and development</li>
                                                      <li>Baseline recommendations without external dependencies</li>
                                                      <li>Quick validation without API costs</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Response Time</b>
                                              </td>
                                              <td>
                                                  &lt; 100ms (in-process, synchronous)
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Capabilities</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>basic_recommendations</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Limitations</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>No AI intelligence - returns hardcoded patterns</li>
                                                      <li>No connection explanations</li>
                                                      <li>Limited to 4 predefined word groups</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Predefined Responses</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>BASS, FLOUNDER, SALMON, TROUT</li>
                                                      <li>PIANO, GUITAR, VIOLIN, DRUMS</li>
                                                      <li>RED, BLUE, GREEN, YELLOW</li>
                                                      <li>APPLE, BANANA, ORANGE, GRAPE</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Error Handling</b>
                                              </td>
                                              <td>
                                                  Returns SimpleProviderError for internal failures
                                                      </td>
                                          </tr>
                                          </tbody>
                                      </table>
                                  </div>
                              </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Openai</b>
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
                                                  <b>Type</b>
                                              </td>
                                              <td>
                                                  external
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Class</b>
                                              </td>
                                              <td>
                                                  OpenAILLMProvider
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Description</b>
                                              </td>
                                              <td>
                                                  Integration with OpenAI API service for production-quality AI-powered recommendations
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Implementation</b>
                                              </td>
                                              <td>
                                                  backend/src/services/llm_provider_factory.py
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Requires External Service</b>
                                              </td>
                                              <td>
                                                  true
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Requires Api Key</b>
                                              </td>
                                              <td>
                                                  true
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Requires Configuration</b>
                                              </td>
                                              <td>
                                                  true
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Configuration Keys</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>OPENAI_API_KEY</li>
                                                      <li>OPENAI_MODEL_NAME</li>
                                                      <li>OPENAI_TIMEOUT</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>External Service Node</b>
                                              </td>
                                              <td>
                                                  openai-llm-service
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Use Cases</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>Production AI recommendations</li>
                                                      <li>High-quality puzzle solving with explanations</li>
                                                      <li>Vision API for image-based puzzle setup</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Response Time</b>
                                              </td>
                                              <td>
                                                  2-5 seconds (network dependent)
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Capabilities</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>ai_recommendations</li>
                                                      <li>connection_explanations</li>
                                                      <li>vision_api</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Error Handling</b>
                                              </td>
                                              <td>
                                                  Returns OpenAIAPIError, maps HTTP 401/429/503 to HTTP 503
                                                      </td>
                                          </tr>
                                          </tbody>
                                      </table>
                                  </div>
                              </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Ollama</b>
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
                                                  <b>Type</b>
                                              </td>
                                              <td>
                                                  local-service
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Class</b>
                                              </td>
                                              <td>
                                                  OllamaLLMProvider
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Description</b>
                                              </td>
                                              <td>
                                                  Integration with local Ollama service for privacy-focused, on-premise AI recommendations
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Implementation</b>
                                              </td>
                                              <td>
                                                  backend/src/services/llm_provider_factory.py
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Requires External Service</b>
                                              </td>
                                              <td>
                                                  true
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Requires Api Key</b>
                                              </td>
                                              <td>
                                                  false
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Requires Configuration</b>
                                              </td>
                                              <td>
                                                  false
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Configuration Keys</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>OLLAMA_BASE_URL</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>External Service Node</b>
                                              </td>
                                              <td>
                                                  ollama-llm-service
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Use Cases</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>Privacy-focused AI recommendations</li>
                                                      <li>No external API costs</li>
                                                      <li>Local deployment scenarios</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Response Time</b>
                                              </td>
                                              <td>
                                                  10-60 seconds (hardware dependent)
                                                      </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Capabilities</b>
                                              </td>
                                              <td>
                                                  <ul>
                                                      <li>ai_recommendations</li>
                                                      <li>connection_explanations</li>
                                                      <li>vision_models</li>
                                                  </ul>
                                              </td>
                                          </tr>
                                          <tr>
                                              <td>
                                                  <b>Error Handling</b>
                                              </td>
                                              <td>
                                                  Returns OllamaConnectionError for connectivity issues
                                                      </td>
                                          </tr>
                                          </tbody>
                                      </table>
                                  </div>
                              </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Selection Mechanism</b>
                              </td>
                              <td>
                                  User selects provider via frontend dropdown, passed in LLMProvider model with API requests
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Validation</b>
                              </td>
                              <td>
                                  Provider configuration validated via POST /api/v2/providers/validate endpoint
                                      </td>
                          </tr>
                          <tr>
                              <td>
                                  <b>Response Normalization</b>
                              </td>
                              <td>
                                  All providers return LLMRecommendationResponse with consistent structure
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
                  Unknown
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
