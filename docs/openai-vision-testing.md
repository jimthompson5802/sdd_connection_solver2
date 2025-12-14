# OpenAI GPT-4 Vision Model Testing

**Feature**: 004-image-puzzle-setup | **Date**: December 13, 2025

## Test Overview

This document covers testing the image-based puzzle setup feature with OpenAI's GPT-4 Vision models, including setup, test procedures, results analysis, and troubleshooting.

## Test Environment Setup

### Prerequisites

1. **OpenAI API Access**
   ```bash
   # Required: Valid OpenAI API key with GPT-4 Vision access
   export OPENAI_API_KEY="sk-proj-your-key-here"
   
   # Verify API access
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY" \
     | jq '.data[] | select(.id | contains("gpt-4")) | .id'
   ```

2. **Application Setup**
   ```bash
   # Backend
   cd backend
   source .venv/bin/activate
   export PYTHONPATH=src
   uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
   
   # Frontend (new terminal)
   cd frontend  
   npm start
   ```

3. **Test Images Prepared**
   - Clear 4x4 word grid screenshots
   - Various image formats (PNG, JPEG)
   - Different quality levels
   - Edge case images (blurry, rotated, etc.)

### OpenAI Vision Models

| Model | Availability | Performance | Quality | Cost |
|-------|-------------|-------------|---------|------|
| `gpt-4-vision-preview` | ✅ Generally Available | Good (3-5s) | High | ~$0.01-0.03 |
| `gpt-4-turbo` | ✅ Generally Available | Faster (2-3s) | High | ~$0.01-0.02 |
| `gpt-4o` | ✅ Generally Available | Fast (2-4s) | Highest | ~$0.015-0.025 |

## Test Cases

### Test Case 1: Basic Functionality

**Objective**: Verify successful word extraction from clear puzzle images

**Test Steps**:
1. Navigate to "From Image" interface
2. Paste clear 4x4 grid screenshot
3. Select "OpenAI" provider
4. Select "gpt-4-vision-preview" model
5. Click "Setup Puzzle"
6. Verify 16 words extracted correctly

**Sample Test Image Content**:
```
APPLE   ORANGE  GRAPE   BANANA
DOG     CAT     BIRD    FISH
RED     BLUE    GREEN   YELLOW
HOUSE   CAR     TREE    BOOK
```

**Expected Results**:
- Response time: 2-5 seconds
- Status: "success"
- Words extracted: 16 unique words
- Words normalized to lowercase
- No hallucinated or incorrect words

**API Test Command**:
```bash
curl -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "'$(base64 -i test_clear_grid.png | tr -d '\n')'",
    "image_mime": "image/png",
    "provider_type": "openai", 
    "model_name": "gpt-4-vision-preview"
  }' | jq .
```

**Success Criteria**:
- ✅ HTTP 200 response
- ✅ 16 words in response array
- ✅ All words match image content
- ✅ Response time < 10 seconds

### Test Case 2: Model Comparison

**Objective**: Compare performance across different GPT-4 Vision models

**Models to Test**:
- gpt-4-vision-preview
- gpt-4-turbo 
- gpt-4o

**Metrics to Measure**:
- Response time (seconds)
- Accuracy (% words correct)
- Token usage (for cost analysis)
- Error rate

**Sample Results Table**:

| Model | Avg Response Time | Accuracy | Tokens Used | Cost per Image |
|-------|------------------|----------|-------------|---------------|
| gpt-4-vision-preview | 4.2s | 98% | 1,250 | $0.028 |
| gpt-4-turbo | 2.8s | 97% | 1,100 | $0.018 |
| gpt-4o | 3.1s | 99% | 1,180 | $0.022 |

### Test Case 3: Image Quality Variations

**Objective**: Test robustness with different image quality levels

**Test Images**:
1. **High Quality (1920x1920 PNG)**
   - Clear text, high contrast
   - Perfect grid alignment
   - Expected: 100% accuracy

2. **Medium Quality (1024x1024 JPEG)**
   - Some compression artifacts
   - Good text clarity
   - Expected: 95-98% accuracy

3. **Low Quality (512x512 JPEG, 60% quality)**
   - Visible compression
   - Some text blur
   - Expected: 85-90% accuracy

