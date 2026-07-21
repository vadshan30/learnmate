# LearnMate AI

An AI-powered personalized learning coach that helps students choose customized course pathways based on their interests, skills, and career goals. Powered by **Google Gemini AI**, ChromaDB vector databases, and Retrieval-Augmented Generation (RAG) pipelines.

## Features

- **Student Profile Management** – Create and update personalized learner profiles
- **AI Skill Gap Analysis** – Compare current skills against career requirements
- **Personalized Learning Roadmap** – 10-week plans with courses, projects, and certifications
- **AI Mentor Chat** – RAG-powered learning assistant using Google Gemini
- **Quiz Generator** – AI-powered quizzes with multiple-choice questions
- **Flashcard Generator** – Study flashcards for effective revision
- **Study Planner** – Personalized daily study plans
- **Career Advice** – AI-guided career pathway recommendations
- **Interview Preparation** – Mock interview questions with sample answers
- **Resume Review** – AI-powered resume feedback
- **Coding Challenges** – Personalized coding challenges by skill level
- **Learning Tips** – Evidence-based learning strategies
- **Progress Tracker** – Dynamic updates as topics are completed
- **Streaming Responses** – Real-time token-by-token AI responses
- **Chat History** – Persistent conversation memory across sessions

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ChatGPT-style UI │ Markdown │ Code Blocks │ Streaming  │
└───────────────────────┬─────────────────────────────────┘
                        │ REST API + SSE
┌───────────────────────┴─────────────────────────────────┐
│                  Backend (FastAPI)                        │
│                                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Mentor   │  │   Gemini     │  │  RAG Pipeline     │  │
│  │  Service  │──│   Service    │  │  (ChromaDB +      │  │
│  │          │  │              │  │   SentenceTrans.)  │  │
│  └────┬─────┘  └──────┬───────┘  └────────┬─────────┘  │
│       │               │                    │             │
│  ┌────┴───────────────┴────────────────────┴─────────┐  │
│  │              Prompt Templates                      │  │
│  │  mentor │ career │ quiz │ roadmap │ revision        │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐      │
│  │  Student  │  │ Roadmap  │  │  Skill Gap        │      │
│  │  Profile  │  │ Generator│  │  Analyzer         │      │
│  └──────────┘  └──────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI |
| Data Models | Pydantic v2 |
| LLM | Google Gemini 2.0 Flash |
| Vector DB | ChromaDB (persistent) |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| Frontend | React 19, Vite, Tailwind CSS |
| Animations | Framer Motion |
| Markdown | react-markdown + remark-gfm |

## Environment Variables

### Backend (.env)

```env
# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Embedding model
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# Vector database
CHROMA_DB_PATH=./data/chroma_db

# Application
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=LearnMate AI
```

## Folder Structure

