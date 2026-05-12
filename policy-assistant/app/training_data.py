# training_data.py

# This list is used by logic.py to show the LLM how to "think"
FEW_SHOT_EXAMPLES = [
    {
        "question": "Should we approve Vendor X for cloud storage?",
        "domain": "Vendor Risk",
        "reasoning_trace": [
            {
                "step_number": 1,
                "title": "Security Verification",
                "analysis": "Checked Vendor X's SOC2 Type II report. They meet the baseline encryption standards."
            },
            {
                "step_number": 2,
                "title": "Data Residency Check",
                "analysis": "Vendor X stores data in the US. Our internal policy 4.2 requires EU residency for this department."
            }
        ],
        "recommendation": "Denied. Move to a vendor with EU data centers.",
        "confidence_score": 0.95
    },
    {
        "question": "Can we launch a marketing app in Japan next month?",
        "domain": "Compliance",
        "reasoning_trace": [
            {
                "step_number": 1,
                "title": "Regulatory Review",
                "analysis": "Evaluated Japan's APPI privacy laws. The app's current consent flow is missing mandatory opt-out links."
            },
            {
                "step_number": 2,
                "title": "Timeline Assessment",
                "analysis": "Legal review takes 14 days. If fixed today, the launch window is still open."
            }
        ],
        "recommendation": "Escalate. Requires immediate UI updates to the consent banner.",
        "confidence_score": 0.88
    }
]