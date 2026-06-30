"""
Agent Switch Tool for Krishi Mitra.

Allows farmers (or the router) to explicitly pin, switch to, or release
a specific specialist agent. This solves the problem where a farmer may
want to have an extended conversation with ONE specialist agent rather
than being re-routed every turn.

Three modes:
  1. AUTO (default) — Router decides which agent to use each turn.
  2. PINNED — A specific agent handles ALL incoming messages until unpinned.
  3. DIRECT — Farmer types a command like "switch to disease agent" and
     the router immediately transfers there.

Session state keys used:
  - "pinned_agent"     : str | None — name of the currently pinned agent
  - "agent_mode"       : "auto" | "pinned"
  - "last_active_agent": str | None — last agent that responded

Available agents:
  disease_agent, pest_agent, soil_agent, weather_agent,
  irrigation_agent, market_agent, scheme_agent
"""

from __future__ import annotations
from google.adk.tools import ToolContext


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

AVAILABLE_AGENTS = {
    # Canonical name → (display name, description)
    "disease_agent": (
        "🔬 Disease Expert",
        "Plant diseases — blight, mildew, rust, mosaic virus, bacterial/fungal/viral infections",
    ),
    "pest_agent": (
        "🐛 Pest Expert",
        "Insects & pests — aphids, stem borers, armyworms, whiteflies, mites, locusts",
    ),
    "soil_agent": (
        "🪨 Soil & Crop Expert",
        "Soil health, crop recommendations, NPK fertilizer advice, planting calendars",
    ),
    "weather_agent": (
        "🌤️ Weather Expert",
        "Weather forecasts, rain alerts, monsoon guidance, temperature & humidity",
    ),
    "irrigation_agent": (
        "💧 Irrigation Expert",
        "Watering schedules, drip/sprinkler systems, water stress analysis, PMKSY subsidy",
    ),
    "market_agent": (
        "📈 Market Expert",
        "Live mandi prices, APMC rates, MSP comparison, selling guidance",
    ),
    "scheme_agent": (
        "📋 Govt. Scheme Expert",
        "PM-KISAN, PMFBY crop insurance, PM-KUSUM solar pump, KCC loan, PM-KMY pension",
    ),
}

# Aliases: things farmers might type → canonical agent name
AGENT_ALIASES = {
    # Disease
    "disease": "disease_agent", "plant disease": "disease_agent",
    "leaf disease": "disease_agent", "blight": "disease_agent",
    "fungi": "disease_agent", "fungal": "disease_agent",
    # Pest
    "pest": "pest_agent", "insect": "pest_agent", "bug": "pest_agent",
    "caterpillar": "pest_agent", "aphid": "pest_agent",
    # Soil
    "soil": "soil_agent", "crop": "soil_agent", "fertilizer": "soil_agent",
    "npk": "soil_agent", "sowing": "soil_agent", "planting": "soil_agent",
    # Weather
    "weather": "weather_agent", "rain": "weather_agent",
    "forecast": "weather_agent", "monsoon": "weather_agent",
    # Irrigation
    "irrigation": "irrigation_agent", "water": "irrigation_agent",
    "drip": "irrigation_agent", "watering": "irrigation_agent",
    # Market
    "market": "market_agent", "price": "market_agent",
    "mandi": "market_agent", "sell": "market_agent",
    # Scheme
    "scheme": "scheme_agent", "government": "scheme_agent",
    "subsidy": "scheme_agent", "pm-kisan": "scheme_agent",
    "kisan": "scheme_agent", "insurance": "scheme_agent",
}


def _resolve_agent_name(name: str) -> str | None:
    """Resolve a human-typed name to a canonical agent name."""
    name_lower = name.lower().strip()
    # Direct match
    if name_lower in AVAILABLE_AGENTS:
        return name_lower
    # Alias match
    if name_lower in AGENT_ALIASES:
        return AGENT_ALIASES[name_lower]
    # Partial match on canonical names
    for canonical in AVAILABLE_AGENTS:
        if name_lower in canonical or canonical.replace("_agent", "") in name_lower:
            return canonical
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Tool Functions
# ─────────────────────────────────────────────────────────────────────────────

def list_available_agents(tool_context: ToolContext) -> dict:
    """
    List all available specialist agents that the farmer can switch to.

    Returns a formatted menu of all specialist agents with their names,
    icons, and descriptions. Use this when the farmer asks "what can you do?"
    or wants to know which expert to talk to.

    Returns:
        dict with 'agents' list and 'current_mode' string.
    """
    pinned  = tool_context.state.get("pinned_agent", None)
    mode    = tool_context.state.get("agent_mode", "auto")
    last    = tool_context.state.get("last_active_agent", None)

    agents_list = []
    for name, (display, desc) in AVAILABLE_AGENTS.items():
        agents_list.append({
            "agent_name":   name,
            "display_name": display,
            "description":  desc,
            "is_pinned":    (name == pinned),
            "is_last_used": (name == last),
        })

    status = (
        f"Currently PINNED to: {AVAILABLE_AGENTS[pinned][0]}"
        if pinned and mode == "pinned"
        else "Mode: AUTO (router decides which expert to use)"
    )

    return {
        "agents":       agents_list,
        "current_mode": mode,
        "pinned_agent": pinned,
        "status":       status,
        "instructions": (
            "To switch to a specific expert, say: 'switch to weather agent' or "
            "'pin disease agent'. To go back to auto mode, say: 'auto mode' or "
            "'unpin agent'."
        ),
    }


