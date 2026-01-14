# AI Support Automation Sales Bot

**AI Sales Bot** is a FastAPI-based solution designed to engage website visitors, detect buying intent, and notify human sales or support teams via email. It features a lightweight frontend with Tailwind CSS, making it easy to embed on websites and quickly deploy for clients.

---

## Features

- AI-powered chat interface for website visitors
- Detects buying intent or lead qualification
- Automatic email notifications to human agents
- Lightweight, responsive frontend (Tailwind CSS)
- PostgreSQL backend for chat and lead storage
- Easy to extend with WhatsApp, Slack, or CRM integrations
- Modular architecture for scalability

---

## Tech Stack

- **Backend:** FastAPI, Python  
- **Database:** PostgreSQL  
- **Frontend:** Tailwind CSS, HTML, minimal JS  
- **Email Notifications:** SMTP (Gmail/Other)  
- **AI Integration:** OpenAI GPT-4-turbo (or Gemini)  
- **Optional Scalability:** Redis, Celery, Vector DB for advanced workflows  

---

## Installation

### 1. Clone the repository
```
git clone https://github.com/aijazahmed-dev/ai-sales-bot.git
cd ai-sales-bot
```
### 2. Create a virtual environment
```
python -m venv aibot_env
```
### 3. Activate the virtual environment
```
Windows PowerShell
.\aibot_env\Scripts\Activate.ps1

Linux / macOS
source aibot_env/bin/activate
```
### 4. Install dependencies
```
pip install -r requirements.txt
```

### 5. Setup environment variables

Create a .env file in the project root:
```
DATABASE_URL=postgresql://user:password@localhost:5432/aibot
LLM_API_KEY=your_openai_api_key
SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_email_password
```
## Running the Project
```
uvicorn app.main:app --reload
Open your browser at http://127.0.0.1:8000
```
## Project Structure
```
ai_sales_bot/
├── app/
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Environment & API configs
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # LLM, intent detection, notifications
│   ├── routers/           # API routes
│   └── utils/             # Helper functions
├── static/                # Frontend assets (CSS, JS, images)
├── templates/             # HTML templates (chat widget, admin)
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (ignored)
└── Dockerfile             # Optional Docker setup
```
## Future Enhancements

- Add WhatsApp / Slack / CRM integration
- Redis + Celery for async notifications and task management
- Vector DB for long-term memory and document-based responses
- LangChain for multi-step AI workflows

## License

This project is licensed under the MIT License.


