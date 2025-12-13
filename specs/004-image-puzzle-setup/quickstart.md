# Quickstart Guide: Image-Based Puzzle Setup

**Feature**: 004-image-puzzle-setup | **Date**: December 13, 2025

## Overview

This guide helps developers set up, test, and troubleshoot the image-based puzzle setup feature. It covers:
- Development environment setup
- LLM vision model configuration
- Testing workflows (TDD approach)
- Common issues and solutions

## Prerequisites

### System Requirements
- **Backend**: Python 3.11+
- **Frontend**: Node.js 18+, npm 9+
- **Browser**: Chrome 66+, Firefox 63+, Safari 13.1+ (for Clipboard API)
- **Git Branch**: `004-image-puzzle-setup`

### Existing Setup
Ensure the base application is working:

```bash
# From repository root
cd /Users/jim/Desktop/genai/sdd_connection_solver2

# Verify backend runs
cd backend
source .venv/bin/activate
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Verify frontend runs (in new terminal)
cd frontend
npm start
```

If base application doesn't work, see main project README.md first.

---

## Backend Setup

### 1. Install Dependencies

No new Python dependencies required - LangChain vision support is already included.

Verify current dependencies:

```bash
cd backend
source .venv/bin/activate
python -c "from langchain.schema import BaseMessage; print('LangChain OK')"
python -c "from pydantic import BaseModel, Field; print('Pydantic OK')"
```

### 2. Configure LLM Providers

#### OpenAI (Recommended for Development)

**API Key Setup**:
```bash
export OPENAI_API_KEY="sk-proj-..."
```

Add to `.env` file (create if doesn't exist):
```bash
# backend/.env
OPENAI_API_KEY=sk-proj-...
```

**Verify API Key**:
```bash
cd backend
source .venv/bin/activate
python -c "
from openai import OpenAI
client = OpenAI()
print('OpenAI API key valid')
"
```

**Vision Models Available**:
- `gpt-4-vision-preview` (recommended for testing)
- `gpt-4-turbo` (faster, same quality)
- `gpt-4o` (latest, best performance)

**Cost Estimate**: ~$0.01-0.03 per image analysis (4x4 grid)

#### Ollama (Optional, Free Local Inference)

**Installation**:
```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

**Pull Vision Model**:
```bash
# Recommended: LLaVA 7B (fastest)
ollama pull llava

# Alternative: BakLLaVA (better accuracy)
ollama pull bakllava

# Alternative: LLaVA 13B (highest quality, slower)
ollama pull llava:13b
```

**Verify Installation**:
```bash
ollama list  # Should show llava or bakllava

# Test vision capability
curl http://localhost:11434/api/generate -d '{
  "model": "llava",
  "prompt": "What is in this image?",
  "images": ["base64_encoded_image"]
}'
```

**Configuration**:
```bash
# backend/.env (if using remote Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

#### Simple Provider (Not Supported)

The Simple provider does not support vision capabilities. Selecting it will return:
```json
{
  "remaining_words": [],
  "status": "error",
  "message": "Selected model does not support image analysis"
}
```

### 3. Verify LLM Provider Factory

Existing `LLMProviderFactory` should work without changes. Verify:

```bash
cd backend
source .venv/bin/activate
python -c "
from src.services.llm_provider_factory import LLMProviderFactory
from src.models import LLMProvider

# Test OpenAI provider creation
provider_config = LLMProvider(
    provider_type='openai',
    model_name='gpt-4-vision-preview',
    api_key='${OPENAI_API_KEY}'
)
provider = LLMProviderFactory.create_provider(provider_config)
print(f'Provider created: {type(provider.llm).__name__}')
print(f'Has with_structured_output: {hasattr(provider.llm, \"with_structured_output\")}')
"
```

Expected output:
```
Provider created: ChatOpenAI
Has with_structured_output: True
```

---

## Frontend Setup

### 1. Install Dependencies

No new npm packages required - Clipboard API is browser-native.

Verify current dependencies:

```bash
cd frontend
npm install
npm run build  # Should complete without errors
```

### 2. Configure API Endpoint

Ensure frontend points to correct backend URL:

```bash
# frontend/.env
REACT_APP_API_URL=http://127.0.0.1:8000
```

### 3. Verify Clipboard API Support

Test in browser console (Chrome DevTools):

```javascript
// Should return true for modern browsers
console.log('Clipboard API supported:', !!navigator.clipboard);

// Should return ClipboardEvent constructor
console.log('ClipboardEvent supported:', typeof ClipboardEvent !== 'undefined');
```

