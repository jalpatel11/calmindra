# Calmindra - Mental Health Chatbot

A comprehensive mental health chatbot application built with Next.js frontend, FastAPI backend, Ollama AI integration, and persistent conversation management.

## Architecture

```
Frontend (Next.js)     Backend (FastAPI)     AI (Ollama)
     ↓                        ↓                ↓
   Port 3000  ←→  HTTP  ←→  Port 8000  ←→  Port 11434
     ↓                        ↓                ↓
Thread Management      Session Storage      Mental Health Model
(localStorage)         (Redis/Memory)      (mindwell:latest)
```

## Current Features

### Frontend (Next.js + TypeScript)
- Modern responsive UI with Tailwind CSS and shadcn/ui components
- Real-time streaming chat interface with Assistant UI
- Thread management with persistent conversation history
- Sidebar navigation for seamless thread switching
- TypeScript implementation for enhanced type safety

### Backend (FastAPI + Python)
- RESTful API with `/chat/` endpoint
- Ollama integration using `ALIENTELLIGENCE/mindwell:latest` model
- Session persistence with Redis (fallback to in-memory storage)
- Streaming responses for real-time chat experience
- CORS support for frontend integration
- Structured logging with request/response tracking

### AI & Conversation Management
- Specialized mental health model (mindwell:latest)
- Empathetic system prompt as "Calmindra" assistant
- Context-aware responses with conversation history
- Session-based memory for personalized interactions

### Infrastructure
- Docker containerization for both frontend and backend
- Docker Compose setup with Redis integration
- Development scripts for streamlined local setup
- Environment-based configuration management

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.10+ (for backend development)
- Ollama with mindwell:latest model

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd calmindra

# Start all services (Redis, Ollama, Backend, Frontend)
./start-dev.sh

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Manual Setup
```bash
# Start Redis and Ollama services
./start-redis-ollama.sh

# Start backend (in separate terminal)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in separate terminal)
cd frontend
npm install
npm run dev
```

## Project Structure

```
calmindra/
├── frontend/                 # Next.js React application
│   ├── app/                 # App router pages and API routes
│   ├── components/          # Reusable UI components
│   ├── contexts/            # React contexts for state management
│   └── hooks/              # Custom React hooks
├── backend/                 # FastAPI Python application
│   ├── app/
│   │   ├── routes/         # API route handlers
│   │   ├── services/       # Business logic services
│   │   └── main.py        # FastAPI application entry point
│   ├── Dockerfile          # Backend containerization
│   └── requirements.txt    # Python dependencies
├── docker-compose.yml      # Multi-service orchestration
└── start-*.sh             # Development automation scripts
```

## Development Status

### Completed Features
- Full-stack chat application with streaming responses
- Thread creation and management system
- Persistent conversation history
- Session-based memory retention
- Responsive UI with modern design patterns
- Docker containerization and development environment
- Integration with Ollama AI model

### Current Limitations
- Thread switching occasionally loses chat history
- Redis connection warnings (graceful fallback to memory storage)
- No persistent user authentication system

## Roadmap

### Phase 1: Database Integration (Current Priority)
**Neo4j Database Implementation**
- Set up Neo4j container in Docker Compose
- Design graph schema for users, threads, and messages
- Create comprehensive database models and relationships

**Backend Database Integration**
- Add Neo4j Python driver to requirements
- Implement database service layer
- Create thread and message persistence endpoints
- Add user management API endpoints

**Frontend Database Migration**
- Remove localStorage dependency
- Connect to backend for thread management
- Implement user authentication flow
- Add real-time thread synchronization

### Phase 2: Enhanced Features
**User Management System**
- User registration and authentication
- User profiles and preference management
- Multi-device conversation synchronization

**Advanced Thread Management**
- Thread search and filtering capabilities
- Thread categorization and tagging system
- Conversation history export functionality
- Thread sharing and collaboration features

**Analytics and Insights**
- Conversation analytics dashboard
- Mood tracking and trend analysis
- Progress visualization tools
- Usage statistics and reporting

### Phase 3: Production Readiness
**Security Enhancements**
- JWT-based authentication system
- Enhanced rate limiting mechanisms
- Input validation and sanitization
- HTTPS enforcement and security headers

**Performance Optimization**
- Database query optimization
- Caching strategy implementation
- CDN integration for static assets
- Load balancing configuration

**Monitoring and Observability**
- Application performance monitoring
- Error tracking and alerting
- Performance metrics collection
- Health check endpoints

## Configuration

### Environment Variables
```bash
# Backend Configuration
REDIS_URL=redis://localhost:6379
OLLAMA_URL=http://localhost:11434
BACKEND_URL=http://localhost:8000

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development Commands
```bash
# View application logs
docker-compose logs -f

# Reset database and containers
docker-compose down -v
docker-compose up -d

# Run backend tests
cd backend && python -m pytest

# Run frontend tests
cd frontend && npm test

# Build for production
docker-compose -f docker-compose.prod.yml build
```

## API Documentation

### Chat Endpoint
```
POST /chat/
Headers: X-Session-ID: <session_id>
Content-Type: application/json

Request Body:
{
  "user_message": "I've been feeling overwhelmed lately",
  "session_id": "session_123"
}
```

### Response Format
```json
{
  "bot_message": "I understand that feeling overwhelmed can be really challenging...",
  "session_id": "session_123",
  "timestamp": "2025-06-26T10:30:00Z"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with appropriate tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Calmindra** - Professional Mental Health Chatbot Solution
