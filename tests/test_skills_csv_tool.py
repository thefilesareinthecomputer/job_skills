import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path so we can import the tool
sys.path.append(str(Path(__file__).parent.parent))

from src.job_skills.tools.skills_csv_tool import SkillsCSVTool

def test_skills_csv_tool():
    """Test the Skills CSV tool."""
    
    print("🧪 Testing Skills CSV Tool")
    
    # Print the current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")
    
    # Get the CSV path from environment variable
    csv_path = os.getenv("SKILLS_CSV_PATH")
    if not csv_path:
        print("❌ SKILLS_CSV_PATH environment variable not set")
        return False
    
    print(f"CSV path from environment: {csv_path}")
    print(f"CSV file exists: {os.path.exists(csv_path)}")
    
    # Ensure the directory exists before creating the tool
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at {csv_path}")
        return False
    
    # Create the tool
    tool = SkillsCSVTool()
    
    print(f"🔄 Reading skills from CSV file")
    
    # Test with a general query first
    query = "List all skills"
    print(f"\n--- Testing with query: '{query}' ---")
    result = tool._run(query)
    print(result[:1000] + "..." if len(result) > 1000 else result)
    
    # Test with a more specific query
    query = "Python"
    print(f"\n--- Testing with query: '{query}' ---")
    result = tool._run(query)
    print(result[:1000] + "..." if len(result) > 1000 else result)
    
    # Verify the tool is using the correct CSV file
    if hasattr(tool, '_csv_path'):
        print(f"\nTool is using CSV file at: {tool._csv_path}")
        if tool._csv_path != csv_path:
            print(f"❌ Tool is using a different CSV file than specified in the environment variable")
            return False
    
    if result and not result.startswith("Error"):
        print("\n✅ Skills CSV Tool test completed successfully!")
        return True
    else:
        print("\n❌ Skills CSV Tool test failed.")
        return False

if __name__ == "__main__":
    test_skills_csv_tool() 