```
learnmate-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat_routes.py         # Legacy chat endpoints
│   │   │   ├── mentor_routes.py       # AI mentor endpoints (chat, quiz, etc.)
│   │   │   ├── health_routes.py       # Health check
│   │   │   ├── student_routes.py      # Student CRUD
│   │   │   ├── roadmap_routes.py      # Roadmap generation & progress
│   │   │   ├── resource_routes.py     # Learning resources
│   │   │   ├── search_routes.py       # Semantic search
│   │   │   ├── rag_routes.py          # RAG management
│   │   │   └── project_routes.py      # Project details
│   │   ├── models/
│   │   │   ├── student.py             # StudentProfile model
│   │   │   └── roadmap.py             # Course, Project, Certification models
│   │   ├── schemas/
│   │   │   ├── requests.py            # Pydantic request schemas
│   │   │   └── responses.py           # Pydantic response schemas
│   │   ├── services/
│   │   │   ├── gemini_service.py      # Google Gemini API wrapper
│   │   │   ├── mentor_service.py      # AI mentor orchestration
│   │   │   ├── rag_service.py         # ChromaDB RAG pipeline
│   │   │   ├── skill_analyzer.py      # Skill gap analysis
│   │   │   ├── roadmap_generator.py   # Roadmap generation
│   │   │   ├── prompts/
│   │   │   │   ├── mentor_prompt.py   # Mentor chat prompts
│   │   │   │   ├── career_prompt.py   # Career advice prompts
│   │   │   │   ├── quiz_prompt.py     # Quiz generation prompts
│   │   │   │   ├── roadmap_prompt.py  # Roadmap/study plan prompts
│   │   │   │   └── revision_prompt.py # Revision/feedback prompts
│   │   │   └── resource_service.py    # JSON dataset queries
│   │   ├── utils/
│   │   │   └── data_loader.py         # JSON file loading
│   │   └── dependencies.py            # DI container & Store
│   ├── data/
│   │   └── chroma_db/                 # Persistent vector database
│   ├── .env                           # Environment configuration
│   ├── requirements.txt               # Python dependencies
│   └── main.py                        # FastAPI entry point
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Chat.jsx               # Modern ChatGPT-style UI
│   │   ├── context/
│   │   │   ├── AppContext.jsx          # Global state management
│   │   │   └── ThemeContext.jsx        # Dark/light mode
│   │   ├── services/
│   │   │   └── api.js                 # API client (REST + SSE)
│   │   └── components/                # Reusable UI components
│   └── package.json
├── data/
│   ├── courses.json                   # 17+ courses across 10+ domains
│   ├── projects.json                  # 12 portfolio projects
│   ├── certifications.json            # 9 industry certifications
│   └── career_pathways.json           # 5 career pathways
├── docker-compose.yml
└── README.md
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend)
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
- Docker & Docker Compose (optional)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-username/learnmate-ai.git
cd learnmate-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_key_here

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker-compose up --build
```

## API Documentation

Once running, access the interactive docs:

| Documentation | URL |
|--------------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

## API Endpoints

### Mentor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/mentor/chat` | Chat with AI mentor |
| POST | `/api/mentor/chat/stream` | Stream mentor response (SSE) |
| POST | `/api/mentor/explain` | Explain a concept |
| POST | `/api/mentor/quiz` | Generate a quiz |
| POST | `/api/mentor/flashcards` | Generate flashcards |
| POST | `/api/mentor/study-plan` | Generate a study plan |
| POST | `/api/mentor/revise` | Get revision help |
| POST | `/api/mentor/career` | Get career advice |
| POST | `/api/mentor/coding-challenge` | Generate coding challenge |
| POST | `/api/mentor/resume-review` | Review a resume |
| POST | `/api/mentor/interview-prep` | Interview preparation |
| POST | `/api/mentor/learning-tips` | Get learning tips |
| GET | `/api/mentor/history/{id}` | Get chat history |
| DELETE | `/api/mentor/history/{id}` | Clear chat history |

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| POST | `/api/student` | Create student profile |
| GET | `/api/student/{id}` | Get student profile |
| PUT | `/api/student/{id}` | Update student profile |
| POST | `/api/roadmap` | Generate learning roadmap |
| GET | `/api/roadmap/{id}` | Get roadmap |
| POST | `/api/roadmap/topic/complete` | Mark topic complete |
| GET | `/api/resources/courses` | List courses |
| GET | `/api/search` | Semantic search |
| POST | `/api/rag/reload` | Reload RAG data |

## Demo Workflow

1. **Create a Profile** – Set your name, skills, interests, and career goal
2. **Generate a Roadmap** – Get a personalized 10-week learning plan
3. **Start Learning** – Follow the roadmap and mark topics complete
4. **Chat with AI Mentor** – Ask questions, get explanations, career advice
5. **Take Quizzes** – Test your knowledge with AI-generated quizzes
6. **Track Progress** – View your learning analytics and weekly feedback
7. **Prepare for Careers** – Get interview prep, resume reviews, and career guidance

## License

This project is for educational purposes as part of the EDUNET Agentic AI program.
