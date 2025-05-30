from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import uuid
from pathlib import Path
import sys
import os
import json
from datetime import datetime


# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.classifier import ClassifierAgent
from agents.json_agent import JSONAgent
from agents.email_agent import EmailAgent
from agents.pdf_agent import PDFAgent
from memory.store import MemoryStore
from mcp.action_router import ActionRouter

app = FastAPI(
    title="Multi-Agent Document Processor",
    description="An intelligent system for processing various document formats",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
classifier = ClassifierAgent()
json_agent = JSONAgent()
email_agent = EmailAgent()
pdf_agent = PDFAgent()
memory = MemoryStore()
action_router = ActionRouter()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    print("Serving index.html")
    try:
        response = templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "supported_formats": ["JSON", "Email", "PDF"],
                "supported_intents": ["Invoice", "RFQ", "Complaint", "Regulation", "Fraud Risk"]
            }
        )
        print("Template response created successfully")
        return response
    except Exception as e:
        print(f"Error serving template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload")

async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(None)
) -> JSONResponse:
    try:
        # Generate conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        
        # Store initial metadata
        memory.add_conversation(conversation_id, {
            "filename": file.filename,
            "content_type": file.content_type,
            "description": description,
            "size": len(content),
            "upload_time": datetime.now().isoformat()
        })
        
        # Classify document
        classification = classifier.classify(content)
        memory.update_conversation(conversation_id, {
            "classification": classification
        })
        
        # Route to appropriate agent
        target_agent = classifier.get_target_agent(classification)
        result = None
        
        # Process with appropriate agent
        if target_agent == "json_agent":
            result = json_agent.extract(content, classification["intent"])
        elif target_agent == "email_agent":
            result = email_agent.extract(content)
        elif target_agent == "pdf_agent":
            result = pdf_agent.extract(content)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {classification['format']}")
        
        if result:
            memory.update_conversation(conversation_id, {
                "extraction": result
            })
            
            # Route to follow-up actions
            actions = action_router.route_action(result, classification)
            memory.update_conversation(conversation_id, {
                "actions": actions
            })
        
        return JSONResponse({
            "success": True,
            "conversation_id": conversation_id,
            "classification": classification,
            "result": result,
            "actions": actions if result else None,
            "processed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
        )

@app.get("/status/{conversation_id}")
async def get_status(conversation_id: str):
    conversation = memory.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
    return conversation

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    total_processed = len(memory._store)
    formats = {}
    intents = {}
    actions = {}
    
    for conv in memory._store.values():
        if "classification" in conv:
            fmt = conv["classification"].get("format")
            intent = conv["classification"].get("intent")
            if fmt:
                formats[fmt] = formats.get(fmt, 0) + 1
            if intent:
                intents[intent] = intents.get(intent, 0) + 1
        
        if "actions" in conv:
            for action in conv["actions"].get("actions", []):
                action_type = f"{action['service']}_{action['action']}"
                actions[action_type] = actions.get(action_type, 0) + 1
    
    return {
        "total_processed": total_processed,
        "format_distribution": formats,
        "intent_distribution": intents,
        "action_distribution": actions,
        "generated_at": datetime.now().isoformat()
    }
