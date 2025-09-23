import os
from typing import Dict, List, Optional, TypedDict, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langgraph.graph import StateGraph, END
import json
import random
from datetime import datetime, timedelta

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize the Google Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))

# Mock database for appliance failure patterns and repair costs
APPLIANCE_DATA = {
    "cooktop": {
        "V-Zug": {
            "common_errors": {
                "E26": {"description": "Water in machine, pump not draining", "repair_cost": 180, "success_rate": 0.95},
                "F7_E3": {"description": "Heating element failure", "repair_cost": 220, "success_rate": 0.90},
                "power_issue": {"description": "No power/not turning on", "repair_cost": 150, "success_rate": 0.85}
            },
            "warranty_years": 2,
            "avg_lifespan": 12
        },
        "Miele": {
            "common_errors": {
                "heating_failure": {"description": "Uneven heating", "repair_cost": 280, "success_rate": 0.88},
                "display_error": {"description": "Display not working", "repair_cost": 320, "success_rate": 0.75},
                "sensor_fault": {"description": "Temperature sensor malfunction", "repair_cost": 200, "success_rate": 0.92}
            },
            "warranty_years": 2,
            "avg_lifespan": 15
        }
    },
    "dishwasher": {
        "V-Zug": {
            "common_errors": {
                "water_leak": {"description": "Water leaking from door", "repair_cost": 160, "success_rate": 0.94},
                "not_cleaning": {"description": "Poor cleaning performance", "repair_cost": 120, "success_rate": 0.90},
                "pump_noise": {"description": "Unusual pump noise", "repair_cost": 240, "success_rate": 0.85}
            },
            "warranty_years": 2,
            "avg_lifespan": 10
        }
    },
    "oven": {
        "Siemens": {
            "common_errors": {
                "door_seal": {"description": "Door seal damaged", "repair_cost": 200, "success_rate": 0.95},
                "heating_element": {"description": "Heating element burned out", "repair_cost": 300, "success_rate": 0.88},
                "temperature_control": {"description": "Temperature not accurate", "repair_cost": 250, "success_rate": 0.90}
            },
            "warranty_years": 2,
            "avg_lifespan": 12
        }
    }
}

# Mock replacement product catalog
REPLACEMENT_PRODUCTS = {
    "cooktop": [
        {"brand": "V-Zug", "model": "AdoraID V6000 Supreme", "price": 2400, "margin": 480, "stock": "high", "energy_rating": "A++", "features": ["Induction", "Touch Control", "Bridge Function"]},
        {"brand": "V-Zug", "model": "AdoraID V4000", "price": 1800, "margin": 360, "stock": "medium", "energy_rating": "A+", "features": ["Induction", "Touch Control"]},
        {"brand": "Miele", "model": "KM 7897 FL", "price": 2800, "margin": 560, "stock": "low", "energy_rating": "A++", "features": ["Induction", "Con@ct 2.0", "PowerFlex"]},
        {"brand": "Siemens", "model": "EX875LYC1E", "price": 1200, "margin": 240, "stock": "high", "energy_rating": "A", "features": ["Induction", "Touch Control"]}
    ],
    "dishwasher": [
        {"brand": "V-Zug", "model": "Adora SL V4000", "price": 1600, "margin": 320, "stock": "high", "energy_rating": "A+++", "features": ["OptiDos", "EcoManagement", "Silence Program"]},
        {"brand": "Miele", "model": "G 7960 SCVi", "price": 2200, "margin": 440, "stock": "medium", "energy_rating": "A+++", "features": ["AutoDos", "Perfect GlassCare", "3D+ Cutlery Tray"]}
    ],
    "oven": [
        {"brand": "V-Zug", "model": "Combair V6000 Supreme", "price": 3200, "margin": 640, "stock": "medium", "energy_rating": "A++", "features": ["Steam Cooking", "Automatic Programs", "Moisture Plus"]},
        {"brand": "Siemens", "model": "HB678GBS6", "price": 1800, "margin": 360, "stock": "high", "energy_rating": "A+", "features": ["PerfectBake", "coolStart", "ecoClean Direct"]}
    ]
}

