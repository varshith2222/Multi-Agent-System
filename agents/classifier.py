from typing import Dict, Any, Tuple
import json
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO

from datetime import datetime

class ClassifierAgent:
    def __init__(self):
        self.format_detectors = {
            'json': self._is_json,
            'email': self._is_email,
            'pdf': self._is_pdf
        }
        
        # Enhanced intent detection with few-shot examples and weighted keywords
        self.intent_patterns = {
            'invoice': {
                'keywords': {
                    'high': ['invoice number:', 'amount due:', 'payment required', 'bill to:'],
                    'medium': ['invoice', 'payment', 'amount', 'due', 'bill'],
                    'low': ['total', 'cost', 'charge']
                },
                'examples': [
                    "Invoice #12345 for services rendered",
                    "Payment due by 30th April 2025",
                    "Bill to: ACME Corporation"
                ]
            },
            'rfq': {
                'keywords': {
                    'high': ['request for quote', 'rfq:', 'price quote needed', 'quotation required'],
                    'medium': ['quote', 'rfq', 'pricing', 'proposal', 'quotation'],
                    'low': ['cost estimate', 'price', 'budget']
                },
                'examples': [
                    "RFQ: Need pricing for 100 units",
                    "Requesting quotation for services",
                    "Please provide a price proposal"
                ]
            },
            'complaint': {
                'keywords': {
                    'high': ['formal complaint', 'dissatisfied with', 'poor service', 'unacceptable'],
                    'medium': ['complaint', 'issue', 'problem', 'dissatisfied', 'unhappy'],
                    'low': ['concerned', 'disappointed', 'fix', 'wrong']
                },
                'examples': [
                    "I am writing to complain about the service",
                    "This is unacceptable quality",
                    "Issues with recent order #12345"
                ]
            },
            'regulation': {
                'keywords': {
                    'high': ['gdpr compliance', 'regulatory requirement', 'legal obligation', 'compliance mandate'],
                    'medium': ['compliance', 'regulation', 'policy', 'requirement', 'law'],
                    'low': ['standard', 'guideline', 'rule', 'procedure']
                },
                'examples': [
                    "GDPR Compliance Report 2025",
                    "New regulatory requirements for Q2",
                    "Policy update regarding data protection"
                ]
            },
            'fraud_risk': {
                'keywords': {
                    'high': ['suspicious activity', 'fraud alert', 'unauthorized', 'security breach'],
                    'medium': ['fraud', 'risk', 'suspicious', 'unusual', 'breach'],
                    'low': ['verify', 'confirm', 'check', 'validate']
                },
                'examples': [
                    "Suspicious transaction alert",
                    "Potential fraud detected in account",
                    "Security incident report"
                ]
            }
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

    def _detect_intent(self, content: bytes) -> Dict[str, Any]:
        """Enhanced intent detection using few-shot examples and weighted keywords"""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8').lower()
            else:
                content = content.lower()
        except:
            content = str(content).lower()

        # Calculate scores for each intent
        intent_scores = {}
        for intent, pattern in self.intent_patterns.items():
            score = 0
            confidence = 0
            matches = []
            
            # Check keyword matches with weights
            for keyword in pattern['keywords']['high']:
                if keyword in content:
                    score += 3
                    matches.append(keyword)
                    
            for keyword in pattern['keywords']['medium']:
                if keyword in content:
                    score += 2
                    matches.append(keyword)
                    
            for keyword in pattern['keywords']['low']:
                if keyword in content:
                    score += 1
                    matches.append(keyword)
            
            # Compare with examples using simple similarity
            for example in pattern['examples']:
                example = example.lower()
                if any(word in content for word in example.split()):
                    score += 2
            
            # Calculate confidence
            max_possible_score = (
                len(pattern['keywords']['high']) * 3 +
                len(pattern['keywords']['medium']) * 2 +
                len(pattern['keywords']['low']) +
                len(pattern['examples']) * 2
            )
            confidence = (score / max_possible_score) if max_possible_score > 0 else 0
            
            intent_scores[intent] = {
                'score': score,
                'confidence': confidence,
                'matches': matches
            }
        
        # Get the highest scoring intent
        if not intent_scores:
            return {
                'intent': 'unknown',
                'confidence': 0,
                'matches': []
            }
            
        best_intent = max(intent_scores.items(), key=lambda x: x[1]['score'])
        
        return {
            'intent': best_intent[0],
            'confidence': best_intent[1]['confidence'],
            'matches': best_intent[1]['matches']
        }

    def classify(self, content: bytes) -> Dict[str, Any]:
        """Enhanced classification with confidence scores and pattern matching.
        Returns a dict containing format and intent information.
        """
        # Detect format with retry
        try:
            doc_format = self._detect_format(content)
        except ValueError:
            # If format detection fails, default to unknown
            doc_format = 'unknown'
        
        # Enhanced intent detection
        intent_result = self._detect_intent(content)
        
        # Additional metadata
        metadata = {
            'size': len(content),
            'timestamp': datetime.now().isoformat(),
            'format_details': self._get_format_details(content, doc_format)
        }
        
        return {
            'format': doc_format,
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'matches': intent_result['matches'],
            'metadata': metadata
        }

    def _get_format_details(self, content: bytes, doc_format: str) -> Dict[str, Any]:
        """Get additional format-specific details about the content"""
        details = {}
        
        if doc_format == 'json':
            try:
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                data = json.loads(content)
                details['keys'] = list(data.keys())
                details['is_array'] = isinstance(data, list)
            except:
                details['parse_error'] = True
        
        elif doc_format == 'email':
            try:
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                lines = content.split('\n')
                for line in lines[:10]:  # Check first 10 lines for headers
                    if line.startswith('Subject:'):
                        details['subject'] = line[8:].strip()
                    elif line.startswith('From:'):
                        details['from'] = line[5:].strip()
                    elif line.startswith('To:'):
                        details['to'] = line[3:].strip()
            except:
                details['parse_error'] = True
        
        elif doc_format == 'pdf':
            try:
                pdf = PyPDF2.PdfReader(BytesIO(content))
                details['pages'] = len(pdf.pages)
                if pdf.metadata:
                    details['metadata'] = dict(pdf.metadata)
            except:
                details['parse_error'] = True
        
        return details

    def get_target_agent(self, classification: Dict[str, str]) -> str:
        """Determine which agent should handle this document"""
        format_to_agent = {
            'json': 'json_agent',
            'email': 'email_agent',
            'pdf': 'pdf_agent'
        }
        return format_to_agent.get(classification['format'], 'unknown_agent')
