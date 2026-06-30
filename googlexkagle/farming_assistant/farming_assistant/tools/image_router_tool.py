"""
Image Router Tool for Krishi Mitra.

Provides TWO ADK-compatible tool functions used by the root Router Agent:

  1. classify_farm_image(image_url_or_path, tool_context)
     - Calls Gemini Vision to classify the farm image into one of:
       "disease", "pest", "soil", "irrigation", "market", "general"
     - Stores the visual description AND the routing category in session
       state so sub-agents can reuse it without a second API call.

  2. get_image_context(tool_context)
     - Retrieved by any sub-agent to get the cached image description
       from session state (set by classify_farm_image).

  3. clear_image_context(tool_context)
     - Clears the cached image context after a conversation turn.
"""

from __future__ import annotations

import os
import io
from typing import Optional

from google.adk.tools import ToolContext


# ─────────────────────────────────────────────────────────────────────────────
# Routing classification labels → specialist agent names
# ─────────────────────────────────────────────────────────────────────────────

IMAGE_CATEGORY_TO_AGENT = {
    "disease":   "disease_agent",
    "pest":      "pest_agent",
    "soil":      "soil_agent",
    "irrigation":"irrigation_agent",
    "general":   None,   # Router will ask farmer for more context
}

# System prompt given to Gemini for classification
_CLASSIFICATION_PROMPT = """You are an expert Indian agricultural AI assistant.
A farmer has uploaded a photograph. Your task is to:

1. Carefully analyse the image.
2. Classify it into EXACTLY ONE of these categories:
   - "disease"   : The image shows leaves, stems, or fruits with disease symptoms
                   (spots, yellowing, powdery coating, rot, blight, mosaic patterns).
   - "pest"      : The image shows insects, caterpillars, worms, aphids, whiteflies,
                   mites, or clear pest-damage patterns (chewed leaves, boreholes, frass).
   - "soil"      : The image shows bare soil, soil samples, field ground texture,
                   or soil colour.
   - "irrigation": The image shows a crop field, wilting plants, waterlogged soil,
                   dry cracked earth, or irrigation infrastructure.
   - "general"   : The image is a general farm/field photo that does not clearly fit
                   the above categories.

3. Provide:
   a. CATEGORY: one of the five labels above (lowercase, no quotes).
   b. DESCRIPTION: 3-5 sentences describing what you see in practical farming terms —
      crop type (if visible), symptoms, colour, texture, and any urgent observations.
   c. CONFIDENCE: high / medium / low

Format your entire response EXACTLY as:
CATEGORY: <label>
DESCRIPTION: <3-5 sentences>
CONFIDENCE: <high|medium|low>
"""


def _parse_classification_response(text: str) -> dict:
    """Parse the structured classification response from Gemini."""
    result = {
        "category": "general",
        "description": text.strip(),
        "confidence": "low",
        "agent": None,
    }

    lines = text.strip().splitlines()
    for line in lines:
        if line.upper().startswith("CATEGORY:"):
            cat = line.split(":", 1)[1].strip().lower()
            if cat in IMAGE_CATEGORY_TO_AGENT:
                result["category"] = cat
                result["agent"] = IMAGE_CATEGORY_TO_AGENT[cat]
        elif line.upper().startswith("DESCRIPTION:"):
            result["description"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("CONFIDENCE:"):
            result["confidence"] = line.split(":", 1)[1].strip().lower()

    return result


def classify_farm_image(image_url_or_path: str, tool_context: ToolContext) -> dict:
    """
    Classify a farm photograph and cache its description in session state.

    This is the FIRST tool the Router Agent should call when a farmer
    uploads an image. It:
      - Sends the image to Gemini Vision with a classification prompt.
      - Returns the category (disease / pest / soil / irrigation / general)
        and the agent to route to.
      - Caches the visual description in session state under
        "last_image_description" and "last_image_category" so sub-agents
        can call get_image_context() instead of re-processing the image.

    Args:
        image_url_or_path: Public URL or local file path to the uploaded image.

    Returns:
        dict with keys:
            - category      : "disease" | "pest" | "soil" | "irrigation" | "general"
            - suggested_agent: agent name to route to (e.g., "disease_agent")
            - description   : Visual description of what Gemini sees in the image
            - confidence    : "high" | "medium" | "low"
            - image_source  : The source string that was processed
            - error         : Set only if classification failed
    """
    try:
        import google.generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            return {
                "error": "GOOGLE_API_KEY not set.",
                "image_source": image_url_or_path,
                "category": "general",
                "suggested_agent": None,
            }

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Load image bytes
        from farming_assistant.tools.image_tool import load_image_bytes
        raw, mime = load_image_bytes(image_url_or_path)

        import PIL.Image as PILImage
        pil_img = PILImage.open(io.BytesIO(raw))

        response = model.generate_content([_CLASSIFICATION_PROMPT, pil_img])
        parsed = _parse_classification_response(response.text)

        # ── Cache in session state ──────────────────────────────────────────
        tool_context.state["last_image_source"]      = image_url_or_path
        tool_context.state["last_image_category"]    = parsed["category"]
        tool_context.state["last_image_description"] = parsed["description"]
        tool_context.state["last_image_confidence"]  = parsed["confidence"]
        # ───────────────────────────────────────────────────────────────────

        return {
            "category":       parsed["category"],
            "suggested_agent": parsed["agent"],
            "description":    parsed["description"],
            "confidence":     parsed["confidence"],
            "image_source":   image_url_or_path,
        }

    except FileNotFoundError as e:
        return {
            "error": str(e),
            "image_source": image_url_or_path,
            "category": "general",
            "suggested_agent": None,
        }
    except Exception as e:
        return {
            "error": f"Image classification failed: {str(e)}",
            "image_source": image_url_or_path,
            "category": "general",
            "suggested_agent": None,
        }


def get_image_context(tool_context: ToolContext) -> dict:
    """
    Retrieve the cached image description and category from session state.

    Sub-agents should call this BEFORE calling describe_farm_image() to
    avoid redundant Gemini Vision API calls. If the Router has already
    classified the image, this returns the cached description instantly.

    Returns:
        dict with keys:
            - has_image      : bool — True if there is cached image context
            - category       : The classification category or ""
            - description    : The visual description or ""
            - image_source   : The original image path/URL or ""
            - confidence     : "high" | "medium" | "low" | ""
    """
    category    = tool_context.state.get("last_image_category", "")
    description = tool_context.state.get("last_image_description", "")
    source      = tool_context.state.get("last_image_source", "")
    confidence  = tool_context.state.get("last_image_confidence", "")

    return {
        "has_image":    bool(description),
        "category":     category,
        "description":  description,
        "image_source": source,
        "confidence":   confidence,
    }


def clear_image_context(tool_context: ToolContext) -> str:
    """
    Clear the cached image context from session state.

    Call this at the start of a new conversation turn if the farmer
    sends a new image (to avoid stale cached data being used).

    Returns:
        Confirmation message.
    """
    tool_context.state.pop("last_image_source", None)
    tool_context.state.pop("last_image_category", None)
    tool_context.state.pop("last_image_description", None)
    tool_context.state.pop("last_image_confidence", None)
    return "Image context cleared. Ready to process a new image."