# Define the state structure
class ServiceCaseState(TypedDict):
    # Input data
    device_type: str
    brand: str
    age: int
    error_description: str
    customer_preferences: Optional[Dict]
    
    # Triage results
    triage_decision: Optional[Dict]
    
    # Data enrichment results
    repair_cost: Optional[float]
    spare_part_availability: Optional[str]
    customer_data: Optional[Dict]
    device_specs: Optional[Dict]
    cost_ceiling: Optional[float]
    sap_data: Optional[Dict]
    salesforce_data: Optional[Dict]
    pim_data: Optional[Dict]
    
    # Technical analysis results
    warranty_status: Optional[str]
    damage_classification: Optional[str]
    repair_probability: Optional[float]
    repair_complexity: Optional[str]
    technical_analysis: Optional[Dict]
    
    # Economic analysis results
    economic_viability: Optional[str]
    economic_reasoning: Optional[str]
    margin_analysis: Optional[Dict]
    replacement_value: Optional[float]
    
    # Final recommendation
    recommendation: Optional[str]
    repair_order: Optional[Dict]
    replacement_options: Optional[List[Dict]]
    justification: Optional[str]
    confidence_score: Optional[float]
    agent_reasoning: Optional[Dict]

# Enhanced Triage Agent with LLM-powered routing
def triage_agent(state: ServiceCaseState) -> Dict:
    """Analyzes initial damage report and routes the request intelligently"""
    
    # Check if all mandatory fields are present
    if not state["device_type"] or not state["brand"] or not state["age"] or not state["error_description"]:
        return {
            "triage_decision": {
                "status": "incomplete",
                "route": "manual_review",
                "reasoning": "Missing mandatory field information"
            }
        }
    
    # Enhanced routing logic based on device age and type
    age = state["age"]
    device_type = state["device_type"].lower()
    brand = state["brand"]
    error_desc = state["error_description"].lower()
    
    # Route to manufacturer for very new devices under warranty
    if age <= 1 and device_type in ["oven", "refrigerator"]:
        return {
            "triage_decision": {
                "status": "complete",
                "route": "manufacturer",
                "reasoning": f"Device age {age} year(s) - likely under manufacturer warranty"
            }
        }
    
    # Route very old devices directly to replacement consideration
    if age >= 15:
        return {
            "triage_decision": {
                "status": "complete", 
                "route": "replacement_focus",
                "reasoning": f"Device age {age} years exceeds typical lifespan"
            }
        }
    
    # Check for critical safety issues that require immediate manufacturer attention
    safety_keywords = ["smoke", "fire", "burning", "electric shock", "gas leak"]
    if any(keyword in error_desc for keyword in safety_keywords):
        return {
            "triage_decision": {
                "status": "complete",
                "route": "urgent_manufacturer",
                "reasoning": "Safety concern detected - requires immediate manufacturer attention"
            }
        }
    
    # Normal routing for standard cases
    return {
        "triage_decision": {
            "status": "complete",
            "route": "normal",
            "reasoning": "Standard service case - proceeding with full analysis"
        }
    }

