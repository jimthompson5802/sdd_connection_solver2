# Ollama LLaVA Model Testing

**Feature**: 004-image-puzzle-setup | **Date**: December 13, 2025

## Test Overview

This document covers testing the image-based puzzle setup feature with Ollama's local LLaVA (Large Language and Vision Assistant) models for cost-free, local inference.

## Test Environment Setup

### Prerequisites

1. **Ollama Installation**
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from https://ollama.ai/download/windows
   ```

2. **Ollama Service**
   ```bash
   # Start Ollama server
   ollama serve
   
   # Verify installation
   ollama --version
   ```

3. **Vision Models Download**
   ```bash
   # Recommended: LLaVA 7B (fastest, good accuracy)
   ollama pull llava
   
   # Alternative: LLaVA 13B (better accuracy, slower)
   ollama pull llava:13b
   
   # Alternative: BakLLaVA (better text recognition)
   ollama pull bakllava
   
   # Alternative: LLaVA 34B (best quality, requires more resources)
   ollama pull llava:34b
   
   # Verify models installed
   ollama list
   ```

4. **System Requirements Check**
   ```bash
   # Check available memory
   free -h  # Linux
   vm_stat | grep "Pages free" | awk '{print $3*4096/1024/1024" MB"}' # macOS
   
   # Check GPU availability (optional)
   nvidia-smi  # NVIDIA
   lspci | grep VGA  # General GPU info
   ```

### Ollama Configuration

**Environment Setup**:
```bash
# Backend configuration
cd backend
export OLLAMA_BASE_URL=http://localhost:11434  # Default
source .venv/bin/activate
export PYTHONPATH=src
```

**Test Ollama Connection**:
```bash
# Test Ollama API directly
curl http://localhost:11434/api/version

# Test model availability
curl http://localhost:11434/api/tags
```

## LLaVA Model Comparison

| Model | Size | RAM Required | VRAM (GPU) | Speed | Text Recognition | Recommended Use |
|-------|------|-------------|------------|-------|------------------|-----------------|
| **llava:7b** | 4.7GB | 8GB | 6GB | Fast (10-20s) | Good | Development, testing |
| **llava:13b** | 7.3GB | 16GB | 12GB | Medium (15-30s) | Better | Production balance |
| **llava:34b** | 20GB | 32GB | 24GB | Slow (30-60s) | Best | High accuracy needs |
| **bakllava** | 4.1GB | 8GB | 6GB | Fast (10-25s) | Excellent | Text-heavy grids |
| **llava-llama3** | 4.7GB | 8GB | 6GB | Fast (10-20s) | Good | Latest Llama base |

## Test Cases

### Test Case 1: Basic Model Functionality

**Objective**: Verify each LLaVA model can extract words from clear puzzle images

**Test Procedure**:
```bash
# Test each model with same image
for model in llava llava:13b bakllava llava:34b; do
  echo "Testing model: $model"
  
  curl -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
    -H "Content-Type: application/json" \
    -d '{
      "image_base64": "'$(base64 -i test_grid.png | tr -d '\n')'",
      "image_mime": "image/png",
      "provider_type": "ollama",
      "model_name": "'$model'"
    }' | jq -r '.status, (.remaining_words | length)'
  
  echo "---"
done
```

**Success Criteria**:
- ✅ HTTP 200 response for all models
- ✅ Status: "success"
- ✅ 16 words extracted per model
- ✅ Response time < 120 seconds

### Test Case 2: Performance Benchmarking

**Objective**: Measure response times and accuracy across different models

**Test Setup**:
```bash
# Prepare test images
images=(
  "clear_grid.png"      # Perfect 4x4 grid
  "screenshot.jpg"      # Real screenshot
  "phone_photo.jpg"     # Phone camera photo
  "compressed.jpg"      # Heavily compressed
)

