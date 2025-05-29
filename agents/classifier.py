from typing import Dict, Any, Tuple
import json
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO

class ClassifierAgent:
    def __init__(self):
        self.format_detectors = {
            'json': self._is_json,
            'email': self._is_email,
            'pdf': self._is_pdf
        }
        
        self.intent_keywords = {
            'invoice': ['invoice', 'payment', 'amount', 'due', 'bill'],
            'rfq': ['quote', 'rfq', 'pricing', 'proposal', 'quotation'],
            'complaint': ['complaint', 'issue', 'problem', 'dissatisfied', 'unhappy'],
            'regulation': ['compliance', 'regulation', 'policy', 'requirement', 'law']
        }

    def _is_json(self, content: bytes) -> bool:
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            json.loads(content)
            return True
        except:
            return False

    def _is_email(self, content: bytes) -> bool:
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            # Basic email structure check
            return ('From:' in content or 'Subject:' in content) and '@' in content
        except:
            return False

    def _is_pdf(self, content: bytes) -> bool:
        try:
            PyPDF2.PdfReader(BytesIO(content))
            return True
        except:
            return False

    def _detect_format(self, content: bytes) -> str:
        for fmt, detector in self.format_detectors.items():
            if detector(content):
                return fmt
        raise ValueError("Unknown format")

    def _detect_intent(self, content: bytes) -> str:
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8').lower()
            else:
                content = content.lower()
        except:
            content = str(content).lower()

        # Count keyword matches for each intent
        intent_scores = {
            intent: sum(1 for keyword in keywords if keyword in content)
            for intent, keywords in self.intent_keywords.items()
        }
        
        # Return the intent with highest score, default to 'unknown'
        max_score = max(intent_scores.values())
        if max_score > 0:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        return 'unknown'

    def classify(self, content: bytes) -> Dict[str, Any]:
        """
        Classify the input content format and intent
        
        Returns:
            Dict containing format and intent
        """
        doc_format = self._detect_format(content)
        doc_intent = self._detect_intent(content)
        
        return {
            "format": doc_format,
            "intent": doc_intent,
            "confidence": 0.85  # Placeholder for actual confidence scoring
        }

    def get_target_agent(self, classification: Dict[str, str]) -> str:
        """Determine which agent should handle this document"""
        format_to_agent = {
            'json': 'json_agent',
            'email': 'email_agent',
            'pdf': 'pdf_agent'  # Future extension
        }
        return format_to_agent.get(classification['format'], 'unknown_agent')