4. **Phone Screenshot**
   - Realistic user scenario
   - Slight perspective distortion
   - Expected: 90-95% accuracy

**Test Procedure**:
```bash
for image in high_quality.png medium_quality.jpg low_quality.jpg phone_screenshot.png; do
  echo "Testing $image..."
  curl -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
    -H "Content-Type: application/json" \
    -d '{
      "image_base64": "'$(base64 -i "$image" | tr -d '\n')'",
      "image_mime": "image/'${image##*.}'",
      "provider_type": "openai",
      "model_name": "gpt-4-turbo"
    }' | jq '.remaining_words | length'
done
```

### Test Case 4: Error Handling

**Objective**: Verify proper error handling for various failure scenarios

**Test Scenarios**:

1. **Invalid API Key**
   ```bash
   export OPENAI_API_KEY="invalid-key"
   # Expected: HTTP 500, clear error message
   ```

2. **Non-Grid Image** 
   - Use image with random text, not 4x4 grid
   - Expected: HTTP 400, "unable to extract puzzle words"

3. **Blank Image**
   - Use solid color image with no text
   - Expected: HTTP 400, extraction failure

4. **Corrupted Image**
   - Use invalid base64 data
   - Expected: HTTP 422, validation error

**Error Response Validation**:
```json
{
  "detail": "OpenAI API error: Invalid API key provided"
}
```

### Test Case 5: Performance & Load Testing

**Objective**: Measure performance under realistic usage patterns

**Test Scenarios**:

1. **Sequential Requests**
   ```bash
   for i in {1..10}; do
     echo "Request $i..."
     time curl -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
       -H "Content-Type: application/json" \
       -d @test_request.json > /dev/null
   done
   ```

2. **Large Image Processing**
   - Test with 5MB image (maximum allowed)
   - Measure response time and memory usage

3. **Rate Limit Testing**
   - Send requests at OpenAI rate limit boundary
   - Verify graceful degradation

**Performance Targets**:
- ✅ Response time < 10 seconds (95th percentile)
- ✅ Memory usage < 100MB per request
- ✅ No memory leaks over 100 requests
- ✅ Graceful handling of rate limits

### Test Case 6: Integration Testing

**Objective**: Verify end-to-end flow from image paste to puzzle gameplay

**Test Flow**:
1. Start with fresh session
2. Navigate to image setup
3. Paste test image
4. Extract words with OpenAI
5. Verify puzzle session created
6. Get first recommendation
7. Record a response
8. Verify state management

**Validation Points**:
- ✅ Session state initialized correctly
- ✅ 16 words available for gameplay  
- ✅ Recommendation engine works with extracted words
- ✅ Game flow identical to file-based setup

## Test Results Template

### Execution Log

**Test Date**: [Date]
**Tester**: [Name]
**Environment**: [Development/Staging/Production]
**OpenAI Model**: [gpt-4-vision-preview/gpt-4-turbo/gpt-4o]

### Test Case Results

| Test Case | Status | Response Time | Accuracy | Notes |
|-----------|---------|---------------|----------|-------|
| Basic Functionality | ✅ PASS | 3.2s | 100% | Perfect extraction |
| Model Comparison | ✅ PASS | Varies | 97-99% | gpt-4o slightly better |
| Image Quality | ⚠️ PARTIAL | 2.8-6.1s | 85-100% | Low quality struggled |
| Error Handling | ✅ PASS | N/A | N/A | All errors handled correctly |
| Performance | ✅ PASS | 2.1-4.8s | N/A | Within targets |
| Integration | ✅ PASS | N/A | N/A | Full flow works |

### Issues Found

**Issue 1**: [Description]
- **Severity**: High/Medium/Low
- **Steps to Reproduce**: [Steps]
- **Expected**: [Expected behavior] 
- **Actual**: [Actual behavior]
- **Workaround**: [If available]

### Performance Metrics

**Response Time Distribution**:
- Minimum: X.Xs
- 50th percentile: X.Xs  
- 95th percentile: X.Xs
- Maximum: X.Xs

**Accuracy by Image Type**:
- Screenshot (PNG): XX%
- Photo (JPEG): XX%
- Compressed (JPG): XX%

