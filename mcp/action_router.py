from typing import Dict, Any, List
import requests
from datetime import datetime

import json
import logging

class ActionRouter:
    def __init__(self):
        self.endpoints = {
            'crm': 'http://localhost:8001/crm',
            'risk': 'http://localhost:8001/risk',
            'compliance': 'http://localhost:8001/compliance',
            'finance': 'http://localhost:8001/finance'
        }
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def route_action(self, agent_output: Dict[str, Any], classification: Dict[str, str]) -> Dict[str, Any]:
        """
        Route the agent output to appropriate follow-up actions
        """
        actions_taken = []
        
        try:
            # Route based on document format and intent
            if classification['format'] == 'email':
                actions_taken.extend(self._handle_email_actions(agent_output))
            elif classification['format'] == 'json':
                actions_taken.extend(self._handle_json_actions(agent_output))
            elif classification['format'] == 'pdf':
                actions_taken.extend(self._handle_pdf_actions(agent_output))
            
            return {
                "success": True,
                "actions": actions_taken,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Action routing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _handle_email_actions(self, agent_output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle email-specific actions"""
        actions = []
        
        if not agent_output.get('success', False):
            return actions
            
        data = agent_output.get('data', {})
        metadata = data.get('metadata', {})
        content = data.get('content', {})
        
        # Check urgency and tone
        urgency = metadata.get('urgency', 'normal')
        tone = content.get('tone', 'neutral')
        
        # Handle high urgency or negative tone
        if urgency == 'high' or tone in ['angry', 'threatening']:
            action = self._simulate_api_call(
                'crm',
                'escalate',
                {
                    'sender': metadata.get('sender', {}),
                    'urgency': urgency,
                    'tone': tone,
                    'content': content
                }
            )
            actions.append(action)
        
        # Handle complaints
        if content.get('intent') == 'complaint':
            action = self._simulate_api_call(
                'crm',
                'create_ticket',
                {
                    'type': 'complaint',
                    'priority': 'high' if urgency == 'high' else 'medium',
                    'content': content
                }
            )
            actions.append(action)
        
        return actions

    def _handle_json_actions(self, agent_output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle JSON-specific actions"""
        actions = []
        
        if not agent_output.get('success', False):
            return actions
            
        data = agent_output.get('data', {})
        
        # Handle anomalies
        if data.get('anomalies'):
            action = self._simulate_api_call(
                'risk',
                'report_anomaly',
                {
                    'anomalies': data['anomalies'],
                    'source_data': data.get('content', {})
                }
            )
            actions.append(action)
        
        # Handle missing required fields
        if data.get('missing_fields'):
            action = self._simulate_api_call(
                'risk',
                'validation_error',
                {
                    'missing_fields': data['missing_fields'],
                    'source_data': data.get('content', {})
                }
            )
            actions.append(action)
        
        return actions

    def _handle_pdf_actions(self, agent_output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle PDF-specific actions"""
        actions = []
        
        if not agent_output.get('success', False):
            return actions
            
        data = agent_output.get('data', {})
        
        # Handle high-value invoices
        if data.get('type') == 'invoice':
            total = data.get('extracted_fields', {}).get('total', 0)
            if total > 10000:
                action = self._simulate_api_call(
                    'finance',
                    'high_value_review',
                    {
                        'invoice_total': total,
                        'invoice_data': data['extracted_fields']
                    }
                )
                actions.append(action)
        
        # Handle compliance flags
        if data.get('compliance_flags'):
            for flag in data['compliance_flags']:
                if flag['severity'] == 'high':
                    action = self._simulate_api_call(
                        'compliance',
                        'review_required',
                        {
                            'category': flag['category'],
                            'matches': flag['matches']
                        }
                    )
                    actions.append(action)
        
        return actions

    def _simulate_api_call(self, service: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate an API call to external service
        In production, this would make real API calls
        """
        endpoint = self.endpoints.get(service)
        if not endpoint:
            raise ValueError(f"Unknown service: {service}")
            
        # Log the action
        self.logger.info(f"Simulating {action} call to {service}")
        self.logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Simulate API response
        response = {
            "service": service,
            "action": action,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "request_id": f"{service}_{action}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "payload": payload
        }
        
        return response