# Enhanced Data Enrichment Agent with realistic mock data
def data_enrichment_agent(state: ServiceCaseState) -> Dict:
    """Enriches the service case with data from internal systems (SAP, Salesforce, PIM)"""
    
    device_type = state["device_type"].lower()
    brand = state["brand"]
    age = state["age"]
    error_desc = state["error_description"].lower()
    
    # Mock SAP data - repair costs and spare parts
    sap_data = simulate_sap_integration(device_type, brand, error_desc)
    
    # Mock Salesforce data - customer information
    salesforce_data = simulate_salesforce_integration(brand)
    
    # Mock PIM/Snowflake data - product specifications and inventory
    pim_data = simulate_pim_integration(device_type, brand, age)
    
    # Calculate cost ceiling based on device value and company policy
    device_value = pim_data.get("current_market_value", 1000)
    # For old devices (>10 years), use strategic replacement pricing
    if age > 10:
        # For replacement scenarios, ensure minimum viable ceiling
        cost_ceiling = max(device_value * 0.6, 1800)  # At least 1800 CHF for replacement options
        cost_ceiling = min(cost_ceiling, 2500)  # Cap at 2500 CHF
    else:
        cost_ceiling = min(device_value * 0.6, 800)  # Standard repair-focused ceiling
    
    return {
        "repair_cost": sap_data["estimated_repair_cost"],
        "spare_part_availability": sap_data["parts_availability"],
        "customer_data": salesforce_data,
        "device_specs": pim_data["specifications"],
        "cost_ceiling": cost_ceiling,
        "sap_data": sap_data,
        "salesforce_data": salesforce_data,
        "pim_data": pim_data
    }

def simulate_sap_integration(device_type: str, brand: str, error_desc: str) -> Dict:
    """Simulate SAP system integration for repair costs and parts availability"""
    
    # Get device data if available
    device_data = APPLIANCE_DATA.get(device_type, {}).get(brand, {})
    common_errors = device_data.get("common_errors", {})
    
    # Try to match error description to known patterns
    repair_cost = 300  # Default
    parts_availability = "medium"
    
    for error_code, error_info in common_errors.items():
        if error_code.lower() in error_desc or any(word in error_desc for word in error_info["description"].lower().split()):
            repair_cost = error_info["repair_cost"]
            parts_availability = "high" if error_info["success_rate"] > 0.9 else "medium"
            break
    
    # Add some realistic variation
    repair_cost += random.randint(-50, 100)
    
    return {
        "estimated_repair_cost": repair_cost,
        "parts_availability": parts_availability,
        "labor_cost": repair_cost * 0.4,
        "parts_cost": repair_cost * 0.6,
        "estimated_repair_time": "2-5 business days",
        "technician_availability": "next week"
    }

def simulate_salesforce_integration(brand: str) -> Dict:
    """Simulate Salesforce CRM integration for customer data"""
    
    # Generate realistic customer profile
    service_history = [
        {"date": "2023-08-15", "device": "Dishwasher", "issue": "Pump replacement", "satisfaction": 4.5},
        {"date": "2022-11-20", "device": "Oven", "issue": "Door seal repair", "satisfaction": 4.8}
    ]
    
    return {
        "customer_id": "CUST_" + str(random.randint(10000, 99999)),
        "name": "Premium Customer",
        "customer_tier": "Gold",
        "brand_loyalty": brand,
        "service_history": service_history,
        "preferences": {
            "preferred_brands": [brand, "V-Zug", "Miele"],
            "budget_range": "premium",
            "installation_preference": "professional",
            "warranty_preference": "extended"
        },
        "last_service_satisfaction": 4.6,
        "total_purchases": 85000  # CHF
    }

def simulate_pim_integration(device_type: str, brand: str, age: int) -> Dict:
    """Simulate PIM/Snowflake integration for product specifications and market data"""
    
    # Calculate depreciated value
    original_value = {"cooktop": 2000, "dishwasher": 1500, "oven": 2500}.get(device_type, 1800)
    depreciation_rate = 0.08  # 8% per year
    current_value = original_value * (1 - depreciation_rate) ** age
    
    # Get replacement options from catalog
    replacement_options = REPLACEMENT_PRODUCTS.get(device_type, [])
    
    return {
        "specifications": {
            "original_purchase_price": original_value,
            "current_market_value": max(current_value, original_value * 0.1),  # Minimum 10% of original
            "energy_rating": "A+" if age < 5 else "A",
            "installation_dimensions": "60x60x85 cm",
            "warranty_remaining": max(0, 2 - age) if age <= 2 else 0
        },
        "market_analysis": {
            "replacement_models_available": len(replacement_options),
            "average_replacement_cost": sum(p["price"] for p in replacement_options) / len(replacement_options) if replacement_options else 2000,
            "inventory_status": "good",
            "delivery_time": "1-2 weeks"
        },
        "sustainability_score": max(10 - age, 1)  # Encourages repair for newer devices
    }

