"""
Krishi Mitra — Multi-Agent Farming Assistant
Entry point for running the farming assistant via CLI or ADK web UI.

Usage:
  python main.py               # Interactive CLI mode (text + image + voice)
  adk web                      # Launch browser chat UI (from farming_assistant/ directory)
  adk run farming_assistant    # ADK terminal runner

CLI Interaction Guide:
  - Type any farming question in English, Hindi, or Kannada.
  - To send an IMAGE:   type  image:/path/to/photo.jpg  or  image:https://url.com/photo.jpg
  - To send a VOICE:    type  voice:/path/to/audio.wav  or  voice:https://url.com/audio.mp3
  - To switch agents:   type  switch:weather   or  pin:disease  or  unpin
  - To list agents:     type  agents
  - To quit:            type  quit  or  exit
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from farming_assistant.agent import root_agent
from google.genai import types


APP_NAME  = "krishi_mitra"
USER_ID   = "farmer_001"
SESSION_ID = "session_001"

# ─────────────────────────────────────────────────────────────────────────────
# ANSI colours for CLI
# ─────────────────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def print_banner():
    print("\n" + "═" * 64)
    print(f"  {BOLD}🌾  KRISHI MITRA — Your AI Farming Assistant  🌾{RESET}")
    print("═" * 64)
    print(f"  {CYAN}Supports: Text | Images | Voice | 9 Languages{RESET}")
    print(f"  {GREEN}Type 'help' for usage guide | 'quit' to exit{RESET}")
    print("═" * 64 + "\n")


def print_help():
    print(f"""
{BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📖  HOW TO USE KRISHI MITRA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}

{YELLOW}💬 TEXT QUESTIONS:{RESET}
  Just type your question normally.
  Examples:
    → My tomato leaves have brown spots, what disease is it?
    → What crop should I plant in black cotton soil this Kharif?
    → What is the price of onion in Hubli market today?
    → How do I apply for PM-KISAN?
    → Will it rain this week in Bengaluru?
    → मेरी फसल पर सफेद कीड़े हैं क्या करूं?  (Hindi)
    → ನನ್ನ ಟೊಮೆಟೊ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ  (Kannada)

{YELLOW}🖼️  IMAGE (Photo of leaf/soil/pest/field):{RESET}
  Type:  image:<path or URL>
  Examples:
    → image:C:\\Users\\gagan\\Pictures\\leaf_disease.jpg
    → image:C:/Users/gagan/Downloads/soil_sample.png
    → image:https://example.com/pest_photo.jpg
  
  You can also add a question after the image:
    → image:C:\\leaf.jpg What disease is this?
    → image:C:\\field.jpg Is my crop waterlogged?

{YELLOW}🎙️  VOICE (Audio file in any Indian language):{RESET}
  Type:  voice:<path or URL>
  Supported formats: .wav  .mp3  .ogg  .flac  .m4a  .webm
  Supported languages: Hindi, Kannada, Telugu, Tamil, Marathi,
                       Bengali, Gujarati, Punjabi, English
  Examples:
    → voice:C:\\Users\\gagan\\Downloads\\question.wav
    → voice:C:/recordings/farm_query.mp3

{YELLOW}🔀  AGENT SWITCHING:{RESET}
  switch:<agent>   → Talk to a specific expert for ONE message
  pin:<agent>      → Lock all messages to that expert
  unpin            → Go back to automatic routing
  agents           → Show list of all available experts

  Agent names you can use:
    disease  |  pest  |  soil  |  weather  |  irrigation
    market   |  scheme  (or: govt / subsidy / kisan)

  Examples:
    → switch:weather         (one-turn weather query)
    → pin:market             (stay with market agent)
    → switch:disease         (switch to disease expert)
    → unpin                  (back to auto mode)

{YELLOW}🌐  LANGUAGES:{RESET}
  Type in English, Hindi, or Kannada — the agent will respond
  in the same language. Voice supports 9 Indian languages.

{YELLOW}🚨  EMERGENCY:{RESET}
  PM-Kisan Helpline: 155261
  Kisan Call Centre: 1800-180-1551 (6 AM – 10 PM, toll-free)

{YELLOW}⌨️   COMMANDS:{RESET}
  help     → Show this guide
  agents   → List all specialist agents
  quit     → Exit Krishi Mitra
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