If Clipboard API not supported, browser may be too old or page not served over HTTPS (localhost is exempt).

---

## Testing Workflow (TDD)

### Backend Tests

#### 1. Contract Tests (Write First)

**Location**: `backend/tests/contract/test_setup_puzzle_from_image.py`

**Run**:
```bash
cd backend
source .venv/bin/activate
pytest tests/contract/test_setup_puzzle_from_image.py -v
```

**Example Test**:
```python
def test_success_response_contract(client, mock_llm_provider):
    """Test successful extraction returns 16 words."""
    response = client.post('/api/v2/setup_puzzle_from_image', json={
        'image_base64': 'fake_base64_data',
        'image_mime': 'image/png',
        'provider_type': 'openai',
        'model_name': 'gpt-4-vision-preview'
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert len(data['remaining_words']) == 16
    assert data.get('message') is None
```

#### 2. Unit Tests (Write After Contract Tests Pass)

**Location**: `backend/tests/unit/test_image_word_extractor.py`

**Run**:
```bash
pytest tests/unit/test_image_word_extractor.py -v
```

**Example Test**:
```python
def test_extract_words_with_openai_vision(mock_llm):
    """Test word extraction using OpenAI GPT-4 Vision."""
    extractor = ImageWordExtractor(provider=mock_llm)
    
    words = extractor.extract_words(
        image_base64='fake_base64',
        image_mime='image/png'
    )
    
    assert len(words) == 16
    assert all(isinstance(w, str) for w in words)
    assert all(w.islower() for w in words)  # Normalized to lowercase
```

#### 3. Integration Tests (Write Last)

**Location**: `backend/tests/integration/test_image_puzzle_flow.py`

**Run**:
```bash
pytest tests/integration/test_image_puzzle_flow.py -v
```

**Example Test**:
```python
def test_full_image_setup_flow(client, real_llm_provider):
    """Test complete flow: image → extraction → session creation."""
    # Load test image
    with open('tests/fixtures/4x4_grid.png', 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # Call API
    response = client.post('/api/v2/setup_puzzle_from_image', json={
        'image_base64': image_data,
        'image_mime': 'image/png',
        'provider_type': 'openai',
        'model_name': 'gpt-4-vision-preview'
    })
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert len(data['remaining_words']) == 16
    
    # Verify session created
    session = session_manager.get_session()
    assert session is not None
    assert len(session.remaining_words) == 16
```

#### Test Coverage

Run all backend tests with coverage:

```bash
cd backend
source .venv/bin/activate
pytest --cov=src --cov-report=html --cov-report=term
```

**Coverage Requirements**: >80% for all new code
- `src/api/v2_image_setup.py`
- `src/services/image_word_extractor.py`
- New Pydantic models in `src/models.py`

View HTML coverage report:
```bash
open htmlcov/index.html
```

### Frontend Tests

#### 1. Component Tests (Write First)

**Location**: `frontend/src/components/ImagePuzzleSetup.test.tsx`

**Run**:
```bash
cd frontend
npm test -- ImagePuzzleSetup.test.tsx
```

**Example Test**:
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ImagePuzzleSetup from './ImagePuzzleSetup';

