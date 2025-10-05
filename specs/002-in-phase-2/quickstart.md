# Quickstart: LLM Provider Integration

## Overview
This quickstart validates the LLM Provider Integration feature by walking through the complete user journey from provider selection to AI-powered recommendations.

## Prerequisites

### Environment Setup
1. **Backend Dependencies**
   ```bash
   cd backend
   uv add langchain openai ollama-python python-dotenv
   ```

2. **Environment Configuration**
   Create `.env` file in project root:
   ```env
   # OpenAI Configuration (optional)
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1
   
   # Ollama Configuration (optional)
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama2
   
   # Development Settings
   DEBUG=true
   LOG_LEVEL=info
   ```

3. **Ollama Setup** (for local LLM testing)
   ```bash
   # Install ollama (macOS)
   brew install ollama
   
   # Start ollama service
   ollama serve
   
   # Pull a model (in separate terminal)
   ollama pull llama2
   ```

### Verification Steps
4. **Verify Provider Availability**
   ```bash
   # Test ollama connection
   curl http://localhost:11434/api/tags
   
   # Should return list of available models
   ```

## User Journey Validation

### Journey 1: Simple Provider (Baseline)
**Objective**: Verify Phase 1 compatibility and default behavior

1. **Start Application**
   ```bash
   # Terminal 1: Backend
   cd backend
   uv run uvicorn src.main:app --reload
   
   # Terminal 2: Frontend  
   cd frontend
   npm run dev
   ```

2. **Load Puzzle**
   - Open browser to `http://localhost:3000`
   - Upload puzzle file with 16 words
   - Verify puzzle displays correctly

3. **Default Provider Test**
   - Confirm "LLM Provider" field shows "simple" as default
   - Click "Next Recommendation" button
   - **Expected**: Returns first 4 words from remaining list
   - **Expected**: No loading delay, immediate response
   - **Expected**: No connection explanation shown

4. **Session Reset Test**
   - Refresh page
   - Upload same puzzle
   - **Expected**: LLM Provider field resets to "simple"

### Journey 2: Ollama Integration
**Objective**: Validate local LLM provider integration

1. **Provider Selection**
   - In LLM Provider field, enter: `ollama:llama2`
   - **Expected**: Field accepts input without error

2. **First Recommendation**
   - Click "Next Recommendation" button
   - **Expected**: Loading indicator appears and persists
   - **Expected**: Eventually returns 4 words with explanation
   - **Expected**: Explanation mentions specific connection (e.g., "These are all fish")

3. **Context-Aware Recommendation**
   - Make an incorrect guess with the recommended words
   - Enter `ollama:llama2` again in provider field
   - Click "Next Recommendation"
   - **Expected**: New recommendation excludes previous guess
   - **Expected**: Response considers previous attempt in context

4. **Error Handling Test**
   - Stop ollama service: `pkill ollama`
   - Try to get recommendation
   - **Expected**: Clear error message about provider unavailability
   - Restart ollama service: `ollama serve`

### Journey 3: OpenAI Integration (if configured)
**Objective**: Validate cloud LLM provider integration

1. **Provider Configuration Test**
   - Enter: `openai:gpt-3.5-turbo` in provider field
   - Click "Next Recommendation"
   - **Expected**: If API key configured, returns recommendation with explanation
   - **Expected**: If no API key, clear error about configuration

2. **Quality Comparison**
   - Compare recommendations between simple, ollama, and openai
   - **Expected**: AI providers give explanations, simple does not
   - **Expected**: AI recommendations show reasoning for connections

### Journey 4: Error Scenarios
**Objective**: Validate error handling and user feedback

1. **Invalid Provider Format**
   - Enter: `invalid_provider` in field
   - Click recommendation button  
   - **Expected**: Clear error message with format examples

2. **Invalid Model Format**
   - Enter: `ollama:nonexistent_model`
   - Click recommendation button
   - **Expected**: Provider-specific error message

3. **Insufficient Words**
   - Play puzzle until fewer than 4 words remain
   - Try to get recommendation
   - **Expected**: Appropriate error message about insufficient words

