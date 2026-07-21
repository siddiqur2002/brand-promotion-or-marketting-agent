# 🚀 AI-Powered Brand Promotion & Marketing Agent

An advanced full-stack application leveraging Multi-Agent AI systems (**CrewAI**) to automate brand research, market analysis, and ad copywriting, powered by **FastAPI** and **Celery** for asynchronous task execution.

---

## 🛠️ Tech Stack

### **Backend:**
* **FastAPI** - High-performance Python web framework for building APIs.
* **Celery** - Distributed task queue for managing long-running AI background operations.
* **CrewAI** - Framework for orchestrating role-playing autonomous AI agents.
* **Upstash Redis (Serverless)** - Message broker and result backend with SSL support (`rediss://`).

### **Frontend:**
* Modern Web Frontend (React / Vite / Next.js) for user interaction and campaign tracking.

---

## 📁 Project Structure

```text
brand-promotion-or-marketting-agent/
├── backend/                # FastAPI application & Celery workers
│   ├── app/
│   │   ├── config/         # Settings & configurations
│   │   ├── workers/        # Celery app & background tasks
│   │   └── db/             # Database sessions & models
│   ├── requirements.txt    # Python dependencies
│   └── main.py             # FastAPI entry point
├── frontend/               # Frontend user interface
│   ├── src/
│   └── package.json        # Node.js dependencies
├── .gitignore              # Git ignored files
└── README.md               # Project documentation
⚙️ Environment Variables
Create a .env file in your backend/root directory based on the following template:

Code snippet
# FastAPI Settings
PORT=8000

# Celery & Upstash Redis Configuration (Serverless SSL)
CELERY_BROKER_URL="rediss://default:your_password@your-redis-url.upstash.io:6379/0?ssl_cert_reqs=none"
CELERY_RESULT_BACKEND="rediss://default:your_password@your-redis-url.upstash.io:6379/0?ssl_cert_reqs=none"

# AI API Keys (e.g., OpenAI / Gemini)
OPENAI_API_KEY="your-api-key-here"
🚀 Installation & Setup Guide
1. Clone the Repository
Bash
git clone [https://github.com/your-username/brand-promotion-or-marketting-agent.git](https://github.com/your-username/brand-promotion-or-marketting-agent.git)
cd brand-promotion-or-marketting-agent
2. Backend Setup
Bash
# Navigate to backend directory (or create venv in root if unified)
cd backend  # (or skip if your setup is in root)

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
3. Run Celery Worker (For AI Tasks)
Open a separate terminal window, activate your virtual environment, and start the Celery worker:

Bash
celery -A app.workers.celery_app.celery worker --loglevel=info --pool=solo
4. Run FastAPI Backend Server
Open another terminal window, activate the virtual environment, and start the API:

Bash
uvicorn app.main:app --reload
5. Frontend Setup
Open a new terminal for the frontend:

Bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
📌 Features & Optimizations  
Secure Redis SSL Handling: Seamless connection with Upstash Serverless Redis using custom SSL parameters.  

Robust Celery Configuration: Features task_acks_late=True, worker_prefetch_multiplier=1, and task_track_started=True for reliable handling of heavy AI processes.

Multi-Agent Collaboration: Integrates Market Research Analysts and Creative Copywriters to generate automated marketing insights.