# Performance test script
for model in llava bakllava llava:13b; do
  echo "Benchmarking $model..."
  
  for image in "${images[@]}"; do
    echo "  Testing with $image..."
    
    start_time=$(date +%s.%N)
    
    response=$(curl -s -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
      -H "Content-Type: application/json" \
      -d '{
        "image_base64": "'$(base64 -i "$image" | tr -d '\n')'",
        "image_mime": "image/'${image##*.}'",
        "provider_type": "ollama",
        "model_name": "'$model'"
      }')
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    status=$(echo "$response" | jq -r '.status')
    word_count=$(echo "$response" | jq -r '.remaining_words | length')
    
    echo "    Duration: ${duration}s, Status: $status, Words: $word_count"
  done
done
```

**Expected Results Table**:

| Model | Clear Grid | Screenshot | Phone Photo | Compressed | Avg Time |
|-------|------------|------------|-------------|------------|----------|
| llava | 10-15s | 12-18s | 15-25s | 18-30s | ~18s |
| bakllava | 12-18s | 15-20s | 18-28s | 20-35s | ~22s |
| llava:13b | 20-30s | 25-35s | 30-45s | 35-60s | ~38s |

### Test Case 3: Hardware Performance Impact

**Objective**: Compare CPU-only vs GPU-accelerated performance

**CPU-Only Test**:
```bash
# Force CPU usage (disable GPU)
export OLLAMA_GPU_LAYERS=0
ollama serve

# Run benchmark
time curl -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

**GPU-Accelerated Test** (if available):
```bash
# Enable GPU usage
unset OLLAMA_GPU_LAYERS
ollama serve

# Monitor GPU usage
nvidia-smi -l 1 &  # NVIDIA
watch -n 1 'rocm-smi'  # AMD

# Run same benchmark
time curl -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

**Performance Comparison**:

| Hardware | Model | Time (CPU) | Time (GPU) | Speedup |
|----------|-------|------------|------------|---------|
| M1 MacBook | llava | 45s | 15s | 3x |
| RTX 3080 | llava | 60s | 12s | 5x |
| RTX 4090 | llava:13b | 120s | 25s | 4.8x |

### Test Case 4: Memory Usage Monitoring

**Objective**: Verify memory requirements don't exceed system limits

**Memory Monitoring Script**:
```bash
#!/bin/bash
# monitor_ollama_memory.sh

echo "Starting memory monitoring..."

# Get baseline memory
baseline_ram=$(free -m | awk 'NR==2{printf "%.1f", $3/1024}')
echo "Baseline RAM usage: ${baseline_ram}GB"

# Start processing
curl -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
  -H "Content-Type: application/json" \
  -d @large_test_image.json &

pid=$!

# Monitor during processing
while kill -0 $pid 2>/dev/null; do
  current_ram=$(free -m | awk 'NR==2{printf "%.1f", $3/1024}')
  ram_usage=$(echo "$current_ram - $baseline_ram" | bc)
  
  echo "RAM usage: ${current_ram}GB (+${ram_usage}GB)"
  sleep 2
done

