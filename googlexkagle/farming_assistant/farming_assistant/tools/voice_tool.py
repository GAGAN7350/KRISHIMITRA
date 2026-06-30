"""
Voice Input Tool for Krishi Mitra.

Provides voice-to-text transcription using Gemini 2.0 Flash's native
audio understanding capability — no separate Speech-to-Text API needed.

The tool accepts:
  - A local audio file path (.wav, .mp3, .ogg, .flac, .m4a, .webm)
  - A public audio URL

It sends the audio to Gemini 2.0 Flash with a farming-context prompt
and returns the transcribed text plus a language detection hint.

Supports Indian languages: Hindi, Kannada, Telugu, Tamil, Marathi,
Bengali, Gujarati, Punjabi, and English.
"""

from __future__ import annotations

import os
import mimetypes
from pathlib import Path


# Supported audio MIME types
SUPPORTED_AUDIO_TYPES = {
    ".wav":  "audio/wav",
    ".mp3":  "audio/mpeg",
    ".ogg":  "audio/ogg",
    ".flac": "audio/flac",
    ".m4a":  "audio/mp4",
    ".webm": "audio/webm",
    ".aac":  "audio/aac",
    ".aiff": "audio/aiff",
    ".opus": "audio/opus",
}

_TRANSCRIPTION_PROMPT = """You are a voice assistant for Indian farmers (Krishi Mitra).
A farmer has sent a voice message. Please:

1. Transcribe the audio EXACTLY as spoken (preserve the original language words).
2. Detect the language: English, Hindi, Kannada, Telugu, Tamil, Marathi, Bengali,
   Gujarati, Punjabi, or Other.
3. Provide an English translation if the language is not English.

Format your response EXACTLY as:
LANGUAGE: <detected language>
TRANSCRIPT: <exact transcription in original language>
TRANSLATION: <English translation, or "N/A" if already in English>
FARMING_CONTEXT: <1 sentence summarising what the farmer is asking about>
"""


def _detect_audio_mime(source: str, data: bytes) -> str:
    """Detect MIME type from file extension or default to audio/wav."""
    ext = Path(source).suffix.lower()
    if ext in SUPPORTED_AUDIO_TYPES:
        return SUPPORTED_AUDIO_TYPES[ext]
    # Try python mimetypes
    guessed, _ = mimetypes.guess_type(source)
    if guessed and guessed.startswith("audio/"):
        return guessed
    return "audio/wav"


def _load_audio_bytes(source: str) -> tuple[bytes, str]:
    """Load audio from a local file or URL. Returns (raw_bytes, mime_type)."""
    if source.startswith("http://") or source.startswith("https://"):
        import requests
        resp = requests.get(source, timeout=20)
        resp.raise_for_status()
        raw = resp.content
        ct = resp.headers.get("Content-Type", "").split(";")[0].strip()
        mime = ct if ct.startswith("audio/") else _detect_audio_mime(source, raw)
        return raw, mime
    else:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {source}")
        raw = path.read_bytes()
        mime = _detect_audio_mime(source, raw)
        return raw, mime


def transcribe_voice_input(audio_path_or_url: str) -> dict:
    """
    Transcribe a farmer's voice message using Gemini 2.0 Flash.

    Supports audio in Hindi, Kannada, Telugu, Tamil, Marathi, Bengali,
    Gujarati, Punjabi, and English. Returns a transcription, language
    detection, and English translation.

    Args:
        audio_path_or_url: Local file path or public URL to the audio file.
            Supported formats: .wav, .mp3, .ogg, .flac, .m4a, .webm, .aac

    Returns:
        dict with keys:
            - transcript     : Exact transcription in original language
            - language       : Detected language (e.g., "Hindi", "Kannada")
            - translation    : English translation (or same as transcript if English)
            - farming_context: Brief English summary of what the farmer is asking
            - audio_source   : The source that was processed
            - error          : Set only if transcription failed
    """
    try:
        import google.generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            return {
                "error": "GOOGLE_API_KEY not set.",
                "audio_source": audio_path_or_url,
            }

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        raw, mime = _load_audio_bytes(audio_path_or_url)

        # Build the multimodal content with audio inline data
        # Gemini Python SDK accepts a flat dict: {"mime_type": ..., "data": raw_bytes}
        audio_part = {"mime_type": mime, "data": raw}

        response = model.generate_content([_TRANSCRIPTION_PROMPT, audio_part])
        text = response.text.strip()

        # Parse structured response
        result = {
            "transcript":      "",
            "language":        "Unknown",
            "translation":     "",
            "farming_context": "",
            "audio_source":    audio_path_or_url,
        }

        for line in text.splitlines():
            if line.upper().startswith("LANGUAGE:"):
                result["language"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("TRANSCRIPT:"):
                result["transcript"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("TRANSLATION:"):
                val = line.split(":", 1)[1].strip()
                result["translation"] = "" if val.upper() == "N/A" else val
            elif line.upper().startswith("FARMING_CONTEXT:"):
                result["farming_context"] = line.split(":", 1)[1].strip()

        # If parsing failed, use raw response as transcript
        if not result["transcript"]:
            result["transcript"] = text
            result["translation"] = text

        return result

    except FileNotFoundError as e:
        return {"error": str(e), "audio_source": audio_path_or_url}
    except Exception as e:
        return {
            "error": f"Voice transcription failed: {str(e)}",
            "audio_source": audio_path_or_url,
        }


def list_supported_audio_formats() -> dict:
    """
    Returns the list of supported audio file formats for voice input.

    Use this to inform the farmer about which audio formats they can send.

    Returns:
        dict with 'formats' list and 'instructions' string.
    """
    return {
        "formats": list(SUPPORTED_AUDIO_TYPES.keys()),
        "instructions": (
            "You can send voice messages in the following formats: "
            f"{', '.join(SUPPORTED_AUDIO_TYPES.keys())}. "
            "Speak clearly in Hindi, Kannada, Telugu, Tamil, Marathi, "
            "Bengali, Gujarati, Punjabi, or English. "
            "Keep messages under 2 minutes for best accuracy."
        ),
        "supported_languages": [
            "English", "Hindi (हिंदी)", "Kannada (ಕನ್ನಡ)",
            "Telugu (తెలుగు)", "Tamil (தமிழ்)", "Marathi (मराठी)",
            "Bengali (বাংলা)", "Gujarati (ગુજરાતી)", "Punjabi (ਪੰਜਾਬੀ)",
        ],
    }
