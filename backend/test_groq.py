import os
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

print(f"Testing Groq API...")
print(f"Key present: {'Yes' if API_KEY else 'No'}")
print(f"URL: {API_URL}")
print(f"Model: {MODEL}")

async def test_api():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Hello, just testing the connection."}],
        "temperature": 0.1
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("\nSending request...")
            response = await client.post(API_URL, headers=headers, json=payload, timeout=20.0)
            
            print(f"Status Code: {response.status_code}")
            
            try:
                data = response.json()
                print("\nResponse Body:")
                print(data)
                
                if 'choices' in data:
                    print("\n✅ Success! API is working.")
                    print(f"Response: {data['choices'][0]['message']['content']}")
                elif 'error' in data:
                    print("\n❌ API Error:")
                    print(data['error'])
                else:
                    print("\n⚠️ Unexpected Response Format (Missing 'choices')")
                    
            except Exception as e:
                print(f"\n❌ Failed to parse JSON: {e}")
                print(response.text)
                
    except Exception as e:
        print(f"\n❌ Request Failed: {e}")

if __name__ == "__main__":
    if not API_KEY:
        print("❌ Error: GROQ_API_KEY not found in .env file")
    else:
        asyncio.run(test_api())