def parse_user_input(raw: str) -> list:
    """
    Parse the user's raw CLI input into a list of google.genai.types.Part objects.

    Handles:
      - Plain text  → types.Part.from_text(text)
      - image:<src> [optional question] → image Part + optional text Part
      - voice:<src> → text Part asking agent to transcribe
      - switch:<agent> → text command
      - pin:<agent>   → text command
      - unpin / agents / help → text command
    """
    raw = raw.strip()
    parts = []

    # ── IMAGE input ──────────────────────────────────────────────────────────
    if raw.lower().startswith("image:"):
        rest = raw[6:].strip()  # strip "image:"
        # Check if there's an optional text question after the path
        # Split on first space that comes after the file path/URL
        # Strategy: if it starts with http, split on first space after URL
        if rest.startswith("http://") or rest.startswith("https://"):
            parts_raw = rest.split(" ", 1)
            src = parts_raw[0]
            question = parts_raw[1].strip() if len(parts_raw) > 1 else ""
        else:
            # Local path — might contain spaces, try to find the file
            # Heuristic: find the last segment that looks like an extension
            import shlex
            try:
                tokens = shlex.split(rest)
                # Find where the path ends (first token with image extension)
                src = ""
                question = ""
                for i, t in enumerate(tokens):
                    if any(t.lower().endswith(ext) for ext in
                           [".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"]):
                        src = t
                        question = " ".join(tokens[i+1:])
                        break
                if not src:
                    src = tokens[0]
                    question = " ".join(tokens[1:])
            except Exception:
                src = rest
                question = ""

        # Build image Part
        try:
            from farming_assistant.tools.image_tool import load_image_bytes
            import base64
            raw_bytes, mime = load_image_bytes(src)
            b64 = base64.b64encode(raw_bytes).decode("ascii")
            img_part = types.Part(
                inline_data=types.Blob(mime_type=mime, data=raw_bytes)
            )
            parts.append(img_part)
            # Prepend a text instruction for the router
            prompt = (
                f"[IMAGE UPLOADED: {src}] "
                + (question if question else "Please analyse this farm image and help me.")
            )
            parts.insert(0, types.Part.from_text(text=prompt))
            print(f"  {CYAN}📷 Image loaded: {src}{RESET}")
        except Exception as e:
            print(f"  ❌ Could not load image: {e}")
            parts.append(types.Part.from_text(
                text=f"I tried to upload image from '{src}' but got error: {e}. Please check the path."
            ))

    # ── VOICE input ──────────────────────────────────────────────────────────
    elif raw.lower().startswith("voice:"):
        src = raw[6:].strip()
        print(f"  {CYAN}🎙️  Voice file: {src} — transcribing...{RESET}")
        # Tell the agent to transcribe this voice file
        parts.append(types.Part.from_text(
            text=f"[VOICE MESSAGE] Please transcribe and respond to this voice recording: {src}"
        ))

    # ── SWITCH command ────────────────────────────────────────────────────────
    elif raw.lower().startswith("switch:"):
        agent = raw[7:].strip()
        parts.append(types.Part.from_text(
            text=f"switch to {agent} agent"
        ))

    # ── PIN command ────────────────────────────────────────────────────────────
    elif raw.lower().startswith("pin:"):
        agent = raw[4:].strip()
        parts.append(types.Part.from_text(
            text=f"pin {agent} agent"
        ))

    # ── UNPIN command ─────────────────────────────────────────────────────────
    elif raw.lower() in ("unpin", "auto", "auto mode"):
        parts.append(types.Part.from_text(text="unpin agent, go to auto mode"))

    # ── LIST AGENTS command ───────────────────────────────────────────────────
    elif raw.lower() in ("agents", "list agents", "show agents", "experts"):
        parts.append(types.Part.from_text(text="list available agents"))

    # ── HELP command ──────────────────────────────────────────────────────────
    elif raw.lower() == "help":
        print_help()
        return []  # Don't send to agent

    # ── Plain text ────────────────────────────────────────────────────────────
    else:
        parts.append(types.Part.from_text(text=raw))

    return parts


async def main():
    print_banner()

    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file.")
        print("   Add your Google AI Studio API key to farming_assistant/.env")
        print("   Get your key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    # Set up runner and session
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    print(f"{GREEN}✅ Krishi Mitra is ready! Type 'help' for usage guide.{RESET}\n")

    while True:
        try:
            user_input = input(f"{BOLD}You:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{GREEN}Goodbye! Happy farming! 🌱{RESET}")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye", "goodbye"):
            print(f"{GREEN}Goodbye! Happy farming! 🌱{RESET}")
            break

        # Parse input into Parts (text / image / voice)
        parts = parse_user_input(user_input)
        if not parts:
            continue  # e.g. 'help' already printed, no agent call needed

        new_msg = types.Content(role="user", parts=parts)

        print(f"\n{YELLOW}Krishi Mitra:{RESET} ", end="", flush=True)
        try:
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=new_msg,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        response_text = ""
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                response_text += part.text
                        print(response_text)
                    break
        except Exception as e:
            print(f"\n[Error] {e}")
            print("Please try again or rephrase your question.")

        print()  # blank line between turns


if __name__ == "__main__":
    asyncio.run(main())
