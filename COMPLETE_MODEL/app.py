import io, os, requests, time
from pathlib import Path

import sounddevice as sd
import streamlit as st
import wavio
from dotenv import load_dotenv
from openai import OpenAI

from modules_gpt import decide_and_answer_full  # ← use your EN/VI helper

# ---------- setup & folders ----------
load_dotenv()

DATA_ROOT  = Path(__file__).parent / "data"
DIR_PIPER  = DATA_ROOT / "audio" / "piper"
DIR_VITS   = DATA_ROOT / "audio" / "vits"
DIR_TXT    = DATA_ROOT / "transcripts"
DIR_ANS    = DATA_ROOT / "answers"

for d in (DIR_PIPER, DIR_VITS, DIR_TXT, DIR_ANS):
    d.mkdir(parents=True, exist_ok=True)

def save_bytes(path: Path, b: bytes):
    path.write_bytes(b); return path

def save_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8"); return path

# Endpoints (env overrideable)
WHISPER_ENDPOINT = os.getenv("WHISPER_ENDPOINT", "http://127.0.0.1:9000/transcribe")
PIPER_TTS_API    = os.getenv("PIPER_TTS_API",    "http://127.0.0.1:5000/tts")
VITS_TTS_API     = os.getenv("VITS_TTS_API",     "http://127.0.0.1:6000/tts")

# OpenAI (only for LLM answer)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Whisper → TTS", page_icon="🎙", layout="centered")
st.title("🎙 Talk to AI")

# ---------- helpers ----------
def record_audio(duration=10, fs=16000) -> io.BytesIO:
    """Record mic and return a WAV buffer (BytesIO)."""
    st.info("Recording... Speak now!")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    st.success("Recording complete.")
    buf = io.BytesIO()
    wavio.write(buf, audio, fs, sampwidth=2)   # write .wav into memory
    buf.seek(0)
    return buf  # IMPORTANT: return ONLY the buffer

def transcribe(buf: io.BytesIO, task: str = "transcribe", language: str = "") -> str:
    """Send audio to your local Whisper server."""
    st.write("🧠 Transcribing (Whisper server)…")
    buf.seek(0)
    files = {"file": ("speech.wav", buf, "audio/wav")}
    data = {
        "task": task,                 # "transcribe" or "translate"
        "language": language,         # "" = auto, or "en"/"vi"
        "return_timestamps": "false",
    }
    r = requests.post(WHISPER_ENDPOINT, files=files, data=data, timeout=None)
    r.raise_for_status()
    j = r.json()
    return (j.get("text") or "").strip()

def synthesize_piper(answer_text: str, lang: str | None = None) -> io.BytesIO | None:
    st.write("🔊 Generating audio (Piper TTS)…")
    try:
        payload = {"text": answer_text}
        if lang:
            payload["lang"] = lang          # your Piper API uses en/vi to pick voice
        r = requests.post(PIPER_TTS_API, json=payload, timeout=60)
        r.raise_for_status()
        st.success("Piper audio generated ✅")
        return io.BytesIO(r.content)
    except Exception as e:
        st.error(f"Piper TTS failed: {e}")
        return None

def synthesize_vits(answer_text: str) -> io.BytesIO | None:
    if not VITS_TTS_API:
        st.info("VITS endpoint not configured; skipping.")
        return None
    st.write("🔊 Generating audio (VITS TTS)…")
    try:
        r = requests.post(VITS_TTS_API, json={"text": answer_text}, timeout=120)
        r.raise_for_status()
        st.success("VITS audio generated ✅")
        return io.BytesIO(r.content)
    except Exception as e:
        st.error(f"VITS TTS failed: {e}")
        return None

# ---------- UI ----------
with st.sidebar:
    st.header("Options")
    duration = st.slider("Record seconds", 3, 20, 8)
    st.caption(f"Whisper: {WHISPER_ENDPOINT}")
    st.caption(f"Piper:   {PIPER_TTS_API}")
    st.caption(f"VITS:    {VITS_TTS_API or '(disabled)'}")

