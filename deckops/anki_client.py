"""Shared AnkiConnect client and helpers used by both import/export scripts."""

import re
from typing import Any

import requests

from deckops.config import ANKI_CONNECT_URL


def invoke(action: str, **params) -> Any:
    """Send a request to AnkiConnect and return the result.

    Raises an Exception when AnkiConnect returns an error.
    """
    response = requests.post(
        ANKI_CONNECT_URL,
        json={"action": action, "version": 6, "params": params},
        timeout=10,
    )
    result = response.json()
    if result.get("error"):
        raise Exception(f"AnkiConnect error: {result['error']}")
    return result["result"]


def extract_deck_id(content: str) -> tuple[int | None, str]:
    """Extract deck_id from the first line and return (deck_id, remaining content)."""
    match = re.match(r"<!--\s*deck_id:\s*(\d+)\s*-->\n?", content)
    if match:
        return int(match.group(1)), content[match.end() :]
    return None, content