# Enhanced Technical Analyst Agent with sophisticated analysis
def technical_analyst_agent(state: ServiceCaseState) -> Dict:
    """Evaluates technical feasibility of repair using historical data and AI analysis"""
    
    device_type = state["device_type"].lower()
    brand = state["brand"]
    age = state["age"]
    error_desc = state["error_description"].lower()
    
    # Determine warranty status
    warranty_years = APPLIANCE_DATA.get(device_type, {}).get(brand, {}).get("warranty_years", 2)
    warranty_status = "under_warranty" if age <= warranty_years else "out_of_warranty"
    
    # Classify damage type
    electrical_keywords = ["power", "display", "electric", "electronic", "circuit", "control"]
    mechanical_keywords = ["leak", "pump", "door", "seal", "heating", "noise", "vibration"]
    
    if any(keyword in error_desc for keyword in electrical_keywords):
        damage_type = "electrical"
        complexity = "medium"
    elif any(keyword in error_desc for keyword in mechanical_keywords):
        damage_type = "mechanical" 
        complexity = "low"
    else:
        damage_type = "unknown"
        complexity = "high"
    
    # Calculate repair probability based on historical data
    device_data = APPLIANCE_DATA.get(device_type, {}).get(brand, {})
    common_errors = device_data.get("common_errors", {})
    
    repair_probability = 0.75  # Default
    matched_error = None
    
    for error_code, error_info in common_errors.items():
        if error_code.lower() in error_desc or any(word in error_desc for word in error_info["description"].lower().split()):
            repair_probability = error_info["success_rate"]
            matched_error = error_code
            break
    
    # Adjust probability based on device age
    age_factor = max(0.5, 1 - (age - 5) * 0.05) if age > 5 else 1.0
    repair_probability *= age_factor
    
    # Determine repair complexity and timeline
    if repair_probability > 0.9:
        complexity = "low"
        timeline = "1-2 days"
    elif repair_probability > 0.7:
        complexity = "medium"
        timeline = "3-5 days"
    else:
        complexity = "high"
        timeline = "1-2 weeks"
    
    return {
        "warranty_status": warranty_status,
        "damage_classification": damage_type,
        "repair_probability": repair_probability,
        "repair_complexity": complexity,
        "technical_analysis": {
            "matched_error_pattern": matched_error,
            "age_impact_factor": age_factor,
            "estimated_timeline": timeline,
            "required_expertise": "specialist" if complexity == "high" else "standard",
            "parts_complexity": "standard" if damage_type == "mechanical" else "electronic",
            "risk_assessment": "low" if repair_probability > 0.8 else "medium"
        }
    }