**Cost Analysis**:
- Average tokens per request: XXX
- Cost per successful extraction: $X.XX
- Estimated monthly cost (1000 images): $XXX

## Troubleshooting Guide

### Common Issues

**1. "OpenAI API key not configured"**
- **Cause**: Missing or invalid OPENAI_API_KEY
- **Solution**: Set valid API key in environment
- **Verification**: `echo $OPENAI_API_KEY`

**2. "Rate limit exceeded"**
- **Cause**: Too many requests to OpenAI API
- **Solution**: Implement exponential backoff
- **Prevention**: Add rate limiting to frontend

**3. "Model does not support vision"**
- **Cause**: Using non-vision model (e.g., gpt-3.5-turbo)
- **Solution**: Select vision-capable model
- **Fix**: Update frontend model validation

**4. "Unable to extract puzzle words"**
- **Cause**: Image doesn't contain clear 4x4 grid
- **Solution**: Use higher quality image
- **Debug**: Check image content manually

**5. Slow response times (>10s)**
- **Cause**: Large image or network issues
- **Solution**: Compress image or retry
- **Monitoring**: Add response time logging

### Debug Commands

**Test API Key Validity**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  | jq '.data[0].id'
```

**Check Model Availability**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  | jq '.data[] | select(.id | contains("gpt-4"))'
```

**Test Vision Capability**:
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4-vision-preview",
    "messages": [{
      "role": "user", 
      "content": [{
        "type": "text",
        "text": "What is in this image?"
      }, {
        "type": "image_url",
        "image_url": {"url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}
      }]
    }],
    "max_tokens": 100
  }'
```

### Monitoring & Alerting

**Key Metrics to Track**:
- API response time (target: <5s average)
- Error rate (target: <5%)
- Token usage (for cost monitoring)
- Image processing success rate (target: >95%)

**Alerting Thresholds**:
- Response time >10s for 3 consecutive requests
- Error rate >10% over 5-minute window
- Cost exceeding $50/day
- Zero successful extractions in 10 minutes

## Cost Optimization

### Usage Patterns
- **Development**: ~$5-10/month (testing)
- **Light Production**: ~$20-50/month (100 images/day)
- **Heavy Production**: ~$100-300/month (1000 images/day)

### Cost Reduction Strategies
1. **Image preprocessing**: Resize to optimal dimensions
2. **Model selection**: Use gpt-4-turbo for speed/cost balance
3. **Caching**: Cache results for identical images (optional)
4. **Fallback**: Use Ollama for cost-sensitive scenarios

---

## Test Checklist

### Pre-Test Setup
- [ ] OpenAI API key configured and verified
- [ ] Application running (backend + frontend)
- [ ] Test images prepared (various formats/quality)
- [ ] Monitoring tools ready (if applicable)

### Basic Functionality Tests
- [ ] Clear 4x4 grid extraction works
- [ ] Response time under 10 seconds
- [ ] 16 words extracted correctly
- [ ] Session created successfully

### Model Comparison Tests
- [ ] gpt-4-vision-preview tested
- [ ] gpt-4-turbo tested  
- [ ] gpt-4o tested (if available)
- [ ] Performance comparison documented

### Error Handling Tests
- [ ] Invalid API key handling
- [ ] Non-grid image handling
- [ ] Corrupted image handling
- [ ] Rate limit handling

### Quality Tests
- [ ] High quality images (>95% accuracy)
- [ ] Medium quality images (>90% accuracy)
- [ ] Low quality images (>80% accuracy)
- [ ] Real user screenshots tested

### Integration Tests
- [ ] End-to-end flow works
- [ ] Session management correct
- [ ] Recommendation engine integration
- [ ] No regressions in existing features

### Performance Tests
- [ ] Load testing completed
- [ ] Memory usage within limits
- [ ] No memory leaks detected
- [ ] Rate limits respected

---

**Test Status**: ✅ **READY FOR EXECUTION**

**Prerequisites**: Valid OpenAI API key, running application

**Next Steps**: Execute test cases, document results, address any issues found

---

**Last Updated**: December 13, 2025  
**Test Version**: 1.0  
**Feature**: Image-based puzzle setup with OpenAI GPT-4 Vision