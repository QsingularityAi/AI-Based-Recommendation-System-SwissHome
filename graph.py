from langgraph.graph import StateGraph, END
from agents import ServiceCaseState, triage_agent, data_enrichment_agent, technical_analyst_agent, economic_analyst_agent, recommendation_engine_agent

def route_after_triage(state):
    """Enhanced routing based on triage decision"""
    decision = state.get("triage_decision", {})
    route = decision.get("route", "normal")
    
    # Handle all possible triage routes
    if route in ["manufacturer", "urgent_manufacturer", "manual_review"]:
        return route
    elif route == "replacement_focus":
        return "data_enrichment"  # Still need data, but will bias toward replacement
    else:
        return "normal"  # Standard workflow

def should_continue_to_recommendation(state):
    """Determine if we have enough data to make a recommendation"""
    # Check if both technical and economic analyses are complete
    has_technical = state.get("repair_probability") is not None
    has_economic = state.get("economic_viability") is not None
    
    if has_technical and has_economic:
        return "recommendation"
    elif not has_technical:
        return "missing_technical"
    else:
        return "missing_economic"

# Create the enhanced workflow graph
def create_workflow():
    # Initialize the state graph
    workflow = StateGraph(ServiceCaseState)
    
    # Add nodes for each agent
    workflow.add_node("triage", triage_agent)
    workflow.add_node("data_enrichment", data_enrichment_agent)
    workflow.add_node("technical_analysis", technical_analyst_agent)
    workflow.add_node("economic_analysis", economic_analyst_agent)
    workflow.add_node("recommendation", recommendation_engine_agent)
    
    # Add special end nodes for different outcomes
    workflow.add_node("manufacturer_referral", lambda state: {
        "recommendation": "manufacturer_referral",
        "justification": state.get("triage_decision", {}).get("reasoning", "Referred to manufacturer"),
        "confidence_score": 1.0
    })
    workflow.add_node("manual_review_required", lambda state: {
        "recommendation": "manual_review",
        "justification": state.get("triage_decision", {}).get("reasoning", "Requires manual review"),
        "confidence_score": 0.0
    })
    
    # Add conditional edges based on triage decision
    workflow.add_conditional_edges(
        "triage",
        route_after_triage,
        {
            "normal": "data_enrichment",
            "manufacturer": "manufacturer_referral",
            "urgent_manufacturer": "manufacturer_referral", 
            "manual_review": "manual_review_required",
            "data_enrichment": "data_enrichment"  # For replacement_focus route
        }
    )
    
    # Parallel processing: data enrichment triggers both analyses
    workflow.add_edge("data_enrichment", "technical_analysis")
    workflow.add_edge("data_enrichment", "economic_analysis")
    
    # Both analyses feed into recommendation
    workflow.add_edge("technical_analysis", "recommendation")
    workflow.add_edge("economic_analysis", "recommendation")
    
    # End nodes
    workflow.add_edge("recommendation", END)
    workflow.add_edge("manufacturer_referral", END)
    workflow.add_edge("manual_review_required", END)
    
    # Set the entry point
    workflow.set_entry_point("triage")
    
    # Compile the graph
    app = workflow.compile()
    
    return app

def get_workflow_visualization():
    """Return a text representation of the workflow for debugging/demo purposes"""
    return """
    Service Recommendation System - Multi-Agent Workflow
    
    1. TRIAGE AGENT
       ├─ Input Validation
       ├─ Safety Check
       ├─ Age/Warranty Assessment
       └─ Routing Decision
    
    2. DATA ENRICHMENT AGENT (Parallel)
       ├─ SAP Integration (Repair Costs)
       ├─ Salesforce Integration (Customer Data)
       └─ PIM/Snowflake Integration (Product Specs)
    
    3. TECHNICAL ANALYST AGENT        4. ECONOMIC ANALYST AGENT
       ├─ Damage Classification       ├─ Cost-Benefit Analysis
       ├─ Repair Probability          ├─ Margin Analysis
       ├─ Complexity Assessment       ├─ Customer Tier Impact
       └─ Risk Evaluation            └─ Sustainability Factor
    
    5. RECOMMENDATION ENGINE
       ├─ Synthesis of All Data
       ├─ Confidence Scoring
       ├─ Override Logic
       └─ Final Decision + Justification
    
    Possible Outcomes:
    • Repair Order (with detailed specifications)
    • Replacement Options (ranked by profitability & preference)
    • Manufacturer Referral
    • Manual Review Required
    """
