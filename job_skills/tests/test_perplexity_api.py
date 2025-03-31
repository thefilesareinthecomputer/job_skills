import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_perplexity_api():
    """Test the Perplexity API endpoint with a simple query."""
    
    # Get API key from environment variables
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        print("❌ Error: PERPLEXITY_API_KEY not found in environment variables")
        return False
    
    # API endpoint
    url = "https://api.perplexity.ai/chat/completions"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Request body
    data = {
        "model": "sonar-deep-research",
        "messages": [
            {
                "role": "system", 
                "content": "You are a helpful AI assistant."
            },
            {
                "role": "user", 
                "content": "What are the top 3 skills for AI engineers in 2025?"
            }
        ]
    }
    
    try:
        # Make the API request
        print("🔄 Sending request to Perplexity API...")
        response = requests.post(url, headers=headers, json=data)
        
        # Check response status
        if response.status_code == 200:
            print("✅ API request successful!")
            result = response.json()
            print("\n--- Response Content ---")
            print(f"Model: {result.get('model', 'N/A')}")
            
            # Extract and print the assistant's response
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})
                content = message.get('content', 'No content returned')
                print(f"\nResponse: {content}")
            
            return True
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Error message: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Perplexity API Connection")
    success = test_perplexity_api()
    
    if success:
        print("\n✅ Perplexity API test completed successfully!")
    else:
        print("\n❌ Perplexity API test failed. Please check your API key and connection.") 