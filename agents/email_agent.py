from typing import Dict, Any
import re
from bs4 import BeautifulSoup
from datetime import datetime
from email import message_from_string
from email.utils import parseaddr

class EmailAgent:
    def __init__(self):
        self.urgency_keywords = {
            'high': ['urgent', 'asap', 'emergency', 'critical', 'immediate'],
            'medium': ['important', 'priority', 'attention', 'needed'],
            'low': ['when possible', 'fyi', 'update']
        }

    def extract(self, content: str) -> Dict[str, Any]:
        """
        Extract structured information from email content
        
        Args:
            content: Raw email content (plain text or HTML)
            
        Returns:
            Dict containing extracted email metadata and content
        """
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8')
                
            # Parse email message
            email_msg = message_from_string(content)
            
            # Extract basic metadata
            sender_name, sender_email = self._extract_sender(email_msg.get('From', ''))
            subject = email_msg.get('Subject', '')
            
            # Get email body
            body = self._get_email_body(email_msg)
            
            # Process content
            urgency = self._detect_urgency(subject + ' ' + body)
            intent = self._detect_intent(subject + ' ' + body)
            
            # Create CRM-style record
            record = {
                "success": True,
                "metadata": {
                    "sender": {
                        "name": sender_name,
                        "email": sender_email
                    },
                    "subject": subject,
                    "timestamp": email_msg.get('Date', datetime.now().isoformat()),
                    "urgency": urgency
                },
                "content": {
                    "intent": intent,
                    "body": body,
                    "key_points": self._extract_key_points(body),
                    "action_items": self._extract_action_items(body)
                },
                "processed_at": datetime.now().isoformat()
            }
            
            return record
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }

    def _extract_sender(self, from_header: str) -> tuple:
        """Extract sender name and email from From header"""
        name, email = parseaddr(from_header)
        if not name:
            name = email.split('@')[0]
        return name, email

    def _get_email_body(self, email_msg) -> str:
        """Extract email body, handling both plain text and HTML"""
        body = ""
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
                elif part.get_content_type() == "text/html":
                    html = part.get_payload(decode=True).decode()
                    body = BeautifulSoup(html, 'html.parser').get_text()
                    break
        else:
            body = email_msg.get_payload(decode=True).decode()
            
        return body.strip()

    def _detect_urgency(self, text: str) -> str:
        """Determine email urgency based on keywords"""
        text = text.lower()
        
        for level, keywords in self.urgency_keywords.items():
            if any(keyword in text for keyword in keywords):
                return level
        
        return 'normal'

    def _detect_intent(self, text: str) -> str:
        """Determine the primary intent of the email"""
        text = text.lower()
        
        # Simple rule-based intent detection
        if any(word in text for word in ['quote', 'pricing', 'cost']):
            return 'rfq'
        elif any(word in text for word in ['complaint', 'issue', 'problem']):
            return 'complaint'
        elif any(word in text for word in ['invoice', 'payment', 'bill']):
            return 'invoice'
        elif any(word in text for word in ['regulation', 'compliance', 'policy']):
            return 'regulation'
        
        return 'general'

    def _extract_key_points(self, text: str) -> list:
        """Extract key points from email body"""
        # Simple extraction of sentences with important markers
        key_points = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(marker in sentence.lower() for marker in 
                  ['important', 'key', 'must', 'need', 'require', 'critical']):
                key_points.append(sentence)
                
        return key_points

    def _extract_action_items(self, text: str) -> list:
        """Extract action items from email body"""
        action_items = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(marker in sentence.lower() for marker in 
                  ['please', 'could you', 'need to', 'action required', 'todo']):
                action_items.append(sentence)
                
        return action_items
