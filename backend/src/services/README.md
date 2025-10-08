Keep ollama models in memory longer:
```bash
curl -X POST http://localhost:11434/api/generate -d '{"model": "llama2:13b", "keep_alive": "60m"}'
```
This will keep the model in memory for 60 minutes after the request completes.

Change `model` to the name of the model you want to use.

The `keep_alive` parameter accepts durations in seconds (e.g., "300s"), minutes (e.g., "30m"), or hours (e.g., "2h") or "-1" to keep the model in memory indefinitely until the server is restarted or the model is explicitly unloaded.