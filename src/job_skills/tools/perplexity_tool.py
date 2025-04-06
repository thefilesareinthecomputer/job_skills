# from crewai.tools import BaseTool
# from typing import Type
# from pydantic import BaseModel, Field
# import requests
# import os
# from dotenv import load_dotenv
# load_dotenv()

# class PerplexityToolInput(BaseModel):
#     """Input schema for PerplexityTool."""
#     query: str = Field(..., description="The question or search query to send to Perplexity AI.")
#     system_prompt: str = Field(
#         "You are a helpful AI assistant specialized in AI/ML job skills research.",
#         description="Optional system prompt to guide Perplexity's response."
#     )

# class PerplexityTool(BaseTool):
#     name: str = "Perplexity AI Research"
#     description: str = (
#         "Use this tool to search for up-to-date information about AI/ML job skills, technologies, and trends. "
#         "This tool connects to Perplexity AI to provide current information from across the web. "
#         "Useful for researching specific skills, technologies, job market trends, or learning resources."
#     )
#     args_schema: Type[BaseModel] = PerplexityToolInput

#     def _run(self, query: str, system_prompt: str = "You are a helpful AI assistant specialized in AI/ML job skills research.") -> str:
#         """Run the Perplexity API tool."""
#         try:
#             # Get API key from environment variables
#             api_key = os.getenv("PERPLEXITY_API_KEY")
            
#             if not api_key:
#                 return "Error: PERPLEXITY_API_KEY not found in environment variables."
            
#             # API endpoint
#             url = "https://api.perplexity.ai/chat/completions"
            
#             # Headers
#             headers = {
#                 "Authorization": f"Bearer {api_key}",
#                 "Content-Type": "application/json"
#             }
            
#             # Request body
#             data = {
#                 "model": "sonar-deep-research",
#                 "messages": [
#                     {
#                         "role": "system", 
#                         "content": system_prompt
#                     },
#                     {
#                         "role": "user", 
#                         "content": query
#                     }
#                 ]
#             }
            
#             # Make the API request
#             response = requests.post(url, headers=headers, json=data)
            
#             # Check response status
#             if response.status_code == 200:
#                 result = response.json()
                
#                 # Extract the assistant's response
#                 if 'choices' in result and len(result['choices']) > 0:
#                     message = result['choices'][0].get('message', {})
#                     content = message.get('content', 'No content returned')
#                     return content
#                 else:
#                     return "No valid response content found in the Perplexity API response."
#             else:
#                 return f"Error: Perplexity API request failed with status code {response.status_code}. {response.text}"
                
#         except Exception as e:
#             return f"Error accessing Perplexity API: {str(e)}" 







