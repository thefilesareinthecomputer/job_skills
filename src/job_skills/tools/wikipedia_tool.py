# from crewai.tools import BaseTool
# from typing import Type, Optional, Union
# from pydantic import BaseModel, Field
# import wikipedia
# from dotenv import load_dotenv
# load_dotenv()

# class WikipediaToolInput(BaseModel):
#     """Input schema for WikipediaTool."""
#     query: str = Field(..., description="The search query for Wikipedia.")

# class WikipediaTool(BaseTool):
#     name: str = "Wikipedia Search"
#     description: str = (
#         "Search Wikipedia for information about a topic. "
#         "This tool is useful for getting factual information about concepts, technologies, "
#         "historical events, and notable figures. Use this tool when you need background "
#         "information or definitions for technical terms related to AI/ML skills."
#     )
#     args_schema: Type[BaseModel] = WikipediaToolInput
    
#     def _parse_input(self, tool_input):
#         """Parse the input before validation."""
#         if isinstance(tool_input, str):
#             return {"query": tool_input}
#         return tool_input
    
#     def _run(self, query) -> str:
#         """Run the Wikipedia tool."""
#         try:
#             # Handle different input formats
#             if isinstance(query, dict):
#                 if 'query' in query:
#                     query = query['query']
#                 elif 'input' in query:
#                     query = query['input']
#                 elif len(query) == 1:  # If there's only one key-value pair
#                     query = list(query.values())[0]
#                 else:
#                     return "Error: Could not extract query from dictionary input. Please provide a simple string query."
            
#             # Ensure query is a string
#             if not isinstance(query, str):
#                 return f"Error: Expected string query but got {type(query)}. Please provide a simple string query."
            
#             # Search Wikipedia
#             search_results = wikipedia.search(query, results=5)
            
#             if not search_results:
#                 return f"No Wikipedia articles found for '{query}'."
            
#             # Try to get the most relevant page
#             page = None
#             error_messages = []
            
#             for result in search_results:
#                 try:
#                     page = wikipedia.page(result, auto_suggest=False)
#                     break  # Found a valid page
#                 except wikipedia.DisambiguationError as e:
#                     # If there's a disambiguation page, try the first option
#                     try:
#                         page = wikipedia.page(e.options[0], auto_suggest=False)
#                         break  # Found a valid page from disambiguation
#                     except Exception as inner_e:
#                         error_messages.append(f"Disambiguation error for '{result}': {str(inner_e)}")
#                 except Exception as e:
#                     error_messages.append(f"Error retrieving page '{result}': {str(e)}")
            
#             if not page:
#                 if error_messages:
#                     return f"Could not retrieve Wikipedia page for '{query}'. Errors: {'; '.join(error_messages)}"
#                 else:
#                     return f"Could not retrieve Wikipedia page for '{query}'."
            
#             # Format the result
#             result = f"# Wikipedia: {page.title}\n\n"
            
#             # Get a summary (first few paragraphs)
#             summary = page.summary
#             if len(summary) > 1500:
#                 summary = summary[:1500] + "..."
            
#             result += summary + "\n\n"
            
#             # Add sections if available
#             if hasattr(page, 'sections') and page.sections:
#                 result += "## Key Sections\n\n"
#                 for section in page.sections[:5]:  # Limit to first 5 sections
#                     result += f"- {section}\n"
                
#                 if len(page.sections) > 5:
#                     result += f"- ... and {len(page.sections) - 5} more sections\n"
                
#                 result += "\n"
            
#             # Add URL for reference
#             result += f"For more information: {page.url}\n\n"
            
#             # Add search results for reference
#             if len(search_results) > 1:
#                 result += "## Other Relevant Articles\n\n"
#                 for i, title in enumerate(search_results[1:5], 1):
#                     if title != page.title:
#                         result += f"{i}. {title}\n"
#                 result += "\n"
            
#             return result
            
#         except Exception as e:
#             return f"Error searching Wikipedia: {str(e)}" 































from crewai.tools import BaseTool
from typing import Type, Optional, Union
from pydantic import BaseModel, Field, PrivateAttr
import wikipedia
import os
import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

class WikipediaToolInput(BaseModel):
    """Input schema for WikipediaTool."""
    query: str = Field(..., description="The search query for Wikipedia.")

