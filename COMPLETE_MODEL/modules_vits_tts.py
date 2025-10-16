# COMPLETE_MODEL/modules_vits_tts.py
import io
import os
import requests
from dotenv import load_dotenv

load_dotenv()
VITS_TTS_API = os.getenv("VITS_TTS_API", "http://127.0.0.1:6000/tts")

class VitsTTSError(Exception):
    pass

def synthesize_vits(text: str, timeout: float = 120.0) -> bytes:
    """
    Call your MMS/VITS Flask endpoint:
      POST /tts { "text": "..." }  -> returns audio/wav
    Returns raw WAV bytes.
    """
    if not text or not text.strip():
        raise VitsTTSError("Empty text for VITS TTS")

    try:
        r = requests.post(
            VITS_TTS_API,
            json={"text": text.strip()},
            timeout=timeout,
        )
    except Exception as e:
        raise VitsTTSError(f"VITS request failed: {e}") from e

    if r.status_code != 200:
        # try to parse server message
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise VitsTTSError(f"VITS server error {r.status_code}: {detail}")

    return r.content  # WAV bytes
