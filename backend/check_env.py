from dotenv import load_dotenv
import os

def check_env():
    load_dotenv()
    
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    print("--- Environment Check ---")
    
    if google_key:
        print("[OK] GOOGLE_API_KEY is present.")
        # Optional: Print first few chars to confirm it's not a placeholder if helpful, but safe to just check presence
        if "your_google_api_key" in google_key:
             print("[WARNING] GOOGLE_API_KEY seems to be the placeholder value.")
    else:
        print("[FAIL] GOOGLE_API_KEY is MISSING.")
        
    if groq_key:
        print("[OK] GROQ_API_KEY is present.")
    else:
        print("[INFO] GROQ_API_KEY is missing (optional if using Google).")

    print("-------------------------")

if __name__ == "__main__":
    check_env()
