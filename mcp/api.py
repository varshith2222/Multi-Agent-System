from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import uuid
from pathlib import Path
import sys
import os

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.classifier import ClassifierAgent
from agents.json_agent import JSONAgent
from agents.email_agent import EmailAgent
from memory.store import MemoryStore

app = FastAPI(title="Multi-Agent Document Processor")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize agents and memory store
classifier = ClassifierAgent()
json_agent = JSONAgent()
email_agent = EmailAgent()
memory = MemoryStore()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(None)
):
    # Generate conversation ID
    conversation_id = str(uuid.uuid4())
    
    # Read file content
    content = await file.read()
    
    # Store initial metadata
    memory.add_conversation(conversation_id, {
        "filename": file.filename,
        "content_type": file.content_type,
        "description": description
    })
    
    # Classify document
    classification = classifier.classify(content)
    memory.update_conversation(conversation_id, {
        "classification": classification
    })
    
    # Route to appropriate agent
    target_agent = classifier.get_target_agent(classification)
    result = None
    
    if target_agent == "json_agent":
        result = json_agent.extract(content, classification["intent"])
    elif target_agent == "email_agent":
        result = email_agent.extract(content)
    
    if result:
        memory.update_conversation(conversation_id, {
            "extraction": result
        })
    
    return {
        "conversation_id": conversation_id,
        "classification": classification,
        "result": result
    }

@app.get("/status/{conversation_id}")
async def get_status(conversation_id: str):
    return memory.get_conversation(conversation_id)
