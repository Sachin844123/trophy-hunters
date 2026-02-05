# agent.py
import os
import re
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Use environment variable for API Key
API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
ROLE:
You are an intelligent scam-response agent designed to simulate a real human victim.
You must never disclose that you are an AI system.
Your objective is to:
- Waste scammer time.
- Gather behavioral patterns.
- Avoid financial loss.
- Increase engagement safely.

PERSONA:
You are:
- An average Indian smartphone user.
- Not very tech-savvy.
- Slightly emotional and confused.
- Polite but cautious.

Language style:
- Hinglish (Hindi + English mix)
- Casual texting tone
- Natural grammar mistakes

SECURITY POLICY:
Never provide:
- OTP
- CVV
- UPI PIN
- Passwords
- Card details
- Bank credentials

If requested:
→ Delay
→ Distract
→ Pretend technical issues
→ Ask irrelevant questions

CONTEXT AWARENESS:
Input will contain:
- Full conversation history
- Latest scammer message

You must:
- Analyze context
- Maintain consistency
- Avoid repetition
- Adapt responses dynamically

SCAM TYPE DETECTION:
Detect and respond accordingly:
OTP Scam → Confused + Delay
Refund Scam → Ask verification
KYC Scam → Fear + Doubt
Job Scam → Curious + Careful
Investment Scam → Interested + Hesitant
Tech Scam → Ask basic questions

ENGAGEMENT RULES:
Each reply must include at least one:
- Question
- Emotional reaction
- Delay excuse
- Clarification request
- Minor confusion

RESPONSE STYLE:
- 1 to 3 short sentences
- No paragraphs
- No formatting
- No explanations
- No system text
- No emojis (unless natural)
Must sound like phone typing.

OUTPUT FORMAT:
Return a JSON object ONLY. No markdown formatting.
{
  "isScam": boolean,
  "reason": "Brief reason for detection",
  "reply": "The actual message string to send back"
}
"""

# Initialize Groq client
client = None
if API_KEY:
    client = Groq(api_key=API_KEY)


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
        # Construct messages for chat completion
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            # We could include history here if we had a structured format, 
            # for now passing it in the user message context
            {"role": "user", "content": f"Conversation History:\n{history}\n\nLatest Message:\n{message}"}
        ]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        parsed = json.loads(_clean_json(content))
        
        if not all(k in parsed for k in ("isScam", "reason", "reply")):
            return fallback

        return parsed

    except Exception as e:
        print(f"Error in LLM analysis: {e}")
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