def switch_to_agent(agent_name: str, tool_context: ToolContext) -> dict:
    """
    Switch to a specific specialist agent for this conversation turn only.

    Use this when the farmer explicitly asks to talk to a specific expert,
    e.g., "switch to market agent", "I want to talk to the disease expert".
    The router will transfer immediately to that agent for THIS turn only.
    The mode remains AUTO after the turn completes.

    Args:
        agent_name: Name of the agent to switch to. Can be a natural name like
                    "disease", "weather", "market", or full name like
                    "disease_agent", "weather_agent".

    Returns:
        dict with 'success', 'target_agent', 'display_name', and 'message'.
    """
    resolved = _resolve_agent_name(agent_name)

    if not resolved:
        available = ", ".join(
            f'"{k.replace("_agent", "")}"' for k in AVAILABLE_AGENTS
        )
        return {
            "success":     False,
            "agent_name":  agent_name,
            "error":       f"Agent '{agent_name}' not found.",
            "available":   available,
            "message":     (
                f"I couldn't find an agent called '{agent_name}'. "
                f"Available experts: {available}. "
                f"Try: 'switch to weather agent' or 'switch to market'."
            ),
        }

    display_name, desc = AVAILABLE_AGENTS[resolved]
    tool_context.state["requested_agent"] = resolved
    tool_context.state["last_active_agent"] = resolved

    return {
        "success":      True,
        "target_agent": resolved,
        "display_name": display_name,
        "description":  desc,
        "message":      (
            f"Switching you to {display_name}! "
            f"They specialise in: {desc}."
        ),
    }


def pin_agent(agent_name: str, tool_context: ToolContext) -> dict:
    """
    Pin a specific specialist agent so ALL future messages go to that agent.

    Use this when the farmer says "keep talking to disease expert" or
    "I only want weather information for now". Pinning overrides automatic
    routing until the farmer says "unpin" or "auto mode".

    Args:
        agent_name: Name of the agent to pin (e.g., "disease", "weather_agent").

    Returns:
        dict with 'success', 'pinned_agent', 'display_name', and 'message'.
    """
    resolved = _resolve_agent_name(agent_name)

    if not resolved:
        return {
            "success":  False,
            "error":    f"Agent '{agent_name}' not recognised.",
            "message":  (
                f"I couldn't find '{agent_name}'. "
                f"Say 'list agents' to see all available experts."
            ),
        }

    tool_context.state["pinned_agent"]  = resolved
    tool_context.state["agent_mode"]    = "pinned"
    display_name, desc = AVAILABLE_AGENTS[resolved]

    return {
        "success":     True,
        "pinned_agent": resolved,
        "display_name": display_name,
        "message":     (
            f"✅ Pinned to {display_name}. "
            f"All your questions will now go to this expert until you say "
            f"'auto mode' or 'unpin'. "
            f"They cover: {desc}."
        ),
    }


def unpin_agent(tool_context: ToolContext) -> dict:
    """
    Unpin any currently pinned agent and return to automatic routing mode.

    Use this when the farmer says "auto mode", "unpin", "back to normal",
    or "let the assistant decide". After unpinning, the router will again
    automatically decide which specialist to call for each message.

    Returns:
        dict with 'success' and 'message'.
    """
    was_pinned = tool_context.state.get("pinned_agent", None)
    tool_context.state["pinned_agent"] = None
    tool_context.state["agent_mode"]   = "auto"
    tool_context.state.pop("requested_agent", None)

    if was_pinned and was_pinned in AVAILABLE_AGENTS:
        prev_name = AVAILABLE_AGENTS[was_pinned][0]
        msg = (
            f"Unpinned from {prev_name}. "
            f"I'll now automatically decide which expert is best for each of your questions. 🔄"
        )
    else:
        msg = "Already in auto mode. I'll route your questions to the best expert automatically. 🔄"

    return {"success": True, "message": msg, "agent_mode": "auto"}


def get_active_agent_status(tool_context: ToolContext) -> dict:
    """
    Get the current agent routing status.

    Returns which agent is active/pinned, the mode (auto vs pinned),
    and the last agent that handled a message. Use this at the start
    of each router turn to check if a specific agent is pinned.

    Returns:
        dict with 'mode', 'pinned_agent', 'last_active_agent',
        'should_override_routing' (True if agent is pinned and routing
        should be skipped), and 'target_agent' to use if overriding.
    """
    mode    = tool_context.state.get("agent_mode", "auto")
    pinned  = tool_context.state.get("pinned_agent", None)
    last    = tool_context.state.get("last_active_agent", None)
    requested = tool_context.state.get("requested_agent", None)

    # Clear one-time requested agent after reading
    if requested:
        tool_context.state.pop("requested_agent", None)

    should_override = mode == "pinned" and pinned is not None
    target = requested or (pinned if should_override else None)

    return {
        "mode":                   mode,
        "pinned_agent":           pinned,
        "last_active_agent":      last,
        "requested_agent":        requested,
        "should_override_routing": should_override,
        "target_agent":           target,
        "status_message": (
            f"PINNED to {AVAILABLE_AGENTS[pinned][0]}" if should_override
            else "AUTO routing mode"
        ),
    }
