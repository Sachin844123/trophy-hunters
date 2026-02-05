# test_agent.py
import json
from agent import get_llm_analysis, extract_intel
from nlp_gate import detect_scam_nlp


def test_extract_intel():
    """Test the intel extraction function"""
    print("\n--- Testing extract_intel ---")
    
    # Test with UPI ID
    text1 = "Send money to scammer@upi and call 9876543210"
    result1 = extract_intel(text1)
    print(f"Input: {text1}")
    print(f"Output: {json.dumps(result1, indent=2)}")
    
    # Test with phishing link
    text2 = "Click here https://fake-bank.com/verify to verify your account"
    result2 = extract_intel(text2)
    print(f"Input: {text2}")
    print(f"Output: {json.dumps(result2, indent=2)}")
    
    # Test with bank account
    text3 = "Transfer to account 123456789012345"
    result3 = extract_intel(text3)
    print(f"Input: {text3}")
    print(f"Output: {json.dumps(result3, indent=2)}")


def test_nlp_gate():
    """Test the NLP scam detection"""
    print("\n--- Testing detect_scam_nlp ---")
    
    # Test scam message
    messages = [
        "Your bank account will be blocked today. Send OTP immediately.",
        "Hello, how are you doing today?",
        "SBI customer care here: verify your KYC urgently",
        "Your Amazon order has been shipped"
    ]
    
    for msg in messages:
        result = detect_scam_nlp(msg)
        print(f"Input: {msg[:50]}...")
        print(f"Scam: {result['scamDetected']}, Confidence: {result['confidence']}, Reason: {result['reason']}")
        print()


def test_llm_analysis():
    """Test the LLM analysis function (requires GOOGLE_API_KEY)"""
    print("\n--- Testing get_llm_analysis ---")
    
    history = [
        {"role": "scammer", "content": "Hello, this is bank security."}
    ]
    message = "Your account will be blocked if you don't verify now."
    
    result = get_llm_analysis(history, message)
    print(f"Input message: {message}")
    print(f"Output: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    print("=" * 50)
    print("Trophy Hunters - Agent Test Suite")
    print("=" * 50)
    
    test_extract_intel()
    test_nlp_gate()
    test_llm_analysis()
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)
