"""
Image processing utilities for Krishi Mitra.

Provides helpers to:
  - Load an image from a local file path or a public URL and encode it as
    a base64 data URI (so it can be embedded in any HTML / markdown response).
  - Build a google.genai.types.Part object (inline_data) that can be passed
    directly to Gemini multimodal models alongside a text prompt.
  - Identify image MIME type from extension or bytes magic-number.

These helpers are intentionally *not* ADK Tool functions themselves — they are
utility functions called by the multimodal agent helpers and by the notebook's
`ask_with_image()` wrapper.
"""

from __future__ import annotations

import base64
import os
import io
import mimetypes
from typing import Optional, Tuple

# ─────────────────────────────────────────────────────────────
# MIME-type detection
# ─────────────────────────────────────────────────────────────

# Supported image types for plant / field photos
SUPPORTED_IMAGE_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png":  [".png"],
    "image/webp": [".webp"],
    "image/heic": [".heic"],
    "image/heif": [".heif"],
}

# Magic byte signatures → MIME type
_MAGIC = [
    (b"\xff\xd8\xff",           "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n",     "image/png"),
    (b"RIFF",                   "image/webp"),   # RIFF....WEBP
]


def detect_mime_type(data: bytes, filename: str = "") -> str:
    """
    Detect the MIME type of raw image bytes.

    First tries magic-byte sniffing, then falls back to the file extension,
    and finally defaults to 'image/jpeg'.

    Args:
        data:     Raw image bytes (at least the first 16 bytes suffice).
        filename: Optional filename / path used for extension fallback.

    Returns:
        A MIME type string such as 'image/jpeg'.
    """
    for magic, mime in _MAGIC:
        if data[:len(magic)] == magic:
            # Extra check: RIFF is shared by WAV; confirm WEBP marker
            if mime == "image/webp" and data[8:12] != b"WEBP":
                continue
            return mime

    # Extension fallback
    if filename:
        ext = os.path.splitext(filename)[-1].lower()
        for mime, exts in SUPPORTED_IMAGE_TYPES.items():
            if ext in exts:
                return mime

    return "image/jpeg"


# ─────────────────────────────────────────────────────────────
# Image loading
# ─────────────────────────────────────────────────────────────

def load_image_bytes(source: str) -> Tuple[bytes, str]:
    """
    Load raw image bytes from a local file path or a public HTTP/HTTPS URL.

    Args:
        source: An absolute / relative file path  OR  an http(s):// URL.

    Returns:
        A tuple of (raw_bytes, mime_type).

    Raises:
        FileNotFoundError: If the local file does not exist.
        ValueError: If the URL fetch fails or the source format is unsupported.
    """
    if source.startswith("http://") or source.startswith("https://"):
        import requests
        response = requests.get(source, timeout=15)
        response.raise_for_status()
        raw = response.content
        # Try Content-Type header first
        ct = response.headers.get("Content-Type", "").split(";")[0].strip()
        mime = ct if ct.startswith("image/") else detect_mime_type(raw, source)
        return raw, mime
    else:
        if not os.path.exists(source):
            raise FileNotFoundError(f"Image file not found: {source}")
        with open(source, "rb") as f:
            raw = f.read()
        mime = detect_mime_type(raw, source)
        return raw, mime


def image_to_base64_data_uri(source: str) -> str:
    """
    Convert a local file or URL image into a base64 data URI string.

    Useful for embedding images in HTML or markdown responses.

    Args:
        source: File path or public URL.

    Returns:
        A data URI string like: 'data:image/jpeg;base64,/9j/4AAQ...'
    """
    raw, mime = load_image_bytes(source)
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


# ─────────────────────────────────────────────────────────────
# Gemini Part builder
# ─────────────────────────────────────────────────────────────

def build_image_part(source: str):
    """
    Build a google.genai.types.Part (inline_data) from a local path or URL.

    This Part can be appended to the `parts` list of a Content object when
    calling runner.run_async() with a multimodal message.

    Args:
        source: File path or public HTTP/HTTPS URL.

    Returns:
        A google.genai.types.Part with inline_data set.

    Example:
        >>> from google.genai import types
        >>> image_part = build_image_part("/tmp/leaf.jpg")
        >>> text_part  = types.Part(text="What disease does this leaf have?")
        >>> content = types.Content(role="user", parts=[text_part, image_part])
    """
    from google.genai import types  # lazy import to avoid circular at module level

    raw, mime = load_image_bytes(source)
    return types.Part(
        inline_data=types.Blob(mime_type=mime, data=raw)
    )


# ─────────────────────────────────────────────────────────────
# ADK Tool: describe_farm_image  (callable by any agent)
# ─────────────────────────────────────────────────────────────

def describe_farm_image(image_url_or_path: str, question: str = "") -> dict:
    """
    Use Gemini's vision capability to describe a farm-related image.

    This ADK-compatible tool function can be listed in any agent's `tools=`.
    It sends the image + an optional farmer question to a Gemini Flash model
    and returns the model's description as a plain text string.

    Args:
        image_url_or_path: Public URL or local file path to the image.
        question: Optional specific question about the image
                  (e.g., "What disease do you see on this leaf?").

    Returns:
        A dict with keys:
            - "description": The model's free-text description of the image.
            - "image_source": The source string that was processed.
            - "error":  Set only if the call failed.
    """
    try:
        import google.generativeai as genai  # type: ignore
        import os

        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            return {"error": "GOOGLE_API_KEY not set.", "image_source": image_url_or_path}

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        raw, mime = load_image_bytes(image_url_or_path)

        # Build a multimodal prompt
        prompt_text = (
            question.strip()
            if question.strip()
            else (
                "You are an agricultural expert assistant. "
                "Carefully describe what you see in this farming-related image. "
                "Focus on: crop type, visible symptoms, pest damage, soil condition, "
                "and any issues that a farmer should be aware of. "
                "Be specific and practical."
            )
        )

        import PIL.Image as PILImage
        pil_img = PILImage.open(io.BytesIO(raw))
        response = model.generate_content([prompt_text, pil_img])

        return {
            "description": response.text,
            "image_source": image_url_or_path,
        }

    except FileNotFoundError as e:
        return {"error": str(e), "image_source": image_url_or_path}
    except Exception as e:
        return {"error": f"Image analysis failed: {str(e)}", "image_source": image_url_or_path}