test('renders with empty placeholder', () => {
  const mockProps = {
    onImageSetup: jest.fn(),
    providers: [{ type: 'openai', displayName: 'OpenAI', models: ['gpt-4-vision-preview'] }],
    defaultProvider: { type: 'openai', displayName: 'OpenAI', models: ['gpt-4-vision-preview'] },
    defaultModel: 'gpt-4-vision-preview',
    onError: jest.fn()
  };
  
  render(<ImagePuzzleSetup {...mockProps} />);
  
  expect(screen.getByText(/Paste image here/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Setup Puzzle/i })).toBeDisabled();
});
```

#### 2. Integration Tests (Write Last)

**Location**: `frontend/tests/integration/test_image_setup_flow.test.tsx`

**Run**:
```bash
npm test -- test_image_setup_flow.test.tsx
```

**Example Test**:
```typescript
test('complete flow: paste → select provider → setup → play', async () => {
  // Mock API
  const mockApi = {
    setupPuzzleFromImage: jest.fn().mockResolvedValue({
      remaining_words: Array(16).fill('word'),
      status: 'success'
    })
  };
  
  // Render component
  const { container } = render(<ImagePuzzleSetup {...mockProps} />);
  
  // Simulate paste
  const pasteEvent = createPasteEvent('image/png', mockImageBlob);
  fireEvent.paste(container, pasteEvent);
  
  // Wait for preview
  await waitFor(() => {
    expect(screen.getByAltText(/Preview/i)).toBeInTheDocument();
  });
  
  // Select provider/model
  fireEvent.change(screen.getByLabelText(/Provider/i), { target: { value: 'openai' } });
  fireEvent.change(screen.getByLabelText(/Model/i), { target: { value: 'gpt-4-vision-preview' } });
  
  // Click setup
  fireEvent.click(screen.getByRole('button', { name: /Setup Puzzle/i }));
  
  // Verify API called
  await waitFor(() => {
    expect(mockApi.setupPuzzleFromImage).toHaveBeenCalledWith(
      expect.any(String),  // base64 data
      'image/png',
      'openai',
      'gpt-4-vision-preview'
    );
  });
});
```

#### Test Coverage

Run all frontend tests with coverage:

```bash
cd frontend
npm test -- --coverage --watchAll=false
```

**Coverage Requirements**: >80% for all new code
- `src/components/ImagePuzzleSetup.tsx`
- New methods in `src/services/api.ts`
- Navigation changes in `src/App.tsx`

View HTML coverage report:
```bash
open coverage/lcov-report/index.html
```

---

## Manual Testing Guide

### 1. Create Test Image

Create a simple 4x4 grid image for testing:

**Option A: Screenshot**
1. Open Google Docs or similar
2. Create table: 4 columns × 4 rows
3. Fill with words:
   ```
   APPLE    BANANA   CHERRY   DATE
   ELDER    FIG      GRAPE    HONEY
   KIWI     LEMON    MANGO    NECTAR
   ORANGE   PAPAYA   QUINCE   RASP
   ```
4. Screenshot the table (CMD+Shift+4 on macOS)
5. Result should be ~100-500KB PNG

**Option B: Use Test Fixture**

```bash
# Copy test fixture from project
cp backend/tests/fixtures/4x4_grid.png ~/Desktop/test_puzzle.png
```

### 2. Test Happy Path

1. **Start Backend**:
   ```bash
   cd backend
   source .venv/bin/activate
   export OPENAI_API_KEY="sk-proj-..."
   uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Navigate to Image Setup**:
   - Open http://localhost:3000
   - Click "From Image" in sidebar
   - Should see "Setup Puzzle from Image" page

4. **Paste Image**:
   - Open test image in Preview/Photos
   - Copy image (CMD+C)
   - Switch to browser
   - Paste (CMD+V) anywhere on page
   - Should see image preview immediately (<2s)

5. **Select Provider/Model**:
   - Provider dropdown should show "OpenAI" (or available providers)
   - Model dropdown should show vision models
   - Select "gpt-4-vision-preview"

6. **Setup Puzzle**:
   - Click "Setup Puzzle" button
   - Should see loading indicator
   - Wait ~3-5 seconds
   - Should transition to puzzle gameplay

7. **Verify Puzzle**:
   - 16 words should appear as buttons
   - Words should match test image (lowercase)
   - Gameplay should work identically to file-based setup

### 3. Test Error Paths

#### Oversized Image

```bash
# Create 6MB image (should fail)
dd if=/dev/zero of=large_image.png bs=1024 count=6144
```

Expected:
- Error message: "Image too large (max 5MB)"
- Image remains in component for retry

#### Wrong Format

```bash
# Create unsupported .bmp file
convert test_puzzle.png test_puzzle.bmp
```

Expected:
- Error message: "Unsupported format: image/bmp. Use PNG, JPEG, or GIF."
- Allow retry with different image

#### Model Without Vision (Simple Provider)

1. Select "Simple" provider from dropdown
2. Click "Setup Puzzle"

Expected:
- Error message: "This model doesn't support image analysis. Try a different model."
- Image preserved, allow model change

#### Wrong Word Count

Create image with 12 words (3×4 grid) or 20 words (5×4 grid).

Expected:
- Error message: "Unable to detect 16 words. Please try a clearer image."
- Allow retry with different image

### 4. Performance Testing

**Paste to Preview**:
- Metric: Time from CMD+V to preview displayed
- Target: <2 seconds
- Test: Use browser DevTools Performance tab

**LLM Extraction**:
- Metric: Time from "Setup Puzzle" click to puzzle display
- Target: <10 seconds (OpenAI), <15 seconds (Ollama)
- Test: Console.time() around API call

