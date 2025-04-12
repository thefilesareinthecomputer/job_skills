import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.job_skills.tools.serper_tool import SerperTool

from dotenv import load_dotenv

load_dotenv()

def test_serper_tool():
    """Test the SerperTool with various AI/ML related queries."""
    
    # Create the tool
    tool = SerperTool()
    
    # Test queries related to AI/ML
    test_queries = [
        "latest advancements in transformer models",
        "best practices for fine-tuning LLMs",
        "Python libraries for machine learning",
        "TensorFlow vs PyTorch comparison",
        "how to implement a neural network from scratch"
    ]
    
    # Run tests
    for query in test_queries:
        print(f"\n{'='*80}\nTesting query: {query}\n{'='*80}\n")
        
        # Run the tool
        result = tool._run(query, num_results=3)
        
        # Print the result
        print(result)
        
        # Check if the result contains useful information
        assert len(result) > 100, f"Result for '{query}' is too short, might indicate an error"
        assert "Error" not in result[:20], f"Error detected in result for '{query}'"
        
        print(f"\n{'='*80}\nTest passed for: {query}\n{'='*80}\n")
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_serper_tool() 