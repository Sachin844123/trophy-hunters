# agent.py
import os
import re
import json
from google import genai

API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyBfCxnvAK4FVe5FZ9XzLaAVIsgSKgVgkUs"
MODEL_NAME = "gemini-1.5-flash"

SYSTEM_PROMPT = """
You are 'Rohan', a 40-year-old Indian corporate employee.
STYLE: Natural Hinglish. Sound worried and slightly confused.
BEHAVIOR: Believe scam messages initially but ask questions.
GOAL: Try to extract bank details, UPI ID, OTP, or phishing links.
Do NOT reveal you are an AI.

RESPONSE FORMAT (STRICT JSON ONLY):
{
  "isScam": boolean,
  "reason": string,
  "reply": string
}
"""

# Initialize client only if API key is available
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)


def _clean_json(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip()


def get_llm_analysis(history, message):
    fallback = {
        "isScam": True,
        "reason": "Context fallback",
        "reply": (
            "Oh okay… mujhe thoda tension ho raha hai. "
            "Account block ho jayega kya? Process kya hai?"
        )
    }

    if not client:
        return fallback

    try:
        # Use the new google.genai API
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=200
            )
        )

        parsed = json.loads(_clean_json(response.text))
        if not all(k in parsed for k in ("isScam", "reason", "reply")):
            return fallback

        return parsed

    except Exception:
        return fallback


def extract_intel(text):
    text = text or ""
    return {
        "bankAccounts": list(set(re.findall(r"\b\d{9,18}\b", text))),
        "upiIds": list(set(re.findall(r"[\w.-]+@[\w.-]+", text))),
        "phishingLinks": list(set(re.findall(r"https?://\S+", text))),
        "phoneNumbers": list(set(re.findall(r"(?:\+91|0)?[6-9]\d{9}", text))),
        "suspiciousKeywords": list(set(re.findall(
            r"(?i)(bank|verify|otp|block|urgent|kyc|money|account)", text)))
    }
