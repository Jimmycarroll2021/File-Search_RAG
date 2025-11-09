"""
Response Modes Configuration
Defines different response modes for tender/sales document analysis
"""

RESPONSE_MODES = {
    "tender": {
        "name": "Tender Response",
        "system_prompt": (
            "You are an expert tender response specialist analyzing tender documents. "
            "Provide compliance-focused, professional responses suitable for formal tender submissions. "
            "Include specific document references, compliance evidence, win themes, and risk mitigation strategies. "
            "Format responses in clear sections with headers. Be thorough and precise in your analysis."
        ),
        "temperature": 0.3,
        "icon": "📋",
        "description": "Formal, polished responses for tender submissions"
    },
    "quick": {
        "name": "Quick Answer",
        "system_prompt": (
            "Provide concise, direct answers focusing on key facts. "
            "Use bullet points for clarity. Keep responses under 200 words unless more detail is explicitly requested. "
            "Be clear and actionable."
        ),
        "temperature": 0.5,
        "icon": "⚡",
        "description": "Brief, bullet-point answers"
    },
    "analysis": {
        "name": "Deep Analysis",
        "system_prompt": (
            "Conduct comprehensive analysis across all relevant documents. "
            "Provide detailed findings with cross-references, comparative analysis, patterns and insights, "
            "and evidence-based recommendations. Use structured sections with specific citations. "
            "Be thorough and analytical in your approach."
        ),
        "temperature": 0.4,
        "icon": "🔍",
        "description": "Detailed insights with citations"
    },
    "strategy": {
        "name": "Strategy Advisor",
        "system_prompt": (
            "Act as a strategic business advisor. Provide strategic recommendations, "
            "competitive positioning analysis, risk and opportunity assessment, and actionable next steps. "
            "Focus on business outcomes and decision-making support. Be forward-thinking and practical."
        ),
        "temperature": 0.6,
        "icon": "💡",
        "description": "Recommendations and next steps"
    },
    "checklist": {
        "name": "Compliance Checklist",
        "system_prompt": (
            "Generate detailed compliance checklists and requirement matrices. "
            "Extract all requirements, create actionable items, identify mandatory vs. optional requirements, "
            "and flag potential gaps. Format as structured checklists with priority indicators "
            "(High/Medium/Low). Be systematic and comprehensive."
        ),
        "temperature": 0.2,
        "icon": "✅",
        "description": "Action items and requirements"
    }
}


def get_mode_config(mode_key: str = None) -> dict:
    """
    Get configuration for a specific response mode.
    Returns quick mode as default if mode not found.

    Args:
        mode_key: Key of the response mode (e.g., 'tender', 'quick')

    Returns:
        Dictionary containing mode configuration
    """
    if mode_key is None or mode_key not in RESPONSE_MODES:
        return RESPONSE_MODES['quick']
    return RESPONSE_MODES[mode_key]
