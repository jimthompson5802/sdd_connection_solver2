---
id: image-puzzle-setup-flow
title: Image-Based Puzzle Setup Process
---

## Details
<div className="table-container">
| Field               | Value                    |
|---------------------|--------------------------|
| **Unique ID**       | image-puzzle-setup-flow                   |
| **Name**            | Image-Based Puzzle Setup Process                 |
| **Description**     | User uploads an image of a puzzle grid and LLM vision capabilities extract the 16 words          |
</div>

## Sequence Diagram
```mermaid
sequenceDiagram
            Puzzle Player ->> Connection Solver Web Application: Player uploads puzzle image through web interface
            Connection Solver Web Application ->> Connection Solver Backend API: Frontend sends base64-encoded image to backend
            Connection Solver Backend API ->> OpenAI LLM Service: Backend invokes OpenAI Vision API to extract words from image
            OpenAI LLM Service -->> Connection Solver Backend API: OpenAI Vision returns extracted 16 words
            Connection Solver Backend API -->> Connection Solver Web Application: Backend creates session and returns word list to frontend
            Connection Solver Web Application -->> Puzzle Player: Frontend displays extracted words and initializes puzzle interface
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
                  Image-Based Setup
                      </td>
          </tr>
          <tr>
              <td>
                  <b>User Journey Step</b>
              </td>
              <td>
                  1-Setup-Alternative
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Api Endpoint</b>
              </td>
              <td>
                  POST /api/v2/setup_puzzle_from_image
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Llm Capability</b>
              </td>
              <td>
                  Vision API
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Image Format</b>
              </td>
              <td>
                  base64-encoded, JPEG/PNG
                      </td>
          </tr>
          <tr>
              <td>
                  <b>Success Criteria</b>
              </td>
              <td>
                  16 words extracted from 4x4 grid
                      </td>
          </tr>
          </tbody>
      </table>
  </div>
