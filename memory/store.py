from typing import Dict, Any, Optional
import json
from datetime import datetime
import os
from pathlib import Path

class MemoryStore:
    def __init__(self, storage_path: str = "memory_store.json"):
        self.storage_path = storage_path
        self._store = self._load_store()

    def _load_store(self) -> Dict:
        """Load the memory store from disk if it exists"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_store(self):
        """Save the current memory store to disk"""
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self._store, f, indent=2)

    def add_conversation(self, conversation_id: str, metadata: Dict[str, Any]):
        """Create a new conversation entry"""
        self._store[conversation_id] = {
            "metadata": metadata,
            "history": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self._save_store()

    def update_conversation(self, conversation_id: str, agent_output: Dict[str, Any]):
        """Add new agent output to conversation history"""
        if conversation_id not in self._store:
            raise KeyError(f"Conversation {conversation_id} not found")
        
        self._store[conversation_id]["history"].append({
            "timestamp": datetime.now().isoformat(),
            "agent_output": agent_output
        })
        self._store[conversation_id]["last_updated"] = datetime.now().isoformat()
        self._save_store()

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a conversation by ID"""
        return self._store.get(conversation_id)

    def get_latest_agent_output(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent agent output for a conversation"""
        conv = self.get_conversation(conversation_id)
        if conv and conv["history"]:
            return conv["history"][-1]["agent_output"]
        return None
