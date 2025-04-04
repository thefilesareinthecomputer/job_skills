from crewai.tools import BaseTool
from typing import Type, Optional, Union
from pydantic import BaseModel, Field
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# https://docs.crewai.com/tools/csvsearchtool

class SkillsCSVToolInput(BaseModel):
    """Input schema for SkillsCSVTool."""
    query: str = Field(..., description="Query to search for skills or get all skills.")

class SkillsCSVTool(BaseTool):
    name: str = "AI/ML Skills Dataset"
    description: str = (
        "Access a dataset of real AI/ML skills extracted from job postings. "
        "This tool provides information about in-demand skills for AI Engineers and ML Engineers "
        "based on actual job listings. Use this to understand the exact terminology and skills "
        "that current employers on job boards are looking for before conducting further research."
    )
    args_schema: Type[BaseModel] = SkillsCSVToolInput
    
    def __init__(self):
        """Initialize the tool with the path to the CSV file."""
        super().__init__()
        
        # Use the exact path to the real CSV file
        self._csv_path = os.getenv("SKILLS_CSV_PATH")
        
        # Verify the file exists
        if os.path.exists(self._csv_path):
            print(f"Using real CSV file at: {self._csv_path}")
        else:
            print(f"WARNING: Real CSV file not found at: {self._csv_path}")
            
            # Try to find the project root as a fallback
            project_root = self._find_project_root()
            fallback_path = os.path.join(project_root, "src", "output", "skill_analysis.csv")
            
            if os.path.exists(fallback_path):
                self._csv_path = fallback_path
                print(f"Using fallback CSV file at: {self._csv_path}")
    
    def _find_project_root(self):
        """Find the project root directory (not including 'job_skills' twice)."""
        current_path = Path(os.getcwd()).resolve()
        
        # Navigate up until we find the first 'job_skills' directory
        while current_path.name != 'job_skills' and current_path != current_path.parent:
            current_path = current_path.parent
            
        # If we found 'job_skills', return its parent to avoid nested 'job_skills/job_skills'
        if current_path.name == 'job_skills':
            return current_path.parent / 'job_skills'
        
        # Fallback to current directory
        return Path(os.getcwd()).resolve()
    
    def _parse_input(self, tool_input):
        """Parse the input before validation."""
        if isinstance(tool_input, str):
            return {"query": tool_input}
        return tool_input
    
    def _run(self, query) -> str:
        """Run the Skills CSV tool."""
        try:
            # Handle different input formats
            if isinstance(query, dict):
                # If it's a dictionary, extract the query
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
            
            # Check if the CSV file exists
            if not os.path.exists(self._csv_path):
                return f"Error: CSV file not found at {self._csv_path}. Please ensure the file exists at this location."
            
            # Read the CSV file
            df = pd.read_csv(self._csv_path)
            
            # Basic validation of the dataframe
            if df.empty:
                return "The skills CSV file is empty."
            
            # Print column names for debugging
            columns = df.columns.tolist()
            result = f"# AI/ML Skills from Job Postings\n\n"
            result += f"Found CSV with columns: {', '.join(columns)}\n\n"
            
            # If query is for listing all skills or general information
            if "list all" in query.lower() or "show all" in query.lower() or "skill" in query.lower() or "all" in query.lower() or "skills" in query.lower() or "top 50" in query.lower() or "get all" in query.lower():
                result += "## Top AI/ML Skills by Occurrence\n\n"
                
                # Sort by occurrences (descending)
                if 'occurrences' in columns:
                    df = df.sort_values('occurrences', ascending=False)
                
                # Get the top 50 skills
                top_skills = df.head(50)
                for index, row in top_skills.iterrows():
                    result += self._format_row(row, columns)
                
                # Add note about total skills
                if len(df) > 25:
                    result += f"\n*Showing top 50 skills out of {len(df)} total skills.*\n"
            # Otherwise, filter based on the query
            else:
                # Convert all columns to string for searching
                for col in columns:
                    df[col] = df[col].astype(str)
                
                # Search in all columns
                mask = df.apply(lambda row: any(query.lower() in val.lower() for val in row), axis=1)
                filtered_df = df[mask]
                
                if filtered_df.empty:
                    result += f"No skills found matching '{query}'.\n\n"
                    result += "Here are the top 10 skills by occurrence instead:\n\n"
                    # Show top skills instead
                    if 'occurrences' in columns:
                        df = df.sort_values('occurrences', ascending=False)
                    for index, row in df.head(10).iterrows():
                        result += self._format_row(row, columns)
                else:
                    result += f"## Skills matching '{query}'\n\n"
                    # Sort by occurrences if available
                    if 'occurrences' in columns:
                        filtered_df = filtered_df.sort_values('occurrences', ascending=False)
                    for index, row in filtered_df.iterrows():
                        result += self._format_row(row, columns)
            
            result += f"\n## Summary\n"
            result += f"Total skills in dataset: {len(df)}\n"
            
            return result
                
        except Exception as e:
            return f"Error reading skills CSV: {str(e)}"
    
    def _format_row(self, row, columns):
        """Format a row of data as a markdown bullet point."""
        skill_info = "- "
        
        # For the actual file structure with 'skill' and 'occurrences'
        if 'skill' in columns and 'occurrences' in columns:
            skill_info += f"{row['skill']} ({row['occurrences']} occurrences)\n"
        else:
            # Fallback for other column structures
            details = []
            for col in columns:
                if pd.notna(row[col]) and row[col] != "nan":
                    details.append(f"**{col}**: {row[col]}")
            skill_info += ", ".join(details) + "\n"
        
        return skill_info 