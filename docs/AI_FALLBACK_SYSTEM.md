# AI Fallback System - Niya Help Bot

## Overview

The RAG system now includes an intelligent fallback mechanism that automatically switches between multiple Gemini models when rate limits are hit, ensuring continuous availability and optimal performance.

## Model Priority Order

The system tries models in this order:

### 1. **gemini-2.5-flash** (Primary)
- **Category**: Text-out models
- **Rate Limits**: 
  - RPM: 5 requests per minute
  - TPM: 250,000 tokens per minute
  - RPD: 20 requests per day
- **Use Case**: Primary model for all queries
- **Best For**: High-quality responses, general queries

### 2. **gemini-2.5-flash-lite** (Fallback 1)
- **Category**: Text-out models
- **Rate Limits**:
  - RPM: 10 requests per minute (2x primary)
  - TPM: 250,000 tokens per minute
  - RPD: 20 requests per day
- **Use Case**: When primary hits rate limit
- **Best For**: Faster responses, higher throughput

### 3. **gemma-3-1b** (Fallback 2)
- **Category**: Other models
- **Rate Limits**:
  - RPM: 30 requests per minute (6x primary)
  - TPM: 15,000 tokens per minute
  - RPD: 14,400 requests per day
- **Use Case**: When Gemini models are exhausted
- **Best For**: Lightweight, fast responses

### 4. **gemma-3-2b** (Fallback 3)
- **Category**: Other models
- **Rate Limits**:
  - RPM: 30 requests per minute
  - TPM: 15,000 tokens per minute
  - RPD: 14,400 requests per day
- **Use Case**: If gemma-3-1b fails
- **Best For**: Better quality than 1b, still fast

### 5. **gemma-3-4b** (Fallback 4)
- **Category**: Other models
- **Rate Limits**:
  - RPM: 30 requests per minute
  - TPM: 15,000 tokens per minute
  - RPD: 14,400 requests per day
- **Use Case**: Last resort fallback
- **Best For**: Best quality among Gemma models

## How It Works

### Automatic Rate Limit Detection

The system detects rate limit errors by checking for these keywords in error messages:
- `rate limit`
- `quota`
- `429` (HTTP status code)
- `resource exhausted`
- `too many requests`
- `per minute`
- `per day`

### Fallback Flow

```
1. Try gemini-2.5-flash
   ↓ (if rate limit)
2. Try gemini-2.5-flash-lite
   ↓ (if rate limit)
3. Try gemma-3-1b
   ↓ (if rate limit)
4. Try gemma-3-2b
   ↓ (if rate limit)
5. Try gemma-3-4b
   ↓ (if all fail)
6. Use stored Q&A answer (RAG fallback)
```

### Model State Management

- **Current Model Index**: Tracks which model is currently active
- **Automatic Switching**: Switches to next model on rate limit
- **Circular Fallback**: After last model, wraps back to first (with delay)
- **Model Persistence**: Current model index persists during session

## Response Data

Each response includes:
```python
{
    'query': 'user question',
    'similarity_scores': [0.85, 0.78, 0.72],
    'used_rag': True,
    'response': 'AI generated response',
    'rag_context': ['relevant questions'],
    'model_used': 'gemini-2.5-flash'  # Which model actually responded
}
```

## Error Handling

### Rate Limit Errors
- **Action**: Automatically switch to next model
- **Logging**: Logs model switch with reason
- **User Impact**: None (seamless transition)

### Non-Rate-Limit Errors
- **Action**: Use stored Q&A answer as fallback
- **Logging**: Logs error details
- **User Impact**: Still gets helpful response

### All Models Exhausted
- **Action**: Use best matching Q&A pair from RAG index
- **Logging**: Logs fallback to RAG
- **User Impact**: Gets stored answer (still helpful)

## Benefits

✅ **High Availability**: System continues working even when primary model hits limits  
✅ **Optimal Performance**: Uses best available model at any time  
✅ **Cost Efficient**: Automatically uses cheaper models when possible  
✅ **Seamless UX**: Users don't notice model switches  
✅ **Resilient**: Multiple layers of fallback ensure responses always available  

## Configuration

Models are configured in `utils/rag_system.py`:

```python
self.models = [
    'gemini-2.5-flash',      # Primary
    'gemini-2.5-flash-lite', # Fallback 1
    'gemma-3-1b',            # Fallback 2
    'gemma-3-2b',            # Fallback 3
    'gemma-3-4b',            # Fallback 4
]
```

## Monitoring

Check logs for:
- Model switches: `"Rate limit hit on X, switching to Y"`
- Model used: `"model_used": "gemini-2.5-flash"`
- Errors: `"Error calling Gemini API (model_name): error_details"`

## Rate Limit Strategy

### Primary Model (gemini-2.5-flash)
- Best quality
- Use for normal traffic
- 5 RPM limit

### Fallback 1 (gemini-2.5-flash-lite)
- 2x RPM capacity (10 RPM)
- Use when primary is busy
- Same quality as primary

### Gemma Models (1b, 2b, 4b)
- 6x RPM capacity (30 RPM)
- Use during high traffic
- Slightly lower quality but still good
- Much higher daily limits (14.4K RPD)

## Best Practices

1. **Monitor Model Usage**: Check which model is being used most
2. **Adjust Priority**: Reorder models if needed based on usage patterns
3. **Rate Limit Alerts**: Set up alerts if all models are frequently exhausted
4. **Quality Monitoring**: Track response quality across models

## Troubleshooting

### All Models Failing
- Check API key validity
- Verify internet connection
- Check Google AI Studio for service status
- Review error logs for specific issues

### Frequent Model Switches
- Normal during high traffic
- Consider upgrading API tier if needed
- Monitor rate limit patterns

### Quality Degradation
- Gemma models may have slightly lower quality
- System automatically uses best available
- RAG fallback ensures helpful responses

## Future Enhancements

- [ ] Model performance tracking
- [ ] Automatic model selection based on query complexity
- [ ] Rate limit prediction and preemptive switching
- [ ] Model health monitoring
- [ ] Cost tracking per model