# Enhanced Economic Analyst Agent with comprehensive financial analysis
def economic_analyst_agent(state: ServiceCaseState) -> Dict:
    """Evaluates economic viability of repair vs replacement with detailed financial modeling"""
    
    repair_cost = state.get("repair_cost", 0)
    cost_ceiling = state.get("cost_ceiling", 500)
    device_specs = state.get("device_specs", {})
    customer_data = state.get("customer_data", {})
    device_type = state["device_type"].lower()
    age = state["age"]
    
    # Get current device value and replacement options
    current_value = device_specs.get("current_market_value", 1000)
    replacement_options = REPLACEMENT_PRODUCTS.get(device_type, [])
    
    # Calculate repair economics
    repair_roi = (current_value - repair_cost) / repair_cost if repair_cost > 0 else 0
    
    # Calculate replacement economics - find best margin options
    replacement_margins = []
    for option in replacement_options:
        margin = option["margin"]
        price = option["price"]
        margin_percentage = (margin / price) * 100
        replacement_margins.append({
            "model": option["model"],
            "price": price,
            "margin": margin,
            "margin_percentage": margin_percentage
        })
    
    # Sort by margin percentage
    replacement_margins.sort(key=lambda x: x["margin_percentage"], reverse=True)
    best_replacement_margin = replacement_margins[0]["margin"] if replacement_margins else 0
    
    # Economic decision factors
    factors = {
        "repair_within_ceiling": repair_cost <= cost_ceiling,
        "repair_cost_ratio": repair_cost / current_value if current_value > 0 else 1,
        "customer_tier": customer_data.get("customer_tier", "Standard"),
        "device_age_factor": age / 15,  # Normalized by typical 15-year lifespan
        "sustainability_impact": age < 8,  # Favor repair for devices < 8 years
        "replacement_margin_opportunity": best_replacement_margin
    }
    
    # Decision logic with weighted scoring
    score = 0
    reasoning_points = []
    
    # Cost ceiling check (40% weight)
    if factors["repair_within_ceiling"]:
        score += 40
        reasoning_points.append(f"Repair cost ({repair_cost} CHF) within ceiling ({cost_ceiling} CHF)")
    else:
        reasoning_points.append(f"Repair cost ({repair_cost} CHF) exceeds ceiling ({cost_ceiling} CHF)")
    
    # Cost ratio check (25% weight)
    if factors["repair_cost_ratio"] < 0.5:
        score += 25
        reasoning_points.append("Repair cost is reasonable relative to device value")
    elif factors["repair_cost_ratio"] < 0.8:
        score += 10
        reasoning_points.append("Repair cost is acceptable relative to device value")
    else:
        reasoning_points.append("Repair cost is high relative to device value")
    
    # Customer tier consideration (15% weight)
    if factors["customer_tier"] == "Gold":
        score += 15
        reasoning_points.append("Premium customer - prioritize satisfaction")
    elif factors["customer_tier"] == "Silver":
        score += 10
    
    # Sustainability factor (10% weight)
    if factors["sustainability_impact"]:
        score += 10
        reasoning_points.append("Environmental benefit from repair")
    
    # Age factor (10% weight)
    if factors["device_age_factor"] < 0.5:
        score += 10
        reasoning_points.append("Device is relatively new")
    
    # Make recommendation
    if score >= 60:
        recommendation = "repair"
        primary_reasoning = "Economic analysis favors repair"
    else:
        recommendation = "replace"
        primary_reasoning = f"Economic analysis favors replacement (margin opportunity: {best_replacement_margin} CHF)"
    
    return {
        "economic_viability": recommendation,
        "economic_reasoning": primary_reasoning,
        "margin_analysis": {
            "repair_roi": repair_roi,
            "best_replacement_margin": best_replacement_margin,
            "economic_score": score,
            "cost_effectiveness_ratio": repair_cost / current_value if current_value > 0 else 1
        },
        "replacement_value": replacement_margins[0]["price"] if replacement_margins else 2000,
        "detailed_reasoning": reasoning_points,
        "economic_factors": factors
    }