4. **LLM Response Validation**
   - (This requires implementation with deliberate bad response simulation)
   - **Expected**: When LLM returns invalid words, user sees "try again" message

### Journey 5: Complete Game Flow
**Objective**: Validate end-to-end puzzle solving with LLM assistance

1. **Mixed Provider Usage**
   - Start with `simple` provider for first recommendation
   - Switch to `ollama:llama2` for second recommendation
   - Alternate between providers throughout game

2. **Recommendation Quality Assessment**
   - **Expected**: AI recommendations should be contextually relevant
   - **Expected**: AI should avoid repeating previous failed guesses
   - **Expected**: Explanations should be specific, not generic

3. **Game Completion**
   - Complete entire puzzle using mix of provider recommendations
   - **Expected**: All provider types work seamlessly
   - **Expected**: No provider state persistence between sessions

## Acceptance Criteria Verification

### Functional Requirements Checklist
- [ ] **FR-001**: LLM Provider text field appears above file chooser
- [ ] **FR-001a**: Provider selection resets to default each session
- [ ] **FR-001b**: Default value is "simple" on first visit
- [ ] **FR-002**: "simple" provider uses Phase 1 algorithm
- [ ] **FR-003**: Accepts "provider:model" format for ollama/openai
- [ ] **FR-003a**: Credentials obtained from environment variables only
- [ ] **FR-004**: Routes to appropriate provider based on selection
- [ ] **FR-005**: LLM prompts include puzzle context and history
- [ ] **FR-006**: LLM prompts request specific connections
- [ ] **FR-007**: Validates LLM responses contain exactly 4 valid words
- [ ] **FR-007a**: Shows error message for invalid LLM responses
- [ ] **FR-008**: Excludes previously guessed words from recommendations
- [ ] **FR-009**: Handles provider errors with user-friendly messages
- [ ] **FR-009a**: Shows persistent loading indicator without timeout
- [ ] **FR-010**: Maintains backward compatibility with Phase 1

### Technical Validation
- [ ] **API Contracts**: All endpoints respond according to OpenAPI spec
- [ ] **Error Handling**: All error responses include required fields
- [ ] **Type Safety**: All requests/responses validated by Pydantic
- [ ] **Environment Config**: Credentials loaded from .env file only
- [ ] **Session Management**: No persistent storage, session-only state

### Performance Validation
- [ ] **Loading States**: UI remains responsive during LLM requests
- [ ] **Error Recovery**: App remains functional after provider errors
- [ ] **Memory Usage**: No memory leaks during extended usage
- [ ] **Provider Switching**: Seamless transitions between providers

## Troubleshooting

### Common Issues
1. **Ollama Connection Failed**
   - Verify ollama service running: `ps aux | grep ollama`
   - Check ollama API: `curl http://localhost:11434/api/tags`
   - Restart service: `ollama serve`

2. **OpenAI Authentication Failed**
   - Verify API key in `.env` file
   - Check key format (starts with `sk-`)
   - Verify account has API credits

3. **LLM Provider Field Not Visible**
   - Clear browser cache
   - Verify frontend rebuild completed
   - Check browser console for JavaScript errors

4. **Recommendations Take Too Long**
   - Check provider-specific logs
   - Verify network connectivity
   - Consider using faster models for testing

### Debug Commands
```bash
# Check backend logs
cd backend && uv run uvicorn src.main:app --reload --log-level debug

# Test API directly
curl -X POST http://localhost:8000/api/v2/providers/validate \
  -H "Content-Type: application/json" \
  -d '{"provider_type": "ollama", "model_name": "llama2"}'

# Check environment variables
env | grep -E "(OPENAI|OLLAMA)"
```

## Success Criteria
✅ **Complete**: All functional requirements pass  
✅ **Complete**: Error scenarios handled gracefully  
✅ **Complete**: Performance meets expectations  
✅ **Complete**: User experience is intuitive  
✅ **Complete**: Backward compatibility maintained