class WikipediaTool(BaseTool):
    name: str = "Wikipedia Search"
    description: str = (
        "Search Wikipedia for information about a topic. "
        "This tool is useful for getting factual information about concepts, technologies, "
        "historical events, and notable figures. Use this tool when you need background "
        "information or definitions for technical terms related to AI/ML skills."
    )
    args_schema: Type[BaseModel] = WikipediaToolInput
    
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
            # Go up to find the project root (assuming src/job_skills/tools/wikipedia_tool.py structure)
            project_root = current_file.parent.parent.parent.parent
        else:
            project_root = Path(project_root)
        
        # Create logs directory structure if it doesn't exist
        self._log_dir = project_root / "logs" / "tool_logs" / "wikipedia"
        
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            print(f"Wikipedia tool log directory: {self._log_dir}")
        except Exception as e:
            print(f"Error creating Wikipedia log directory: {e}")
            # Fallback to a directory we know we can write to
            self._log_dir = Path.home() / "job_skills_logs" / "wikipedia"
            self._log_dir.mkdir(parents=True, exist_ok=True)
            print(f"Using fallback Wikipedia log directory: {self._log_dir}")
    
    def _log_interaction(self, query, response, timestamp):
        """Log the query and response to a file."""
        try:
            # Create a filename-safe version of the query
            safe_query = self._create_safe_filename(query)
            
            # Limit the query length in the filename
            if len(safe_query) > 50:
                safe_query = safe_query[:50]
            
            # Put timestamp first for chronological sorting
            log_file = self._log_dir / f"wikipedia_{safe_query}.txt"
            
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("=== WIKIPEDIA TOOL INTERACTION ===\n\n")
                f.write(f"Timestamp: {timestamp}\n\n")
                f.write("=== INPUT ===\n")
                f.write(f"Query: {query}\n\n")
                f.write("=== OUTPUT ===\n")
                f.write(f"{response}\n")
            
            print(f"Wikipedia interaction logged to: {log_file}")
            return log_file
        except Exception as e:
            print(f"Error writing Wikipedia log file: {e}")
            # Try writing to a different location as fallback
            try:
                fallback_file = Path.home() / f"{timestamp}_wikipedia_{safe_query}.txt"
                with open(fallback_file, "w", encoding="utf-8") as f:
                    f.write("=== WIKIPEDIA TOOL INTERACTION ===\n\n")
                    f.write(f"Timestamp: {timestamp}\n\n")
                    f.write("=== INPUT ===\n")
                    f.write(f"Query: {query}\n\n")
                    f.write("=== OUTPUT ===\n")
                    f.write(f"{response}\n")
                print(f"Wrote Wikipedia log to fallback location: {fallback_file}")
                return fallback_file
            except Exception as e2:
                print(f"Failed to write Wikipedia log to fallback location: {e2}")
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
    
    def _parse_input(self, tool_input):
        """Parse the input before validation."""
        if isinstance(tool_input, str):
            return {"query": tool_input}
        return tool_input
    
    def _run(self, query) -> str:
        """Run the Wikipedia tool."""
        # Generate timestamp for logging
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Handle different input formats
            if isinstance(query, dict):
                if 'query' in query:
                    query = query['query']
                elif 'input' in query:
                    query = query['input']
                elif len(query) == 1:  # If there's only one key-value pair
                    query = list(query.values())[0]
                else:
                    error_msg = "Error: Could not extract query from dictionary input. Please provide a simple string query."
                    self._log_interaction(str(query), error_msg, timestamp)
                    return error_msg
            
            # Ensure query is a string
            if not isinstance(query, str):
                error_msg = f"Error: Expected string query but got {type(query)}. Please provide a simple string query."
                self._log_interaction(str(query), error_msg, timestamp)
                return error_msg
            
            # Search Wikipedia
            search_results = wikipedia.search(query, results=5)
            
            if not search_results:
                error_msg = f"No Wikipedia articles found for '{query}'."
                self._log_interaction(query, error_msg, timestamp)
                return error_msg
            
            # Try to get the most relevant page
            page = None
            error_messages = []
            
            for result in search_results:
                try:
                    page = wikipedia.page(result, auto_suggest=False)
                    break  # Found a valid page
                except wikipedia.DisambiguationError as e:
                    # If there's a disambiguation page, try the first option
                    try:
                        page = wikipedia.page(e.options[0], auto_suggest=False)
                        break  # Found a valid page from disambiguation
                    except Exception as inner_e:
                        error_messages.append(f"Disambiguation error for '{result}': {str(inner_e)}")
                except Exception as e:
                    error_messages.append(f"Error retrieving page '{result}': {str(e)}")
            
            if not page:
                if error_messages:
                    error_msg = f"Could not retrieve Wikipedia page for '{query}'. Errors: {'; '.join(error_messages)}"
                    self._log_interaction(query, error_msg, timestamp)
                    return error_msg
                else:
                    error_msg = f"Could not retrieve Wikipedia page for '{query}'."
                    self._log_interaction(query, error_msg, timestamp)
                    return error_msg
            
            # Format the result
            result = f"# Wikipedia: {page.title}\n\n"
            
            # Get a summary (first few paragraphs)
            summary = page.summary
            if len(summary) > 1500:
                summary = summary[:1500] + "..."
            
            result += summary + "\n\n"
            
            # Add sections if available
            if hasattr(page, 'sections') and page.sections:
                result += "## Key Sections\n\n"
                for section in page.sections[:5]:  # Limit to first 5 sections
                    result += f"- {section}\n"
                
                if len(page.sections) > 5:
                    result += f"- ... and {len(page.sections) - 5} more sections\n"
                
                result += "\n"
            
            # Add URL for reference
            result += f"For more information: {page.url}\n\n"
            
            # Add search results for reference
            if len(search_results) > 1:
                result += "## Other Relevant Articles\n\n"
                for i, title in enumerate(search_results[1:5], 1):
                    if title != page.title:
                        result += f"{i}. {title}\n"
                result += "\n"
            
            # Log the successful interaction
            self._log_interaction(query, result, timestamp)
            
            return result
            
        except Exception as e:
            error_msg = f"Error searching Wikipedia: {str(e)}"
            self._log_interaction(query if isinstance(query, str) else str(query), error_msg, timestamp)
            return error_msg 