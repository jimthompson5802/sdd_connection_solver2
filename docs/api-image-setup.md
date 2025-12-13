# API Documentation: Image-Based Puzzle Setup

**Feature**: 004-image-puzzle-setup | **Version**: v2 | **Date**: December 13, 2025

## Overview

This document describes the `/api/v2/setup_puzzle_from_image` endpoint for extracting words from 4x4 puzzle grid images using LLM vision capabilities.

## Base URL

```
http://localhost:8000  # Development
https://your-domain.com  # Production
```

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Endpoint

### POST /api/v2/setup_puzzle_from_image

Extract 16 words from a 4x4 puzzle grid image and create a new puzzle session.

**Authentication**: None required (single-user application)

#### Request

**Content-Type**: `application/json`

**Request Body Schema**:

```typescript
interface ImageSetupRequest {
  image_base64: string;      // Base64-encoded image (without data URL prefix)
  image_mime: string;        // MIME type: image/png, image/jpeg, image/jpg, image/gif, image/webp
  provider_type: string;     // LLM provider: "openai", "ollama", "simple"
  model_name: string;        // Model name (e.g., "gpt-4-vision-preview")
}
```

**Field Validation**:
- `image_base64`: Maximum 6.67MB (5MB original image + base64 overhead)
- `image_mime`: Must be one of supported formats (PNG, JPEG, JPG, GIF, WebP)
- `provider_type`: Must be "openai", "ollama", or "simple"
- `model_name`: Must be vision-capable model for the selected provider

#### Response

**Content-Type**: `application/json`

**Success Response (200 OK)**:

```json
{
  "remaining_words": [
    "apple", "banana", "orange", "grape",
    "dog", "cat", "bird", "fish", 
    "red", "blue", "green", "yellow",
    "house", "car", "tree", "book"
  ],
  "status": "success",
  "message": null
}
```

**Error Response Schema**:

```json
{
  "remaining_words": [],
  "status": "error", 
  "message": "Error description"
}
```

#### HTTP Status Codes

| Status | Description | Common Causes |
|--------|-------------|---------------|
| **200** | Success | Words extracted successfully |
| **400** | Bad Request | Extraction failure, wrong word count, invalid provider |
| **413** | Payload Too Large | Image exceeds 5MB size limit |
| **422** | Unprocessable Entity | Validation errors (invalid MIME type, missing fields) |
| **500** | Internal Server Error | LLM provider failures, system errors |

#### Error Examples

**400 Bad Request - Extraction Failure**:
```json
{
  "detail": "LLM unable to extract puzzle words from image"
}
```

**413 Payload Too Large**:
```json
{
  "detail": "Image size exceeds 5MB limit"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "image_mime"],
      "msg": "Unsupported MIME type: image/bmp. Supported types: ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']",
      "type": "value_error"
    }
  ]
}
```

**500 Provider Error**:
```json
{
  "detail": "OpenAI API key not configured"
}
```

## Usage Examples

### cURL Examples

**Basic Request (OpenAI)**:
```bash
curl -X POST "http://localhost:8000/api/v2/setup_puzzle_from_image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "'$(base64 -i puzzle.png | tr -d '\n')'",
    "image_mime": "image/png",
    "provider_type": "openai",
    "model_name": "gpt-4-vision-preview"
  }'
```

**Ollama Local Model**:
```bash
curl -X POST "http://localhost:8000/api/v2/setup_puzzle_from_image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "'$(base64 -i puzzle.jpg | tr -d '\n')'",
    "image_mime": "image/jpeg",
    "provider_type": "ollama", 
    "model_name": "llava"
  }'
```

### JavaScript/TypeScript Examples

**Using Fetch API**:
```typescript
// Convert File to base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64 = reader.result as string;
      // Remove data URL prefix (e.g., "data:image/png;base64,")
      const base64Data = base64.split(',')[1];
      resolve(base64Data);
    };
    reader.onerror = reject;
  });
};

// API call
const setupPuzzleFromImage = async (
  imageFile: File,
  provider: string = 'openai',
  model: string = 'gpt-4-vision-preview'
) => {
  try {
    const imageBase64 = await fileToBase64(imageFile);
    
    const response = await fetch('/api/v2/setup_puzzle_from_image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_base64: imageBase64,
        image_mime: imageFile.type,
        provider_type: provider,
        model_name: model
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Setup failed');
    }

    const result = await response.json();
    return result.remaining_words; // Array of 16 words
  } catch (error) {
    console.error('Puzzle setup failed:', error);
    throw error;
  }
};
```

