from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import os
from dotenv import load_dotenv
load_dotenv()

class PerplexityToolInput(BaseModel):
    """Input schema for PerplexityTool."""
    query: str = Field(..., description="The question or search query to send to Perplexity AI.")
    system_prompt: str = Field(
        "You are a helpful AI assistant specialized in AI/ML job skills research.",
        description="Optional system prompt to guide Perplexity's response."
    )

class PerplexityTool(BaseTool):
    name: str = "Perplexity AI Research"
    description: str = (
        "Use this tool to search for up-to-date information about AI/ML job skills, technologies, and trends. "
        "This tool connects to Perplexity AI to provide current information from across the web. "
        "Useful for researching specific skills, technologies, job market trends, or learning resources."
    )
    args_schema: Type[BaseModel] = PerplexityToolInput

    def _run(self, query: str, system_prompt: str = "You are a helpful AI assistant specialized in AI/ML job skills research.") -> str:
        """Run the Perplexity API tool."""
        try:
            # Get API key from environment variables
            api_key = os.getenv("PERPLEXITY_API_KEY")
            
            if not api_key:
                return "Error: PERPLEXITY_API_KEY not found in environment variables."
            
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
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ]
            }
            
            # Make the API request
            response = requests.post(url, headers=headers, json=data)
            
            # Check response status
            if response.status_code == 200:
                result = response.json()
                
                # Extract the assistant's response
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    content = message.get('content', 'No content returned')
                    return content
                else:
                    return "No valid response content found in the Perplexity API response."
            else:
                return f"Error: Perplexity API request failed with status code {response.status_code}. {response.text}"
                
        except Exception as e:
            return f"Error accessing Perplexity API: {str(e)}" 