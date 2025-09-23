"""
SAP Integration Module for Service Recommendation System

This module provides real SAP integration capabilities for:
- Repair cost estimation
- Parts availability checking
- Technician scheduling
- Service order creation
"""

import os
import httpx
import json
import random
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SAPIntegration:
    """Real SAP system integration for repair costs and service orders"""
    
    def __init__(self):
        self.base_url = os.getenv("SAP_API_ENDPOINT", "https://your-sap-instance.com/api")
        self.api_key = os.getenv("SAP_API_KEY", "")
        self.timeout = 30
        
    async def get_repair_cost_estimate(self, device_type: str, brand: str, error_description: str) -> Dict:
        """
        Get repair cost estimate from SAP system
        
        Args:
            device_type: Type of device (cooktop, oven, etc.)
            brand: Device brand
            error_description: Description of the error
            
        Returns:
            Dict containing cost breakdown and availability
        """
        
        # In production, this would make real SAP API calls
        if self.api_key and self.base_url != "https://your-sap-instance.com/api":
            return await self._call_sap_api("repair-costs", {
                "device_type": device_type,
                "brand": brand,
                "error_description": error_description
            })
        
        # Fallback to enhanced simulation for demo
        return self._simulate_sap_repair_costs(device_type, brand, error_description)
    
    async def check_parts_availability(self, part_numbers: List[str]) -> Dict:
        """Check parts availability in SAP inventory"""
        
        if self.api_key and self.base_url != "https://your-sap-instance.com/api":
            return await self._call_sap_api("parts-availability", {
                "part_numbers": part_numbers
            })
            
        # Enhanced simulation
        return {
            "parts_status": {
                part: {
                    "available": True,
                    "quantity": 50,
                    "lead_time": "2-3 days",
                    "cost": 45.50
                } for part in part_numbers
            },
            "total_parts_cost": len(part_numbers) * 45.50,
            "availability_score": "high"
        }
    
    async def create_service_order(self, order_data: Dict) -> Dict:
        """Create a comprehensive service order in SAP"""
        
        if self.api_key and self.base_url != "https://your-sap-instance.com/api":
            return await self._call_sap_api("service-orders", order_data, method="POST")
            
        # Enhanced simulation with realistic order creation
        order_id = f"SO_{datetime.now().strftime('%Y%m%d')}_{hash(str(order_data)) % 10000:04d}"
        
        # Calculate priority-based scheduling
        priority = order_data.get("priority", "standard")
        if priority == "urgent":
            scheduled_days = 1
            technician_level = "Senior"
        elif priority == "high":
            scheduled_days = 2
            technician_level = "Standard"
        else:
            scheduled_days = 3
            technician_level = "Standard"
        
        # Generate comprehensive service order
        service_order = {
            "order_id": order_id,
            "status": "created",
            "priority": priority,
            "scheduled_date": (datetime.now() + timedelta(days=scheduled_days)).isoformat(),
            "technician_assignment": {
                "technician_id": f"TECH_{random.randint(100, 999)}",
                "skill_level": technician_level,
                "estimated_duration": "2-4 hours",
                "contact_phone": "+41 79 XXX XX XX"
            },
            "service_details": {
                "device_type": order_data.get("device_type", ""),
                "customer_id": order_data.get("customer_id", ""),
                "service_address": "Customer premises",
                "access_instructions": "Ring doorbell, customer will be present"
            },
            "cost_breakdown": {
                "labor_cost": order_data.get("total_cost", 0) * 0.4,
                "parts_cost": order_data.get("total_cost", 0) * 0.6,
                "travel_cost": 50,
                "total_cost": order_data.get("total_cost", 0) + 50,
                "currency": "CHF"
            },
            "workflow_automation": {
                "customer_notification": "scheduled",
                "parts_ordered": True,
                "calendar_blocked": True,
                "invoice_preparation": "pending"
            },
            "quality_assurance": {
                "follow_up_call": True,
                "satisfaction_survey": True,
                "warranty_registration": True
            },
            "tracking": {
                "sap_tracking_url": f"https://sap-portal.company.com/orders/{order_id}",
                "customer_portal_url": f"https://service.company.com/track/{order_id}",
                "estimated_completion": (datetime.now() + timedelta(days=scheduled_days + 1)).isoformat()
            },
            "created_by": order_data.get("created_by", "system"),
            "created_timestamp": datetime.now().isoformat()
        }
        
        return service_order
    
    async def get_technician_availability(self, region: str, skill_level: str = "standard") -> Dict:
        """Get technician availability for scheduling"""
        
        if self.api_key and self.base_url != "https://your-sap-instance.com/api":
            return await self._call_sap_api("technician-schedule", {
                "region": region,
                "skill_level": skill_level
            })
            
        # Enhanced simulation
        return {
            "available_slots": [
                {
                    "date": (datetime.now() + timedelta(days=2)).date().isoformat(),
                    "time_slots": ["09:00-13:00", "14:00-18:00"],
                    "technician_id": "TECH_001",
                    "skill_rating": 4.8
                },
                {
                    "date": (datetime.now() + timedelta(days=3)).date().isoformat(),
                    "time_slots": ["08:00-12:00", "13:00-17:00"],
                    "technician_id": "TECH_002", 
                    "skill_rating": 4.9
                }
            ],
            "earliest_available": (datetime.now() + timedelta(days=2)).date().isoformat(),
            "average_response_time": "2-3 business days"
        }
    
    async def _call_sap_api(self, endpoint: str, data: Dict, method: str = "GET") -> Dict:
        """Make actual SAP API call"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=data)
                else:
                    response = await client.post(url, headers=headers, json=data)
                
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"SAP API request failed: {e}")
            raise Exception(f"SAP integration error: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"SAP API HTTP error: {e.response.status_code}")
            raise Exception(f"SAP API error: {e.response.status_code}")
    
    def _simulate_sap_repair_costs(self, device_type: str, brand: str, error_description: str) -> Dict:
        """Enhanced simulation with realistic SAP data structure"""
        
        # Base costs by device type and brand
        base_costs = {
            "cooktop": {"V-Zug": 250, "Miele": 280, "Siemens": 200, "Bosch": 190},
            "oven": {"V-Zug": 320, "Miele": 350, "Siemens": 280, "Bosch": 260},
            "dishwasher": {"V-Zug": 220, "Miele": 240, "Siemens": 200, "Bosch": 180},
        }
        
        base_cost = base_costs.get(device_type, {}).get(brand, 250)
        
        # Error-specific adjustments
        error_multipliers = {
            "heating": 1.2,
            "pump": 1.4,
            "electronic": 1.6,
            "display": 1.8,
            "sensor": 1.1,
            "seal": 0.8,
            "door": 0.9
        }
        
        multiplier = 1.0
        for keyword, mult in error_multipliers.items():
            if keyword in error_description.lower():
                multiplier = mult
                break
        
        parts_cost = base_cost * 0.6 * multiplier
        labor_cost = base_cost * 0.4
        total_cost = parts_cost + labor_cost
        
        return {
            "cost_breakdown": {
                "parts_cost": round(parts_cost, 2),
                "labor_cost": round(labor_cost, 2),
                "total_cost": round(total_cost, 2),
                "tax_rate": 0.077,  # 7.7% Swiss VAT
                "total_with_tax": round(total_cost * 1.077, 2)
            },
            "parts_availability": "high" if multiplier < 1.5 else "medium",
            "lead_time": "2-3 days" if multiplier < 1.5 else "5-7 days",
            "warranty_coverage": "6 months parts and labor",
            "sap_cost_center": f"CC_{device_type.upper()}_{brand}",
            "estimated_margin": round(total_cost * 0.25, 2)
        }

# Global SAP integration instance
sap_integration = SAPIntegration()
