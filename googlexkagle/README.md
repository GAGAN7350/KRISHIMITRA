# Krishi Mitra: Multi-Agent Multimodal Farming Assistant

Krishi Mitra (Friend of Farming) is an intelligent, localized agricultural extension system designed for smallholder farmers. Built on the Google Agent Development Kit (ADK) and powered by Gemini 2.0 Flash, it utilizes a decoupled multi-agent architecture to provide specialized support in agricultural diagnostics, market analytics, meteorology, and government services. 

The system supports multilingual inputs in English, Kannada, and Hindi. It also includes multimodal capabilities, allowing farmers to upload images of diseased leaves, insect pests, or soil profiles for visual analysis.

---

## System Architecture

```
                  [ Farmer Input: Text or Image ]
                                 |
                                 v
                         [ Router Agent ]
                                 |
       +---------+-------+-------+---+-------+-------+---------+
       |         |       |           |       |       |         |
       v         v       v           v       v       v         v
   [Disease]  [Pest]  [Soil]     [Weather] [Irrig] [Market] [Scheme]
    Agent     Agent   Agent       Agent     Agent   Agent    Agent
       |         |       |           |       |       |         |
       v         v       v           v       v       v         v
    (Vision)  (Vision)(NPK/Crop)  (Forecast)(Water) (Mandi) (Subsidies)
       |         |       |           |       |       |         |
       +---------+-------+-------+---+-------+-------+---------+
                                 |
                                 v
                    [ Unified Response Engine ]
                                 |
                                 v
                         [ Farmer Output ]
```

---

## Repository Structure

```
farming_assistant/
│
├── farming_assistant/
│   ├── sub_agents/
│   │   ├── __init__.py
│   │   ├── disease_agent.py          (Fungal and bacterial pathogen diagnostics)
│   │   ├── pest_agent.py             (Insect tracking and IPM rules)
│   │   ├── soil_agent.py             (Fertilizer dosing and crop selection)
│   │   ├── weather_agent.py          (Forecast assessments)
│   │   ├── irrigation_agent.py       (Precipitation-aware watering schedules)
│   │   ├── market_agent.py           (APMC mandi price calculations)
│   │   └── scheme_agent.py           (Welfare and loan eligibility checkers)
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── image_tool.py             (Gemini Vision integrations)
│   │   ├── scheme_tool.py            (Subsidy database engine)
│   │   ├── weather_tool.py           (OpenWeatherMap client)
│   │   ├── market_tool.py            (Agmarknet APMC pricing client)
│   │   └── profile_tool.py           (Session state profile persistence)
│   │
│   └── agent.py                      (Master Router configurations)
│
├── krishi_mitra_kaggle.ipynb         (Clean, 19-cell runtime notebook)
└── requirements.txt                  (Dependency definitions)
```

---

## Key Features

### 1. Decoupled 7-Agent Architecture
By separating concerns into specialized agents, the system reduces system prompt token overhead, avoids context dilution, and improves attention focus for safety-critical tasks.

### 2. Multimodal Agriculture Scanner
Integrates the Gemini Vision API directly into diagnostic agents. The system downloads user-submitted photos (or public URLs) and extracts crop type, visual symptoms (spots, wilt), pests, or soil color before generating advice.

### 3. Native Session Memory
Utilizes ADK ToolContext state parameters to track the farmer's location, soil type, crop portfolio, and language preference across conversation turns.

### 4. Real-time API Integration
*   **OpenWeatherMap**: Fetches live 5-day forecasts. The Irrigation Agent analyzes predictions to recommend skipping watering runs if precipitation is expected.
*   **Agmarknet**: Fetches pricing data from the Government of India APMC network, converting unstructured inputs into formal commodity database matches.

### 5. Automated Safety Guardrails
Intercepts input strings via callback checks. The system blocks requests regarding unsafe tank-mixing of pesticides, alterations to manufacturer chemical dosages, or overconfident profit projections, directing farmers to local Krishi Vigyan Kendras (KVK).

---

## Installation and Local Setup

1. Clone this repository to your workspace.

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your environment variables in your terminal:
```bash
export GOOGLE_API_KEY="your_gemini_api_key"
export OPENWEATHER_API_KEY="your_open_weather_key"
export AGMARKNET_API_KEY="your_agmarknet_api_key"
```

4. Run the Python application or load the modular workspace:
```python
from farming_assistant.agent import root_agent
# Execute using ADK runners
```

---

## Run on Kaggle

To run the unified notebook:

1. Open `krishi_mitra_kaggle.ipynb` in Kaggle.
2. In the right-hand panel (Settings), toggle **Internet ON** (required for vision downloads, weather queries, and mandi API connections).
3. In the top menu, go to **Add-ons -> Secrets** and add the following keys:
   - `geminie api key` (Your Gemini API key)
   - `weather api key` (OpenWeatherMap API key)
   - `agmarket api key` (Government of India Agmarknet API key)
4. Select **Run All**.

Note: If weather or mandi keys are not provided, the notebook will use rate-limited public demo endpoints to ensure the code executes successfully.
