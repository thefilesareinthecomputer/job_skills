from crewai.tools import BaseTool
from typing import Type, Optional, Union
from pydantic import BaseModel, Field
import wikipedia
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
    
    def _parse_input(self, tool_input):
        """Parse the input before validation."""
        if isinstance(tool_input, str):
            return {"query": tool_input}
        return tool_input
    
    def _run(self, query) -> str:
        """Run the Wikipedia tool."""
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
                    return "Error: Could not extract query from dictionary input. Please provide a simple string query."
            
            # Ensure query is a string
            if not isinstance(query, str):
                return f"Error: Expected string query but got {type(query)}. Please provide a simple string query."
            
            # Search Wikipedia
            search_results = wikipedia.search(query, results=5)
            
            if not search_results:
                return f"No Wikipedia articles found for '{query}'."
            
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
                    return f"Could not retrieve Wikipedia page for '{query}'. Errors: {'; '.join(error_messages)}"
                else:
                    return f"Could not retrieve Wikipedia page for '{query}'."
            
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
            
            return result
            
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}" 