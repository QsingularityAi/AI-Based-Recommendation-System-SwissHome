"""
Digital Decision Tree Engine

This module replaces manual decision trees with a flexible, 
configurable business rules engine that can be easily updated
without code changes.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class RuleCondition(Enum):
    EQUALS = "equals"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    CONTAINS = "contains"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"

class RuleAction(Enum):
    RECOMMEND_REPAIR = "recommend_repair"
    RECOMMEND_REPLACE = "recommend_replace"
    REFER_MANUFACTURER = "refer_manufacturer"
    MANUAL_REVIEW = "manual_review"
    ESCALATE = "escalate"
    SET_PRIORITY = "set_priority"
    APPLY_DISCOUNT = "apply_discount"

class BusinessRulesEngine:
    """
    Configurable business rules engine for service recommendations
    
    Rules are defined in JSON format and can be updated without code changes.
    This digitizes and enhances the existing manual decision tree.
    """
    
    def __init__(self, rules_file: str = "business_rules/rules_config.json"):
        self.rules_file = rules_file
        self.rules = self._load_rules()
        
    def _load_rules(self) -> Dict:
        """Load business rules from configuration file"""
        
        default_rules = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "rule_sets": {
                "safety_rules": {
                    "priority": 1,
                    "rules": [
                        {
                            "name": "smoke_fire_emergency",
                            "conditions": [
                                {
                                    "field": "error_description",
                                    "operator": "contains",
                                    "value": ["smoke", "fire", "burning", "gas leak"],
                                    "match_any": True
                                }
                            ],
                            "action": "refer_manufacturer",
                            "override": True,
                            "reasoning": "Safety concern detected - immediate manufacturer attention required"
                        },
                        {
                            "name": "electrical_hazard",
                            "conditions": [
                                {
                                    "field": "error_description", 
                                    "operator": "contains",
                                    "value": ["electric shock", "sparks", "burning smell from electrical"],
                                    "match_any": True
                                }
                            ],
                            "action": "refer_manufacturer",
                            "override": True,
                            "reasoning": "Electrical safety hazard - requires immediate professional attention"
                        }
                    ]
                },
                "warranty_rules": {
                    "priority": 2,
                    "rules": [
                        {
                            "name": "under_warranty_new",
                            "conditions": [
                                {
                                    "field": "age",
                                    "operator": "lte",
                                    "value": 1
                                },
                                {
                                    "field": "device_type",
                                    "operator": "in_list",
                                    "value": ["oven", "refrigerator", "dishwasher"]
                                }
                            ],
                            "action": "refer_manufacturer",
                            "reasoning": "Device under warranty - manufacturer responsibility"
                        }
                    ]
                },
                "economic_rules": {
                    "priority": 3,
                    "rules": [
                        {
                            "name": "high_value_customer_repair_preference",
                            "conditions": [
                                {
                                    "field": "customer_tier",
                                    "operator": "in_list",
                                    "value": ["Gold", "Platinum"]
                                },
                                {
                                    "field": "repair_cost",
                                    "operator": "lte",
                                    "value": 800
                                },
                                {
                                    "field": "repair_probability",
                                    "operator": "gte",
                                    "value": 0.7
                                }
                            ],
                            "action": "recommend_repair",
                            "weight": 20,
                            "reasoning": "Premium customer - prioritize repair when feasible"
                        },
                        {
                            "name": "cost_ceiling_exceeded",
                            "conditions": [
                                {
                                    "field": "repair_cost",
                                    "operator": "gt",
                                    "value_field": "cost_ceiling"
                                }
                            ],
                            "action": "recommend_replace",
                            "weight": 30,
                            "reasoning": "Repair cost exceeds economic threshold"
                        },
                        {
                            "name": "high_margin_replacement",
                            "conditions": [
                                {
                                    "field": "replacement_margin",
                                    "operator": "gt",
                                    "value": 500
                                },
                                {
                                    "field": "repair_probability",
                                    "operator": "lt",
                                    "value": 0.8
                                }
                            ],
                            "action": "recommend_replace",
                            "weight": 25,
                            "reasoning": "High margin replacement opportunity with repair uncertainty"
                        }
                    ]
                },
                "technical_rules": {
                    "priority": 4,
                    "rules": [
                        {
                            "name": "very_old_device",
                            "conditions": [
                                {
                                    "field": "age",
                                    "operator": "gte",
                                    "value": 15
                                }
                            ],
                            "action": "recommend_replace",
                            "weight": 25,
                            "reasoning": "Device exceeds typical lifespan"
                        },
                        {
                            "name": "low_repair_probability",
                            "conditions": [
                                {
                                    "field": "repair_probability",
                                    "operator": "lt",
                                    "value": 0.6
                                }
                            ],
                            "action": "recommend_replace",
                            "weight": 20,
                            "reasoning": "Low technical success probability"
                        },
                        {
                            "name": "high_success_repair",
                            "conditions": [
                                {
                                    "field": "repair_probability",
                                    "operator": "gte",
                                    "value": 0.9
                                },
                                {
                                    "field": "repair_cost",
                                    "operator": "lte",
                                    "value": 500
                                }
                            ],
                            "action": "recommend_repair",
                            "weight": 25,
                            "reasoning": "High success probability with reasonable cost"
                        }
                    ]
                },
                "sustainability_rules": {
                    "priority": 5,
                    "rules": [
                        {
                            "name": "young_device_sustainability",
                            "conditions": [
                                {
                                    "field": "age",
                                    "operator": "lt",
                                    "value": 8
                                },
                                {
                                    "field": "repair_probability",
                                    "operator": "gte",
                                    "value": 0.7
                                }
                            ],
                            "action": "recommend_repair",
                            "weight": 15,
                            "reasoning": "Environmental benefit from extending device lifespan"
                        }
                    ]
                }
            }
        }
        
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default rules file
                os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
                with open(self.rules_file, 'w') as f:
                    json.dump(default_rules, f, indent=2)
                return default_rules
        except Exception as e:
            print(f"Error loading rules: {e}, using defaults")
            return default_rules
    
    def evaluate_rules(self, case_data: Dict) -> Dict:
        """
        Evaluate all business rules against case data
        
        Returns recommendation with detailed reasoning
        """
        
        results = {
            "final_recommendation": None,
            "confidence_score": 0.0,
            "applied_rules": [],
            "rule_weights": {},
            "override_applied": False,
            "reasoning_chain": []
        }
        
        # Sort rule sets by priority
        rule_sets = sorted(
            self.rules["rule_sets"].items(),
            key=lambda x: x[1].get("priority", 999)
        )
        
        total_weight = 0
        recommendation_weights = {"repair": 0, "replace": 0, "manufacturer": 0, "manual": 0}
        
        for rule_set_name, rule_set in rule_sets:
            for rule in rule_set["rules"]:
                if self._evaluate_rule_conditions(rule["conditions"], case_data):
                    results["applied_rules"].append({
                        "rule_set": rule_set_name,
                        "rule_name": rule["name"],
                        "action": rule["action"],
                        "reasoning": rule["reasoning"],
                        "weight": rule.get("weight", 0),
                        "override": rule.get("override", False)
                    })
                    
                    # Check for override rules (safety, etc.)
                    if rule.get("override", False):
                        results["override_applied"] = True
                        results["final_recommendation"] = self._action_to_recommendation(rule["action"])
                        results["confidence_score"] = 1.0
                        results["reasoning_chain"].append(rule["reasoning"])
                        return results
                    
                    # Accumulate weights for non-override rules
                    weight = rule.get("weight", 0)
                    if weight > 0:
                        action = rule["action"]
                        recommendation = self._action_to_recommendation(action)
                        recommendation_weights[recommendation] += weight
                        total_weight += weight
                        results["reasoning_chain"].append(rule["reasoning"])
        
        # Calculate final recommendation based on weights
        if total_weight > 0:
            results["rule_weights"] = recommendation_weights
            
            # Find recommendation with highest weight
            max_weight = max(recommendation_weights.values())
            final_rec = [k for k, v in recommendation_weights.items() if v == max_weight][0]
            
            results["final_recommendation"] = final_rec
            results["confidence_score"] = min(max_weight / total_weight, 1.0)
        else:
            # No rules applied - use default
            results["final_recommendation"] = "repair"
            results["confidence_score"] = 0.5
            results["reasoning_chain"].append("No specific rules matched - using default recommendation")
        
        return results
    
    def _evaluate_rule_conditions(self, conditions: List[Dict], case_data: Dict) -> bool:
        """Evaluate if all conditions in a rule are met"""
        
        for condition in conditions:
            if not self._evaluate_single_condition(condition, case_data):
                return False
        return True
    
    def _evaluate_single_condition(self, condition: Dict, case_data: Dict) -> bool:
        """Evaluate a single rule condition"""
        
        field = condition["field"]
        operator = condition["operator"]
        expected_value = condition.get("value")
        value_field = condition.get("value_field")  # For dynamic comparisons
        match_any = condition.get("match_any", False)
        
        # Get actual value from case data
        actual_value = self._get_nested_value(case_data, field)
        if actual_value is None:
            return False
        
        # Get comparison value
        if value_field:
            expected_value = self._get_nested_value(case_data, value_field)
            if expected_value is None:
                return False
        
        # Evaluate based on operator
        if operator == "equals":
            return actual_value == expected_value
        elif operator == "gt":
            return actual_value > expected_value
        elif operator == "lt":
            return actual_value < expected_value
        elif operator == "gte":
            return actual_value >= expected_value
        elif operator == "lte":
            return actual_value <= expected_value
        elif operator == "contains":
            if isinstance(expected_value, list):
                if match_any:
                    return any(val.lower() in str(actual_value).lower() for val in expected_value)
                else:
                    return all(val.lower() in str(actual_value).lower() for val in expected_value)
            else:
                return str(expected_value).lower() in str(actual_value).lower()
        elif operator == "in_list":
            return actual_value in expected_value
        elif operator == "not_in_list":
            return actual_value not in expected_value
        
        return False
    
    def _get_nested_value(self, data: Dict, field_path: str) -> Any:
        """Get nested value from data using dot notation"""
        
        keys = field_path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _action_to_recommendation(self, action: str) -> str:
        """Convert rule action to recommendation type"""
        
        action_mapping = {
            "recommend_repair": "repair",
            "recommend_replace": "replace", 
            "refer_manufacturer": "manufacturer",
            "manual_review": "manual",
            "escalate": "manual"
        }
        
        return action_mapping.get(action, "repair")
    
    def add_custom_rule(self, rule_set: str, rule: Dict) -> bool:
        """Add a custom rule to the engine"""
        
        try:
            if rule_set not in self.rules["rule_sets"]:
                self.rules["rule_sets"][rule_set] = {"priority": 99, "rules": []}
            
            self.rules["rule_sets"][rule_set]["rules"].append(rule)
            
            # Save updated rules
            with open(self.rules_file, 'w') as f:
                json.dump(self.rules, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding custom rule: {e}")
            return False
    
    def get_rule_summary(self) -> Dict:
        """Get summary of all loaded rules"""
        
        summary = {
            "version": self.rules.get("version", "unknown"),
            "last_updated": self.rules.get("last_updated", "unknown"),
            "rule_sets": {},
            "total_rules": 0
        }
        
        for rule_set_name, rule_set in self.rules["rule_sets"].items():
            rule_count = len(rule_set["rules"])
            summary["rule_sets"][rule_set_name] = {
                "priority": rule_set.get("priority", 999),
                "rule_count": rule_count,
                "rules": [rule["name"] for rule in rule_set["rules"]]
            }
            summary["total_rules"] += rule_count
        
        return summary

# Global business rules engine instance
business_rules = BusinessRulesEngine()
