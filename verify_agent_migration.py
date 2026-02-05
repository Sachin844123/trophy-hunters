
import sys
import os

# Ensure the current directory is in the python path to import agent
sys.path.append(os.getcwd())

from agent import get_llm_analysis

def test_migration():
    history = "User: Hello\nScammer: Sir your bank account KYC is pending. Please provide OTP to verify immediately otherwise account blocked."
    latest_message = "Sir send OTP fast."
    
    print("Testing get_llm_analysis with Groq...")
    result = get_llm_analysis(history, latest_message)
    
    print("\n--- Result ---")
    print(result)
    
    if result.get("isScam") is True and result.get("reply"):
        print("\nSUCCESS: Scam detected and reply generated.")
    else:
        print("\nFAILURE: Unexpected result format or logic.")

if __name__ == "__main__":
    test_migration()