echo "Processing complete"
```

**Memory Usage Targets**:
- llava (7B): <8GB RAM increase
- llava:13b (13B): <12GB RAM increase  
- llava:34b (34B): <24GB RAM increase

### Test Case 5: Error Handling & Recovery

**Objective**: Test graceful handling of Ollama-specific errors

**Test Scenarios**:

1. **Model Not Installed**
   ```bash
   curl -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
     -H "Content-Type: application/json" \
     -d '{
       "image_base64": "...",
       "image_mime": "image/png",
       "provider_type": "ollama",
       "model_name": "nonexistent-model"
     }'
   
   # Expected: HTTP 500, "Model not found" error
   ```

2. **Ollama Server Down**
   ```bash
   # Stop Ollama
   pkill ollama
   
   # Attempt request
   curl -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
     -H "Content-Type: application/json" \
     -d @test_request.json
   
   # Expected: HTTP 500, connection error
   ```

3. **Out of Memory**
   ```bash
   # Test with very large model on limited RAM system
   # Expected: Graceful degradation or clear error message
   ```

4. **Corrupted Model**
   ```bash
   # Simulate corrupted model files
   # Expected: Clear error message, no crash
   ```

### Test Case 6: Text Recognition Quality

**Objective**: Compare text recognition accuracy across models

**Test Images with Known Content**:

1. **Perfect Grid (Digital)**
   ```
   APPLE  ORANGE GRAPE  BANANA
   DOG    CAT    BIRD   FISH
   RED    BLUE   GREEN  YELLOW
   HOUSE  CAR    TREE   BOOK
   ```

2. **Screenshot Grid (Compressed)**
   - Same content, JPEG compressed
   - Some antialiasing artifacts

3. **Phone Photo Grid**
   - Slight perspective distortion
   - Variable lighting
   - Some blur from camera shake

**Accuracy Measurement**:
```bash
# Test script for accuracy measurement
test_accuracy() {
  local model=$1
  local image=$2
  local expected_words=$3
  
  response=$(curl -s -X POST http://localhost:8000/api/v2/setup_puzzle_from_image \
    -H "Content-Type: application/json" \
    -d '{
      "image_base64": "'$(base64 -i "$image" | tr -d '\n')'",
      "image_mime": "image/png",
      "provider_type": "ollama", 
      "model_name": "'$model'"
    }')
  
  extracted_words=$(echo "$response" | jq -r '.remaining_words[]' | tr '\n' ' ')
  
  # Calculate accuracy (manual verification needed)
  echo "Expected: $expected_words"
  echo "Extracted: $extracted_words"
  echo "Manual verification required for accuracy calculation"
}
```

**Expected Accuracy Results**:

| Model | Perfect Grid | Screenshot | Phone Photo | Overall |
|-------|-------------|------------|-------------|---------|
| llava | 95% | 88% | 82% | 88% |
| bakllava | 98% | 92% | 87% | 92% |
| llava:13b | 98% | 94% | 89% | 94% |
| llava:34b | 99% | 96% | 92% | 96% |

## Troubleshooting Guide

### Common Issues

**1. "Model not found"**
```bash
# Check installed models
ollama list

# Pull missing model
ollama pull llava
```

**2. "Connection refused"**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama server
ollama serve &
```

**3. "Out of memory"**
```bash
# Check system memory
free -h

# Try smaller model
ollama pull llava  # Instead of llava:34b

# Or increase swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**4. Very slow performance**
```bash
# Check if GPU is being used
nvidia-smi  # Should show ollama process if GPU enabled

# Enable GPU if available
export OLLAMA_GPU_LAYERS=32  # Adjust based on VRAM

# Or reduce context size
export OLLAMA_NUM_CTX=2048  # Default 4096
```

**5. Inconsistent results**
```bash
# Set consistent temperature
export OLLAMA_TEMPERATURE=0.1  # More deterministic

# Or test multiple times and average
for i in {1..5}; do
  echo "Test run $i"
  # Run extraction test
done
```

### Performance Optimization

**1. Model Selection Guidelines**
- **Development/Testing**: Use `llava` (fastest)
- **Production (Speed)**: Use `llava` with good hardware
- **Production (Quality)**: Use `bakllava` for better text recognition
- **High Accuracy**: Use `llava:13b` if resources permit

**2. Hardware Optimization**
```bash
# Enable GPU layers (adjust based on VRAM)
export OLLAMA_GPU_LAYERS=35  # Full GPU offload
export OLLAMA_GPU_LAYERS=20  # Partial GPU offload

# Optimize CPU usage
export OLLAMA_NUM_THREAD=8   # Match CPU cores

# Reduce memory usage
export OLLAMA_NUM_CTX=2048   # Smaller context window
```

**3. Image Preprocessing**
- Resize images to 1024x1024 or smaller
- Use PNG for clear text, JPEG for photos
- Increase contrast if text is faint
- Ensure 4x4 grid structure is clear

### Monitoring & Health Checks

**System Health Script**:
```bash
#!/bin/bash
# ollama_health_check.sh