if st.button("🎙 Start Talking"):
    # 1) Record
    wav_buf = record_audio(duration=duration)  # <-- returns BytesIO, not tuple

    # 2) Transcribe (Whisper server)
    transcript = transcribe(wav_buf)
    st.markdown(f"**You said:** {transcript}")

    # Shared session id
    session_id = str(int(time.time()))

    # Save transcript
    trans_path = DIR_TXT / f"transcript_{session_id}.txt"
    save_text(trans_path, transcript)
    st.caption(f"📝 Transcript saved → {trans_path}")

    # 3) GPT: decide language + answer (with [en]/[vi] prefix)
    lang, answer = decide_and_answer_full(transcript)  # lang in {"en","vi"}
    st.markdown(f"**AI:** {answer}")

    # Save answer text (keep prefix in file)
    ans_path = DIR_ANS / f"session_{session_id}.txt"
    save_text(ans_path, answer)
    st.caption(f"💾 Answer saved → {ans_path}")

    # Strip prefix for TTS output only
    tts_text = answer
    pref = f"[{lang}] "
    if tts_text.startswith(pref):
        tts_text = tts_text[len(pref):]

    # 4) Piper → data/audio/piper/session_<id>.wav
    piper_audio = synthesize_piper(tts_text, lang=lang)  # <— pass GPT-detected lang
    if piper_audio:
        piper_path = DIR_PIPER / f"session_{session_id}.wav"
        save_bytes(piper_path, piper_audio.getvalue())
        st.audio(piper_audio, format="audio/wav")
        st.caption(f"🔊 Piper audio saved → {piper_path}")

    # 5) VITS → data/audio/vits/session_<id>.wav
    vits_audio = synthesize_vits(tts_text)
    if vits_audio:
        vits_path = DIR_VITS / f"session_{session_id}.wav"
        save_bytes(vits_path, vits_audio.getvalue())
        st.audio(vits_audio, format="audio/wav")
        st.caption(f"🔊 VITS audio saved → {vits_path}")

# import streamlit as st
# import sounddevice as sd
# import numpy as np
# import wavio
# import io, os, requests
# from openai import OpenAI
# from dotenv import load_dotenv
# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# st.set_page_config(page_title="Whisper → TTS", page_icon="🎙", layout="centered")
# st.title("🎙 Talk to AI")

# def record_audio(duration=10, fs=16000):
#     st.info("Recording... Speak now!")
#     audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
#     sd.wait()
#     st.success("Recording complete.")
#     buf = io.BytesIO()
#     wavio.write(buf, audio, fs, sampwidth=2)
#     buf.seek(0)
#     return buf

# def transcribe(buf):
#     st.write("🧠 Transcribing...")
#     audio_file = io.BytesIO(buf.read())
#     audio_file.name = "speech.wav"
#     resp = client.audio.transcriptions.create(
#         model="gpt-4o-mini-transcribe",
#         file=audio_file
#     )
#     return resp.text.strip()

# def get_answer(transcript):
#     st.write("💬 Thinking...")
#     resp = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are a friendly conversational assistant. Reply naturally."},
#             {"role": "user", "content": transcript}
#         ]
#     )
#     return resp.choices[0].message.content.strip()

# def synthesize_tts(answer_text):
#     st.write("🔊 Generating audio (via Piper TTS)...")
#     try:
#         response = requests.post(
#             "http://localhost:5000/tts",
#             json={"text": answer_text},   # 👈 send JSON body, not raw bytes
#             timeout=30
#         )
#         if response.status_code != 200:
#             raise RuntimeError(f"TTS server error {response.status_code}: {response.text}")

#         audio_data = io.BytesIO(response.content)
#         st.success("Audio generated successfully ✅")
#         return audio_data

#     except Exception as e:
#         st.error(f"TTS generation failed: {e}")
#         return None

# # --- UI ---
# if st.button("🎙 Start Talking"):
#     buf = record_audio(duration=8)
#     transcript = transcribe(buf)
#     st.markdown(f"**You said:** {transcript}")

#     answer = get_answer(transcript)
#     st.markdown(f"**AI:** {answer}")

#     audio_data = synthesize_tts(answer)
#     st.audio(audio_data, format="audio/mp3")
