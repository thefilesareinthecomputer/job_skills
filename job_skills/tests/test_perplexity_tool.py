import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the tool
sys.path.append(str(Path(__file__).parent.parent))

from src.job_skills.tools.perplexity_tool import PerplexityTool

def test_perplexity_tool():
    """Test the Perplexity tool."""
    
    print("🧪 Testing Perplexity Tool")
    
    # Create the tool
    tool = PerplexityTool()
    
    # Test query
    query = "What are the top 5 programming languages for AI Engineers in 2025?"
    
    print(f"🔄 Sending query to Perplexity: '{query}'")
    
    # Run the tool
    result = tool._run(query)
    
    # Print the result
    print("\n--- Response Content ---")
    print(result)
    
    if result and not result.startswith("Error"):
        print("\n✅ Perplexity Tool test completed successfully!")
        return True
    else:
        print("\n❌ Perplexity Tool test failed.")
        return False

if __name__ == "__main__":
    test_perplexity_tool() 