# Enhanced Recommendation Engine Agent with intelligent synthesis
def recommendation_engine_agent(state: ServiceCaseState) -> Dict:
    """Generates final recommendation by synthesizing all agent analyses"""
    
    # Gather all analysis results
    economic_viability = state.get("economic_viability", "repair")
    technical_analysis = state.get("technical_analysis", {})
    repair_probability = state.get("repair_probability", 0.75)
    margin_analysis = state.get("margin_analysis", {})
    customer_data = state.get("customer_data", {})
    device_type = state["device_type"].lower()
    
    # Calculate overall confidence score
    economic_score = margin_analysis.get("economic_score", 50)
    technical_confidence = repair_probability * 100
    
    # Weighted final score (60% economic, 40% technical)
    final_score = (economic_score * 0.6) + (technical_confidence * 0.4)
    confidence_score = min(final_score / 100, 0.95)  # Cap at 95%
    
    # Determine final recommendation with override logic
    final_recommendation = economic_viability
    
    # Override for very low repair probability
    if repair_probability < 0.6:
        final_recommendation = "replace"
        override_reason = "Low technical success probability"
    # Override for very high repair probability and premium customers
    elif repair_probability > 0.9 and customer_data.get("customer_tier") == "Gold":
        final_recommendation = "repair"
        override_reason = "High success probability with premium customer"
    else:
        override_reason = None
    
    # Generate detailed justification
    justification_parts = []
    
    if final_recommendation == "repair":
        justification_parts.append(f"Technical Analysis: {repair_probability:.0%} success probability")
        justification_parts.append(f"Economic Analysis: Score {economic_score}/100")
        justification_parts.append(f"Customer: {customer_data.get('customer_tier', 'Standard')} tier")
        
        if override_reason:
            justification_parts.append(f"Override: {override_reason}")
    else:
        best_margin = margin_analysis.get("best_replacement_margin", 0)
        justification_parts.append(f"Replacement offers better value proposition")
        justification_parts.append(f"Potential margin: {best_margin} CHF")
        justification_parts.append(f"Technical risk: {100-technical_confidence:.0f}%")
    
    # Create detailed response based on recommendation
    if final_recommendation == "repair":
        repair_order = generate_repair_order(state)
        replacement_options = []
    else:
        repair_order = None
        replacement_options = generate_replacement_options(state)
    
    # Compile agent reasoning for transparency
    agent_reasoning = {
        "triage": state.get("triage_decision", {}),
        "technical": {
            "probability": repair_probability,
            "complexity": state.get("repair_complexity", "unknown"),
            "risk": technical_analysis.get("risk_assessment", "medium")
        },
        "economic": {
            "viability": economic_viability,
            "score": economic_score,
            "reasoning": state.get("economic_reasoning", "")
        },
        "final": {
            "confidence": confidence_score,
            "override_applied": override_reason is not None,
            "override_reason": override_reason
        }
    }
    
    return {
        "recommendation": final_recommendation,
        "repair_order": repair_order,
        "replacement_options": replacement_options,
        "justification": " | ".join(justification_parts),
        "confidence_score": confidence_score,
        "agent_reasoning": agent_reasoning
    }

def generate_repair_order(state: ServiceCaseState) -> Dict:
    """Generate a comprehensive repair order"""
    sap_data = state.get("sap_data", {})
    technical_analysis = state.get("technical_analysis", {})
    
    return {
        "order_id": f"REP_{random.randint(100000, 999999)}",
        "device_info": {
            "type": state["device_type"],
            "brand": state["brand"],
            "age": state["age"],
            "error_description": state["error_description"]
        },
        "cost_breakdown": {
            "parts_cost": sap_data.get("parts_cost", 0),
            "labor_cost": sap_data.get("labor_cost", 0),
            "total_cost": state.get("repair_cost", 0)
        },
        "timeline": {
            "estimated_duration": technical_analysis.get("estimated_timeline", "3-5 days"),
            "technician_availability": sap_data.get("technician_availability", "next week"),
            "parts_delivery": "2-3 days"
        },
        "warranty_info": {
            "status": state.get("warranty_status", "out_of_warranty"),
            "repair_warranty": "6 months",
            "coverage": "parts and labor"
        },
        "priority": "standard",
        "technician_assignment": {
            "skill_level_required": technical_analysis.get("complexity", "standard"),
            "estimated_duration": technical_analysis.get("estimated_timeline", "3-5 days"),
            "priority": "high" if "urgent" in str(state.get("error_description", "")).lower() else "standard"
        },
        "quality_assurance": {
            "follow_up_required": True,
            "customer_satisfaction_survey": True,
            "warranty_registration": True
        },
        "special_instructions": "Follow standard safety protocols. Customer preferred contact: email",
        "created_timestamp": datetime.now().isoformat(),
        "status": "created"
    }

