from typing import Dict, Any, List
import json
from datetime import datetime

class JSONAgent:
    def __init__(self):
        self.required_fields = {
            'invoice': ['invoice_number', 'amount', 'due_date'],
            'rfq': ['product', 'quantity', 'delivery_date'],
            'complaint': ['issue', 'severity', 'customer_id'],
            'regulation': ['policy_id', 'effective_date', 'requirements']
        }

    def extract(self, content: str, intent: str) -> Dict[str, Any]:
        """
        Extract and validate JSON content based on intent
        
        Args:
            content: JSON string
            intent: Document intent (invoice, rfq, etc.)
            
        Returns:
            Dict containing extracted data and validation results
        """
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            data = json.loads(content)
            
            # Convert to FlowBit schema
            formatted_data = self._format_data(data, intent)
            
            # Validate required fields
            missing_fields = self._validate_required_fields(formatted_data, intent)
            
            # Check for anomalies
            anomalies = self._detect_anomalies(formatted_data)
            
            return {
                "success": True,
                "data": formatted_data,
                "missing_fields": missing_fields,
                "anomalies": anomalies,
                "processed_at": datetime.now().isoformat()
            }
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON format",
                "processed_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }

    def _format_data(self, data: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """Format raw JSON data into standardized FlowBit schema"""
        formatted = {
            "metadata": {
                "intent": intent,
                "source": "json_agent",
                "version": "1.0"
            },
            "content": {}
        }

        # Map fields based on intent
        if intent == "invoice":
            formatted["content"] = {
                "invoice_number": data.get("invoice_number") or data.get("id"),
                "amount": float(data.get("amount", 0)),
                "due_date": data.get("due_date"),
                "currency": data.get("currency", "USD"),
                "line_items": data.get("items", [])
            }
        elif intent == "rfq":
            formatted["content"] = {
                "request_id": data.get("id") or data.get("request_id"),
                "product": data.get("product"),
                "quantity": int(data.get("quantity", 0)),
                "delivery_date": data.get("delivery_date"),
                "specifications": data.get("specs", {})
            }
        
        return formatted

    def _validate_required_fields(self, data: Dict[str, Any], intent: str) -> List[str]:
        """Check for missing required fields based on intent"""
        required = self.required_fields.get(intent, [])
        content = data.get("content", {})
        return [field for field in required if not content.get(field)]

    def _detect_anomalies(self, data: Dict[str, Any]) -> List[str]:
        """Detect potential anomalies in the data"""
        anomalies = []
        content = data.get("content", {})
        
        # Example anomaly checks
        if "amount" in content and content["amount"] < 0:
            anomalies.append("Negative amount detected")
        
        if "quantity" in content and content["quantity"] <= 0:
            anomalies.append("Invalid quantity")
            
        return anomalies
