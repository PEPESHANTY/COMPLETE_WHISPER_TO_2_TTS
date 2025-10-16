# Whisper_to_TTS_Setup

# 🎙️ Whisper → GPT → Piper + VITS TTS (Voice Assistant)

This project is a real-time speech assistant that:
1. Listens to your voice.
2. Transcribes it using **Whisper** (running locally or remotely).
3. Sends the transcript to **GPT-4o-mini** for a conversational response.
4. Converts the answer into speech using **Piper TTS** and **VITS TTS** for multi-voice synthesis.

---

## 🚀 Prerequisites

Before running, ensure:
- You have **SSH access** to the remote TPU/VM where the Whisper, Piper, and VITS servers are hosted.
- You have **Python 3.10+** and **Streamlit** installed locally.
- You’ve set up your **OpenAI API key**.

---

## 🔌 Step 1. Start Tunneling

You need to tunnel **Whisper** (port 9000), **Piper TTS** (port 5000), and **VITS TTS** (port 6000) to your local machine.

### Example:

```bash
# Tunnel Piper TTS (Port 5000)
ssh -i <path-to-ssh-key> -L 5000:127.0.0.1:5000 <user-name>@<ip>

# Tunnel Whisper (Port 9000)
ssh -i <path-to-ssh-key> -L 9000:127.0.0.1:9000 <user-name>@<ip>

# Tunnel VITS TTS (Port 6000)
ssh -i <path-to-ssh-key> -L 6000:127.0.0.1:6000 <user-name>@<ip>
```

Example for reference:
```bash
ssh -i C:\Users\<private-key path> -L 5000:127.0.0.1:5000 shantanu_tpu@35.186.40.29
ssh -i C:\Users\<private-key path> -L 9000:127.0.0.1:9000 shantanu_tpu@35.186.40.29
ssh -i C:\Users\<private-key path> -L 6000:127.0.0.1:6000 shantanu_tpu@35.186.40.29
```

Keep all three terminals running while you use the app.

---

## ⚙️ Step 2. Setup Environment

Create a `.env` file inside the project directory:

```bash
OPENAI_API_KEY=<your-openai-api-key>

WHISPER_ENDPOINT=http://127.0.0.1:9000/transcribe
PIPER_TTS_API=http://127.0.0.1:5000/tts
VITS_TTS_API=http://127.0.0.1:6000/tts
```

---

## 🧩 Step 3. Install Dependencies on venv

```bash
python -m venv whisper_tts_env
whisper_tts_env\Scripts\activate
pip install -r requirements.txt
```

(or manually install the key packages:)

```bash
pip install streamlit sounddevice soundfile webrtcvad openai requests python-dotenv
```

---

## ▶️ Step 4. Run the Streamlit App

Navigate to the complete code folder:

```bash
cd COMPLETE_MODEL
streamlit run app.py
```
<img width="548" height="287" alt="recording" src="https://github.com/user-attachments/assets/da222d59-f1f7-4ade-a4e1-8f992dfad0c9" />

---


---

## 🗣️ Step 5. Usage

1. Click **“Start Talking”**
2. Speak for up to **10 seconds** (default duration).
3. Wait for transcription to appear on screen.
4. The AI will process your query and speak back using both **Piper TTS** and **VITS TTS**.
---
<img width="769" height="591" alt="answer2" src="https://github.com/user-attachments/assets/ecd51217-ede1-4c6b-8719-bc6151065e9c" />

---
✅ You’ll see messages like:
- *Recording... Speak now!*
- *Thinking...*
- *Generating audio (Piper TTS)…*
- *Generating audio (VITS TTS)…*
- *Audio generated successfully ✅*

Then you can **play both audio outputs** directly in the UI.
---
![image 1](https://github.com/user-attachments/assets/4d4ba158-59db-40da-870b-4dd363b45cbc)

---

## 🧠 Notes
- If you see an error like `Missing 'text'`, ensure the answer string isn’t empty before TTS conversion.
- Whisper, Piper, and VITS must all be running and reachable at the tunneled ports.
- The current model used is `gpt-4o-mini` (via OpenAI API).
- Output files are stored as:
  - **data/transcripts/** → user voice transcripts  
  - **data/answers/** → GPT responses  
  - **data/audio/piper/** → Piper-generated WAVs  
  - **data/audio/vits/** → VITS-generated WAVs  

---