def generate_replacement_options(state: ServiceCaseState) -> List[Dict]:
    """Generate intelligently ranked replacement product options"""
    device_type = state["device_type"].lower()
    customer_data = state.get("customer_data", {})
    customer_preferences = state.get("customer_preferences", {})
    cost_ceiling = state.get("cost_ceiling", 2000)
    current_device_age = state.get("age", 0)
    
    # Get available products
    available_products = REPLACEMENT_PRODUCTS.get(device_type, [])
    
    # Filter by budget constraints - be more flexible for replacement scenarios
    # For old devices (>10 years), allow higher price tolerance as replacement is strategic
    flexibility_multiplier = 2.0 if current_device_age > 10 else 1.5
    max_price = cost_ceiling * flexibility_multiplier
    budget_filtered = [p for p in available_products if p["price"] <= max_price]
    
    # Score and rank products
    scored_products = []
    for product in budget_filtered:
        score = 0
        scoring_details = {}
        
        # 1. Customer Brand Loyalty (25 points)
        customer_brands = customer_preferences.get("preferred_brands", customer_data.get("brand_loyalty", []))
        if product["brand"] in customer_brands:
            brand_score = 25
            scoring_details["brand_loyalty"] = f"Preferred brand match: +{brand_score}"
        else:
            brand_score = 10  # Base score for other brands
            scoring_details["brand_loyalty"] = f"Alternative brand: +{brand_score}"
        score += brand_score
        
        # 2. Business Margin Optimization (25 points)
        max_margin = max(p["margin"] for p in budget_filtered) if budget_filtered else product["margin"]
        margin_score = (product["margin"] / max_margin) * 25 if max_margin > 0 else 0
        score += margin_score
        scoring_details["margin_optimization"] = f"Margin score: +{margin_score:.1f}"
        
        # 3. Inventory & Delivery (20 points)
        stock_scores = {"high": 20, "medium": 12, "low": 5, "out_of_stock": 0}
        stock_score = stock_scores.get(product["stock"], 0)
        score += stock_score
        scoring_details["inventory_availability"] = f"Stock level ({product['stock']}): +{stock_score}"
        
        # 4. Energy Efficiency & Sustainability (15 points)
        energy_scores = {"A+++": 15, "A++": 12, "A+": 9, "A": 6, "B": 3}
        energy_score = energy_scores.get(product["energy_rating"], 0)
        score += energy_score
        scoring_details["energy_efficiency"] = f"Energy rating ({product['energy_rating']}): +{energy_score}"
        
        # 5. Technology Upgrade Value (10 points)
        if current_device_age > 8:  # Old device
            upgrade_score = 10  # Full points for significant upgrade
            scoring_details["technology_upgrade"] = "Significant technology upgrade: +10"
        elif current_device_age > 4:
            upgrade_score = 6  # Moderate upgrade
            scoring_details["technology_upgrade"] = "Moderate technology upgrade: +6"
        else:
            upgrade_score = 2  # Minimal upgrade benefit
            scoring_details["technology_upgrade"] = "Minimal upgrade benefit: +2"
        score += upgrade_score
        
        # 6. Price Value Proposition (5 points)
        avg_price = sum(p["price"] for p in budget_filtered) / len(budget_filtered) if budget_filtered else product["price"]
        if product["price"] <= avg_price * 0.9:  # Below average price
            price_score = 5
            scoring_details["price_value"] = "Excellent value (below avg price): +5"
        elif product["price"] <= avg_price * 1.1:  # Around average
            price_score = 3
            scoring_details["price_value"] = "Good value (avg price): +3"
        else:
            price_score = 1  # Above average
            scoring_details["price_value"] = "Premium pricing: +1"
        score += price_score
        
        # Calculate final recommendation details
        product_with_score = product.copy()
        product_with_score.update({
            "recommendation_score": round(score, 1),
            "scoring_breakdown": scoring_details,
            "estimated_delivery": get_delivery_estimate(product["stock"]),
            "installation_included": True,
            "warranty_years": get_warranty_years(product["brand"]),
            "trade_in_value": estimate_trade_in_value(current_device_age, device_type),
            "financing_available": product["price"] > 1500,
            "recommended_reason": get_recommendation_reason(product, score, customer_preferences),
            "total_cost_of_ownership": calculate_tco(product, current_device_age),
            "sustainability_impact": get_sustainability_score(product, current_device_age)
        })
        
        scored_products.append(product_with_score)
    
    # Sort by score (highest first) and return top 3
    scored_products.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    # Add ranking position
    for i, product in enumerate(scored_products[:3]):
        product["ranking_position"] = i + 1
        product["recommendation_confidence"] = "High" if product["recommendation_score"] > 70 else "Medium" if product["recommendation_score"] > 50 else "Standard"
    
    return scored_products[:3]