**React Hook Example**:
```typescript
import { useState } from 'react';

interface ImageSetupResult {
  words: string[] | null;
  loading: boolean;
  error: string | null;
}

const useImagePuzzleSetup = () => {
  const [result, setResult] = useState<ImageSetupResult>({
    words: null,
    loading: false,
    error: null
  });

  const setupFromImage = async (
    imageBase64: string,
    imageMime: string,
    provider: string,
    model: string
  ) => {
    setResult({ words: null, loading: true, error: null });

    try {
      const response = await fetch('/api/v2/setup_puzzle_from_image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_base64: imageBase64,
          image_mime: imageMime,
          provider_type: provider,
          model_name: model
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      setResult({ words: data.remaining_words, loading: false, error: null });
      return data.remaining_words;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setResult({ words: null, loading: false, error: errorMessage });
      throw error;
    }
  };

  return { ...result, setupFromImage };
};
```

### Python Examples

**Using requests library**:
```python
import requests
import base64
from typing import List

def setup_puzzle_from_image(
    image_path: str,
    provider: str = 'openai',
    model: str = 'gpt-4-vision-preview',
    api_url: str = 'http://localhost:8000'
) -> List[str]:
    """
    Setup puzzle from image file.
    
    Args:
        image_path: Path to image file
        provider: LLM provider ('openai', 'ollama', 'simple')
        model: Model name for the provider
        api_url: Base URL of the API
        
    Returns:
        List of 16 extracted words
        
    Raises:
        requests.HTTPError: If API request fails
        ValueError: If response format is invalid
    """
    # Read and encode image
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Determine MIME type from extension
    mime_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg', 
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }.get(image_path.lower().split('.')[-1], 'image/jpeg')
    
    # Make API request
    response = requests.post(
        f'{api_url}/api/v2/setup_puzzle_from_image',
        json={
            'image_base64': image_data,
            'image_mime': mime_type,
            'provider_type': provider,
            'model_name': model
        }
    )
    
    # Handle response
    response.raise_for_status()
    data = response.json()
    
    if data['status'] == 'error':
        raise ValueError(f"Extraction failed: {data['message']}")
    
    return data['remaining_words']

# Usage example
try:
    words = setup_puzzle_from_image('puzzle_grid.png')
    print(f"Extracted {len(words)} words: {words}")
except Exception as e:
    print(f"Error: {e}")
```

## Provider-Specific Configuration

### OpenAI Provider

**Required Environment**:
```bash
export OPENAI_API_KEY="sk-proj-your-key-here"
```

**Supported Models**:
- `gpt-4-vision-preview` (recommended for development)
- `gpt-4-turbo` (fastest response)
- `gpt-4o` (latest model)

**Performance**: 2-5 seconds typical response time

### Ollama Provider

**Setup Requirements**:
```bash
# Install Ollama
ollama serve

# Pull vision model
ollama pull llava
```

**Supported Models**:
- `llava` (7B parameters, fastest)
- `llava:13b` (13B parameters, better accuracy)
- `llava:34b` (34B parameters, best quality)
- `bakllava` (better text recognition)
- `llava-llama3` (latest Llama 3 base)

**Performance**: 10-60 seconds depending on hardware

### Simple Provider

**Note**: Simple provider does NOT support vision capabilities and will return:
```json
{
  "remaining_words": [],
  "status": "error",
  "message": "Selected model does not support image analysis"
}
```

## Rate Limits & Quotas

### OpenAI
- **Rate limit**: Per API key limits (typically 500 RPM for GPT-4 Vision)
- **Token limits**: Images consume ~765 tokens + prompt tokens
- **Cost**: ~$0.01-0.03 per image analysis

### Ollama
- **Rate limit**: Hardware dependent (local processing)
- **Concurrent requests**: 1 (sequential processing recommended)
- **Cost**: Free (local inference)

### Simple
- **Rate limit**: N/A (no vision support)

## Integration Notes

### Session Management

After successful image setup, the API automatically:
1. Creates a new puzzle session with extracted words
2. Clears any existing session state
3. Initializes tracking for attempts and recommendations

The session is immediately ready for:
- Getting recommendations (`/api/v1/next-recommendation`)
- Recording responses (`/api/v1/record-response`)

### Error Handling Best Practices

1. **Client-side validation**: Validate image size and MIME type before API call
2. **Retry logic**: Implement exponential backoff for 500 errors
3. **User feedback**: Display clear error messages for different error types
4. **Fallback options**: Allow users to try different providers/models

### Performance Optimization

1. **Image preprocessing**: Resize images to 1024x1024 for faster processing
2. **Format selection**: Use PNG for screenshots, JPEG for photos
3. **Caching**: Cache successful extractions by image hash (if applicable)
4. **Provider selection**: Use OpenAI for speed, Ollama for cost savings

---

## Related Endpoints

This endpoint integrates with existing puzzle management endpoints:

- `POST /api/v1/setup-puzzle` - File-based puzzle setup
- `GET /api/v1/next-recommendation` - Get solving recommendations
- `POST /api/v1/record-response` - Record user attempts
- `GET /api/v1/status` - Check puzzle status

For complete API documentation, see the interactive docs at `/docs`.

---

**Last Updated**: December 13, 2025  
**API Version**: v2  
**Feature Status**: Implemented and tested