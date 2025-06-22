# Calmindra Backend 🚀

A mental-health chatbot backend built with FastAPI, Ollama, and Redis for stateful, empathetic conversations.

## ✅ Completed Features

- **FastAPI** server exposing a `/chat/` endpoint  
- **Ollama integration** using the local model `ALIENTELLIGENCE/mindwell:latest`  
- **System prompt** that defines the bot as “Calmindra,” an empathetic mental-health assistant  
- **Session persistence** via Redis, so chat history survives restarts  
- **Context window** that retains the last 10 messages per session  
- **In-memory rate limiting** (max 5 requests/minute per IP)  
- **Dockerized** with a `Dockerfile` and `docker-compose.yml` for Redis + backend  
- **UUID-based session IDs**, passed via `X-Session-Id` header or generated automatically  

## 🚀 Next Steps

1. **Frontend Integration**  
   - Build a React/Tailwind chat UI.  
   - Store and send `session_id` in `localStorage` for persistent conversations.

2. **Redis-Backed Rate Limiting**  
   - Replace the in-memory limiter with a Redis token-bucket approach.  
   - Ensures rate limits persist across service restarts and scale-outs.

3. **Prompt Refinement & Fine-Tuning**  
   - Experiment with more nuanced system prompts based on user profiles or sentiment.  
   - Fine-tune on an empathetic dialogue dataset for deeper domain alignment.

4. **Monitoring & Logging**  
   - Add structured request/response logging (redacting PII).  
   - Integrate with an APM (e.g., Prometheus, New Relic) to track latency and error rates.

5. **Production Deployment**  
   - Add TLS termination and environment-specific configuration.  
   - Deploy via Docker Compose or Kubernetes to a cloud provider.

6. **Long-Term Conversation Tracking**  
   - Extend Redis schema to track user sentiment trends over time.  
   - Build journaling and progress-summary endpoints for user follow-up.

7. **Accessibility & UX Enhancements**  
   - Implement web-accessible UI improvements (screen reader support, keyboard navigation).  
   - Add features like typing indicators, read receipts, and message timestamps.
