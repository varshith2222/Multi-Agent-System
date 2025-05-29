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
├── agents/             # Specialized AI agents
│   ├── classifier.py   # Main classifier agent
│   ├── json_agent.py  # JSON processing agent
│   ├── email_agent.py # Email parsing agent
├── mcp/               # Master Control Program
│   ├── router.py     # Main routing logic
│   └── api.py        # FastAPI endpoints
├── memory/           # Memory management
│   └── store.py      # Memory implementation
├── data/             # Sample data files
├── utils/            # Helper functions
└── requirements.txt  # Dependencies
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

## License

MIT
"# multi-agent-system" 
