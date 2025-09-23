"""
Microsoft Ecosystem Integration Module

This module provides integration with Microsoft services:
- Azure AD for authentication
- Power Automate for workflow automation
- Office 365 for document management
- Teams for collaboration
"""

import os
import httpx
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MicrosoftIntegration:
    """Microsoft ecosystem integration for enterprise features"""
    
    def __init__(self):
        self.tenant_id = os.getenv("AZURE_TENANT_ID", "")
        self.client_id = os.getenv("AZURE_CLIENT_ID", "")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET", "")
        self.graph_api_url = "https://graph.microsoft.com/v1.0"
        
    async def authenticate_user(self, access_token: str) -> Dict:
        """Authenticate user via Azure AD"""
        
        if not self.tenant_id:
            # Simulation mode for demo
            return {
                "authenticated": True,
                "user": {
                    "id": "user_12345",
                    "displayName": "Sales Representative",
                    "mail": "sales.rep@company.com",
                    "jobTitle": "Senior Sales Consultant",
                    "department": "After Sales Service",
                    "officeLocation": "Zürich Office"
                },
                "roles": ["ServiceAgent", "SalesConsultant"],
                "permissions": ["read_customer_data", "create_service_orders", "view_pricing"]
            }
        
        # Real Azure AD integration
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.graph_api_url}/me", headers=headers)
                response.raise_for_status()
                
                user_data = response.json()
                
                # Get user's group memberships for role determination
                groups_response = await client.get(f"{self.graph_api_url}/me/memberOf", headers=headers)
                groups_data = groups_response.json()
                
                roles = self._extract_roles_from_groups(groups_data.get("value", []))
                
                return {
                    "authenticated": True,
                    "user": user_data,
                    "roles": roles,
                    "permissions": self._get_permissions_for_roles(roles)
                }
                
        except Exception as e:
            logger.error(f"Azure AD authentication failed: {e}")
            return {"authenticated": False, "error": str(e)}
    
    async def trigger_power_automate_workflow(self, workflow_name: str, trigger_data: Dict) -> Dict:
        """Trigger Power Automate workflow for service automation"""
        
        workflows = {
            "repair_order_approval": {
                "url": "https://prod-123.westeurope.logic.azure.com/workflows/repair-approval/triggers/manual/invoke",
                "description": "Automated approval workflow for repair orders"
            },
            "customer_notification": {
                "url": "https://prod-124.westeurope.logic.azure.com/workflows/customer-notify/triggers/manual/invoke", 
                "description": "Send automated customer notifications"
            },
            "escalation_workflow": {
                "url": "https://prod-125.westeurope.logic.azure.com/workflows/escalation/triggers/manual/invoke",
                "description": "Escalate complex cases to management"
            }
        }
        
        if workflow_name not in workflows:
            return {"error": f"Workflow {workflow_name} not found"}
        
        workflow_url = workflows[workflow_name]["url"]
        
        if not self.client_secret:
            # Simulation mode
            return {
                "triggered": True,
                "workflow_name": workflow_name,
                "run_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "running",
                "estimated_completion": (datetime.now() + timedelta(minutes=5)).isoformat(),
                "description": workflows[workflow_name]["description"]
            }
        
        # Real Power Automate trigger
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(workflow_url, json=trigger_data)
                response.raise_for_status()
                
                return {
                    "triggered": True,
                    "workflow_name": workflow_name,
                    "response": response.json() if response.content else {},
                    "status": "triggered"
                }
                
        except Exception as e:
            logger.error(f"Power Automate workflow trigger failed: {e}")
            return {"triggered": False, "error": str(e)}
    
    async def create_teams_notification(self, channel_id: str, message: Dict) -> Dict:
        """Send notification to Microsoft Teams channel"""
        
        if not self.client_secret:
            # Simulation mode
            return {
                "sent": True,
                "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "channel": "Service Recommendations",
                "timestamp": datetime.now().isoformat(),
                "content": message.get("text", "Service recommendation notification")
            }
        
        # Real Teams integration would require proper Graph API setup
        teams_url = f"{self.graph_api_url}/teams/{channel_id}/channels/general/messages"
        
        try:
            # This would require proper authentication flow
            pass
        except Exception as e:
            logger.error(f"Teams notification failed: {e}")
            return {"sent": False, "error": str(e)}
    
    async def create_sharepoint_document(self, site_id: str, document_data: Dict) -> Dict:
        """Create service report document in SharePoint"""
        
        if not self.client_secret:
            # Simulation mode
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return {
                "created": True,
                "document_id": doc_id,
                "url": f"https://company.sharepoint.com/sites/service/Documents/{doc_id}.docx",
                "filename": f"Service_Report_{doc_id}.docx",
                "created_by": "Service System",
                "created_date": datetime.now().isoformat()
            }
        
        # Real SharePoint integration
        sharepoint_url = f"{self.graph_api_url}/sites/{site_id}/drive/root/children"
        
        try:
            # Implementation would require proper document creation logic
            pass
        except Exception as e:
            logger.error(f"SharePoint document creation failed: {e}")
            return {"created": False, "error": str(e)}
    
    def _extract_roles_from_groups(self, groups: List[Dict]) -> List[str]:
        """Extract user roles from Azure AD group memberships"""
        
        role_mapping = {
            "Service-Agents": "ServiceAgent",
            "Sales-Consultants": "SalesConsultant", 
            "Service-Managers": "ServiceManager",
            "System-Administrators": "SystemAdmin"
        }
        
        roles = []
        for group in groups:
            group_name = group.get("displayName", "")
            if group_name in role_mapping:
                roles.append(role_mapping[group_name])
        
        return roles if roles else ["ServiceAgent"]  # Default role
    
    def _get_permissions_for_roles(self, roles: List[str]) -> List[str]:
        """Get permissions based on user roles"""
        
        permission_mapping = {
            "ServiceAgent": ["read_customer_data", "create_service_orders", "view_basic_pricing"],
            "SalesConsultant": ["read_customer_data", "create_service_orders", "view_pricing", "create_opportunities"],
            "ServiceManager": ["read_customer_data", "create_service_orders", "view_pricing", "approve_orders", "view_reports"],
            "SystemAdmin": ["*"]  # All permissions
        }
        
        all_permissions = set()
        for role in roles:
            permissions = permission_mapping.get(role, [])
            if "*" in permissions:
                return ["*"]  # Admin has all permissions
            all_permissions.update(permissions)
        
        return list(all_permissions)

# Global Microsoft integration instance
microsoft_integration = MicrosoftIntegration()

