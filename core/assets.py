"""
Asset management helper for Arctus.
Provides fast access to brand logo images and base64 data URIs for embedding in HTML components and Streamlit UI.
Supports both Light and Dark mode variations of the official brand artwork.
"""

import os
import base64
from typing import Optional

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# Dark mode logos (light artwork for dark background #101722)
LOGO_DARK_ICON_PATH = os.path.join(ASSETS_DIR, "logo_dark_icon.png")
LOGO_DARK_FULL_PATH = os.path.join(ASSETS_DIR, "logo_dark_full.png")

# Light mode logos (dark artwork for light background #F4F1E8)
LOGO_LIGHT_ICON_PATH = os.path.join(ASSETS_DIR, "logo_light_icon.png")
LOGO_LIGHT_FULL_PATH = os.path.join(ASSETS_DIR, "logo_light_full.png")

# Fallback paths
LOGO_ICON_PATH = os.path.join(ASSETS_DIR, "logo_icon.png")
LOGO_FULL_PATH = os.path.join(ASSETS_DIR, "logo_full.png")

_CACHE = {}


def _load_b64(file_path: str) -> str:
    """Helper to read and cache base64 image data URIs."""
    if file_path not in _CACHE:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
                _CACHE[file_path] = f"data:image/png;base64,{data}"
        else:
            _CACHE[file_path] = ""
    return _CACHE[file_path]


def get_logo_dark_icon_b64() -> str:
    """Returns base64 data URI of the Dark Mode emblem icon (ivory/gold for dark bg)."""
    return _load_b64(LOGO_DARK_ICON_PATH) or _load_b64(LOGO_ICON_PATH)


def get_logo_dark_full_b64() -> str:
    """Returns base64 data URI of the Dark Mode full brandmark (ivory/gold for dark bg)."""
    return _load_b64(LOGO_DARK_FULL_PATH) or _load_b64(LOGO_FULL_PATH)


def get_logo_light_icon_b64() -> str:
    """Returns base64 data URI of the Light Mode emblem icon (obsidian/gold for light bg)."""
    return _load_b64(LOGO_LIGHT_ICON_PATH) or _load_b64(LOGO_ICON_PATH)


def get_logo_light_full_b64() -> str:
    """Returns base64 data URI of the Light Mode full brandmark (obsidian/gold for light bg)."""
    return _load_b64(LOGO_LIGHT_FULL_PATH) or _load_b64(LOGO_FULL_PATH)


def get_logo_icon_b64(theme: str = "dark") -> str:
    """Returns base64 icon according to the requested theme."""
    return get_logo_light_icon_b64() if theme == "light" else get_logo_dark_icon_b64()


def get_logo_full_b64(theme: str = "dark") -> str:
    """Returns base64 full logo according to the requested theme."""
    return get_logo_light_full_b64() if theme == "light" else get_logo_dark_full_b64()
