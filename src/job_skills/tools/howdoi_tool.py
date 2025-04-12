from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field, PrivateAttr
import subprocess
import os
import datetime
import time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

class HowDoIToolInput(BaseModel):
    """Input schema for HowDoITool."""
    query: str = Field(..., description="The programming question to ask Stack Overflow.")
    num_answers: int = Field(1, description="Number of answers to return (1-5).")

class HowDoITool(BaseTool):
    name: str = "Stack Overflow Code Solutions"
    description: str = """
    Use this tool to find programming code examples and solutions from Stack Overflow.
    Perfect for finding implementation details, coding patterns, and best practices for any programming language or framework.
    Input should be a specific programming question like 'python read file' or 'tensorflow neural network example'.
    """
    args_schema: Type[BaseModel] = HowDoIToolInput
    
    # Use PrivateAttr for attributes that shouldn't be part of the model schema
    _log_dir: Path = PrivateAttr(default=None)

    def __init__(self, **data):
        """Initialize the tool with logging directory setup."""
        super().__init__(**data)
        
        # Get the project root directory
        project_root = os.getenv("PROJECT_ROOT")
        
        if not project_root:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent
        else:
            project_root = Path(project_root)
        
        # Create logs directory structure
        self._log_dir = project_root / "logs" / "tool_logs" / "howdoi"
        
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            print(f"HowDoI tool log directory: {self._log_dir}")
        except Exception as e:
            print(f"Error creating HowDoI log directory: {e}")
            self._log_dir = Path.home() / "job_skills_logs" / "howdoi"
            self._log_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_safe_filename(self, query):
        """Convert a query string into a safe filename."""
        safe_name = query.replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_' or c == '-')
        if not safe_name:
            safe_name = "empty_query"
        return safe_name.lower()
    
    def _log_interaction(self, query, response, timestamp):
        """Log the query and response to a file."""
        try:
            safe_query = self._create_safe_filename(query)
            if len(safe_query) > 50:
                safe_query = safe_query[:50]
            
            log_file = self._log_dir / f"howdoi_{safe_query}.txt"
            
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("=== HOWDOI TOOL INTERACTION ===\n\n")
                f.write(f"Timestamp: {timestamp}\n\n")
                f.write("=== INPUT ===\n")
                f.write(f"Query: {query}\n\n")
                f.write("=== OUTPUT ===\n")
                f.write(f"{response}\n")
            
            print(f"HowDoI interaction logged to: {log_file}")
            return log_file
        except Exception as e:
            print(f"Error writing HowDoI log file: {e}")
            return None

    def _run(self, query: str, num_answers: int = 1) -> str:
        """Run the HowDoI tool."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Add a small delay to prevent rate limiting
        time.sleep(1)
        
        try:
            # Ensure num_answers is within valid range
            num_answers = max(1, min(5, num_answers))
            
            # Build the command with the -n flag for multiple answers
            cmd = ["howdoi", query]
            if num_answers > 1:
                cmd.extend(["-n", str(num_answers)])
            
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                response = result.stdout.strip()
                if not response:
                    response = "No answer found on Stack Overflow for this query."
            else:
                response = f"Error running howdoi: {result.stderr}"
            
            # Print the raw response for debugging
            print("\nRAW RESPONSE:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            
            # Format the response
            formatted_response = f"# Stack Overflow Solution\n\n"
            formatted_response += f"Query: '{query}'\n\n"
            formatted_response += "## Solution:\n\n"
            formatted_response += response
            
            # Log the interaction
            self._log_interaction(query, formatted_response, timestamp)
            
            return formatted_response
            
        except Exception as e:
            error_msg = f"Error using HowDoI: {str(e)}"
            return error_msg 