**Memory Usage**:
- Check no memory leaks after multiple paste operations
- Use Chrome DevTools Memory profiler
- Should release object URLs after new paste

---

## Troubleshooting

### Issue: "No module named 'langchain'"

**Solution**:
```bash
cd backend
source .venv/bin/activate
pip install -e .
```

### Issue: "OPENAI_API_KEY not found"

**Solution**:
```bash
export OPENAI_API_KEY="sk-proj-..."
# Or add to backend/.env file
echo "OPENAI_API_KEY=sk-proj-..." >> backend/.env
```

### Issue: Clipboard API not working

**Symptoms**:
- Paste event not firing
- `navigator.clipboard` is undefined

**Causes**:
1. Browser too old (upgrade to Chrome 66+, Firefox 63+, Safari 13.1+)
2. Page not served over HTTPS (localhost is exempt)
3. Browser permissions not granted

**Solution**:
```bash
# Check browser console
console.log('Clipboard API:', !!navigator.clipboard);

# Grant permissions (Chrome)
# Settings → Privacy and security → Site settings → Clipboard → Allow
```

### Issue: "LLM provider error - please retry"

**Symptoms**:
- API returns HTTP 500
- Backend logs show LLM timeout or API error

**Causes**:
1. OpenAI API key invalid or quota exceeded
2. Ollama service not running
3. Network connectivity issues

**Solution**:

**For OpenAI**:
```bash
# Verify API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check quota
# Visit https://platform.openai.com/usage
```

**For Ollama**:
```bash
# Check service running
curl http://localhost:11434/api/tags

# Restart service
killall ollama
ollama serve
```

### Issue: "Could not extract 16 words from image"

**Symptoms**:
- API returns HTTP 400
- Words extracted: 12, 14, 15, 17, 18 (not 16)

**Causes**:
1. Image grid is not 4×4 (wrong dimensions)
2. Image quality too low (blurry, small font)
3. Words overlap or unclear boundaries
4. Image contains non-word elements (icons, borders)

**Solution**:
1. **Verify Grid Structure**:
   - Must be exactly 4 columns × 4 rows
   - Clear separation between cells
   - No merged cells or irregular layout

2. **Improve Image Quality**:
   - Use higher resolution screenshot
   - Ensure good contrast (dark text on light background)
   - Avoid compression artifacts (use PNG, not JPEG)

3. **Retry with Different Model**:
   - Try `gpt-4-turbo` instead of `gpt-4-vision-preview`
   - Ollama models may have lower accuracy on complex grids

### Issue: Word Extraction Takes >10 Seconds

**Symptoms**:
- Loading indicator shows for >10 seconds
- Eventually succeeds or times out

**Causes**:
1. Large image size (>2MB)
2. Ollama model running on slow hardware
3. Network latency to OpenAI API

**Solution**:

**For Large Images**:
```bash
# Compress image before paste
convert original.png -resize 1024x1024 -quality 85 compressed.png
```

**For Ollama Performance**:
```bash
# Use smaller model
ollama pull llava:7b  # Faster than llava:13b

# Or switch to OpenAI for speed
```

**For Network Latency**:
```bash
# Test latency
curl -w "@curl-format.txt" -o /dev/null -s https://api.openai.com/v1/models
```

### Issue: Frontend Tests Fail with "Cannot read property 'clipboardData'"

**Symptoms**:
- Jest tests fail when simulating paste event
- Error: `Cannot read property 'clipboardData' of undefined`

**Cause**:
- ClipboardEvent not properly mocked in Jest

**Solution**:
```typescript
// In test file
function createPasteEvent(mimeType: string, blob: Blob): ClipboardEvent {
  const clipboardData = {
    items: [
      {
        type: mimeType,
        getAsFile: () => blob
      }
    ]
  };
  
  return new ClipboardEvent('paste', {
    clipboardData: clipboardData as any
  });
}
```

### Issue: Backend Tests Fail with "AttributeError: 'ChatOpenAI' object has no attribute 'with_structured_output'"

**Symptoms**:
- Unit tests fail when calling `llm.with_structured_output()`
- Error: `AttributeError: 'ChatOpenAI' object has no attribute 'with_structured_output'`

**Cause**:
- Older LangChain version (<0.1.0)

**Solution**:
```bash
cd backend
source .venv/bin/activate
pip install --upgrade langchain langchain-openai
pip show langchain  # Should be >=0.1.0
```