echo "=== Ollama Health Check ==="

# Check Ollama service
if pgrep -f "ollama serve" > /dev/null; then
  echo "✅ Ollama service running"
else
  echo "❌ Ollama service not running"
  exit 1
fi

# Check API response
if curl -s http://localhost:11434/api/version | grep -q "version"; then
  echo "✅ Ollama API responding"
else
  echo "❌ Ollama API not responding"
  exit 1
fi

# Check models
models=$(ollama list | grep -v "NAME" | wc -l)
echo "📊 Models installed: $models"

# Check memory
ram_usage=$(free -m | awk 'NR==2{printf "%.1f", $3*100/$2}')
echo "💾 RAM usage: ${ram_usage}%"

# Check GPU (if available)
if command -v nvidia-smi &> /dev/null; then
  gpu_usage=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
  echo "🎮 GPU usage: ${gpu_usage}%"
fi

echo "=== Health Check Complete ==="
```

## Test Results Template

### Test Environment
- **OS**: [Linux/macOS/Windows]
- **CPU**: [Processor details]
- **RAM**: [Total RAM available]
- **GPU**: [GPU model, VRAM] or "CPU-only"
- **Ollama Version**: [Version]
- **Models Tested**: [List of models]

### Performance Results

| Model | Avg Response Time | Success Rate | Memory Usage | Notes |
|-------|------------------|--------------|--------------|-------|
| llava | XXs | XX% | XGB | [Notes] |
| bakllava | XXs | XX% | XGB | [Notes] |
| llava:13b | XXs | XX% | XGB | [Notes] |

### Accuracy Results

| Model | Perfect Grid | Real Screenshot | Phone Photo | Overall Score |
|-------|-------------|----------------|-------------|---------------|
| llava | XX% | XX% | XX% | XX% |
| bakllava | XX% | XX% | XX% | XX% |
| llava:13b | XX% | XX% | XX% | XX% |

### Issues Encountered
1. **Issue**: [Description]
   - **Resolution**: [How resolved]
   - **Prevention**: [How to prevent]

### Recommendations

**For Development**:
- Model: [Recommended model]
- Hardware: [Minimum requirements]
- Configuration: [Optimal settings]

**For Production**:
- Model: [Recommended model]  
- Hardware: [Recommended specifications]
- Monitoring: [Key metrics to watch]

---

## Test Checklist

### Pre-Test Setup
- [ ] Ollama installed and service running
- [ ] Vision models downloaded (llava, bakllava, llava:13b)
- [ ] System resources verified (RAM, GPU)
- [ ] Test images prepared
- [ ] Backend application configured for Ollama

### Basic Functionality Tests  
- [ ] llava model extracts words correctly
- [ ] bakllava model extracts words correctly
- [ ] llava:13b model extracts words correctly (if resources permit)
- [ ] Response times within acceptable limits
- [ ] Memory usage within system limits

### Performance Tests
- [ ] CPU-only performance measured
- [ ] GPU performance measured (if available)
- [ ] Memory usage monitored
- [ ] Multiple concurrent requests tested

### Quality Tests
- [ ] Perfect grid images tested
- [ ] Real screenshot images tested
- [ ] Phone photo images tested
- [ ] Accuracy rates documented

### Error Handling Tests
- [ ] Model not found error handled
- [ ] Ollama server down error handled
- [ ] Out of memory scenario tested
- [ ] Network timeout scenarios tested

### Integration Tests
- [ ] End-to-end flow works with Ollama
- [ ] Session management correct
- [ ] No regressions in existing functionality
- [ ] Fallback to other providers works

---

**Test Status**: ✅ **READY FOR EXECUTION**

**Prerequisites**: Ollama installed, models downloaded, sufficient system resources

**Estimated Time**: 2-4 hours (depending on model download times and hardware)

---

**Last Updated**: December 13, 2025  
**Test Version**: 1.0  
**Feature**: Image-based puzzle setup with Ollama LLaVA models