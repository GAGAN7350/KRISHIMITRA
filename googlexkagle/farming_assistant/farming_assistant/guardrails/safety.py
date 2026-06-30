"""
Safety guardrails applied as before_model_callback to all agents.
Blocks harmful chemical mixing advice, dangerous dosage escalation,
overconfident financial advice, and irrelevant content.
"""

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse

# Patterns that indicate potentially dangerous or harmful requests
BLOCKED_INPUT_PATTERNS = [
    "mix pesticide",
    "mix chemical",
    "mix urea with",
    "mix fertilizer with",
    "double the dose",
    "triple the dose",
    "double the amount",
    "guaranteed profit",
    "guaranteed income",
    "certain cure",
    "100% effective",
    "sell everything",
    "invest all",
    "take loan",
]

SAFE_RESPONSE_TEMPLATE = (
    "I'm sorry, I can't provide advice on that. "
    "For chemical applications, please always follow the manufacturer's label and "
    "consult your local Krishi Vigyan Kendra (KVK) or agricultural extension officer. "
    "They can give you safe, certified guidance specific to your situation."
)

FINANCIAL_SAFE_RESPONSE = (
    "I can share current market price information to help you make an informed decision, "
    "but I'm not able to give guaranteed financial advice. "
    "Agricultural markets can be unpredictable — please consult a local market expert or FPO "
    "(Farmer Producer Organization) before making major selling decisions."
)


async def safety_guardrail(
    callback_context: CallbackContext,
    llm_request,
) -> LlmResponse | None:
    """
    Inspects the latest user message for harmful or dangerous content.
    Returns a safe response if a blocked pattern is detected, else None (allows normal execution).
    """
    user_text = ""
    if llm_request.contents:
        last_content = llm_request.contents[-1]
        if last_content.role == "user" and last_content.parts:
            user_text = last_content.parts[0].text or ""

    user_text_lower = user_text.lower()

    # Check for chemical/dosage safety violations
    chemical_patterns = [p for p in BLOCKED_INPUT_PATTERNS[:8] if p in user_text_lower]
    if chemical_patterns:
        print(f"[SAFETY GUARDRAIL] Blocked chemical/dosage pattern: {chemical_patterns}")
        return LlmResponse(text=SAFE_RESPONSE_TEMPLATE)

    # Check for financial overconfidence patterns
    financial_patterns = [p for p in BLOCKED_INPUT_PATTERNS[8:] if p in user_text_lower]
    if financial_patterns:
        print(f"[SAFETY GUARDRAIL] Flagged financial advice pattern: {financial_patterns}")
        return LlmResponse(text=FINANCIAL_SAFE_RESPONSE)

    # Allow normal execution
    return None
