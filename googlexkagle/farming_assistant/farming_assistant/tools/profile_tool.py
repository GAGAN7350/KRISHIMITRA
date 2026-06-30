"""
FarmerProfile state management tools.
Uses ADK ToolContext.state to persist the farmer's profile
(location, soil type, current crops, preferred language) across messages in a session.

Also provides image context helpers (store_image_context / get_image_context)
so any sub-agent can reuse the image description that was cached by the router's
classify_farm_image tool — avoiding redundant Gemini Vision API calls.
"""

from google.adk.tools import ToolContext


def save_farmer_profile(
    location: str,
    soil_type: str,
    current_crops: str,
    tool_context: ToolContext,
) -> str:
    """
    Saves the farmer's profile to session state so it persists throughout the conversation.
    Call this as soon as you learn the farmer's location, soil type, and crops.

    Args:
        location: The farmer's village, taluk, or city (e.g., "Hubli", "Bengaluru").
        soil_type: The type of soil on the farm (e.g., "red loamy", "black cotton", "sandy").
        current_crops: Comma-separated list of crops the farmer is currently growing (e.g., "tomato, maize").

    Returns:
        Confirmation message.
    """
    tool_context.state["farmer_location"] = location
    tool_context.state["farmer_soil_type"] = soil_type
    tool_context.state["farmer_current_crops"] = [
        c.strip() for c in current_crops.split(",") if c.strip()
    ]
    return (
        f"Profile saved! Location: {location}, Soil: {soil_type}, "
        f"Crops: {current_crops}. I'll remember this throughout our conversation."
    )


def get_farmer_profile(tool_context: ToolContext) -> dict:
    """
    Retrieves the farmer's saved profile from session state.
    Use this at the start of any query to personalize the response.

    Returns:
        A dictionary with farmer_location, farmer_soil_type, farmer_current_crops,
        and farmer_language. Returns empty strings/lists if not yet set.
    """
    return {
        "farmer_location": tool_context.state.get("farmer_location", ""),
        "farmer_soil_type": tool_context.state.get("farmer_soil_type", ""),
        "farmer_current_crops": tool_context.state.get("farmer_current_crops", []),
        "farmer_language": tool_context.state.get("farmer_language", "English"),
    }


def update_farmer_language(language: str, tool_context: ToolContext) -> str:
    """
    Updates the farmer's preferred language in session state.
    Supported languages: English, Kannada, Hindi.

    Args:
        language: The preferred language (e.g., "Kannada", "Hindi", "English").

    Returns:
        Confirmation message in the requested language.
    """
    language = language.strip().capitalize()
    supported = ["English", "Kannada", "Hindi"]
    if language not in supported:
        return f"Language '{language}' not supported. Supported: {', '.join(supported)}"
    tool_context.state["farmer_language"] = language
    confirmations = {
        "Kannada": "ಸರಿ! ನಾನು ಇನ್ನು ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡುತ್ತೇನೆ. (OK! I will now speak in Kannada.)",
        "Hindi": "ठीक है! मैं अब हिंदी में बात करूंगा। (OK! I will now speak in Hindi.)",
        "English": "Got it! I'll respond in English from now on.",
    }
    return confirmations[language]


def add_crop_to_profile(crop: str, tool_context: ToolContext) -> str:
    """
    Adds a new crop to the farmer's existing crop list in session state.

    Args:
        crop: The crop to add (e.g., "ragi", "sugarcane").

    Returns:
        Updated crop list confirmation.
    """
    crops = tool_context.state.get("farmer_current_crops", [])
    crop = crop.strip().lower()
    if crop not in [c.lower() for c in crops]:
        crops.append(crop)
        tool_context.state["farmer_current_crops"] = crops
    return f"Added '{crop}' to your crop list. Current crops: {', '.join(crops)}"


def store_image_context(
    description: str,
    category: str,
    image_source: str,
    tool_context: ToolContext,
) -> str:
    """
    Store an image description in session state for reuse by other agents.

    Call this after describing an image with describe_farm_image(), so other
    agents in the same conversation turn can retrieve it via get_image_context()
    without making a second Gemini Vision API call.

    Args:
        description:  The visual description text returned by describe_farm_image.
        category:     The image category: "disease", "pest", "soil", "irrigation", "general".
        image_source: The original image URL or file path.

    Returns:
        Confirmation message.
    """
    tool_context.state["last_image_source"]      = image_source
    tool_context.state["last_image_category"]    = category
    tool_context.state["last_image_description"] = description
    return f"Image context stored: [{category}] {description[:80]}..."


def get_image_context(tool_context: ToolContext) -> dict:
    """
    Retrieve the cached image description and category from session state.

    Sub-agents should call this BEFORE calling describe_farm_image() to
    check whether the router has already analysed the image. If cached
    context is available (has_image=True), use description directly.

    Returns:
        dict with keys:
            - has_image      : bool — True if cached image context exists
            - category       : The image classification ("disease", "pest", etc.) or ""
            - description    : The visual description of the image or ""
            - image_source   : The original image path/URL or ""
    """
    description = tool_context.state.get("last_image_description", "")
    return {
        "has_image":    bool(description),
        "category":     tool_context.state.get("last_image_category", ""),
        "description":  description,
        "image_source": tool_context.state.get("last_image_source", ""),
    }