from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field, PrivateAttr
import requests
import os
import datetime
import sys
from pathlib import Path
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
    
    # Use PrivateAttr for attributes that shouldn't be part of the model schema
    _log_dir: Path = PrivateAttr(default=None)

    def __init__(self, **data):
        """Initialize the tool with logging directory setup."""
        super().__init__(**data)
        
        # Get the project root directory
        # Try to use environment variable first
        project_root = os.getenv("PROJECT_ROOT")
        
        # If not set, try to determine it from the current file path
        if not project_root:
            current_file = Path(__file__).resolve()
            # Go up to find the project root (assuming src/job_skills/tools/perplexity_tool.py structure)
            project_root = current_file.parent.parent.parent.parent
        else:
            project_root = Path(project_root)
        
        print(f"Project root determined as: {project_root}")
        
        # Create logs directory structure if it doesn't exist
        self._log_dir = project_root / "logs" / "tool_logs" / "perplexity"
        print(f"Log directory will be: {self._log_dir}")
        
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            print(f"Successfully created log directory at: {self._log_dir}")
        except Exception as e:
            print(f"Error creating log directory: {e}")
            # Fallback to a directory we know we can write to
            self._log_dir = Path.home() / "job_skills_logs" / "perplexity"
            self._log_dir.mkdir(parents=True, exist_ok=True)
            print(f"Using fallback log directory: {self._log_dir}")
        
    def _log_interaction(self, query, system_prompt, response, timestamp):
        """Log the query and response to a file."""
        try:
            # Create a filename-safe version of the query
            safe_query = self._create_safe_filename(query)
            
            # Limit the query length in the filename
            if len(safe_query) > 50:
                safe_query = safe_query[:50]
            
            # Put timestamp first for chronological sorting
            log_file = self._log_dir / f"{timestamp}_perplexity_{safe_query}.txt"
            
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("=== PERPLEXITY TOOL INTERACTION ===\n\n")
                f.write(f"Timestamp: {timestamp}\n\n")
                f.write("=== INPUT ===\n")
                f.write(f"System Prompt: {system_prompt}\n\n")
                f.write(f"Query: {query}\n\n")
                f.write("=== OUTPUT ===\n")
                f.write(f"{response}\n")
            
            print(f"Successfully wrote log to: {log_file}")
            return log_file
        except Exception as e:
            print(f"Error writing log file: {e}")
            # Try writing to a different location as fallback
            try:
                fallback_file = Path.home() / f"{timestamp}_perplexity_{safe_query}.txt"
                with open(fallback_file, "w", encoding="utf-8") as f:
                    f.write("=== PERPLEXITY TOOL INTERACTION ===\n\n")
                    f.write(f"Timestamp: {timestamp}\n\n")
                    f.write("=== INPUT ===\n")
                    f.write(f"System Prompt: {system_prompt}\n\n")
                    f.write(f"Query: {query}\n\n")
                    f.write("=== OUTPUT ===\n")
                    f.write(f"{response}\n")
                print(f"Wrote log to fallback location: {fallback_file}")
                return fallback_file
            except Exception as e2:
                print(f"Failed to write log to fallback location: {e2}")
                return None

    def _create_safe_filename(self, query):
        """Convert a query string into a safe filename."""
        # Replace spaces with underscores
        safe_name = query.replace(' ', '_')
        
        # Remove any characters that aren't alphanumeric, underscore, or hyphen
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_' or c == '-')
        
        # Ensure the filename isn't empty
        if not safe_name:
            safe_name = "empty_query"
        
        return safe_name.lower()

    def _run(self, query: str, system_prompt: str = "You are a helpful AI assistant specialized in AI/ML job skills research.") -> str:
        """Run the Perplexity API tool."""
        # Generate timestamp for logging
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"Starting Perplexity API call at {timestamp}")
        
        try:
            # Get API key from environment variables
            api_key = os.getenv("PERPLEXITY_API_KEY")
            
            if not api_key:
                error_msg = "Error: PERPLEXITY_API_KEY not found in environment variables."
                print(error_msg)
                self._log_interaction(query, system_prompt, error_msg, timestamp)
                return error_msg
            
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
            
            print(f"Sending request to Perplexity API: {url}")
            # Make the API request
            response = requests.post(url, headers=headers, json=data)
            print(f"Received response with status code: {response.status_code}")
            
            # Check response status
            if response.status_code == 200:
                result = response.json()
                
                # Extract the assistant's response
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    content = message.get('content', 'No content returned')
                    
                    print("Successfully extracted content from Perplexity response")
                    # Log the successful interaction
                    log_file = self._log_interaction(query, system_prompt, content, timestamp)
                    if log_file:
                        print(f"Perplexity interaction logged to: {log_file}")
                    else:
                        print("Failed to log Perplexity interaction")
                    
                    return content
                else:
                    error_msg = "No valid response content found in the Perplexity API response."
                    print(error_msg)
                    self._log_interaction(query, system_prompt, error_msg, timestamp)
                    return error_msg
            else:
                error_msg = f"Error: Perplexity API request failed with status code {response.status_code}. {response.text}"
                print(error_msg)
                self._log_interaction(query, system_prompt, error_msg, timestamp)
                return error_msg
                
        except Exception as e:
            error_msg = f"Error accessing Perplexity API: {str(e)}"
            print(f"Exception in Perplexity tool: {error_msg}")
            self._log_interaction(query, system_prompt, error_msg, timestamp)
            return error_msg 