def get_delivery_estimate(stock_level: str) -> str:
    """Calculate delivery estimate based on stock level"""
    delivery_map = {
        "high": "1-2 weeks",
        "medium": "2-3 weeks", 
        "low": "3-4 weeks",
        "out_of_stock": "4-6 weeks"
    }
    return delivery_map.get(stock_level, "2-3 weeks")

def get_warranty_years(brand: str) -> int:
    """Get warranty years based on brand"""
    premium_brands = ["V-Zug", "Miele"]
    return 3 if brand in premium_brands else 2

def estimate_trade_in_value(device_age: int, device_type: str) -> int:
    """Estimate trade-in value for old device"""
    base_values = {"cooktop": 200, "oven": 300, "dishwasher": 250}
    base_value = base_values.get(device_type, 200)
    
    # Depreciate by age
    depreciation_rate = 0.15  # 15% per year
    trade_in = base_value * max(0.1, (1 - depreciation_rate) ** device_age)
    return int(trade_in)

def calculate_tco(product: Dict, current_age: int) -> Dict:
    """Calculate Total Cost of Ownership over 10 years"""
    purchase_price = product["price"]
    annual_energy_cost = 120 if product["energy_rating"] in ["A+++", "A++"] else 150
    annual_maintenance = 50
    
    tco_10_years = purchase_price + (annual_energy_cost + annual_maintenance) * 10
    
    return {
        "initial_cost": purchase_price,
        "annual_operating_cost": annual_energy_cost + annual_maintenance,
        "tco_10_years": tco_10_years,
        "monthly_cost": round(tco_10_years / 120, 2)  # 10 years = 120 months
    }

def get_sustainability_score(product: Dict, current_age: int) -> Dict:
    """Calculate sustainability impact"""
    energy_savings = 30 if product["energy_rating"] in ["A+++", "A++"] else 15
    years_extended = max(0, 12 - current_age)  # Assume 12-year typical lifespan
    
    return {
        "energy_savings_percent": energy_savings,
        "co2_reduction_kg_year": energy_savings * 2.5,  # Rough estimate
        "device_lifespan_extension": years_extended,
        "recyclability_score": "High" if product["brand"] in ["V-Zug", "Miele"] else "Medium"
    }

def get_recommendation_reason(product: Dict, score: float, preferences: Dict) -> str:
    """Generate explanation for why this product is recommended"""
    reasons = []
    
    if product["brand"] in preferences.get("preferred_brands", []):
        reasons.append("Matches your brand preference")
    
    if product["stock"] == "high":
        reasons.append("Available for quick delivery")
    
    if product["energy_rating"] in ["A+++", "A++"]:
        reasons.append("Excellent energy efficiency")
    
    if score > 80:
        reasons.append("Outstanding overall value")
    elif score > 60:
        reasons.append("Great value proposition")
    
    if product.get("margin", 0) > 400:
        reasons.append("Competitive pricing")
    
    if not reasons:
        reasons.append("Good fit for your requirements")
    
    return " • ".join(reasons[:3])  # Limit to top 3 reasons
