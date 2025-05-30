# 🤖 Multi-Agent AI System

An intelligent document processing system that classifies and extracts information from multiple input formats using specialized agents.

---

## ✨ Features

- 📄 Supports **PDF**, **JSON**, and **Email** input formats  
- 🧠 Intelligent **classification and routing**  
- 🤹 Specialized **extraction agents**  
- 🧬 Shared **memory system** for context preservation  
- ⚡ Built with **Python**, **FastAPI**, and **LangChain**  

---

## 🗂️ Project Structure

```
/multi-agent-system
multi agent system/
├── memory_store.json
├── README.md
├── requirements.txt
├── agents/
│   ├── classifier.py
│   ├── email_agent.py
│   ├── json_agent.py
│   └── pdf_agent.py
├── data/
│   ├── sample_email.txt
│   ├── sample_invoice.json
│   └── sample_policy.txt
├── mcp/
│   ├── action_router.py
│   └── api.py
├── memory/
│   └── store.py
├── static/
│   ├── app.js
│   └── styles.css
└── templates/
    ├── agent_flow.html
    └── index.html
```

## ⚙️ Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate


2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
    cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

Run the FastAPI server:
```bash
uvicorn mcp.api:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

- `POST /process`: Process any input document
- `GET /memory/{conversation_id}`: Retrieve processing history
"# multi-agent-system" 
"# Multi-Agent-System" 
