# LearnMate AI

An AI-powered personalized learning coach that helps students choose customized course pathways based on their interests, skills, and career goals. Powered by IBM Granite LLM, ChromaDB/FAISS vector databases, and RAG pipelines.

## Features

- **Student Profile Management** – Create and update personalized learner profiles
- **AI Skill Gap Analysis** – Compare current skills against career requirements
- **Personalized Learning Roadmap** – 10-week plans with courses, projects, and certifications
- **AI Mentor Chat** – RAG-powered learning assistant using IBM Granite
- **Progress Tracker** – Dynamic updates as topics are completed

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI |
| Data Models | Pydantic v2 |
| LLM | IBM Granite via Watsonx.ai |
| Vector DB | ChromaDB / FAISS |
| Hosting | IBM Cloud Lite |
| Frontend | React (future phase) |

## Folder Structure

```
learnmate-ai/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── student.py          # StudentProfile model
│   │   │   ├── roadmap.py          # Course, Project, Certification, Roadmap models
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── .env
│   └── main.py                     # FastAPI entry point
├── frontend/
│   └── src/
├── data/
│   ├── courses.json                # 17 courses across 10 domains
│   ├── career_pathways.json        # 5 career pathways
│   ├── certifications.json         # 9 industry certifications
│   └── projects.json              # 12 portfolio projects
├── docker-compose.yml
├── README.md
└── .gitignore
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip
- Docker & Docker Compose (optional)

### Local Setup

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
cp .env.example .env   # if .env.example exists, or edit .env directly
# Update .env with your IBM API key and project ID

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
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

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| POST | `/api/profile` | Create/update student profile |
| GET | `/api/profile/{name}` | Get student profile by name |
| GET | `/api/courses` | List all courses |
| GET | `/api/courses/{course_id}` | Get course by ID |
| GET | `/api/certifications` | List all certifications |
| GET | `/api/projects` | List all projects |

## Future Roadmap

- **Phase 2** – Skill gap analysis engine and roadmap generation with IBM Granite
- **Phase 3** – RAG pipeline with ChromaDB/FAISS and AI Mentor Chat
- **Phase 4** – Progress tracking and dynamic roadmap updates
- **Phase 5** – React frontend with responsive UI
- **Phase 6** – IBM Cloud Lite deployment and CI/CD

## License

This project is for educational purposes as part of the EDUNET Agentic AI program.
