from typing import Dict, Any, List
import PyPDF2
from io import BytesIO
import re
from datetime import datetime

import json

class PDFAgent:
    def __init__(self):
        self.compliance_keywords = {
            'gdpr': ['gdpr', 'data protection', 'privacy', 'personal data'],
            'fda': ['fda', 'food and drug', 'medical device', 'pharmaceutical'],
            'hipaa': ['hipaa', 'health insurance', 'medical privacy'],
            'pci': ['pci dss', 'payment card', 'credit card security']
        }
        
        self.invoice_fields = [
            'invoice number',
            'date',
            'due date',
            'total',
            'subtotal',
            'tax'
        ]

    def extract(self, content: bytes) -> Dict[str, Any]:
        """
        Extract and analyze content from PDF
        """
        try:
            # Parse PDF using PyPDF2
            full_text = self._extract_text_pypdf2(content)
            
            # Detect document type
            is_invoice = self._is_invoice(full_text)
            
            if is_invoice:
                result = self._process_invoice(full_text)
            else:
                result = self._process_policy(full_text)
            
            # Add basic metadata
            result['metadata'] = {
                'pages': len(PyPDF2.PdfReader(BytesIO(content)).pages),
                'size': len(content)
            }
            
            return {
                "success": True,
                "data": result,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }

    def _extract_text_pypdf2(self, content: bytes) -> str:
        """Extract text using PyPDF2"""
        pdf = PyPDF2.PdfReader(BytesIO(content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text

    def _is_invoice(self, text: str) -> bool:
        """Determine if the document is an invoice"""
        invoice_indicators = ['invoice', 'bill to', 'payment due', 'total amount']
        text = text.lower()
        return any(indicator in text for indicator in invoice_indicators)

    def _process_invoice(self, text: str) -> Dict[str, Any]:
        """Process invoice-specific content"""
        result = {
            "type": "invoice",
            "extracted_fields": {},
            "line_items": [],
            "flags": []
        }
        
        # Extract invoice fields
        for field in self.invoice_fields:
            pattern = f"{field}[:\s]+([\d,.]+)"
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                value = match.group(1).replace(',', '')
                try:
                    value = float(value)
                    result["extracted_fields"][field] = value
                except ValueError:
                    continue
        
        # Extract line items (simple pattern matching)
        lines = text.split('\n')
        for line in lines:
            if re.search(r'\d+\s+[\w\s]+\s+[\d,.]+\s+[\d,.]+', line):
                result["line_items"].append(line.strip())
        
        # Check for high-value invoice
        total = result["extracted_fields"].get("total", 0)
        if total > 10000:
            result["flags"].append({
                "type": "high_value",
                "message": f"Invoice total (${total:,.2f}) exceeds $10,000",
                "severity": "high"
            })
        
        return result

    def _process_policy(self, text: str) -> Dict[str, Any]:
        """Process policy document content"""
        text = text.lower()
        result = {
            "type": "policy",
            "compliance_flags": [],
            "key_sections": []
        }
        
        # Check for compliance keywords
        for category, keywords in self.compliance_keywords.items():
            matches = []
            for keyword in keywords:
                if keyword in text:
                    # Get surrounding context
                    pattern = f".{{0,100}}{keyword}.{{0,100}}"
                    for match in re.finditer(pattern, text):
                        matches.append(match.group(0))
            
            if matches:
                result["compliance_flags"].append({
                    "category": category,
                    "matches": matches,
                    "severity": "high" if category in ["gdpr", "hipaa"] else "medium"
                })
        
        # Extract key sections (headers and their content)
        lines = text.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            if re.match(r'^[A-Z\s]{5,}:?$', line):  # Possible header
                if current_section:
                    result["key_sections"].append({
                        "title": current_section,
                        "content": ' '.join(section_content)
                    })
                current_section = line.strip()
                section_content = []
            elif current_section:
                section_content.append(line.strip())
        
        return result
