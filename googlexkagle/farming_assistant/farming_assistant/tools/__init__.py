from farming_assistant.tools.profile_tool import (
    save_farmer_profile,
    get_farmer_profile,
    update_farmer_language,
    add_crop_to_profile,
    store_image_context,
    get_image_context,
)
from farming_assistant.tools.weather_tool import (
    get_current_weather,
    get_irrigation_advice,
    get_5day_forecast,
)
from farming_assistant.tools.market_tool import (
    get_mandi_price,
    get_price_trend,
)
from farming_assistant.tools.crop_tool import (
    recommend_crops,
    get_fertilizer_advice,
    get_planting_calendar,
)
from farming_assistant.tools.image_tool import (
    describe_farm_image,
    build_image_part,
    image_to_base64_data_uri,
)
from farming_assistant.tools.image_router_tool import (
    classify_farm_image,
    get_image_context as get_cached_image_context,
    clear_image_context,
)
from farming_assistant.tools.scheme_tool import (
    get_scheme_info,
    list_all_schemes,
    check_scheme_eligibility,
)
from farming_assistant.tools.voice_tool import (
    transcribe_voice_input,
    list_supported_audio_formats,
)
from farming_assistant.tools.agent_switch_tool import (
    list_available_agents,
    switch_to_agent,
    pin_agent,
    unpin_agent,
    get_active_agent_status,
)

__all__ = [
    # Profile
    "save_farmer_profile",
    "get_farmer_profile",
    "update_farmer_language",
    "add_crop_to_profile",
    "store_image_context",
    "get_image_context",
    # Weather
    "get_current_weather",
    "get_irrigation_advice",
    "get_5day_forecast",
    # Market
    "get_mandi_price",
    "get_price_trend",
    # Crop / Soil
    "recommend_crops",
    "get_fertilizer_advice",
    "get_planting_calendar",
    # Image (multimodal)
    "describe_farm_image",
    "build_image_part",
    "image_to_base64_data_uri",
    # Image routing & caching
    "classify_farm_image",
    "get_cached_image_context",
    "clear_image_context",
    # Government Schemes
    "get_scheme_info",
    "list_all_schemes",
    "check_scheme_eligibility",
    # Voice input
    "transcribe_voice_input",
    "list_supported_audio_formats",
    # Agent switching
    "list_available_agents",
    "switch_to_agent",
    "pin_agent",
    "unpin_agent",
    "get_active_agent_status",
]