---

## Development Workflow

### Recommended Order

1. **Phase 1: Backend TDD**
   - Write contract tests → red
   - Implement Pydantic models → green
   - Write unit tests → red
   - Implement `ImageWordExtractor` service → green
   - Write integration tests → red
   - Implement endpoint `v2_image_setup.py` → green

2. **Phase 2: Frontend TDD**
   - Write component tests → red
   - Implement `ImagePuzzleSetup` component → green
   - Update navigation (Sidebar, App.tsx) → verify existing tests pass
   - Write integration tests → red
   - Connect component to backend API → green

3. **Phase 3: End-to-End Testing**
   - Manual testing (happy path + error paths)
   - Performance testing (paste timing, LLM extraction timing)
   - Cross-browser testing (Chrome, Firefox, Safari)

4. **Phase 4: Documentation & Polish**
   - Update README with image setup instructions
   - Add example screenshots
   - Code review and refinement

### Git Workflow

```bash
# Feature branch (should already exist)
git checkout 004-image-puzzle-setup

# Commit frequently with descriptive messages
git add backend/src/models.py
git commit -m "Add ImageSetupRequest/Response Pydantic models"

git add backend/tests/contract/test_setup_puzzle_from_image.py
git commit -m "Add contract tests for image setup endpoint"

git add backend/src/services/image_word_extractor.py
git commit -m "Implement ImageWordExtractor service with LLM vision"

# Push regularly
git push origin 004-image-puzzle-setup

# When feature complete, create PR
gh pr create --title "Feature: Image-Based Puzzle Setup" --body "See specs/004-image-puzzle-setup/spec.md"
```

---

## Configuration Reference

### Backend Environment Variables

```bash
# Required for OpenAI
OPENAI_API_KEY=sk-proj-...

# Optional for remote Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Optional for custom timeout
LLM_TIMEOUT=10  # seconds
```

### Frontend Environment Variables

```bash
# Required
REACT_APP_API_URL=http://127.0.0.1:8000

# Optional for development
REACT_APP_DEBUG=true
```

### LLM Provider Configuration

**OpenAI Vision Models**:
| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| gpt-4-vision-preview | Medium | High | $0.01/image |
| gpt-4-turbo | Fast | High | $0.01/image |
| gpt-4o | Fastest | Highest | $0.015/image |

**Ollama Vision Models**:
| Model | Size | Speed | Quality | Cost |
|-------|------|-------|---------|------|
| llava:7b | 4.7GB | Fast | Medium | Free |
| llava:13b | 8.0GB | Medium | High | Free |
| bakllava | 4.7GB | Fast | Medium-High | Free |
| llava-llama3 | 5.5GB | Medium | High | Free |

---

## Performance Benchmarks

### Image Paste (Frontend)

| Operation | Target | Typical | Notes |
|-----------|--------|---------|-------|
| Clipboard read | <100ms | 50-80ms | Browser-dependent |
| Base64 encoding | <500ms | 200-400ms | 2MB image |
| Preview display | <2s | 1-1.5s | Includes validation |

### LLM Extraction (Backend)

| Provider | Model | Target | Typical | Notes |
|----------|-------|--------|---------|-------|
| OpenAI | gpt-4-vision-preview | <10s | 3-5s | Network-dependent |
| OpenAI | gpt-4-turbo | <8s | 2-4s | Faster than preview |
| OpenAI | gpt-4o | <5s | 2-3s | Fastest |
| Ollama | llava:7b | <15s | 8-12s | Local, CPU-dependent |
| Ollama | llava:13b | <20s | 12-18s | Slower, higher quality |

### Memory Usage

| Component | Initial | Peak | Sustained |
|-----------|---------|------|-----------|
| Frontend (no image) | ~50MB | ~50MB | ~50MB |
| Frontend (with preview) | ~50MB | ~70MB | ~60MB |
| Backend (idle) | ~100MB | ~100MB | ~100MB |
| Backend (during extraction) | ~100MB | ~300MB | ~120MB |

---

## Next Steps

1. ✅ **Quickstart guide created** - This document
2. ⏳ **Update agent context** - Run `update-agent-context.sh copilot`
3. ⏳ **Generate tasks** - Run `/speckit.tasks` to create detailed task breakdown
4. ⏳ **Begin implementation** - Follow TDD workflow starting with backend contract tests

---

**Quickstart Status**: ✅ COMPLETE
**Last Updated**: December 13, 2025
