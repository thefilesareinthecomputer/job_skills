import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.job_skills.tools.serper_tool import SerperTool
from dotenv import load_dotenv

load_dotenv()

def test_serper_knowledge_graph():
    """Test the SerperTool with queries likely to return knowledge graph data."""
    
    # Create the tool
    tool = SerperTool()
    
    # Test queries that are likely to return knowledge graph data
    test_queries = [
        "TensorFlow",
        "PyTorch",
        "OpenAI",
        "machine learning",
        "artificial intelligence",
        "neural networks",
        "deep learning"
    ]
    
    # Run tests
    kg_found = False
    
    for query in test_queries:
        print(f"\n{'='*80}\nTesting query: {query}\n{'='*80}\n")
        
        # Run the tool
        result = tool._run(query, num_results=3)
        
        # Print the result
        print(result)
        
        # Check if knowledge graph data is present
        if "## Knowledge Graph" in result:
            print(f"\n✅ Knowledge Graph found for query: '{query}'")
            kg_found = True
        else:
            print(f"\n❌ No Knowledge Graph found for query: '{query}'")
    
    if kg_found:
        print("\n✅ At least one query returned Knowledge Graph data!")
    else:
        print("\n❌ No Knowledge Graph data found in any query. This might be normal depending on the queries.")

if __name__ == "__main__":
    test_serper_knowledge_graph() 